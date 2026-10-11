#!/usr/bin/env python3
"""Comandos DEMO idempotentes y lecturas canónicas QA; jamás modifica main."""
import argparse
import concurrent.futures
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import statistics
import subprocess
import threading
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads((ROOT / 'data/synthetic/benchmark.json').read_text())
DB = 'bovicierre_release_replay'
DATASET = 'DEMO-BENCH-V11'
E = '11111111-1111-4111-8111-111111111111'
S = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
U = '99999999-9999-4999-8999-999999999999'
STATE = ROOT / 'db/tests/benchmark-dataset-result.json'
CALLS = {}
FINANCIAL = {'confirmar_operacion', 'registrar_gasto', 'repartir_gasto',
             'validar_pago', 'aplicar_pago'}


def connect(pool=False, readonly=False):
    # Mismo patrón de conexión del harness academic; no se importa su ejecución.
    import psycopg
    secret = Path(os.environ.get('BOVI_SECRET_DIR',
                  Path.home() / '.local/share/bovicierre-academic/secrets'))
    options = '-c statement_timeout=10000 -c lock_timeout=2000'
    if readonly:
        options += ' -c default_transaction_read_only=on'
    return psycopg.connect(host='127.0.0.1', port=19999 if pool else 15432,
                           dbname=DB, user='bovi_app_a',
                           password=(secret / 'app_a_password').read_text().strip(),
                           options=options, autocommit=readonly)


def guard(connection):
    assert connection.execute('SELECT current_database()').fetchone()[0] == DB
    assert connection.execute('SHOW server_version_num').fetchone()[0].startswith('18')
    company = connection.execute('SELECT razon_social FROM bovi.empresa WHERE id=%s',
                                 (E,)).fetchone()
    assert company and company[0].startswith('DEMO ')
    assert connection.execute('SELECT bovi.fn_nodo()').fetchone()[0] == 'A'
    # Runtime no tiene SELECT del historial administrativo; no ampliar grants.
    definition = connection.execute("SELECT pg_get_functiondef("
            "'bovi.cmd_ejecutar(uuid,uuid,uuid,text,text,uuid,text,jsonb)'::regprocedure)").fetchone()[0]
    assert "WHEN 'cancelar_operacion'" in definition
    assert definition.count("IF NOT FOUND OR op.version_lock IS DISTINCT FROM") >= 3
    assert 'composicion_distinta' in definition and 'motivo_correccion' in definition
    return {'version_funciones_validada': 'V13', 'cmd_sha256': hashlib.sha256(definition.encode()).hexdigest(),
            'nota': 'Dataset V11 conserva namespace histórico; ejecución actual valida funciones V13.'}


def command(connection, name, step, body, financial):
    # Interfaz y hash del harness/semilla; no INSERT/UPDATE financiero directo.
    from psycopg.types.json import Jsonb
    payload = {**financial, **body} if name in FINANCIAL else body
    key = DATASET + '-' + step
    assert 16 <= len(key) <= 80
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    CALLS[name] = CALLS.get(name, 0) + 1
    return connection.execute('SELECT bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',
                              (E, S, U, key, digest, uuid.uuid4(), name,
                               Jsonb(payload))).fetchone()[0]


def money(amount):
    return {'importe': amount, 'moneda': 'MXN'}


def counts(connection):
    return {table: connection.execute('SELECT count(*) FROM bovi.' + table).fetchone()[0]
            for table in ('animal', 'operacion', 'posicion_inventario', 'liquidacion',
                          'gasto_operacion', 'asignacion_costo', 'pago',
                          'aplicacion_pago', 'movimiento_inventario')}


