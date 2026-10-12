#!/usr/bin/env python3
"""DIV-03 / RN-023: UPDATE y DELETE deben fallar (BV016) en las 13 tablas de hechos con trigger hecho_inmutable.

No muta datos: cada intento corre en BEGIN … ROLLBACK sobre una fila existente de pg-a local.
Se ejecuta como superusuario para que sólo el trigger (no los GRANT) pueda impedir el cambio.
Uso: python3 db/tests/immutability.py --out <archivo.json>
"""
import argparse
import json
import subprocess
from pathlib import Path

TABLES = ['liquidacion', 'concepto_liquidacion', 'ajuste_liquidacion', 'asignacion_costo', 'asiento_valoracion',
          'aplicacion_pago', 'cierre_periodo_version', 'movimiento_inventario', 'documento', 'auditoria_evento',
          'evento_outbox', 'revision_administrativa', 'revision_documento']
CONTAINER = 'bovicierre-academic-pg-a-1'


def psql(sql):
    r = subprocess.run(['docker', 'exec', '-i', CONTAINER, 'psql', '-U', 'postgres', '-d', 'bovicierre', '-At', '-v', 'ON_ERROR_STOP=0'],
                       input=sql, capture_output=True, text=True)
    return r.stdout.strip(), r.stderr.strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    out = Path(p.parse_args().out)
    declared, _ = psql("select string_agg(event_object_table, ',' order by event_object_table) from (select distinct event_object_table from information_schema.triggers where trigger_schema='bovi' and trigger_name='hecho_inmutable') t;")
    results, failures = {}, 0
    for t in TABLES:
        rows, _ = psql(f'select count(*) from bovi.{t};')
        col, _ = psql(f"select column_name from information_schema.columns where table_schema='bovi' and table_name='{t}' order by ordinal_position limit 1;")
        if rows == '0':
            results[t] = {'filas': 0, 'update': 'SIN_FIXTURE', 'delete': 'SIN_FIXTURE'}
            continue
        entry = {'filas': int(rows)}
        for op, stmt in [('update', f'UPDATE bovi.{t} SET {col}={col} WHERE ctid=(SELECT ctid FROM bovi.{t} LIMIT 1);'),
                         ('delete', f'DELETE FROM bovi.{t} WHERE ctid=(SELECT ctid FROM bovi.{t} LIMIT 1);')]:
            stdout, stderr = psql(f'BEGIN;\n{stmt}\nROLLBACK;\n')
            blocked = 'ERROR' in stderr and ('BV016' in stderr or 'inmutable' in stderr.lower())
            entry[op] = 'BLOQUEADO_BV016' if blocked else ('ERROR_OTRO: ' + stderr[:160] if 'ERROR' in stderr else 'PERMITIDO')
            failures += not blocked
        results[t] = entry
    after = {t: psql(f'select count(*) from bovi.{t};')[0] for t in TABLES}
    unchanged = all(str(results[t]['filas']) == after[t] for t in TABLES)
    summary = {'regla': 'RN-023', 'divergencia': 'DIV-03', 'tablas_con_trigger_en_catalogo': declared.split(','),
               'ejecutados': sum(1 for r in results.values() for op in ('update', 'delete') if r[op] != 'SIN_FIXTURE'),
               'resultados': results, 'filas_sin_cambio_tras_rollback': unchanged, 'fallos': failures,
               'sin_fixture': [t for t, r in results.items() if r['filas'] == 0]}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    for t, r in results.items():
        print(f"{t:26} filas={r['filas']:<6} update={r['update']:<18} delete={r['delete']}")
    print(f"fallos={failures} sin_fixture={summary['sin_fixture']} filas_intactas={unchanged}")
    return 1 if failures or not unchanged else 0


if __name__ == '__main__':
    raise SystemExit(main())
