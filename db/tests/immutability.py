#!/usr/bin/env python3
"""DIV-03 / RN-023: UPDATE y DELETE deben fallar (BV016) en las 13 tablas de hechos con trigger hecho_inmutable.
DIV-04 (V14): estados terminales de operacion, gasto_operacion, pago y posicion_inventario también fallan, y las
transiciones legítimas de cmd_ejecutar (anular, estado_entrega, aprobar, validar, liberar) siguen permitidas.

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
TOGGLE_ENTREGA = "estado_entrega=CASE WHEN estado_entrega='COMPLETA' THEN 'PENDIENTE' ELSE 'COMPLETA' END"
# (id, tabla, filtro de la fila, preparación legítima opcional, sentencia, esperado)
TERMINAL = [
    ('OP-CONF-UPD', 'operacion', "estado='CONFIRMADA'", None, "SET fecha_operacion=fecha_operacion+1", 'BLOQUEADO'),
    ('OP-CONF-REABRIR', 'operacion', "estado='CONFIRMADA'", None, "SET estado='BORRADOR'", 'BLOQUEADO'),
    ('OP-CONF-DEL', 'operacion', "estado='CONFIRMADA'", None, 'DELETE', 'BLOQUEADO'),
    ('OP-CANC-UPD', 'operacion', "estado='CANCELADA'", None, 'SET ' + TOGGLE_ENTREGA, 'BLOQUEADO'),
    ('OP-CANC-DEL', 'operacion', "estado='CANCELADA'", None, 'DELETE', 'BLOQUEADO'),
    ('OP-ANUL-REVIVIR', 'operacion', "estado='CONFIRMADA'", "SET estado='ANULADA'", "SET estado='CONFIRMADA'", 'BLOQUEADO'),
    ('GASTO-APR-UPD', 'gasto_operacion', "estado='APROBADO'", None, 'SET importe=importe', 'BLOQUEADO'),
    ('GASTO-APR-DEL', 'gasto_operacion', "estado='APROBADO'", None, 'DELETE', 'BLOQUEADO'),
    ('PAGO-VAL-UPD', 'pago', "estado='VALIDADO'", None, 'SET importe=importe', 'BLOQUEADO'),
    ('PAGO-VAL-DEL', 'pago', "estado='VALIDADO'", None, 'DELETE', 'BLOQUEADO'),
    ('POS-CERR-REABRIR', 'posicion_inventario', "estado='CERRADA_VENTA'", None, "SET estado='DISPONIBLE',cerrada_en=NULL", 'BLOQUEADO'),
    ('POS-CERR-DEL', 'posicion_inventario', "estado='CERRADA_VENTA'", None, 'DELETE', 'BLOQUEADO'),
    ('POS-BAJA-UPD', 'posicion_inventario', "estado='DISPONIBLE'", "SET estado='BAJA',motivo_baja='PERDIDA',cerrada_en=now()", "SET motivo_baja='MUERTE'", 'BLOQUEADO'),
    ('OP-CONF-ENTREGA', 'operacion', "estado='CONFIRMADA'", None, 'SET ' + TOGGLE_ENTREGA + ',version_lock=version_lock+1', 'PERMITIDO'),
    ('OP-CONF-ANULAR', 'operacion', "estado='CONFIRMADA'", None, "SET estado='ANULADA',version_lock=version_lock+1", 'PERMITIDO'),
    ('GASTO-BORR-UPD', 'gasto_operacion', "estado='BORRADOR'", None, 'SET concepto=concepto', 'PERMITIDO'),
    ('PAGO-REG-UPD', 'pago', "estado='REGISTRADO'", None, 'SET referencia=referencia', 'PERMITIDO'),
    ('POS-VEND-LIBERAR', 'posicion_inventario', "estado='VENDIDA_PENDIENTE_ENTREGA'", None, "SET estado='DISPONIBLE'", 'PERMITIDO'),
]


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
    terminal, counts_before = {}, {t: psql(f'select count(*) from bovi.{t};')[0] for t in {c[1] for c in TERMINAL}}
    for cid, t, where, setup, stmt, expected in TERMINAL:
        row = f'ctid=(SELECT ctid FROM bovi.{t} WHERE {where} ORDER BY ctid LIMIT 1)'
        if psql(f'select count(*) from bovi.{t} where {where};')[0] == '0':
            terminal[cid] = {'tabla': t, 'esperado': expected, 'obtenido': 'SIN_FIXTURE'}
            continue
        prep = f'UPDATE bovi.{t} {setup} WHERE {row} RETURNING ctid AS fila \\gset\n' if setup else ''
        target = "ctid=:'fila'::tid" if setup else row
        sql = f'DELETE FROM bovi.{t} WHERE {target};' if stmt == 'DELETE' else f'UPDATE bovi.{t} {stmt} WHERE {target};'
        _, stderr = psql(f'BEGIN;\n{prep}{sql}\nROLLBACK;\n')
        errors = [l for l in stderr.splitlines() if 'ERROR' in l]
        if setup and errors and 'BV016' not in stderr and 'inmutable' not in stderr.lower():
            got = 'ERROR_PREPARACION: ' + errors[0][:160]
        elif errors:
            got = 'BLOQUEADO' if ('BV016' in stderr or 'inmutable' in stderr.lower()) and len(errors) == 1 else 'ERROR_OTRO: ' + ' | '.join(errors)[:200]
        else:
            got = 'PERMITIDO'
        terminal[cid] = {'tabla': t, 'esperado': expected, 'obtenido': got}
        failures += got != expected
    counts_after = {t: psql(f'select count(*) from bovi.{t};')[0] for t in counts_before}
    after = {t: psql(f'select count(*) from bovi.{t};')[0] for t in TABLES}
    unchanged = all(str(results[t]['filas']) == after[t] for t in TABLES) and counts_before == counts_after
    summary = {'regla': 'RN-023', 'divergencia': 'DIV-03', 'tablas_con_trigger_en_catalogo': declared.split(','),
               'ejecutados': sum(1 for r in results.values() for op in ('update', 'delete') if r[op] != 'SIN_FIXTURE')
               + sum(1 for r in terminal.values() if r['obtenido'] != 'SIN_FIXTURE'),
               'resultados': results, 'estados_terminales_div04': terminal, 'filas_sin_cambio_tras_rollback': unchanged, 'fallos': failures,
               'sin_fixture': [t for t, r in results.items() if r['filas'] == 0] + [c for c, r in terminal.items() if r['obtenido'] == 'SIN_FIXTURE']}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    for t, r in results.items():
        print(f"{t:26} filas={r['filas']:<6} update={r['update']:<18} delete={r['delete']}")
    for cid, r in terminal.items():
        print(f"{cid:26} {r['tabla']:20} esperado={r['esperado']:<10} obtenido={r['obtenido']}")
    print(f"fallos={failures} sin_fixture={summary['sin_fixture']} filas_intactas={unchanged}")
    return 1 if failures or not unchanged else 0


if __name__ == '__main__':
    raise SystemExit(main())
