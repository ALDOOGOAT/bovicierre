#!/usr/bin/env python3
"""Pruebas dinámicas de seguridad SEC-01/03/04/05/06/07/09/10/11 contra la instancia LOCAL de BoviCierre.

Sólo 127.0.0.1/localhost (se rechaza otro host). Datos sintéticos con prefijo DEMO SEC. Lee secretos de archivos
externos y nunca los imprime. Cada caso valida estado final, no sólo códigos HTTP.
Uso: python3 tests/security/sec_dynamic.py --out docs/testing/evidence/security/<run>/dynamic.json
"""
import argparse
import http.cookiejar
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

BASE = os.environ.get('BOVI_API_TEST_URL', 'http://127.0.0.1:15180/api/v1')
SECRETS = Path(os.environ.get('BOVI_SECRET_DIR', Path.home() / '.local/share/bovicierre-academic/secrets'))
if urllib.parse.urlparse(BASE).hostname not in ('127.0.0.1', 'localhost'):
    raise SystemExit('Sólo se permite la instancia local.')
RUN = time.strftime('%Y%m%d%H%M%S')
results = []


class Client:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.csrf = None

    def call(self, method, path, body=None, headers=None, raw=None, csrf=True):
        url = path if path.startswith('http') else BASE + path
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        h = {'Accept': 'application/json'}
        if data is not None:
            h['Content-Type'] = 'application/json'
        if method not in ('GET', 'HEAD') and csrf and self.csrf:
            h[self.csrf[0]] = self.csrf[1]
        if method == 'POST' and csrf:
            h.setdefault('Idempotency-Key', str(uuid.uuid4()))
        h.update(headers or {})
        req = urllib.request.Request(url, data=data, method=method, headers=h)
        try:
            with self.opener.open(req, timeout=30) as r:
                payload = r.read()
                return r.status, dict(r.headers), payload
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read()

    def json(self, *a, **k):
        s, h, p = self.call(*a, **k)
        try:
            return s, json.loads(p or b'null')
        except json.JSONDecodeError:
            return s, None

    def refresh(self):
        s, d = self.json('GET', '/sesion/csrf')
        self.csrf = (d['headerName'], d['token'])

    def login(self, user, secret_file=None, password=None):
        self.refresh()
        pw = password if password is not None else (SECRETS / secret_file).read_text().strip()
        s, _ = self.json('POST', '/sesion/login', {'login': user, 'contrasena': pw})
        if s < 300:
            self.refresh()
        return s

    def session_cookie(self):
        return next((c.value for c in self.jar if c.name.upper() in ('JSESSIONID', 'SESSION', 'BOVI_SESSION')), None)


