#!/usr/bin/env python3
"""Diagnóstico local sin modificar servicios ni mostrar configuración privada."""
import json
import os
import platform
from pathlib import Path
import shutil
import socket
import subprocess
import sys

COMMANDS = {
    'java': ['java', '-version'], 'maven': ['mvn', '-version'],
    'node': ['node', '--version'], 'npm': ['npm', '--version'],
    'python': ['python3', '--version'], 'docker': ['docker', 'version', '--format', '{{.Server.Version}}'],
    'compose': ['docker', 'compose', 'version', '--short'], 'psql': ['psql', '--version'],
    'codex': ['codex', '--version'], 'graphify': ['graphify', '--version'],
}


def inspect_command(command):
    if not shutil.which(command[0]):
        return {'ok': False, 'error': 'ejecutable ausente'}
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        return {'ok': False, 'error': type(error).__name__}
    lines = (result.stdout or result.stderr).strip().splitlines()
    return {'ok': result.returncode == 0, 'exit_code': result.returncode, 'version': lines[0] if lines else ''}


def listening(port):
    with socket.socket() as connection:
        connection.settimeout(.2)
        return connection.connect_ex(('127.0.0.1', port)) == 0


def resources():
    memory = Path('/proc/meminfo')
    total = next((int(line.split()[1]) // 1024 for line in memory.read_text().splitlines() if line.startswith('MemTotal:')), None) if memory.exists() else None
    return {'sistema': platform.platform(), 'shell': os.environ.get('SHELL'), 'cpu_logicos': os.cpu_count(), 'memoria_total_mib': total}


def main():
    if '--self-check' in sys.argv:
        assert inspect_command([sys.executable, '-c', 'print("diagnostico")'])['version'] == 'diagnostico'
        assert not inspect_command(['bovicierre-ejecutable-inexistente'])['ok']
        assert resources()['sistema']
        assert resources()['memoria_total_mib'] is None or resources()['memoria_total_mib'] > 0
        print('doctor self-check OK')
        return 0
    result = {name: inspect_command(command) for name, command in COMMANDS.items()}
    result['recursos'] = resources()
    result['puertos'] = {str(port): 'ocupado; identificar servicio antes de arrancar' if listening(port) else 'libre'
                         for port in (15432, 15433, 15434, 19999, 19998, 18080, 15173, 15180)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if all(result[name]['ok'] for name in ('java', 'node', 'npm', 'python', 'docker', 'compose', 'psql')) else 1


if __name__ == '__main__':
    raise SystemExit(main())
