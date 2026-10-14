#!/usr/bin/env python3
"""Verifica las cuentas de la entrega contra un despliegue real sin imprimir contraseñas (TEST-42).

Lee <BOVI_ENTREGA_DIR>/accesos.json. API en BOVI_PUBLIC_URL; PostgreSQL en BOVI_PG_TARGETS (como academic_users.py).
"""
import json, os, urllib.request, uuid
from http.cookiejar import CookieJar
from pathlib import Path
import psycopg

SECRET = Path(os.environ.get('BOVI_SECRET_DIR', Path.home() / '.local/share/bovicierre-academic/secrets'))
OUT = Path(os.environ.get('BOVI_ENTREGA_DIR', SECRET.parent / 'entrega'))
URL = os.environ.get('BOVI_PUBLIC_URL', 'http://localhost:15180').rstrip('/')
TARGETS = json.loads(os.environ.get('BOVI_PG_TARGETS', '{"a":"127.0.0.1:15432","b":"127.0.0.1:15433","prov":"127.0.0.1:15434"}'))
creds = json.loads((OUT / 'accesos.json').read_text())
SEDE_A = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'


class Client:
    def __init__(self):
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar())); self.csrf = {}

    def call(self, method, path, body=None):
        headers = {'Content-Type': 'application/json', **self.csrf}
        if method != 'GET': headers['Idempotency-Key'] = str(uuid.uuid4())
        req = urllib.request.Request(URL + '/api/v1' + path, method=method, headers=headers, data=None if body is None else json.dumps(body).encode())
        try:
            with self.op.open(req, timeout=30) as r: return r.status, (json.loads(r.read() or b'null'))
        except urllib.error.HTTPError as e: return e.code, None

    def login(self, user):
        _, t = self.call('GET', '/sesion/csrf'); self.csrf = {t['headerName']: t['token']}
        status, _ = self.call('POST', '/sesion/login', {'login': user, 'contrasena': creds[user]})
        _, t = self.call('GET', '/sesion/csrf'); self.csrf = {t['headerName']: t['token']}
        return status


status, health = Client().call('GET', '/salud')
assert status == 200, status
print('PASS TEST-42 /salud', json.dumps(health, ensure_ascii=False))
for user, must in (('profesor.tabd', {'OPERADOR', 'CAJA', 'AUDITOR'}), ('aldo.admin', {'ADMIN'}), ('jared.admin', {'ADMIN'})):
    c = Client(); assert c.login(user) in (200, 204), user
    _, me = c.call('GET', '/sesion/actual')
    sedes = {s['id']: set(s['roles']) for s in me['sedes']}
    assert len(sedes) == 2 and all(must <= r for r in sedes.values()), (user, sedes)
    assert c.call('GET', f'/sedes/{SEDE_A}/operaciones?pagina=1&tamano=1')[0] == 200
    # Sin contraseña: ADMIN pasa la autorización y la validación responde 400; otro rol recibe 403. No crea nada.
    creating = c.call('POST', f'/sedes/{SEDE_A}/usuarios', {'login': 'demo.no.creado', 'nombre': 'DEMO no creado'})[0]
    assert creating == (400 if 'ADMIN' in must else 403), (user, creating)
    print(f'PASS TEST-42 {user}: entra, roles {sorted(must)} en 2 sedes, consulta 200, administración de usuarios {"autorizada (400 por validación)" if creating == 400 else "denegada 403"}')
bad = Client(); _, t = bad.call('GET', '/sesion/csrf'); bad.csrf = {t['headerName']: t['token']}
assert bad.call('POST', '/sesion/login', {'login': 'profesor.tabd', 'contrasena': 'incorrecta'})[0] == 401
print('PASS TEST-42 contraseña incorrecta → 401')

for node in ('a', 'b'):
    host, port = TARGETS[node].rsplit(':', 1)
    with psycopg.connect(host=host, port=int(port), dbname='bovicierre', user='profesor_bd', password=creds['profesor_bd'], autocommit=True) as c:
        tables = c.execute("select count(*) from information_schema.tables where table_schema='bovi'").fetchone()[0]
        c.execute('select count(*) from bovi.operacion').fetchone()
        subs = c.execute('select count(*) from pg_stat_subscription').fetchone()[0]
        for stmt, code in (('select hash_contrasena from bovi.usuario limit 1', '42501'), ("update bovi.parte set nombre=nombre where false", '42501')):
            try: c.execute(stmt); raise AssertionError('permitido: ' + stmt)
            except psycopg.Error as e: assert e.sqlstate == code, (stmt, e.sqlstate)
    print(f'PASS TEST-42 profesor_bd en {node.upper()}: lee {tables} tablas y {subs} suscripción(es); hash y UPDATE → 42501')
host, port = TARGETS['prov'].rsplit(':', 1)
with psycopg.connect(host=host, port=int(port), dbname='bovicierre', user='profesor_bd', password=creds['profesor_bd'], autocommit=True) as c:
    assert c.execute('select count(*) from proveedor.tarifa_transporte').fetchone()[0] >= 1
print('PASS TEST-42 profesor_bd lee el proveedor (tercera instancia)')
