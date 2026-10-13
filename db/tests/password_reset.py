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
    out = cmd(ADMIN, {'usuario_id': target, 'hash_contrasena': new})
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
finally:
    conn.rollback(); conn.close()
