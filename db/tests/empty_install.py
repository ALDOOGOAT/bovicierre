#!/usr/bin/env python3
"""Instalación vacía (mandato §8.1): base aislada nueva, empresa/sedes/admin propios, sin DEMO ni hechos comerciales.

Crea bovicierre_vacia_check en A/B/proveedor si falta (nunca DROP), migra y ejecuta bootstrap con BOVI_INSTALL=vacia.
Repetible: el archivo de instalación privado conserva los UUID y el bootstrap es idempotente.
"""
import hashlib, json, os, subprocess, uuid
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb

ROOT = Path(__file__).resolve().parents[2]
SECRET = Path(os.environ.get('BOVI_SECRET_DIR', Path.home() / '.local/share/bovicierre-academic/secrets'))
DB = 'bovicierre_vacia_check'
INSTALL = SECRET.parent / 'install-vacia-check.json'
COMPANY = 'Rancho Prueba Instalación Vacía'
for node in ('a', 'b', 'prov'):
    c = f'bovicierre-academic-pg-{node}-1'
    run = lambda q, d='postgres': subprocess.run(['docker', 'exec', c, 'psql', '-qAt', '-U', 'postgres', '-d', d, '-c', q], capture_output=True, text=True, check=True).stdout.strip()
    if run(f"SELECT count(*) FROM pg_database WHERE datname='{DB}'") == '0':
        run(f'CREATE DATABASE {DB}')
env = {**os.environ, 'BOVI_DB_NAME': DB, 'BOVI_INSTALL': 'vacia', 'BOVI_INSTALL_FILE': str(INSTALL), 'BOVI_EMPRESA': COMPANY,
       'BOVI_SEDE_A': 'Corral norte', 'BOVI_SEDE_B': 'Corral sur', 'BOVI_ADMIN_LOGIN': 'admin.rancho'}
subprocess.run(['sh', str(ROOT / 'db/bootstrap/migrate.sh')], env=env, check=True, capture_output=True)
subprocess.run(['python3', str(ROOT / 'db/bootstrap/bootstrap.py')], env=env, check=True)
cfg = json.loads(INSTALL.read_text())
assert oct(INSTALL.stat().st_mode & 0o777) == '0o600'
admin_pw = (SECRET / 'install_admin_password').read_text().strip()


def q(port, sql, args=()):
    with psycopg.connect(host='127.0.0.1', port=port, dbname=DB, user='postgres', password=(SECRET / 'admin_password').read_text().strip()) as c:
        return c.execute(sql, args).fetchone()


assert q(15432, 'select count(*), min(razon_social) from bovi.empresa') == (1, COMPANY)
assert q(15432, "select count(*) from bovi.sucursal where nombre like 'DEMO%%' or codigo like 'DEMO%%'") == (0,)
assert q(15432, 'select count(*), min(login_normalizado) from bovi.usuario') == (1, 'admin.rancho')
assert q(15432, "select count(*) from bovi.membresia_usuario where rol_codigo='ADMIN' and vigente") == (2,)
assert q(15432, "select hash_contrasena = '{bcrypt}'||public.crypt(%s, substr(hash_contrasena, 9)) from bovi.usuario", (admin_pw,)) == (True,)
for table in ('operacion', 'liquidacion', 'posicion_inventario', 'pago', 'parte', 'animal', 'periodo_cierre'):
    assert q(15432, f'select count(*) from bovi.{table}') == (0,), table
assert q(15433, 'select count(*) from bovi.usuario') == (1,)  # maestros replicados a B
print('PASS TEST-39 instalación vacía: empresa/sedes/admin propios, sin DEMO ni hechos comerciales, réplica a B')
# El primer administrador puede abrir el primer periodo por el comando canónico (se revierte).
with psycopg.connect(host='127.0.0.1', port=15432, dbname=DB, user='bovi_app_a', password=(SECRET / 'app_a_password').read_text().strip()) as c:
    body = {'desde': '2026-10-01', 'hasta': '2026-10-31'}
    out = c.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)', (cfg['empresa'], cfg['sede_a'], cfg['admin'], 'VACIA-' + str(uuid.uuid4()),
                    hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest(), uuid.uuid4(), 'crear_periodo', Jsonb(body))).fetchone()[0]
    assert out.get('id'), out
    c.rollback()
print('PASS TEST-39 primer administrador abre periodo con cmd_ejecutar (revertido)')
