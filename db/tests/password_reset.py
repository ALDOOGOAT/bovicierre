#!/usr/bin/env python3
"""Restablecimiento administrativo de contraseña (V21) por bovi.cmd_ejecutar real; todo se revierte."""
import hashlib, json, os, uuid
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb

SECRET = Path(os.environ.get('BOVI_SECRET_DIR', Path.home() / '.local/share/bovicierre-academic/secrets'))
DB = os.environ.get('BOVI_DB_NAME', 'bovicierre_gold_final')
E = '11111111-1111-4111-8111-111111111111'; S = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'; ADMIN = '99999999-9999-4999-8999-999999999999'
OPERADOR = '89999999-9999-4999-8999-999999999999'


# Una sola transacción: comandos con el rol de aplicación (SET ROLE) y lecturas de verificación como postgres,
# porque bovi_app_a no puede leer bovi.usuario.
conn = psycopg.connect(host='127.0.0.1', port=15432, dbname=DB, user='postgres', password=(SECRET / 'admin_password').read_text().strip())
cur = conn.cursor()


def bcrypt(plain):  # mismo formato que BCryptPasswordEncoder: {bcrypt}$2a$10$…
    cur.execute("select '{bcrypt}'||public.crypt(%s,public.gen_salt('bf',10))", (plain,)); return cur.fetchone()[0]


def q1(sql_, args=()):
    cur.execute(sql_, args); return cur.fetchone()[0]


def cmd(actor, body):
    cur.execute('SET ROLE bovi_app_a')
    cur.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)', (E, S, actor, 'DEMO-PW-' + str(uuid.uuid4()), hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest(), uuid.uuid4(), 'actualizar_usuario', Jsonb(body)))
    out = cur.fetchone()[0]; cur.execute('RESET ROLE'); return out


def fails(actor, body, code):
    cur.execute('SAVEPOINT p')
    try:
        cmd(actor, body); raise AssertionError('debió fallar')
    except psycopg.Error as ex:
        cur.execute('ROLLBACK TO p'); cur.execute('RESET ROLE')
        detail = json.loads(ex.diag.message_detail or '{}') if ex.sqlstate == 'P0001' else {}
        assert ex.sqlstate == code or detail.get('codigo') == code, (ex.sqlstate, detail)


try:
    target = OPERADOR
    cur.execute('select hash_contrasena from bovi.usuario where id=%s', (target,)); before = cur.fetchone()[0]
    new = bcrypt('DEMO-nueva-clave-1')
    cur.execute("insert into infra.spring_session values (%s,%s,0,0,1800,9999999999999,%s)", (str(uuid.uuid4()), str(uuid.uuid4()), target))
    out = cmd(ADMIN, {'usuario_id': target, 'hash_contrasena': new})
    assert q1("select count(*) from infra.spring_session where principal_name=%s", (target,)) == 0
    print('PASS TEST-38 restablecer cierra las sesiones abiertas de la cuenta (V25)')
    assert out == {'id': target, 'contrasena_restablecida': True}, out
    cur.execute('select hash_contrasena from bovi.usuario where id=%s', (target,)); after = cur.fetchone()[0]
    assert after == new and after != before
    cur.execute("select cambio::text from bovi.auditoria_evento where comando='actualizar_usuario' and entidad_id=%s order by ocurrido_en desc limit 1", (target,))
    audit = cur.fetchone()[0]
    assert '$2' not in audit and 'contrasena_restablecida' in audit, audit
    print('PASS TEST-38 restablecimiento ADMIN: hash cambia, auditoría sin hash')
    fails(ADMIN, {'usuario_id': target, 'hash_contrasena': 'texto-plano'}, 'BV015')
    print('PASS TEST-38 hash no bcrypt rechazado BV015')
    fails(OPERADOR, {'usuario_id': ADMIN, 'hash_contrasena': new}, '42501')
    print('PASS TEST-38 OPERADOR no puede restablecer contraseñas')
    # V24: un ADMIN sólo de la sede A no administra una cuenta que es ADMIN en B (escalada entre sedes).
    SB = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'

    def generic(actor, sede, name, body):
        cur.execute('SET ROLE bovi_app_a')
        cur.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)', (E, sede, actor, 'DEMO-PW-' + str(uuid.uuid4()), hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest(), uuid.uuid4(), name, Jsonb(body)))
        out = cur.fetchone()[0]; cur.execute('RESET ROLE'); return out
    run = uuid.uuid4().hex[:8]
    admin_a = generic(ADMIN, S, 'crear_usuario', {'login': 'demo.admina.' + run, 'nombre': 'DEMO admin sólo A', 'hash_contrasena': new})['id']
    generic(ADMIN, S, 'asignar_membresia', {'usuario_id': admin_a, 'rol_codigo': 'ADMIN', 'vigente': True})
    victim = generic(ADMIN, S, 'crear_usuario', {'login': 'demo.adminb.' + run, 'nombre': 'DEMO admin de B', 'hash_contrasena': new})['id']
    generic(ADMIN, S, 'asignar_membresia', {'usuario_id': victim, 'rol_codigo': 'OPERADOR', 'vigente': True})
    generic(ADMIN, SB, 'asignar_membresia', {'usuario_id': victim, 'rol_codigo': 'ADMIN', 'vigente': True})
    for body in ({'usuario_id': victim, 'hash_contrasena': bcrypt('DEMO-tomada-1')}, {'usuario_id': victim, 'estado': 'BLOQUEADO'}):
        fails(admin_a, body, '42501')
    print('PASS TEST-38 ADMIN sólo de A no restablece ni bloquea una cuenta ADMIN en B (42501)')
    only_a = generic(ADMIN, S, 'crear_usuario', {'login': 'demo.soloa.' + run, 'nombre': 'DEMO sólo A', 'hash_contrasena': new})['id']
    generic(ADMIN, S, 'asignar_membresia', {'usuario_id': only_a, 'rol_codigo': 'CAJA', 'vigente': True})
    assert cmd(admin_a, {'usuario_id': only_a, 'hash_contrasena': bcrypt('DEMO-otra-1')})['contrasena_restablecida'] is True
    print('PASS TEST-38 ADMIN de A sí administra una cuenta que sólo existe en A')
finally:
    conn.rollback(); conn.close()
