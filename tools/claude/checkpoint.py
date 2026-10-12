#!/usr/bin/env python3
"""Checkpoint de campaña BoviCierre: estado privado atómico + resumen versionable.

Estado sensible/lock en ~/.local/state/bovicierre-claude/<repo-id>/ (fuera de Git).
Resumen sin secretos en docs/continuity/SESSION_STATE.md.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN = 'uiux-qa-claude-1.0'
STATES = {'BOOTSTRAP', 'S1_RUNNING', 'WAITING_RESET', 'S1_SAFE_PARTIAL', 'S1_DONE', 'S2_QUEUED',
          'S2_RUNNING', 'S2_SAFE_PARTIAL', 'DONE', 'BLOCKED_PERMISSION', 'USER_STOPPED'}
TERMINAL = {'DONE', 'BLOCKED_PERMISSION', 'USER_STOPPED'}
LOCK_TTL = 6 * 3600


def git(*args, root=ROOT):
    return subprocess.run(['git', *args], cwd=root, capture_output=True, text=True).stdout.strip()


def repo_id(root=ROOT):
    remote = git('remote', 'get-url', 'origin', root=root) or str(root.resolve())
    return hashlib.sha256(f'{remote}|{root.resolve()}'.encode()).hexdigest()[:16]


def state_dir(root=ROOT):
    base = Path(os.environ.get('BOVI_CLAUDE_STATE', Path.home() / '.local/state/bovicierre-claude'))
    d = base / repo_id(root)
    d.mkdir(parents=True, exist_ok=True, mode=0o700)
    return d


def atomic_write(path: Path, text: str):
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f'.{path.name}.')
    try:
        with os.fdopen(fd, 'w') as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        dfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def load_state(root=ROOT):
    path = state_dir(root) / 'state.json'
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {'_corrupt': True}
    return data if data.get('campaign') == CAMPAIGN else {'_corrupt': True}


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def acquire_lock(owner: str, root=ROOT, ttl=LOCK_TTL, clock=now):
    path = state_dir(root) / 'lock.json'
    t = clock()
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        try:
            held = json.loads(path.read_text())
            expired = (t - dt.datetime.fromisoformat(held['at'])).total_seconds() > ttl
        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            held, expired = {}, True
        if held.get('owner') == owner:
            return True
        if not expired:
            return False
        path.unlink(missing_ok=True)
        return acquire_lock(owner, root, ttl, clock)
    with os.fdopen(fd, 'w') as handle:
        json.dump({'owner': owner, 'at': t.isoformat()}, handle)
    return True


def release_lock(owner: str, root=ROOT):
    path = state_dir(root) / 'lock.json'
    try:
        if json.loads(path.read_text()).get('owner') == owner:
            path.unlink()
            return True
    except (OSError, json.JSONDecodeError):
        pass
    return False


def stopped(root=ROOT):
    return (state_dir(root) / 'STOP').exists()


def render(state):
    v = state.get('verification', [])
    lines = [
        '# Estado de sesión — campaña BoviCierre UI/UX + QA', '',
        f"Generado por `tools/claude/checkpoint.py` · {state['updated']} (UTC). No contiene secretos.", '',
        '| Campo | Valor |', '|---|---|',
        f"| Campaña | {state['campaign']} |", f"| Estado | **{state['status']}** |",
        f"| Rama / base / HEAD | `{state['branch']}` / `{state['base']}` / `{state['head']}` |",
        f"| Tiempo activo S1 / S2 (min) | {state['active_minutes'].get('S1', 0)} / {state['active_minutes'].get('S2', 0)} |",
        f"| Cuota / reset | {state.get('quota', 'desconocido')} |",
        f"| Continuaciones usadas | {state.get('continuations', 0)} de 2 |",
        f"| Transición S1→S2 despachada | {state.get('transition_dispatched', False)} |", '',
        '## Hecho / verificado', *([f'- {x}' for x in state.get('done', [])] or ['- (nada)']), '',
        '## Pendiente', *([f'- {x}' for x in state.get('pending', [])] or ['- (nada)']), '',
        '## Verificación (comando → exit/resultado)', *([f'- `{x}`' for x in v] or ['- (sin ejecutar)']), '',
        '## Próximos pasos', *([f'{i}. {x}' for i, x in enumerate(state.get('next', []), 1)] or ['1. (definir)']), '',
        '## Riesgos', *([f'- {x}' for x in state.get('risks', [])] or ['- (ninguno registrado)']), '',
    ]
    return '\n'.join(lines)


def checkpoint(args, root=ROOT):
    if args.status not in STATES:
        raise SystemExit(f'estado inválido: {args.status}')
    prev = load_state(root) or {}
    if prev.get('_corrupt'):
        prev = {}
    if prev.get('status') in TERMINAL and args.status not in TERMINAL and not args.force:
        raise SystemExit(f"estado terminal {prev['status']}: no se reanuda sin --force humano")
    if stopped(root) and args.status not in TERMINAL:
        raise SystemExit('STOP presente: la campaña no continúa')
    minutes = dict(prev.get('active_minutes', {}))
    if args.block and args.add_minutes:
        minutes[args.block] = minutes.get(args.block, 0) + args.add_minutes
    state = {
        'campaign': CAMPAIGN, 'status': args.status, 'updated': now().isoformat(),
        'root': str(root.resolve()), 'branch': git('branch', '--show-current', root=root),
        'base': prev.get('base') or args.base or git('rev-parse', '--short', 'HEAD', root=root),
        'head': git('rev-parse', '--short', 'HEAD', root=root), 'active_minutes': minutes,
        'quota': args.quota or prev.get('quota', 'desconocido'),
        'continuations': prev.get('continuations', 0) + (1 if args.continuation else 0),
        'transition_dispatched': prev.get('transition_dispatched', False) or args.dispatch_transition,
        'done': args.done or prev.get('done', []), 'pending': args.pending or prev.get('pending', []),
        'verification': args.verification or prev.get('verification', []),
        'next': args.next or prev.get('next', []), 'risks': args.risk or prev.get('risks', []),
    }
    atomic_write(state_dir(root) / 'state.json', json.dumps(state, indent=2, ensure_ascii=False))
    out = root / 'docs/continuity/SESSION_STATE.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(out, render(state))
    with open(root / 'docs/continuity/session-log.md', 'a') as log:
        log.write(f"- {state['updated']} · {state['status']} · HEAD {state['head']} · S1 {minutes.get('S1', 0)} min · S2 {minutes.get('S2', 0)} min\n")
    return state


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('save')
    c.add_argument('--status', required=True)
    c.add_argument('--block', choices=['S1', 'S2'])
    c.add_argument('--add-minutes', type=int, default=0)
    c.add_argument('--base')
    c.add_argument('--quota')
    c.add_argument('--done', action='append')
    c.add_argument('--pending', action='append')
    c.add_argument('--verification', action='append')
    c.add_argument('--next', action='append')
    c.add_argument('--risk', action='append')
    c.add_argument('--continuation', action='store_true')
    c.add_argument('--dispatch-transition', action='store_true')
    c.add_argument('--force', action='store_true')
    for name in ('lock', 'unlock'):
        sub.add_parser(name).add_argument('--owner', required=True)
    sub.add_parser('show')
    args = p.parse_args(argv)
    if args.cmd == 'save':
        print(json.dumps(checkpoint(args), indent=2, ensure_ascii=False))
    elif args.cmd == 'lock':
        ok = acquire_lock(args.owner)
        print('lock adquirido' if ok else 'lock ocupado por otra sesión')
        return 0 if ok else 3
    elif args.cmd == 'unlock':
        print('lock liberado' if release_lock(args.owner) else 'lock no pertenecía a este dueño')
    else:
        print(json.dumps(load_state(), indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