def prepare():
    started = time.monotonic()
    purchases, sales, settlements, payments = [], [], [], []
    with connect() as connection:
        schema = guard(connection)
        before = counts(connection)
        period = connection.execute("SELECT id::text FROM bovi.periodo_cierre "
                    "WHERE empresa_id=%s AND sucursal_id=%s AND estado='ABIERTO' "
                    "AND %s::date BETWEEN desde AND hasta", (E, S, FIXTURE['fecha'])).fetchone()
        if period:
            period = period[0]
        else:
            # No reabrir/borrar periodos QA anteriores: las reglas canónicas deciden.
            period = command(connection, 'crear_periodo', 'periodo',
                    {'desde': '2026-10-01', 'hasta': '2026-10-31'}, {})['id']
        financial = {'periodo_id': period, 'fecha_reconocimiento': FIXTURE['fecha']}
        party = command(connection, 'crear_contraparte', 'parte',
                        {'nombre': DATASET + ' contraparte sintética'}, financial)['id']
        connection.commit()
        for index in range(FIXTURE['compras']):
            tag = 'ciclo-' + str(index).zfill(4)
            animal = command(connection, 'registrar_animal', tag + '-animal',
                    {'sexo': 'M', 'identificaciones': [{'sistema': 'INTERNO',
                     'codigo': DATASET + ' ' + str(index).zfill(4)}]}, financial)['id']
            purchase = command(connection, 'crear_operacion', tag + '-compra',
                    {'tipo': 'COMPRA', 'parte_id': party, 'fecha_operacion': FIXTURE['fecha'],
                     'lotes': [{'animales': [animal], 'unidad_precio': 'CABEZA',
                                'precio_unitario': FIXTURE['precio_compra']}]}, financial)['id']
            command(connection, 'confirmar_operacion', tag + '-confirmar',
                    {'operacion_id': purchase, 'version_lock': 0}, financial)
            expense = command(connection, 'registrar_gasto', tag + '-gasto',
                    {'operacion_id': purchase, 'importe': money(FIXTURE['costo_compra']),
                     'clasificacion': 'CAPITALIZABLE', 'concepto': DATASET + ' costo compra',
                     'fecha_economica': FIXTURE['fecha']}, financial)['id']
            command(connection, 'repartir_gasto', tag + '-reparto',
                    {'gasto_id': expense, 'metodo': 'POR_CABEZA'}, financial)
            purchases.append(purchase)
            connection.commit()
        for index, purchase in enumerate(purchases[:FIXTURE['ventas']]):
            tag = 'venta-' + str(index).zfill(4)
            position = str(connection.execute('SELECT id FROM bovi.posicion_inventario '
                    'WHERE empresa_id=%s AND sucursal_id=%s AND compra_operacion_id=%s',
                    (E, S, purchase)).fetchone()[0])
            sale = command(connection, 'crear_operacion', tag + '-operacion',
                    {'tipo': 'VENTA', 'parte_id': party, 'fecha_operacion': FIXTURE['fecha'],
                     'lotes': [{'posiciones': [position], 'unidad_precio': 'CABEZA',
                                'precio_unitario': FIXTURE['precio_venta']}]}, financial)['id']
            command(connection, 'reservar_venta', tag + '-reserva',
                    {'operacion_id': sale}, financial)
            settlement = command(connection, 'confirmar_operacion', tag + '-confirmar',
                    {'operacion_id': sale, 'version_lock': 0}, financial)['id']
            expense = command(connection, 'registrar_gasto', tag + '-gasto',
                    {'operacion_id': sale, 'importe': money(FIXTURE['gasto_directo_venta']),
                     'clasificacion': 'DIRECTO_VENTA', 'concepto': DATASET + ' gasto venta',
                     'fecha_economica': FIXTURE['fecha']}, financial)['id']
            command(connection, 'repartir_gasto', tag + '-reparto',
                    {'gasto_id': expense, 'metodo': 'POR_CABEZA'}, financial)
            payment = command(connection, 'registrar_pago', tag + '-cobro',
                    {'parte_id': party, 'tipo': 'COBRO', 'importe': money(FIXTURE['cobro']),
                     'metodo': 'EFECTIVO', 'recibido_el': FIXTURE['fecha']}, financial)['id']
            command(connection, 'validar_pago', tag + '-validar',
                    {'pago_id': payment}, financial)
            command(connection, 'aplicar_pago', tag + '-aplicar',
                    {'pago_id': payment, 'liquidacion_id': settlement,
                     'importe': money(FIXTURE['aplicacion'])}, financial)
            command(connection, 'registrar_movimiento', tag + '-entrega',
                    {'tipo': 'ENTREGA', 'posiciones': [position], 'operacion_id': sale}, financial)
            sales.append(sale)
            settlements.append(settlement)
            payments.append(payment)
            connection.commit()
        actual = {
            'inventario': str(connection.execute('SELECT sum(v.delta_inventario) '
                'FROM bovi.asiento_valoracion v JOIN bovi.posicion_inventario p '
                'ON (p.empresa_id,p.sucursal_id,p.id)=(v.empresa_id,v.sucursal_id,v.posicion_id) '
                'WHERE p.compra_operacion_id=ANY(%s::uuid[])', (purchases,)).fetchone()[0]),
            'costo_vendido': str(connection.execute('SELECT sum(costo_vendido) '
                'FROM bovi.v_margen_operacion WHERE operacion_id=ANY(%s::uuid[])',
                (sales,)).fetchone()[0]),
            'margen': str(connection.execute('SELECT sum(venta_neta-costo_vendido-gastos_directos) '
                'FROM bovi.v_margen_operacion WHERE operacion_id=ANY(%s::uuid[])',
                (sales,)).fetchone()[0]),
            'saldo_ventas': str(connection.execute('SELECT sum(saldo) FROM bovi.v_saldo_liquidacion '
                'WHERE id=ANY(%s::uuid[])', (settlements,)).fetchone()[0]),
            'disponible_pagos': str(connection.execute('SELECT sum(disponible) FROM bovi.v_disponible_pago '
                'WHERE id=ANY(%s::uuid[])', (payments,)).fetchone()[0])}
        for key, expected in FIXTURE['esperados'].items():
            if key.startswith('posiciones_'):
                state = 'DISPONIBLE' if key.endswith('disponibles') else 'CERRADA_VENTA'
                actual[key] = connection.execute('SELECT count(*) FROM bovi.posicion_inventario '
                        'WHERE compra_operacion_id=ANY(%s::uuid[]) AND estado=%s',
                        (purchases, state)).fetchone()[0]
            assert Decimal(str(actual[key])) == Decimal(str(expected)), key
        result = {'dataset': DATASET, 'database': DB, 'estado': 'PASS',
                  'utc': utc(), 'revision': revision(), 'schema': schema, 'elapsed_seconds': round(time.monotonic()-started, 3),
                  'command_calls': sum(CALLS.values()), 'command_counts': CALLS,
                  'before_counts_all_qa': before, 'after_counts_all_qa': counts(connection),
                  'owned': {'animales': 200, 'compras': len(purchases), 'ventas': len(sales),
                            'gastos': 300, 'pagos': len(payments), 'entregas': 100},
                  'expected_actual': actual, 'purchase_ids': purchases, 'sale_ids': sales,
                  'settlement_ids': settlements, 'payment_ids': payments,
                  'limit': 'Sólo QA; seed por claves permanentes, sin borrar ni insertar finanzas directamente.'}
    STATE.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    return result


