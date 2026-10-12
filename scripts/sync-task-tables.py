#!/usr/bin/env python3
"""Genera las tablas/listas del README desde el backlog canónico, sin cambiar estados."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
backlog = (ROOT / 'docs/project/backlog.md').read_text()
sections = []
for title, prefix, expected in [('Aldo — backend, bases de datos e infraestructura', 'A', 33),
                                ('Jared — frontend y experiencia de usuario', 'J', 22)]:
    rows = [line for line in backlog.splitlines() if line.startswith(f'| [ ] | TASK-{prefix}-') or line.startswith(f'| [x] | TASK-{prefix}-')]
    assert len(rows) == expected, (prefix, len(rows))
    header = next(line for line in backlog.splitlines() if line.startswith(('| Verificación local | ID |', '| Estado | ID |')))
    separator = '|' + '---|' * (header.count('|') - 1)
    sections.append('### ' + title + '\n\n' + '\n'.join([header, separator] + rows))
    checks = []
    for row in rows:
        columns = [cell.strip() for cell in row.strip('|').split('|')]
        assert re.fullmatch(r'TASK-[AJ]-\d{3}', columns[1])
        checks.append(f'- {columns[0]} {columns[1]} — {columns[2]}')
    sections.append('### Lista de ' + title.split(' — ')[0] + '\n\n' + '\n'.join(checks))
readme = ROOT / 'README.md'
text = readme.read_text()
start = text.index('## Tareas\n')
end = text.index('## Documentación\n', start)
text = text[:start] + '## Tareas\n\nFuente única: [backlog](docs/project/backlog.md). Estas tablas/listas se regeneran con `python3 scripts/sync-task-tables.py`. Casillas [x] = verificación técnica local con evidencia; aceptación humana y Kanban Hecho se registran por separado.\n\n' + '\n\n'.join(sections) + '\n\n' + text[end:]
readme.write_text(text)
print('README sincronizado: 33 tareas Aldo, 22 Jared; estados conservados.')
