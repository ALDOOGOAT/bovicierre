#!/usr/bin/env python3
"""DIV-11: cada ruta de los controladores Java debe estar en docs/api/openapi.yaml (método + path).

Falla con la lista de rutas sin contrato. No exige lo inverso: OpenAPI puede declarar rutas de Caddy o públicas.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def norm(path):
    return re.sub(r'\{[^}]+\}', '{}', path)


def main():
    spec = yaml.safe_load((ROOT / 'docs/api/openapi.yaml').read_text())
    documented = {(m.upper(), norm(p)) for p, ops in spec['paths'].items() for m in ops if m in ('get', 'post', 'put', 'patch', 'delete')}
    routes = set()
    for source in (ROOT / 'backend/src/main/java').rglob('*.java'):
        text = source.read_text()
        base = re.search(r'@RequestMapping\("([^"]*)"\)', text)
        prefix = base.group(1) if base else ''
        for method, args in re.findall(r'@(Get|Post|Put|Patch|Delete)Mapping\(([^)]*)\)', text):
            for path in re.findall(r'"(/[^"]*)"', args):
                routes.add((method.upper(), (prefix + path).replace('/api/v1', '', 1)))
    missing = sorted(r for r in routes if (r[0], norm(r[1])) not in documented)
    if not routes:
        print('FAIL: no se encontraron rutas Java')
        return 1
    if missing:
        print('FAIL: rutas sin contrato OpenAPI:')
        for method, path in missing:
            print(f'  {method} {path}')
        return 1
    print(f'PASS: {len(routes)} rutas Java documentadas en OpenAPI')
    return 0


if __name__ == '__main__':
    sys.exit(main())