def utc():
    return datetime.now(timezone.utc).isoformat()


def revision():
    def git(*args):
        return subprocess.run(['git', '-C', str(ROOT), *args], check=True,
                              capture_output=True, text=True).stdout.strip()
    return {'commit': git('rev-parse', 'HEAD'), 'dirty': bool(git('status', '--porcelain'))}


def machine():
    mem = {line.split(':')[0]: int(line.split()[1]) for line in
           Path('/proc/meminfo').read_text().splitlines() if line.endswith('kB')}
    cpu = next(line.split(':', 1)[1].strip() for line in
               Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name'))
    return {'cpu': cpu, 'cpu_logicos': os.cpu_count(), 'memoria_total_mib': mem['MemTotal']/1024,
            'memoria_disponible_mib': mem['MemAvailable']/1024,
            'loadavg': Path('/proc/loadavg').read_text().strip(),
            'doctor': 'docs/testing/evidence/doctor-final.json'}


def percentiles(samples):
    return {'samples': len(samples), 'p50_ms': round(statistics.median(samples), 3),
            'p95_ms': round(sorted(samples)[math.ceil(len(samples)*.95)-1], 3),
            'min_ms': round(min(samples), 3), 'max_ms': round(max(samples), 3)}


def params(resource, index, state):
    if resource == 'inventario_posiciones':
        return {'pagina': index % 4 + 1, 'tamano': 25, 'q': DATASET,
                'disponibles_para_venta': True}
    if resource == 'reportes_cartera':
        return {'pagina': index % 12 + 1, 'tamano': 25, 'q': DATASET}
    return {'id': state['settlement_ids' if resource == 'liquidacion' else 'sale_ids'][index % 100]}


def measure():
    from psycopg.types.json import Jsonb
    state = json.loads(STATE.read_text())
    assert state['dataset'] == DATASET and state['database'] == DB and state['estado'] == 'PASS'
    started = time.monotonic()
    resources = ['inventario_posiciones', 'reportes_cartera', 'liquidacion', 'operacion_expediente']
    query = 'SELECT bovi.consultar(%s,%s,%s,%s,%s)'
    report = {'estado': 'PASS', 'database': DB, 'dataset': DATASET,
              'utc': utc(), 'revision': revision(), 'machine_before': machine(),
              'connection': 'Pgpool A19999, rol bovi_app_a, autocommit read-only; cuatro conexiones máximo',
              'seed_command_calls': state['command_calls'], 'dataset_owned': state['owned'],
              'scope': 'Consultas canónicas reales con params de CoreController; tiempos JDBC/HTTP/UI excluidos.',
              'warmups_per_connection_per_resource': 5, 'single': {}, 'concurrent_4': {}}
    def execute(connection, name, index):
        body = params(name, index, state)
        begin = time.perf_counter_ns()
        value = connection.execute(query, (E, S, U, name, Jsonb(body))).fetchone()[0]
        elapsed = (time.perf_counter_ns()-begin)/1e6
        assert (value.get('total') == (100 if name == 'inventario_posiciones' else 300)) if name in ('inventario_posiciones','reportes_cartera') else bool(value.get('id') or value.get('operacion_id'))
        return elapsed
    with connect(pool=True, readonly=True) as connection:
        report['schema'] = guard(connection)
        report['all_qa_counts'] = counts(connection)
        for name in resources:
            for index in range(5): execute(connection, name, index)
            samples = [execute(connection, name, index) for index in range(100)]
            plan = connection.execute('EXPLAIN(ANALYZE,BUFFERS,FORMAT JSON) '+query,
                    (E, S, U, name, Jsonb(params(name, 0, state)))).fetchone()[0][0]
            report['single'][name] = {**percentiles(samples), 'raw_samples_ms': samples,
                    'body_example': params(name, 0, state), 'explain': plan}
    # Cuatro conexiones persistentes; barrera por recurso, 25muestras cada una.
    barrier = threading.Barrier(4)
    def worker(worker_id):
        output = {}
        with connect(pool=True, readonly=True) as connection:
            guard(connection)
            for name in resources:
                for index in range(5): execute(connection, name, worker_id*25+index)
                barrier.wait(timeout=15)
                begin = time.monotonic()
                samples = [execute(connection, name, worker_id*25+index) for index in range(25)]
                output[name] = {'samples': samples, 'seconds': time.monotonic()-begin}
        return output
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        workers = list(executor.map(worker, range(4)))
    for name in resources:
        samples = [sample for worker_result in workers for sample in worker_result[name]['samples']]
        report['concurrent_4'][name] = {**percentiles(samples), 'raw_samples_ms': samples,
                'connections': 4, 'samples_per_connection': 25,
                'slowest_worker_seconds': round(max(w[name]['seconds'] for w in workers), 4)}
    report.update(elapsed_seconds=round(time.monotonic()-started, 3), machine_after=machine(),
            measured_calls=800, warmup_calls=100, explain_calls=4,
            python_maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            limit='Dataset200animales/300operaciones DEMO local. Caché caliente, lectura acotada, sin tráfico HTTP ni escritores durante medida. EXPLAIN del wrapper PLpgSQL incluye ejecución/buffers pero no expone planes internos. No SLO, capacidad comercial ni carga de producción; RAM/CPU host incluyen otros procesos.')
    (ROOT/'db/tests/benchmark-result.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true', help='Crea/reproduce seed QA por comandos idempotentes')
    mode.add_argument('--measure', action='store_true', help='Sólo lectura; requiere seed preparado')
    mode.add_argument('--self-check', action='store_true', help='Valida fixture/params sin conectar ni leer secretos')
    args = parser.parse_args()
    assert os.environ.get('BOVI_DB_NAME', DB) == DB, 'Sólo la base QA exacta está permitida'
    assert os.environ.get('BOVI_ENV','').lower() != 'production'
    assert 'production' not in {p.strip().lower() for p in os.environ.get('SPRING_PROFILES_ACTIVE','').split(',')}
    assert FIXTURE['database'] == DB and FIXTURE['dataset'] == DATASET
    assert FIXTURE['animales'] == FIXTURE['compras'] == 200 and FIXTURE['ventas'] == 100
    if args.self_check:
        mock = {'settlement_ids': ['demo']*100, 'sale_ids': ['demo']*100}
        assert params('inventario_posiciones', 4, mock)['pagina'] == 1
        assert params('reportes_cartera', 11, mock)['pagina'] == 12
        assert len(percentiles(list(range(100)))) == 5
        assert (ROOT/'db/migrations/V11__cancelacion_anulacion_version.sql').read_text().count(
                "IF NOT FOUND OR op.version_lock IS DISTINCT FROM") >= 3
        print('PASS fixture/params/self-check; sin BD, secretos ni servicios')
        return
    report = prepare() if args.prepare else measure()
    summary = {key: report[key] for key in ('estado','database','dataset','elapsed_seconds')}
    summary['command_calls' if args.prepare else 'measured_calls'] = report.get('command_calls', report.get('measured_calls'))
    if args.measure:
        summary['single'] = {k:{p:v[p] for p in ('p50_ms','p95_ms')} for k,v in report['single'].items()}
        summary['concurrent_4'] = {k:{p:v[p] for p in ('p50_ms','p95_ms')} for k,v in report['concurrent_4'].items()}
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # No traceback/conninfo/SQL privado en logs públicos.
        failure = {'estado':'FAIL','utc':utc(),'exception_type':type(error).__name__,
                   'sqlstate':getattr(error,'sqlstate',None),'command_counts':CALLS,
                   'limite':'No se borra QA; volver a preparar reproduce claves confirmadas.'}
        (ROOT/'db/tests/benchmark-failure.json').write_text(json.dumps(failure, indent=2)+'\n')
        print(json.dumps(failure))
        raise SystemExit(1)
