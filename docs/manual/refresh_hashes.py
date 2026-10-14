#!/usr/bin/env python3
"""Recalcula los SHA-256 del capítulo «Fuentes y trazabilidad» con los archivos actuales (ejecutar antes de build.py)."""
import hashlib, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
tex = ROOT / 'docs/manual/source/manual.tex'
s = tex.read_text(); start = s.index('\\chapter{Fuentes y trazabilidad del')
pat = re.compile(r'(\\softcode\{([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)\}\}\{\2\}\n&\n\\texorpdfstring\{\\softcode\{)([0-9a-f]{64})(\}\}\{)([0-9a-f]{64})\}')
count = {'iguales': 0, 'actualizados': 0, 'inexistentes': 0}


def fix(m):
    f = ROOT / m.group(2)
    if not f.is_file(): count['inexistentes'] += 1; return m.group(0)
    new = hashlib.sha256(f.read_bytes()).hexdigest()
    count['iguales' if new == m.group(3) else 'actualizados'] += 1
    return m.group(1) + new + m.group(4) + new + '}'


tex.write_text(s[:start] + pat.sub(fix, s[start:]))
print(count)
