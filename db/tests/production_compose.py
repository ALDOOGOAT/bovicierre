#!/usr/bin/env python3
"""Valida la combinación Compose sin crear servicios ni leer secretos."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
work = Path(tempfile.mkdtemp(prefix='bovi-production-review-'))
os.chmod(work, 0o700)
env = {**os.environ, 'BOVI_DOMAIN': 'bovicierre.example.invalid',
       'TLS_CONTACT_EMAIL': 'revision@example.invalid',
       'BOVI_PRIVATE_DIR': str(work / 'private'),
       'BOVI_SECRET_DIR': str(work / 'private/secrets'),
       'BOVI_UID': '1000', 'BOVI_GID': '1000'}
command = ['docker', 'compose', '-p', 'bovicierre-production-review']
for name in ('compose.academic.yml', 'application.yml', 'production.example.yml'):
    command += ['-f', str(ROOT / 'infra/compose' / name)]
result = subprocess.run(command + ['config', '--format', 'json'], env=env,
                        text=True, capture_output=True, check=True)
resolved = work / 'compose-resolved.json'
resolved.touch(mode=0o600)
resolved.write_text(result.stdout)
config = json.loads(result.stdout)
services = config['services']
assert config['name'] == 'bovicierre-production-review'
assert all(not services[name].get('ports') for name in
           ('pg-a', 'pg-b', 'pg-prov', 'pgpool-a', 'pgpool-b'))
ports = {(port['published'], port['target'], port['protocol'])
         for port in services['caddy']['ports']}
assert ports == {('80', 80, 'tcp'), ('443', 443, 'tcp'), ('443', 443, 'udp')}
assert services['backend']['environment']['BOVI_ENV'] == 'production'
assert services['backend']['environment']['SPRING_PROFILES_ACTIVE'] == 'production'
assert services['caddy']['user'] == '1000:1000'
assert len(services['caddy']['tmpfs']) == 1
assert services['caddy']['tmpfs'][0].startswith('/tmp:')
mounts = {volume['target']: volume for volume in services['caddy']['volumes']}
assert mounts['/etc/caddy/Caddyfile']['source'].endswith('Caddyfile.production.example')
assert mounts['/etc/caddy/Caddyfile']['read_only']
for target, name in (('/data', 'caddy-data'), ('/config', 'caddy-config')):
    assert mounts[target]['type'] == 'volume' and mounts[target]['source'] == name
    assert config['volumes'][name]['driver_opts']['device'] == str(work / 'private' / name)
assert services['caddy']['environment']['TLS_CONTACT_EMAIL'] == 'revision@example.invalid'
assert not any(word in name for name in services for word in ('seed', 'bootstrap', 'migrate'))
report = {'resultado': 'PASS', 'comando': 'docker compose config --format json',
          'proyecto_revision': config['name'], 'servicios_arrancados': 0,
          'dns_tls_real': False, 'puertos_db_pgpool_eliminados': True,
          'caddy_tcp': [80, 443], 'caddy_udp': [443],
          'perfil_api': 'production', 'caddy_uid_gid': '1000:1000',
          'caddy_estado_persistente': True, 'bootstrap_semilla_automaticos': False,
          'configuracion_resuelta_privada': str(resolved),
          'limite': 'Sólo configuración; no acredita VM, TLS ni permisos reales de volúmenes.'}
(ROOT / 'db/tests/production-compose-result.json').write_text(
    json.dumps(report, indent=2, ensure_ascii=False) + '\n')
print(json.dumps(report, indent=2, ensure_ascii=False))
