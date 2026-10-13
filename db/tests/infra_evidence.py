#!/usr/bin/env python3
"""TEST-40 evidencia de infraestructura (mandato §10.3-10.5) sobre la base aislada bovicierre_gold_final.

- Pgpool A/B: SHOW POOL_NODES por el puerto real y el rol de aplicación; un backend por pool (raw, sin failover).
- Réplica M–M con IDs concretos: maestro A→B (contraparte) y local B→A (borrador de operación de sede B).
- Corte de enlace: suscripción B desde A deshabilitada → la fila no llega; al reanudar converge.
- FDW: lectura, escritura denegada, caída simulada del enlace (host del servidor foráneo inexistente sólo en esta
  base) y recuperación. No detiene contenedores compartidos ni toca la base principal.
Escribe db/tests/infra-evidence-result.json con IDs y tiempos medidos; filas creadas son DEMO sintéticas.
"""
import hashlib, json, os, time, uuid
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb

SECRET = Path(os.environ.get('BOVI_SECRET_DIR', Path.home() / '.local/share/bovicierre-academic/secrets'))
DB = os.environ.get('BOVI_DB_NAME', 'bovicierre_gold_final')
E = '11111111-1111-4111-8111-111111111111'; U = '99999999-9999-4999-8999-999999999999'
S = {'A': 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'B': 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'}
PORT = {'A': 15432, 'B': 15433, 'poolA': 19999, 'poolB': 19998}
pw = lambda f: (SECRET / f).read_text().strip()
evidence = {'base': DB, 'medido_en': time.strftime('%Y-%m-%dT%H:%M:%S%z')}


def connect(port, user, password, autocommit=True):
    return psycopg.connect(host='127.0.0.1', port=port, dbname=DB, user=user, password=password, autocommit=autocommit)


def admin(node): return connect(PORT[node], 'postgres', pw('admin_password'))


def cmd(node, name, body):
    with connect(PORT[node], 'bovi_app_' + node.lower(), pw(f'app_{node.lower()}_password')) as c:
        digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        return c.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)', (E, S[node], U, 'DEMO-INFRA-' + str(uuid.uuid4()), digest, uuid.uuid4(), name, Jsonb(body))).fetchone()[0]


def wait_row(node, table, row_id, timeout=15):
    start = time.monotonic()
    with admin(node) as c:
        while time.monotonic() - start < timeout:
            if c.execute(f'select count(*) from bovi.{table} where id=%s', (row_id,)).fetchone()[0]:
                return round(time.monotonic() - start, 3)
            time.sleep(.1)
    return None


# 1. Pgpool: nodos reales detrás de cada pool, con el rol de aplicación.
for pool, node in (('poolA', 'A'), ('poolB', 'B')):
    with connect(PORT[pool], 'bovi_app_' + node.lower(), pw(f'app_{node.lower()}_password')) as c:
        cur = c.execute('SHOW POOL_NODES'); cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        version = c.execute('SHOW POOL_VERSION').fetchone()[0]
    keep = ('node_id', 'hostname', 'port', 'status', 'role', 'lb_weight')
    evidence['pool_nodes_' + node] = {'pgpool': version, 'nodos': [{k: r.get(k) for k in keep} for r in rows]}
    assert len(rows) == 1 and rows[0]['hostname'] == 'pg-' + node.lower() and rows[0]['status'] == 'up', rows
print('PASS TEST-40 Pgpool A→pg-a y B→pg-b (raw, un nodo up cada uno)')

# 2. Réplica con IDs concretos.
party = cmd('A', 'crear_contraparte', {'nombre': 'DEMO INFRA réplica ' + uuid.uuid4().hex[:8]})['id']
lag_ab = wait_row('B', 'parte', party); assert lag_ab is not None, 'A→B no convergió'
draft = cmd('B', 'crear_operacion', {'tipo': 'COMPRA', 'parte_id': party, 'fecha_operacion': '2026-10-11'})['id']  # agregado local de sede B
lag_ba = wait_row('A', 'operacion', draft); assert lag_ba is not None, 'B→A no convergió'
evidence['replica'] = {'A_a_B': {'tabla': 'bovi.parte', 'id': party, 'segundos': lag_ab}, 'B_a_A': {'tabla': 'bovi.operacion', 'id': draft, 'segundos': lag_ba}}
print(f'PASS TEST-40 réplica A→B parte {party} en {lag_ab}s; B→A operación {draft} en {lag_ba}s')

# 3. Corte del enlace A→B y reanudación.
with admin('B') as c:
    sub = c.execute("select subname from pg_subscription where subdbid=(select oid from pg_database where datname=current_database()) and subname like 'sub_b_desde_a%%'").fetchone()[0]
    c.execute(f'ALTER SUBSCRIPTION {sub} DISABLE')
try:
    offline = cmd('A', 'crear_contraparte', {'nombre': 'DEMO INFRA durante corte ' + uuid.uuid4().hex[:8]})['id']
    assert wait_row('B', 'parte', offline, timeout=3) is None, 'llegó con la suscripción deshabilitada'
finally:
    with admin('B') as c: c.execute(f'ALTER SUBSCRIPTION {sub} ENABLE')
lag_resume = wait_row('B', 'parte', offline, timeout=30); assert lag_resume is not None, 'no convergió tras reanudar'
evidence['corte_enlace'] = {'suscripcion': sub, 'id': offline, 'ausente_durante_corte_s': 3, 'converge_tras_reanudar_s': lag_resume}
print(f'PASS TEST-40 corte {sub}: {offline} ausente 3s, converge {lag_resume}s tras reanudar')


# 4. FDW: lectura por Pgpool, DML denegado, caída del enlace y recuperación.
def fdw_read():
    with connect(PORT['poolA'], 'bovi_app_a', pw('app_a_password')) as c:
        return c.execute("select precio_mxn from ext_proveedor.tarifa_transporte where ruta='DEMO-RUTA-01'").fetchone()[0]


assert fdw_read() == 12000
with connect(PORT['poolA'], 'bovi_app_a', pw('app_a_password')) as c:
    try:
        c.execute("insert into ext_proveedor.ticket_bascula(folio) values('DEMO-NO')"); raise AssertionError('INSERT FDW permitido')
    except psycopg.Error as ex: denied = ex.sqlstate
assert denied == '42501', denied
with admin('A') as c: c.execute("ALTER SERVER prov_sim OPTIONS (SET host 'pg-prov-caido.invalid')")
try:
    try:
        fdw_read(); raise AssertionError('FDW respondió sin enlace')
    except psycopg.Error as ex: outage = ex.sqlstate
finally:
    with admin('A') as c: c.execute("ALTER SERVER prov_sim OPTIONS (SET host 'pg-prov')")
assert outage and outage.startswith('08'), outage
assert fdw_read() == 12000
evidence['fdw'] = {'lectura_pgpool': '12000', 'insert_denegado': denied, 'caida_sqlstate': outage, 'recuperado': True}
print(f'PASS TEST-40 FDW lectura 12000, INSERT {denied}, caída {outage}, recuperado')

Path(__file__).with_name('infra-evidence-result.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=1, default=str) + '\n')
