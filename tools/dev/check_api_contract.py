#!/usr/bin/env python3
"""Valida tráfico DEMO real contra OpenAPI; no guarda payloads ni cookies."""
import argparse
import http.cookiejar
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
import urllib.parse
import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='http://127.0.0.1:18080/api/v1')
    args = parser.parse_args()
    url = urllib.parse.urlparse(args.base)
    if url.scheme != 'http' or url.hostname not in ('127.0.0.1', 'localhost') or url.username or url.password or url.path != '/api/v1':
        raise SystemExit('Sólo localhost autorizado para estas credencialesDEMO.')
    contract = yaml.safe_load((ROOT / 'docs/api/openapi.yaml').read_text())
    resolver = jsonschema.RefResolver.from_schema(contract)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    csrf = {}
    results = []

    def call(method, path, template=None, body=None, expected=200):
        op = contract['paths'][template or path][method.lower()]
        if body is not None and 'requestBody' in op:
            schema = op['requestBody']['content']['application/json']['schema']
            if any(jsonschema.Draft202012Validator(schema, resolver=resolver, format_checker=jsonschema.FormatChecker()).iter_errors(body)):
                raise RuntimeError('Request no concuerda con contrato; contenido privado omitido')
        headers = {'Content-Type': 'application/json', **({csrf['headerName']: csrf['token']} if csrf else {})}
        request = urllib.request.Request(args.base + path, data=json.dumps(body).encode() if body is not None else None, headers=headers, method=method)
        try:
            response = opener.open(request, timeout=20)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            raw = response.read()
            spec = op['responses'].get(str(response.status), {})
            if '$ref' in spec:
                spec = resolver.resolve(spec['$ref'])[1]
            payload = json.loads(raw) if raw else None
            errors = [] if response.status == expected else [{'path': 'http', 'rule': 'expected-status'}]
            content = spec.get('content', {})
            media = response.headers.get('Content-Type', '').split(';', 1)[0]
            if content and media not in content:
                errors.append({'path': 'Content-Type', 'rule': 'declared-media-type'})
            if media in content:
                validator = jsonschema.Draft202012Validator(content[media]['schema'], resolver=resolver, format_checker=jsonschema.FormatChecker())
                errors.extend({'path': '.'.join(map(str, e.absolute_path)), 'rule': e.validator} for e in validator.iter_errors(payload))
            results.append({'method': method, 'path': template or path, 'http': response.status, 'errors': errors})
            return payload

    call('GET', '/sesion/actual', expected=401)
    csrf.update(call('GET', '/sesion/csrf'))
    secret = Path(os.environ.get('BOVI_SECRET_DIR', Path.home() / '.local/share/bovicierre-academic/secrets')) / 'demo_password'
    call('POST', '/sesion/login', body={'login': 'demo.admin', 'contrasena': secret.read_text().strip()}, expected=204)
    csrf.update(call('GET', '/sesion/csrf'))
    call('GET', '/sesion/actual')
    site = '/sedes/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
    for suffix in ('operaciones', 'inventario/posiciones', 'pagos', 'gastos', 'documentos', 'periodos', 'usuarios', 'reportes/cartera', 'reportes/margen'):
        call('GET', site+'/'+suffix, '/sedes/{sedeId}/'+suffix)
    call('GET', site+'/integraciones/diagnostico', '/sedes/{sedeId}/integraciones/diagnostico')
    call('GET', '/salud')
    call('POST', '/sesion/logout', body={}, expected=204)
    print(json.dumps({'scope': 'Tráfico DEMO de sesión y nueve consultas; no cubre todo el contrato.', 'checks': results}, indent=2))
    return 1 if any(r['errors'] for r in results) else 0


if __name__ == '__main__':
    raise SystemExit(main())
