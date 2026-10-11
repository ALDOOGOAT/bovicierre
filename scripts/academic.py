#!/usr/bin/env python3
"""Arranque académico integrado; rechaza un backend manual concurrente."""
import os
from pathlib import Path
import socket
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def busy(port):
    with socket.socket() as connection:
        connection.settimeout(.2)
        return connection.connect_ex(('127.0.0.1', port)) == 0


def main():
    if busy(18080):
        raise SystemExit('API manual en18080: detenerla gradualmente antes de iniciar la aplicación en contenedores.')
    private = Path(os.environ.get('BOVI_PRIVATE_DIR', Path.home() / '.local/share/bovicierre-academic'))
    docs = private / 'private-documents'
    docs.mkdir(parents=True, exist_ok=True, mode=0o700)
    if docs.stat().st_uid != os.getuid() or docs.stat().st_mode & 0o077:
        raise SystemExit('El directorio privado debe pertenecer al usuario y tener permisos0700.')
    env = {**os.environ, 'BOVI_PRIVATE_DIR': str(private), 'BOVI_SECRET_DIR': os.environ.get('BOVI_SECRET_DIR', str(private / 'secrets')), 'BOVI_UID': str(os.getuid()), 'BOVI_GID': str(os.getgid())}
    subprocess.run(['sh', 'db/bootstrap/start.sh'], cwd=ROOT, env=env, check=True)
    subprocess.run(['docker', 'compose', '-p', 'bovicierre-academic', '-f', 'infra/compose/compose.academic.yml', '-f', 'infra/compose/application.yml', 'up', '-d', '--build', 'backend', 'frontend', 'caddy'], cwd=ROOT, env=env, check=True)
    print('Aplicación académica: http://localhost:15180; conservando datos.')


if __name__ == '__main__':
    main()
