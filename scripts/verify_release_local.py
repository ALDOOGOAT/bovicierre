#!/usr/bin/env python3
"""Puerta de aceptación local (AUD-02): ejecuta las suites por etapas, en serie, y falla si alguna obligatoria
falla, no se ejecuta o reporta pruebas omitidas. No usa `|| true` ni reescribe reportes.

Requiere la aplicación levantada (`make academic`) y secretos externos. La etapa SQL usa su harness aislado y
no debe coincidir con E2E/carga/backup; por eso todo corre secuencialmente.
Uso: python3 scripts/verify_release_local.py [--out DIR] [--skip-stage NOMBRE ...] [--with-load]
"""
import argparse
import glob
import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRETS = Path(os.environ.get('BOVI_SECRET_DIR', Path.home() / '.local/share/bovicierre-academic/secrets'))
URL = os.environ.get('BOVI_UI_TEST_URL', 'http://127.0.0.1:15180')
MANDATORY = ['docs', 'frontend', 'backend', 'sql', 'immutability', 'e2e', 'security']


def surefire():
    t = f = e = s = 0
    for p in glob.glob(str(ROOT / 'backend/target/surefire-reports/*.txt')):
        m = re.search(r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)', Path(p).read_text())
        if m:
            a, b, c, d = map(int, m.groups()); t += a; f += b; e += c; s += d
    return {'executed': t - s, 'failed': f + e, 'skipped': s}


def node_test(out):
    g = lambda k: int((re.search(rf'^# {k} (\d+)', out, re.M) or [0, 0])[1])
    return {'executed': g('pass') + g('fail'), 'failed': g('fail'), 'skipped': g('skipped') + g('todo')}


def playwright(out):
    g = lambda k: int((re.search(rf'(\d+) {k}', out) or [0, 0])[1])
    return {'executed': g('passed') + g('failed') + g('flaky'), 'failed': g('failed') + g('flaky'), 'skipped': g('skipped')}


def sql(out):
    return {'executed': len(re.findall(r'^PASS', out, re.M)) + len(re.findall(r'^FAIL', out, re.M)), 'failed': len(re.findall(r'^FAIL', out, re.M)), 'skipped': out.count('NO_FIXTURE_UNTESTED')}


def jsonfile(path, ok_key='pass', fail_key='fail'):
    def parse(_):
        d = json.loads(Path(path).read_text())
        return {'executed': d.get('ejecutados', d.get(ok_key, 0)), 'failed': d.get(fail_key, d.get('fallos', 0)), 'skipped': len(d.get('sin_fixture', []))}
    return parse


def stages(out_dir, with_load):
    env = {**os.environ, 'BOVI_API_IT': 'true', 'BOVI_TC_IT': 'true', 'BOVI_API_TEST_URL': URL + '/api/v1',
           'BOVI_TEST_PASSWORD_FILE': str(SECRETS / 'demo_password'), 'BOVI_UI_TEST_URL': URL, 'BOVI_SECRET_DIR': str(SECRETS)}
    s = [
        ('docs', ['make', 'verify-docs'], None),
        ('frontend', ['sh', '-c', 'npm --prefix frontend run build && npm --prefix frontend test'], node_test),
        ('backend', ['./backend/mvnw', '-q', '-f', 'backend/pom.xml', 'verify'], lambda _: surefire()),
        ('sql', ['make', 'verify-sql'], sql),
        ('immutability', ['python3', 'db/tests/immutability.py', '--out', str(out_dir / 'immutability.json')], jsonfile(out_dir / 'immutability.json')),
        ('e2e', ['npm', '--prefix', 'frontend', 'run', 'test:e2e', '--', 'closure.spec.ts', 'additional.spec.ts', 'keyboard.spec.ts', 'visual.spec.ts', 'academic.spec.ts'], playwright),
        ('security', ['python3', 'tests/security/sec_dynamic.py', '--out', str(out_dir / 'security.json')], jsonfile(out_dir / 'security.json')),
    ]
    if with_load:
        s.append(('load', ['k6', 'run', '--quiet', '--summary-export', str(out_dir / 'k6.json'), 'tests/performance/load.js'], None))
    return s, env


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', default=str(ROOT / 'docs/testing/evidence/release-local' / time.strftime('%Y%m%dT%H%M')))
    p.add_argument('--skip-stage', action='append', default=[])
    p.add_argument('--with-load', action='store_true')
    a = p.parse_args()
    out_dir = Path(a.out); out_dir.mkdir(parents=True, exist_ok=True)
    plan, env = stages(out_dir, a.with_load)
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT, capture_output=True, text=True).stdout.strip())
    report = {'head': head, 'arbol_modificado': dirty, 'url': URL, 'host': platform.node(), 'inicio': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'etapas': []}
    ok = True
    for name, cmd, parse in plan:
        if name in a.skip_stage:
            report['etapas'].append({'etapa': name, 'estado': 'OMITIDA', 'obligatoria': name in MANDATORY})
            ok &= name not in MANDATORY
            print(f'OMITIDA {name}')
            continue
        t0 = time.time()
        r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
        log = out_dir / f'{name}.log'
        log.write_text(r.stdout + '\n--- stderr ---\n' + r.stderr)
        counts = parse(r.stdout + r.stderr) if parse else {}
        failed = r.returncode != 0 or counts.get('failed', 0) > 0 or (name in MANDATORY and counts.get('skipped', 0) > 0) or (parse and counts.get('executed', 0) == 0)
        report['etapas'].append({'etapa': name, 'comando': ' '.join(cmd), 'exit': r.returncode, 'segundos': round(time.time() - t0, 1),
                                 **counts, 'estado': 'FALLÓ' if failed else 'PASS', 'obligatoria': name in MANDATORY, 'log': log.name})
        ok &= not failed
        print(f"{'FALLÓ' if failed else 'PASS '} {name} exit={r.returncode} {counts} {round(time.time() - t0)}s")
    report['fin'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    report['resultado'] = 'PASS' if ok else 'FALLÓ'
    report['nota'] = 'Verificación técnica local; no es aceptación humana, despliegue ni certificación de seguridad.'
    (out_dir / 'release-gate.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(f"RESULTADO {report['resultado']} → {out_dir / 'release-gate.json'}")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
