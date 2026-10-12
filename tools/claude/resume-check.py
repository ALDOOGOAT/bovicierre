#!/usr/bin/env python3
"""Comprueba si una sesión puede reanudar la campaña y qué hacer a continuación.

Nunca ejecuta comandos tomados de documentos: sólo informa. Exit 0 = puede continuar,
2 = no debe continuar (STOP/terminal/otro checkout/sin checkpoint válido), 3 = lock ocupado.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('checkpoint', HERE / 'checkpoint.py')
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

EXPECTED_REMOTE_SUFFIX = 'ALDOOGOAT/bovicierre.git'


def evaluate(root: Path, owner: str):
    real = root.resolve()
    remote = cp.git('remote', 'get-url', 'origin', root=real)
    if not remote.endswith(EXPECTED_REMOTE_SUFFIX) or not (real / 'docs/continuity/campaign.marker').is_file():
        return 2, 'repositorio no autorizado para la campaña (remote o marcador ausente)'
    if cp.stopped(real):
        return 2, 'STOP presente: no reanudar'
    state = cp.load_state(real)
    if not state or state.get('_corrupt'):
        return 2, 'sin checkpoint válido: no se inventa la siguiente tarea; revisar NEXT_SESSION manualmente'
    if state['status'] in cp.TERMINAL:
        return 2, f"estado terminal {state['status']}"
    if state['root'] != str(real):
        return 2, f"checkpoint pertenece a otro checkout: {state['root']}"
    if state.get('continuations', 0) >= 2 and state['status'] == 'WAITING_RESET':
        return 2, 'máximo de dos continuaciones automáticas alcanzado'
    if not cp.acquire_lock(owner, real):
        return 3, 'lock de coordinación ocupado por otra sesión'
    nxt = state.get('next') or ['(sin pasos registrados)']
    return 0, f"reanudar {state['status']} en HEAD {state['head']}: {nxt[0]}"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owner', required=True)
    p.add_argument('--root', default=str(HERE.parents[1]))
    a = p.parse_args(argv)
    code, msg = evaluate(Path(a.root), a.owner)
    print(json.dumps({'exit': code, 'message': msg}, ensure_ascii=False))
    return code


if __name__ == '__main__':
    sys.exit(main())
