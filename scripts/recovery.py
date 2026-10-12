#!/usr/bin/env python3
"""Respaldo privado y ensayo aislado BoviCierre; nunca elimina volúmenes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
import urllib.request
import http.cookiejar
import shlex
import uuid

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = Path.home() / '.local/share/bovicierre-academic'
SECRETS = Path(os.environ.get('BOVI_SECRET_DIR', PRIVATE / 'secrets'))
DOCS = Path(os.environ.get('BOVI_DOCUMENTS_DIR', PRIVATE / 'private-documents'))
SOURCE = 'bovicierre-academic'


def run(args, **kwargs):
    result = subprocess.run(args, capture_output=True, **kwargs)
    if result.returncode:
        # Never forward connection strings or private command stderr.
        raise RuntimeError(f'{Path(args[0]).name}: exit {result.returncode}; consulta el diagnóstico privado del proceso')
    return result.stdout


def sql(project, node, query):
    name = f'{project}-pg-{node}-1'
    label = run(['docker', 'inspect', '--format', '{{index .Config.Labels "com.docker.compose.project"}}', name], text=True).strip()
    if label != project or not project.startswith('bovicierre-'):
        raise RuntimeError('Contenedor ajeno al proyecto indicado')
    return run(['docker', 'exec', '-i', name, 'psql', '-X', '-qAt', '-U', 'postgres', '-d', 'bovicierre', '-v', 'ON_ERROR_STOP=1'], input=query, text=True).strip()


def manifest(directory):
    records = {}
    if not directory.exists():
        return records
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise RuntimeError('No se respaldan enlaces simbólicos de documentos')
        if path.is_file():
            records[str(path.relative_to(directory))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return records


def signature(project, node):
    tables = sql(project, node, "SELECT tablename FROM pg_tables WHERE schemaname='bovi' AND tablename NOT IN ('clave_idempotencia','mensaje_inbox') ORDER BY tablename").splitlines()
    return {table: sql(project, node, f"SELECT count(*)::text||':'||coalesce(md5(string_agg(md5(to_jsonb(t)::text),'' ORDER BY md5(to_jsonb(t)::text))),md5('')) FROM bovi.{table} t") for table in tables}


def local_signature(project, node):
    return {table: sql(project, node, f"SELECT count(*)::text||':'||coalesce(md5(string_agg(md5(to_jsonb(t)::text),'' ORDER BY md5(to_jsonb(t)::text))),md5('')) FROM {table} t") for table in ('bovi.clave_idempotencia', 'bovi.mensaje_inbox', 'infra.entrega_outbox', 'infra.tarifa_snapshot', 'infra.flyway_schema_history')}


def private_dir(path):
    path.mkdir(parents=True, exist_ok=False, mode=0o700)
    os.chmod(path, 0o700)


def backend_mode(pid):
    container = SOURCE + '-backend-1'
    state = subprocess.run(['docker', 'inspect', '--format', '{{index .Config.Labels "com.docker.compose.project"}} {{.State.Running}}', container], capture_output=True, text=True)
    running = state.returncode == 0 and state.stdout.strip() == SOURCE + ' true'
    pid_file = PRIVATE / 'run/api.pid'
    if pid is None and pid_file.exists():
        pid = int(pid_file.read_text().strip())
    process = Path(f'/proc/{pid}') if pid is not None else None
    native = bool(process and process.exists() and process.joinpath('cwd').resolve() == ROOT / 'backend' and b'java' in process.joinpath('cmdline').read_bytes())
    if native:
        environment = dict(item.split(b'=', 1) for item in process.joinpath('environ').read_bytes().split(b'\0') if b'=' in item)
        native = environment.get(b'BOVI_API_PORT', b'18080') == b'18080' and environment.get(b'BOVI_RUNTIME_DIR', str(PRIVATE / 'run').encode()) == str(PRIVATE / 'run').encode()
    if native and running:
        raise RuntimeError('Dos API concurrentes; detener una antes de respaldar')
    if running:
        return container, None
    if native:
        return None, process
    raise RuntimeError('No se identificó API propia activa de este checkout/proyecto')


def backup(destination, pid):
    api_container, process = backend_mode(pid)
    if destination.is_relative_to(ROOT):
        raise RuntimeError('El respaldo privado debe quedar fuera del checkout')
    private_dir(destination)
    started = time.monotonic()
    restart = False
    try:
        if api_container:
            run(['docker', 'stop', '--time', '40', api_container], text=True)
            restart = True
            if run(['docker', 'inspect', '--format', '{{.State.Running}}', api_container], text=True).strip() != 'false':
                raise RuntimeError('La API de contenedor no terminó; no se respalda')
        else:
            os.kill(int(process.name), signal.SIGTERM)
            for _ in range(160):
                if not process.exists():
                    break
                time.sleep(.25)
            else:
                raise RuntimeError('Backend no terminó de forma gradual; no se respalda')
        restart = True
        for node in ('a', 'b'):
            active = sql(SOURCE, node, "SELECT count(*) FROM pg_stat_activity WHERE datname=current_database() AND pid<>pg_backend_pid() AND backend_type='client backend' AND xact_start IS NOT NULL")
            if active != '0':
                raise RuntimeError('Hay otra transacción cliente activa; no hay pausa consistente')
            pending = sql(SOURCE, node, "SELECT count(*) FROM bovi.evento_outbox e LEFT JOIN infra.entrega_outbox d ON d.evento_id=e.id AND d.destino=CASE WHEN e.tipo_evento='ANIMAL_MUERTO' THEN 'A' ELSE 'LOCAL' END WHERE e.propietario_despacho=bovi.fn_nodo() AND d.confirmado_en IS NULL")
            if pending != '0':
                raise RuntimeError('Mensajes pendientes; resolver antes del respaldo')
        a, b = signature(SOURCE, 'a'), signature(SOURCE, 'b')
        if a != b:
            raise RuntimeError('No se verificó convergencia A/B; no se respalda')
        source_secrets, source_documents = manifest(SECRETS), manifest(DOCS)
        shutil.copytree(SECRETS, destination / 'secrets')
        for path in (destination / 'secrets').iterdir():
            os.chmod(path, 0o600)
        if DOCS.exists():
            shutil.copytree(DOCS, destination / 'documents')
        if manifest(destination / 'secrets') != source_secrets or manifest(destination / 'documents') != source_documents:
            raise RuntimeError('La copia privada cambió durante el respaldo')
        for node in ('a', 'b', 'prov'):
            container = f'{SOURCE}-pg-{node}-1'
            data = run(['docker', 'exec', container, 'pg_dump', '-U', 'postgres', '-d', 'bovicierre', '-Fc', '--no-publications', '--no-subscriptions', '--exclude-table-data=infra.spring_session*'])
            (destination / f'{node}.dump').write_bytes(data)
            roles = run(['docker', 'exec', container, 'pg_dumpall', '-U', 'postgres', '--roles-only'])
            (destination / f'{node}-roles.sql').write_bytes(roles)
        if manifest(SECRETS) != source_secrets or manifest(DOCS) != source_documents:
            raise RuntimeError('La fuente privada cambió durante la pausa')
        local_signatures = {node: local_signature(SOURCE, node) for node in ('a', 'b')}
        artifacts = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in destination.iterdir() if path.is_file()}
        report = {'artifacts': artifacts, 'local_signatures': local_signatures, 'format': 1, 'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'source_project': SOURCE, 'signature': a, 'documents': manifest(destination / 'documents'), 'pause_seconds': round(time.monotonic() - started, 3), 'revision': run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(), 'dirty': bool(run(['git', '-C', str(ROOT), 'status', '--porcelain'], text=True))}
        (destination / 'manifest.json').write_text(json.dumps(report, indent=2))
        for path in destination.iterdir():
            if path.is_file():
                os.chmod(path, 0o600)
        print(f'Respaldo privado: {destination}; pausa {report["pause_seconds"]} s')
    finally:
        if restart:
            if api_container:
                run(['docker', 'start', api_container], text=True)
            else:
                log_path = PRIVATE / 'backend-restarted.log'
                log = open(log_path, 'ab')
                os.chmod(log_path, 0o600)
                env = {**os.environ, 'BOVI_SECRETS_DIR': str(SECRETS), 'BOVI_DOCUMENTS_DIR': str(DOCS)}
                subprocess.Popen(['./run-local.sh'], cwd=ROOT / 'backend', stdout=log, stderr=log, env=env, start_new_session=True)
                log.close()



def restore(destination):
    import yaml
    expected = json.loads((destination / 'manifest.json').read_text())
    if expected['source_project'] != SOURCE or expected['format'] != 1:
        raise RuntimeError('Manifest no pertenece al respaldo BoviCierre esperado')
    if manifest(destination / 'documents') != expected['documents']:
        raise RuntimeError('Los archivos no coinciden con el manifest')
    for name, digest in expected['artifacts'].items():
        if Path(name).name != name or hashlib.sha256((destination / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('Un dump o archivo de roles no coincide con el manifest')
    project = 'bovicierre-restore-' + time.strftime('%Y%m%d%H%M%S', time.gmtime())
    work = destination / project
    private_dir(work)
    config = yaml.safe_load((ROOT / 'infra/compose/compose.academic.yml').read_text())
    config['name'] = project
    for name, service in config['services'].items():
        if name.startswith('pg-'):
            port = {'pg-a': 18432, 'pg-b': 18433, 'pg-prov': 18434}[name]
            service['ports'] = [f'127.0.0.1:{port}:5432']
        else:
            service['ports'] = [f'127.0.0.1:{18999 if name=="pgpool-a" else 18998}:9999']
            service['build'] = str(ROOT / 'infra/pgpool')
            service['volumes'] = [str(ROOT / 'infra/pgpool' / value.split(':')[0].split('/')[-1]) + ':' + ':'.join(value.split(':')[1:]) for value in service['volumes']]
    compose = work / 'compose.yml'
    compose.write_text(yaml.safe_dump(config, sort_keys=False))
    env = {**os.environ, 'BOVI_SECRET_DIR': str(destination / 'secrets'), 'BOVI_COMPOSE_PROJECT': project, 'BOVI_RESTORE_CONVERGED': '1'}
    command = ['docker', 'compose', '-p', project, '-f', str(compose)]
    started = time.monotonic()
    try:
        run(command + ['up', '-d', '--build', '--wait'], env=env)
        for node in ('a', 'b', 'prov'):
            roles = (destination / f'{node}-roles.sql').read_text()
            roles = '\n'.join(line for line in roles.splitlines() if line != 'CREATE ROLE postgres;')
            sql(project, node, roles)
            container = f'{project}-pg-{node}-1'
            # Host aliases are resolved only inside this project's private network.
            run(['docker', 'exec', '-i', container, 'pg_restore', '-U', 'postgres', '-d', 'bovicierre', '--exit-on-error'], input=(destination / f'{node}.dump').read_bytes())
        for node in ('a', 'b'):
            # El ACL de la base (V14/SF-08: PUBLIC sin TEMP) no viaja en pg_dump sin --create.
            sql(project, node, 'REVOKE TEMPORARY ON DATABASE bovicierre FROM PUBLIC')
            assert sql(project, node, "SELECT has_database_privilege('bovi_auditor',current_database(),'TEMP')") == 'f'
        assert signature(project, 'a') == expected['signature']
        assert signature(project, 'b') == expected['signature']
        for node, records in expected['local_signatures'].items():
            assert local_signature(project, node) == records
        shutil.copytree(destination / 'documents', work / 'documents') if (destination / 'documents').exists() else None
        assert manifest(work / 'documents') == expected['documents']
        # Existing source subscriptions were excluded; bootstrap creates only local aliases.
        run(['python3', str(ROOT / 'db/bootstrap/bootstrap.py')], env=env)
        for node in ('a', 'b'):
            assert sql(project, node, 'SELECT count(*) FROM infra.spring_session') == '0'
            assert sql(project, node, "SELECT count(*) FROM pg_subscription WHERE subdbid=(SELECT oid FROM pg_database WHERE datname=current_database()) AND subconninfo !~ 'host=pg-[ab] '") == '0'
    except Exception:
        subprocess.run(command + ['stop'], env=env, capture_output=True)
        raise
    report = {'project': project, 'seconds': round(time.monotonic()-started, 3), 'signature_match': True, 'document_hashes_match': True, 'sessions_invalidated': True, 'idempotency_inbox_preserved': True, 'publications_recreated': True, 'limitations': 'Aún requiere prueba de nueva operación/idempotencia y descarga HTTP restauradas; no acredita PITR ni pérdida del host.'}
    (work / 'result.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print('Ensayo conserva sus volúmenes. Detener sin borrar: BOVI_SECRET_DIR=' + shlex.quote(str(destination/'secrets')) + ' ' + shlex.join(command + ['stop']))


def verify_http(destination):
    """API restaurada en el puerto exclusivo18180; jamás usa el puerto fuente18080."""
    import datetime
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    base = 'http://127.0.0.1:18180/api/v1'
    csrf = {}

    def call(method, path, payload=None, key=None, match=None, binary=False):
        headers = {'Content-Type': 'application/json'}
        if csrf:
            headers[csrf['headerName']] = csrf['token']
        if key:
            headers['Idempotency-Key'] = key
        if match:
            headers['If-Match'] = match
        data = json.dumps(payload).encode() if payload is not None else None
        with opener.open(urllib.request.Request(base+path, data=data, headers=headers, method=method), timeout=15) as response:
            raw = response.read()
            return raw if binary else (json.loads(raw) if raw else None)

    csrf.update(call('GET', '/sesion/csrf'))
    call('POST', '/sesion/login', {'login': 'demo.admin', 'contrasena': (destination/'secrets/demo_password').read_text().strip()})
    csrf.update(call('GET', '/sesion/csrf'))
    session = call('GET', '/sesion/actual')
    assert session['usuario_id'] == '99999999-9999-4999-8999-999999999999'
    site = '/sedes/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
    documents = call('GET', site+'/documentos?tamano=100')['elementos']
    if not documents:
        raise RuntimeError('Sin documento restaurado: no se acredita recuperación de archivos')
    document = documents[0]
    raw = call('GET', site+'/documentos/'+document['id']+'/contenido', binary=True)
    assert hashlib.sha256(raw).hexdigest() == document['sha256']
    from zoneinfo import ZoneInfo
    today = datetime.datetime.now(ZoneInfo('America/Mexico_City')).date().isoformat()
    periods = call('GET', site+'/periodos?tamano=100')['elementos']
    period = next(p for p in periods if p['estado']=='ABIERTO' and p['desde'] <= today <= p['hasta'])
    recognition = {'periodo_id': period['id'], 'fecha_reconocimiento': today}
    key = str(uuid.uuid4())
    party_body = {'nombre': 'DEMO RESTAURACION '+key}
    party = call('POST', site+'/contrapartes', party_body, key)
    assert call('POST', site+'/contrapartes', party_body, key) == party
    animal = call('POST', site+'/animales', {'sexo':'M','identificaciones':[{'sistema':'INTERNO','codigo':'DEMO '+uuid.uuid4().hex}]}, str(uuid.uuid4()))
    operation = call('POST', site+'/operaciones', {'tipo':'COMPRA','parte_id':party['id'],'fecha_operacion':today,'lotes':[{'unidad_precio':'CABEZA','precio_unitario':'1000.0000','animales':[animal['id']]}]}, str(uuid.uuid4()))
    detail = call('GET', site+'/operaciones/'+operation['id'])
    key = str(uuid.uuid4())
    path = site+'/operaciones/'+operation['id']+'/confirmar'
    etag = '"'+str(detail['version_lock'])+'"'
    confirmed = call('POST', path, recognition, key, etag)
    assert confirmed['total']['importe'] == '1000.00'
    assert call('POST', path, recognition, key, etag) == confirmed
    lookup = call('GET', site+'/comandos/confirmar_operacion/'+key)
    assert lookup['estado'] == 'COMPLETADA' and lookup['resultado'] == confirmed
    inventory = call('GET', site+'/inventario/posiciones?tamano=100&q='+animal['id'])['elementos']
    assert any(p['animal_id']==animal['id'] for p in inventory)
    call('POST', '/sesion/logout', {})
    report = {'restored_document_hash_match': True, 'new_purchase_total':'1000.00', 'retry_original_etag_same_result':True, 'lookup_completed':True, 'inventory_persisted':True, 'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    (destination/'http-result.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['backup', 'restore-check', 'verify-http', 'self-check'])
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--api-pid', type=int)
    args = parser.parse_args()
    if args.action == 'self-check':
        import tempfile
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            (path / 'sample').write_text('DEMO')
            assert manifest(path)['sample'] == hashlib.sha256(b'DEMO').hexdigest()
            (path / 'link').symlink_to(path / 'sample')
            try:
                manifest(path)
            except RuntimeError:
                pass
            else:
                raise AssertionError('Symlink must be rejected')
        print('recovery self-check OK')
    elif args.directory is None:
        parser.error('Indica --directory privado; --api-pid es opcional para la API manual')
    elif args.action == 'backup':
        backup(args.directory.resolve(), args.api_pid)
    elif args.action == 'verify-http':
        verify_http(args.directory.resolve())
    else:
        restore(args.directory.resolve())


if __name__ == '__main__':
    main()