def record(sec, name, ok, evidence, severity_if_fail='media'):
    results.append({'sec': sec, 'caso': name, 'resultado': 'PASS' if ok else 'FAIL', 'evidencia': evidence,
                    'severidad_si_falla': None if ok else severity_if_fail})
    print(('PASS ' if ok else 'FAIL ') + f'{sec} {name}: {evidence}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    out = Path(p.parse_args().out)
    admin = Client()
    assert admin.login('demo.admin', 'demo_password') < 300, 'login admin'
    s, me = admin.json('GET', '/sesion/actual')
    sedes = {x['codigo']: x['id'] for x in me['sedes']}
    A, B = sedes['DEMO-A'], sedes['DEMO-B']

    # SEC-01 SQLi: búsqueda, filtros, paginación. Resultado acotado y sin 500.
    s, base = admin.json('GET', f'/sedes/{A}/contrapartes?pagina=1&tamano=100')
    total = base['total']
    for payload in ["' OR '1'='1", "%' OR 1=1 --", "'; DROP TABLE bovi.parte; --", "x' UNION SELECT usuario_id,login,hash FROM bovi.usuario --", '\\', "%_%"]:
        s, d = admin.json('GET', f'/sedes/{A}/contrapartes?pagina=1&tamano=100&q=' + urllib.parse.quote(payload))
        ok = s == 200 and d['total'] <= total and not any('hash' in json.dumps(e).lower() and '$2' in json.dumps(e) for e in d['elementos'])
        record('SEC-01', f'q={payload!r}', ok, f'HTTP {s}, total {d.get("total") if d else None} ≤ {total}', 'alta')
    for qs in ['estado=CONFIRMADA%27%20OR%201%3D1--', 'tipo=COMPRA%27--', 'pagina=1%20OR%201=1', 'tamano=20;DROP']:
        s, d = admin.json('GET', f'/sedes/{A}/operaciones?{qs}')
        record('SEC-01', f'filtro {qs}', s in (200, 400, 422), f'HTTP {s} (422 = valor de enum rechazado por validación)', 'alta')
    s, after = admin.json('GET', f'/sedes/{A}/contrapartes?pagina=1&tamano=1')
    record('SEC-01', 'tabla intacta tras payloads', s == 200 and after['total'] == total, f'total antes {total}, después {after["total"]}', 'crítica')
    # Nombre legítimo con apóstrofe funciona y se encuentra.
    legit = f"DEMO SEC O'Higgins {RUN}"
    s, c = admin.json('POST', f'/sedes/{A}/contrapartes', {'nombre': legit, 'tipo_persona': 'FISICA'})
    s2, found = admin.json('GET', f'/sedes/{A}/contrapartes?pagina=1&tamano=5&q=' + urllib.parse.quote("O'Higgins " + RUN))
    record('SEC-01', 'apóstrofe legítimo', s < 300 and found['total'] == 1, f'alta HTTP {s}, búsqueda total {found["total"]}', 'media')

    # SEC-10 paginación extrema / tamaño
    for qs in ['tamano=100000', 'tamano=0', 'tamano=-5', 'pagina=0', 'pagina=-1', 'pagina=99999999999999999999', 'tamano=abc']:
        s, d = admin.json('GET', f'/sedes/{A}/operaciones?{qs}')
        ok = s == 400 or (s == 200 and len(d['elementos']) <= 100)
        record('SEC-10', f'paginación {qs}', ok, f'HTTP {s}' + (f', {len(d["elementos"])} elementos' if s == 200 else ''), 'media')
    big = json.dumps({'nombre': 'DEMO SEC ' + 'x' * (3 * 1024 * 1024), 'tipo_persona': 'FISICA'}).encode()
    s, h, _ = admin.call('POST', f'/sedes/{A}/contrapartes', raw=big)
    record('SEC-10', 'cuerpo JSON de 3 MB rechazado antes de procesarse', s == 413, f'HTTP {s}', 'baja')
    s, _ = admin.json('GET', '/salud')
    record('SEC-10', 'servicio sano tras cuerpo grande', s == 200, f'/salud HTTP {s}', 'alta')

    # SEC-05 CSRF
    s, h, _ = admin.call('POST', f'/sedes/{A}/contrapartes', {'nombre': f'DEMO SEC sin csrf {RUN}', 'tipo_persona': 'FISICA'}, csrf=False, headers={'Idempotency-Key': str(uuid.uuid4())})
    record('SEC-05', 'comando sin token', s == 403, f'HTTP {s}', 'alta')
    s, h, _ = admin.call('POST', f'/sedes/{A}/contrapartes', {'nombre': f'DEMO SEC csrf falso {RUN}', 'tipo_persona': 'FISICA'}, headers={admin.csrf[0]: 'falso'})
    record('SEC-05', 'comando con token falso', s == 403, f'HTTP {s}', 'alta')
    s, d = admin.json('GET', f'/sedes/{A}/contrapartes?pagina=1&tamano=5&q=' + urllib.parse.quote(f'DEMO SEC sin csrf {RUN}'))
    record('SEC-05', 'sin efecto persistido', d['total'] == 0, f'coincidencias {d["total"]}', 'alta')
    anon = Client()
    s, h, _ = anon.call('POST', '/sesion/login', {'login': 'demo.admin', 'contrasena': 'x'}, csrf=False)
    record('SEC-05', 'login sin token CSRF', s == 403, f'HTTP {s}', 'media')

    # SEC-06 sesión: rotación al login, logout invalida, contraseña errónea genérica
    c = Client(); c.refresh(); before = c.session_cookie()
    c.login('demo.admin', 'demo_password'); after_login = c.session_cookie()
    record('SEC-06', 'rotación de sesión en login', before != after_login and after_login is not None, 'cookie cambia' if before != after_login else 'cookie igual', 'alta')
    stolen = [k for k in c.jar]
    s, _ = c.json('POST', '/sesion/logout', {})
    reuse = Client()
    for k in stolen:
        reuse.jar.set_cookie(k)
    s2, _ = reuse.json('GET', '/sesion/actual')
    record('SEC-06', 'cookie tras logout no sirve', s2 == 401, f'logout HTTP {s}, reuso HTTP {s2}', 'alta')
    w = Client(); w.refresh()
    s_bad, d_bad = w.json('POST', '/sesion/login', {'login': 'demo.admin', 'contrasena': 'incorrecta'})
    w.refresh(); s_nouser, d_nouser = w.json('POST', '/sesion/login', {'login': f'noexiste.{RUN}', 'contrasena': 'incorrecta'})
    same = s_bad == s_nouser and (d_bad or {}).get('mensaje') == (d_nouser or {}).get('mensaje')
    record('SEC-06', 'error de login uniforme', same, f'{s_bad} vs {s_nouser}', 'media')

    # SEC-10 abuso de login: 25 intentos fallidos seguidos
    codes = []
    target = f'demo.sec.lock.{RUN}'  # login inexistente: no bloquea cuentas DEMO reales
    for _ in range(12):
        w.refresh(); s, _ = w.json('POST', '/sesion/login', {'login': target, 'contrasena': 'incorrecta'}); codes.append(s)
    record('SEC-10', 'limitación de intentos de login (10 fallos/15 min)', codes[:10] == [401] * 10 and codes[10:] == [429, 429], f'secuencia: {codes}', 'media')
    other = Client().login('demo.caja', 'demo_caja_password')
    record('SEC-10', 'bloqueo acotado al usuario atacado (sin bloqueo global)', other < 300, f'otro usuario HTTP {other}', 'alta')

    # SEC-03/04 acceso horizontal: usuario sólo en sede A intenta sede B
    login = f'demo.sec.{RUN}'
    pw = 'DemoSec-' + uuid.uuid4().hex
    s, u = admin.json('POST', f'/sedes/{A}/usuarios', {'login': login, 'nombre': f'DEMO SEC {RUN}', 'contrasena': pw})
    if s < 300:
        s_m, _ = admin.json('POST', f'/sedes/{A}/usuarios/{u["id"]}/membresias', {'rol_codigo': 'OPERADOR', 'vigente': True})
        lim = Client(); st = lim.login(login, password=pw)
        s_me, me2 = lim.json('GET', '/sesion/actual')
        visible = [x['codigo'] for x in (me2 or {}).get('sedes', [])]
        record('SEC-03', 'usuario limitado ve sólo su sede', visible == ['DEMO-A'], f'sedes visibles {visible}', 'alta')
        s_ops, ops_b = admin.json('GET', f'/sedes/{B}/operaciones?pagina=1&tamano=1')
        s_pay, pays_b = admin.json('GET', f'/sedes/{B}/pagos?pagina=1&tamano=1')
        s_an, an_b = admin.json('GET', f'/sedes/{B}/animales?pagina=1&tamano=1')
        probes = [('GET', f'/sedes/{B}/operaciones?pagina=1&tamano=5'), ('GET', f'/sedes/{B}/reportes/cartera'),
                  ('GET', f'/sedes/{B}/reportes/inventario/csv')]
        if ops_b and ops_b['elementos']:
            oid = ops_b['elementos'][0]['id']
            probes += [('GET', f'/sedes/{B}/operaciones/{oid}'), ('GET', f'/sedes/{A}/operaciones/{oid}'), ('GET', f'/sedes/{B}/operaciones/{oid}/expediente')]
        if pays_b and pays_b['elementos']:
            probes += [('GET', f'/sedes/{B}/pagos/{pays_b["elementos"][0]["id"]}')]
        if an_b and an_b['elementos']:
            aid = an_b['elementos'][0]['id']
            probes += [('GET', f'/sedes/{B}/animales/{aid}/qr'), ('GET', f'/sedes/{A}/animales/{aid}')]
        for m, path in probes:
            s, h, body = lim.call(m, path, headers={'Accept': '*/*'})
            record('SEC-03', f'{m} {path.replace(B, "{B}").replace(A, "{A}")}', s in (403, 404), f'HTTP {s}, {len(body)} bytes', 'alta')
        s, h, _ = lim.call('POST', f'/sedes/{B}/contrapartes', {'nombre': f'DEMO SEC cruce {RUN}', 'tipo_persona': 'FISICA'})
        s2, d2 = admin.json('GET', f'/sedes/{B}/contrapartes?pagina=1&tamano=5&q=' + urllib.parse.quote(f'DEMO SEC cruce {RUN}'))
        record('SEC-03', 'escritura en sede ajena', s in (403, 404) and d2['total'] == 0, f'HTTP {s}, persistidos {d2["total"]}', 'crítica')
        # SEC-04: operador no puede crear usuarios ni asignarse ADMIN
        s, h, _ = lim.call('POST', f'/sedes/{A}/usuarios', {'login': f'demo.sec2.{RUN}', 'nombre': 'DEMO SEC 2', 'contrasena': 'DemoSec-' + uuid.uuid4().hex})
        record('SEC-04', 'operador crea usuario', s == 403, f'HTTP {s}', 'alta')
        s, h, _ = lim.call('POST', f'/sedes/{A}/usuarios/{u["id"]}/membresias', {'rol_codigo': 'ADMIN', 'vigente': True})
        record('SEC-04', 'operador se asigna ADMIN', s == 403, f'HTTP {s}', 'crítica')
        # SEC-06 membresía revocada surte efecto en sesión viva
        s_r, _ = admin.json('POST', f'/sedes/{A}/usuarios/{u["id"]}/membresias', {'rol_codigo': 'OPERADOR', 'vigente': False})
        s, h, _ = lim.call('GET', f'/sedes/{A}/operaciones?pagina=1&tamano=1')
        record('SEC-06', 'membresía revocada en sesión viva', s in (401, 403), f'revocar HTTP {s_r}, acceso HTTP {s}', 'alta')
    else:
        record('SEC-03', 'crear usuario de prueba', False, f'HTTP {s}', 'info')

    # SF-01: ADMIN sólo de B no administra usuarios que sólo pertenecen a A; nadie se bloquea a sí mismo.
    def make_user(site, role, tag):
        pw_ = 'DemoSec-' + uuid.uuid4().hex
        s_, u_ = admin.json('POST', f'/sedes/{site}/usuarios', {'login': f'demo.sec.{tag}.{RUN}', 'nombre': f'DEMO SEC {tag} {RUN}', 'contrasena': pw_})
        admin.json('POST', f'/sedes/{site}/usuarios/{u_["id"]}/membresias', {'rol_codigo': role, 'vigente': True})
        return u_['id'], f'demo.sec.{tag}.{RUN}', pw_
    b_admin, b_login, b_pw = make_user(B, 'ADMIN', 'admb')
    a_only, a_login, a_pw = make_user(A, 'OPERADOR', 'opa')
    adm_b = Client(); adm_b.login(b_login, password=b_pw)
    s, h, _ = adm_b.call('PATCH', f'/sedes/{B}/usuarios/{a_only}', {'estado': 'BLOQUEADO'}, headers={'Idempotency-Key': str(uuid.uuid4())})
    still = Client().login(a_login, password=a_pw)
    record('SEC-03', 'SF-01 ADMIN de B bloquea usuario sólo de A', s in (403, 404) and still < 300, f'PATCH HTTP {s}; login del usuario de A HTTP {still}', 'media')
    s, h, _ = adm_b.call('PATCH', f'/sedes/{B}/usuarios/{b_admin}', {'estado': 'BLOQUEADO'}, headers={'Idempotency-Key': str(uuid.uuid4())})
    record('SEC-04', 'ADMIN no puede bloquearse a sí mismo', s == 400, f'HTTP {s}', 'baja')
    s, h, _ = adm_b.call('PATCH', f'/sedes/{B}/usuarios/{b_admin}', {'nombre': f'DEMO SEC admb renombrado {RUN}'}, headers={'Idempotency-Key': str(uuid.uuid4())})
    record('SEC-04', 'ADMIN sí administra usuarios de su sede (sin regresión)', s == 200, f'HTTP {s}', 'media')

    # SF-03: sesiones anónimas creadas por GET /sesion/csrf (medición en pg-a, sólo lectura de conteo).
    import subprocess
    def sessions():
        out_ = subprocess.run(['docker', 'exec', 'bovicierre-academic-pg-a-1', 'psql', '-U', 'postgres', '-d', 'bovicierre', '-Atc', 'select count(*) from infra.spring_session'], capture_output=True, text=True).stdout.strip()
        return int(out_ or -1)
    n0 = sessions()
    for _ in range(100):
        Client().call('GET', '/sesion/csrf')
    n1 = sessions()
    ttl = subprocess.run(['docker', 'exec', 'bovicierre-academic-pg-a-1', 'psql', '-U', 'postgres', '-d', 'bovicierre', '-Atc', 'select max_inactive_interval from infra.spring_session where principal_name is null order by creation_time desc limit 1'], capture_output=True, text=True).stdout.strip()
    record('SEC-10', 'SF-03 sesión anónima de /sesion/csrf caduca en ≤5 min', ttl.isdigit() and int(ttl) <= 300, f'filas spring_session {n0} → {n1} (+{n1 - n0}); TTL anónimo {ttl or "?"} s', 'media')
    live = Client(); live.login('demo.auditor', 'demo_auditor_password')
    sid = live.session_cookie()
    ttl_auth = subprocess.run(['docker', 'exec', 'bovicierre-academic-pg-a-1', 'psql', '-U', 'postgres', '-d', 'bovicierre', '-Atc', "select max_inactive_interval from infra.spring_session where principal_name is not null order by last_access_time desc limit 1"], capture_output=True, text=True).stdout.strip()
    record('SEC-06', 'sesión autenticada conserva 30 min', ttl_auth == '1800', f'TTL autenticado {ttl_auth or "?"} s', 'media')

    # DIV-01: identificación duplicada (UNIQUE autogenerada *_key) → 409, no 500.
    code = f'DEMO-SEC-DUP-{RUN}'
    s1, _ = admin.json('POST', f'/sedes/{A}/animales', {'sexo': 'M', 'identificaciones': [{'sistema': 'INTERNO', 'codigo': code}]})
    s2, d2 = admin.json('POST', f'/sedes/{A}/animales', {'sexo': 'M', 'identificaciones': [{'sistema': 'INTERNO', 'codigo': code.replace('-', '')}]})
    record('SEC-11', 'DIV-01 identificación duplicada → 409 sin detalle SQL', s1 == 201 and s2 == 409 and 'duplicate' not in json.dumps(d2), f'primera HTTP {s1}, duplicada HTTP {s2} {(d2 or {}).get("codigo")}', 'media')
    s3, d3 = admin.json('POST', f'/sedes/{A}/usuarios', {'login': login, 'nombre': 'DEMO SEC duplicado', 'contrasena': 'DemoSec-' + uuid.uuid4().hex})
    record('SEC-11', 'DIV-01 login duplicado → 409', s3 == 409, f'HTTP {s3} {(d3 or {}).get("codigo")}', 'media')

    # SEC-04 mass assignment: campos ajenos en el cuerpo se ignoran o rechazan
    s, c2 = admin.json('POST', f'/sedes/{A}/contrapartes', {'nombre': f'DEMO SEC mass {RUN}', 'tipo_persona': 'FISICA', 'empresa_id': str(uuid.uuid4()), 'sucursal_id': B, 'id': str(uuid.uuid4())})
    s2, d2 = admin.json('GET', f'/sedes/{B}/contrapartes?pagina=1&tamano=5&q=' + urllib.parse.quote(f'DEMO SEC mass {RUN}'))
    record('SEC-04', 'campos protegidos en cuerpo', s in (400, 422) or (s < 300 and d2['total'] == 0), f'HTTP {s}; visible en B: {d2["total"]}', 'alta')

    # SEC-07/09 contenido activo almacenado y CSV
    xss = f'DEMO SEC <img src=x onerror=alert(1)> {RUN}'
    formula = f'=HYPERLINK("http://ejemplo.invalid","DEMO SEC {RUN}")'
    s1, _ = admin.json('POST', f'/sedes/{A}/contrapartes', {'nombre': xss, 'tipo_persona': 'FISICA'})
    s2, _ = admin.json('POST', f'/sedes/{A}/contrapartes', {'nombre': formula, 'tipo_persona': 'FISICA'})
    s, h, body = admin.call('GET', f'/sedes/{A}/contrapartes?pagina=1&tamano=5&q=' + urllib.parse.quote('DEMO SEC <img'))
    record('SEC-07', 'API devuelve JSON (no HTML) para nombre con etiqueta', s == 200 and 'json' in h.get('Content-Type', ''), f'Content-Type {h.get("Content-Type")}', 'media')
    s, h, body = admin.call('GET', f'/sedes/{A}/reportes/cartera/csv')
    text = body.decode('utf-8', 'replace')
    record('SEC-09', 'CSV cartera descargable con tipo y disposición', s == 200 and 'attachment' in h.get('Content-Disposition', ''), f'HTTP {s}, {h.get("Content-Type")}, {h.get("Content-Disposition")}', 'baja')
    unsafe = [line for line in text.splitlines() if any(cell.strip('"').startswith(('=', '+', '-', '@')) and 'DEMO SEC' in cell for cell in line.split(','))]
    record('SEC-09', 'fórmulas neutralizadas en CSV', not unsafe, f'celdas peligrosas: {len(unsafe)} (sólo cuentan si la contraparte aparece en este reporte)', 'media')
    s, h, body = Client().call('GET', f'/sedes/{A}/animales/{uuid.uuid4()}/qr')
    record('SEC-09', 'QR anónimo rechazado', s in (401, 403), f'HTTP {s}', 'alta')

    # SEC-11 cabeceras y errores
    s, h, body = Client().call('GET', BASE.rsplit('/api/', 1)[0] + '/')
    hl = {k.lower(): v for k, v in h.items()}
    for name in ['content-security-policy', 'x-content-type-options', 'referrer-policy', 'x-frame-options']:
        present = name in hl or (name == 'x-frame-options' and 'frame-ancestors' in hl.get('content-security-policy', ''))
        record('SEC-11', f'cabecera {name} en /', present, hl.get(name, 'ausente'), 'media' if name != 'x-content-type-options' else 'baja')
    record('SEC-11', 'sin cabecera Server', 'server' not in hl, hl.get('server', 'ausente'), 'baja')
    s, h, body = admin.call('GET', f'/sedes/{A}/operaciones/no-es-uuid')
    leak = any(k in body.decode('utf-8', 'replace') for k in ['org.postgresql', 'SQLException', 'at mx.', 'Exception:', 'PSQL'])
    record('SEC-11', 'error sin stack/SQL', not leak and s < 500, f'HTTP {s}, fuga={leak}', 'media')
    cookie_hdr = None
    c = Client(); c.refresh()
    req = urllib.request.Request(BASE + '/sesion/login', data=json.dumps({'login': 'demo.auditor', 'contrasena': (SECRETS / 'demo_auditor_password').read_text().strip()}).encode(), method='POST', headers={'Content-Type': 'application/json', c.csrf[0]: c.csrf[1]})
    try:
        with c.opener.open(req) as r:
            cookie_hdr = r.headers.get('Set-Cookie', '')
    except urllib.error.HTTPError as e:
        cookie_hdr = e.headers.get('Set-Cookie', '')
    flags = (cookie_hdr or '').lower()
    record('SEC-11', 'cookie de sesión HttpOnly + SameSite', 'httponly' in flags and 'samesite' in flags, ('HttpOnly' if 'httponly' in flags else 'sin HttpOnly') + ', ' + ('SameSite' if 'samesite' in flags else 'sin SameSite') + ', Secure no aplica en HTTP local', 'media')
    s, h, _ = admin.call('OPTIONS', f'/sedes/{A}/operaciones', headers={'Origin': 'http://evil.invalid', 'Access-Control-Request-Method': 'POST'})
    acao = {k.lower(): v for k, v in h.items()}.get('access-control-allow-origin')
    record('SEC-11', 'CORS no refleja origen ajeno', acao in (None, ''), f'HTTP {s}, ACAO={acao}', 'alta')

    out.parent.mkdir(parents=True, exist_ok=True)
    summary = {'base': BASE, 'run': RUN, 'ejecutados': len(results), 'pass': sum(r['resultado'] == 'PASS' for r in results),
               'fail': sum(r['resultado'] == 'FAIL' for r in results), 'casos': results}
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\n{summary['pass']} PASS / {summary['fail']} FAIL de {summary['ejecutados']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
