#!/usr/bin/env python3
"""Ejecuta API y Vite en primer plano; Ctrl+C detiene únicamente sus hijos."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from doctor import listening

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [(ROOT / 'backend', ['./run-local.sh']),
            (ROOT / 'frontend', ['npm', 'run', 'dev'])]


def stop(children):
    for child in children:
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
    for child in children:
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()


def main():
    if '--self-check' in sys.argv:
        child = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(20)'], start_new_session=True)
        stop([child])
        assert child.poll() is not None
        assert all(directory.is_dir() for directory, _ in COMMANDS)
        print('dev self-check OK')
        return 0
    if any(listening(port) for port in (18080, 15173, 15180)):
        print('API/Vite/Caddy ya ocupan 18080/15173/15180. Identifica esos procesos; no se reemplazan.', file=sys.stderr)
        return 1
    children = []
    try:
        for directory, command in COMMANDS:
            children.append(subprocess.Popen(command, cwd=directory, start_new_session=True))
        print('API http://127.0.0.1:18080 · UI http://127.0.0.1:15173 · Ctrl+C para detener', flush=True)
        while all(child.poll() is None for child in children):
            time.sleep(.25)
        return next((child.returncode for child in children if child.returncode is not None), 1)
    except KeyboardInterrupt:
        return 0
    finally:
        stop(children)


if __name__ == '__main__':
    raise SystemExit(main())
