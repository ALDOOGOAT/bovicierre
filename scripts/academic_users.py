#!/usr/bin/env python3
"""Cuentas personales de la entrega académica (idempotente). No imprime contraseñas.

- Aplicación (maestros en A, comandos canónicos): profesor.tabd (OPERADOR, CAJA, AUDITOR), aldo.admin y jared.admin (ADMIN),
  en ambas sedes.
- PostgreSQL: profesor_bd, aldo_bd, jared_bd con rol bovi_consulta (lectura sin hashes + pg_monitor) en A y B, y
  lectura del proveedor (bovi_fdw_read) en la tercera instancia.
Contraseñas generadas una vez y guardadas en <BOVI_ENTREGA_DIR>/accesos.json (0600); el resumen legible para entregar
por canal privado queda en <BOVI_ENTREGA_DIR>/accesos.md (0600). Destino: BOVI_PG_TARGETS='{"a":"host:puerto",…}'
(por defecto el stack local 15432/15433/15434) y BOVI_PUBLIC_URL para el resumen.
"""
import hashlib, json, os, secrets, uuid
from pathlib import Path
import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

SECRET = Path(os.environ.get('BOVI_SECRET_DIR', Path.home() / '.local/share/bovicierre-academic/secrets'))
OUT = Path(os.environ.get('BOVI_ENTREGA_DIR', SECRET.parent / 'entrega'))
TARGETS = json.loads(os.environ.get('BOVI_PG_TARGETS', '{"a":"127.0.0.1:15432","b":"127.0.0.1:15433","prov":"127.0.0.1:15434"}'))
URL = os.environ.get('BOVI_PUBLIC_URL', 'http://localhost:15180')
E = '11111111-1111-4111-8111-111111111111'; ADMIN = '99999999-9999-4999-8999-999999999999'
SEDES = ['aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb']
APP = {'profesor.tabd': ('Profesor de Tópicos Avanzados de BD', ['OPERADOR', 'CAJA', 'AUDITOR']),
       'aldo.admin': ('Aldo (equipo)', ['ADMIN']), 'jared.admin': ('Jared (equipo)', ['ADMIN'])}
DB = ['profesor_bd', 'aldo_bd', 'jared_bd']

OUT.mkdir(parents=True, exist_ok=True, mode=0o700); os.chmod(OUT, 0o700)
store = OUT / 'accesos.json'
creds = json.loads(store.read_text()) if store.exists() else {}
for name in list(APP) + DB:
    creds.setdefault(name, secrets.token_urlsafe(18))
with os.fdopen(os.open(store, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as f: json.dump(creds, f, indent=1)


def connect(node):
    host, port = TARGETS[node].rsplit(':', 1)
    return psycopg.connect(host=host, port=int(port), dbname='bovicierre', user='postgres', password=(SECRET / 'admin_password').read_text().strip(), autocommit=True)


# Roles de base de datos (no se replican: se crean en cada instancia).
for node, group in (('a', 'bovi_consulta'), ('b', 'bovi_consulta'), ('prov', 'bovi_fdw_read')):
    with connect(node) as c:
        for role in DB:
            exists = c.execute('select 1 from pg_roles where rolname=%s', (role,)).fetchone()
            verb = 'ALTER' if exists else 'CREATE'
            c.execute(sql.SQL(verb + ' ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION CONNECTION LIMIT 5 PASSWORD {}').format(sql.Identifier(role), sql.Literal(creds[role])))
            c.execute(sql.SQL('GRANT {} TO {}').format(sql.Identifier(group), sql.Identifier(role)))

# Usuarios de la aplicación por el comando canónico, en A (maestros), actuando como el administrador DEMO.
with connect('a') as c:
    def cmd(sede, name, body):
        digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        return c.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)', (E, sede, ADMIN, 'ENTREGA-' + str(uuid.uuid4()), digest, uuid.uuid4(), name, Jsonb(body))).fetchone()[0]
    for login, (nombre, roles) in APP.items():
        bcrypt = c.execute("select '{bcrypt}'||public.crypt(%s, public.gen_salt('bf', 10))", (creds[login],)).fetchone()[0]
        row = c.execute('select id from bovi.usuario where empresa_id=%s and login_normalizado=%s', (E, login)).fetchone()
        uid = str(row[0]) if row else cmd(SEDES[0], 'crear_usuario', {'login': login, 'nombre': nombre, 'hash_contrasena': bcrypt})['id']
        if row: cmd(SEDES[0], 'actualizar_usuario', {'usuario_id': uid, 'hash_contrasena': bcrypt, 'estado': 'ACTIVO'})
        for sede in SEDES:
            for rol in roles:
                cmd(sede, 'asignar_membresia', {'usuario_id': uid, 'rol_codigo': rol, 'vigente': True})

lines = ['# Accesos de la entrega académica (PRIVADO: no subir al repositorio)', '', f'Aplicación: {URL}', '',
         '| Usuario de la aplicación | Roles por sede | Contraseña |', '|---|---|---|']
lines += [f'| `{u}` | {", ".join(r)} | `{creds[u]}` |' for u, (_, r) in APP.items()]
lines += ['', '| Usuario PostgreSQL | Permisos | Contraseña |', '|---|---|---|']
lines += [f'| `{u}` | bovi_consulta en A y B (lectura sin hashes, pg_monitor); bovi_fdw_read en proveedor | `{creds[u]}` |' for u in DB]
lines += ['', 'Hosts y puertos de PostgreSQL: ver docs/deploy/railway.md (TCP proxy, si está habilitado).']
with os.fdopen(os.open(OUT / 'accesos.md', os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as f: f.write('\n'.join(lines) + '\n')
print(f'Cuentas listas: {len(APP)} de aplicación y {len(DB)} de PostgreSQL. Resumen privado en {OUT}/accesos.md (0600).')
