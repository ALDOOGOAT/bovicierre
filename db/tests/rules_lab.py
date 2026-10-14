#!/usr/bin/env python3
"""TEST-41 laboratorio del sistema de reglas de PostgreSQL (CREATE RULE), tema “reglas” del pizarrón.

Decisión del producto: las reglas de negocio de BoviCierre viven en CHECK, triggers y funciones porque fallan con un
error explícito (BVxxx). Este laboratorio demuestra el sistema de reescritura en un esquema temporal y se revierte:
- DO INSTEAD sobre una vista: insertar en la vista escribe en la tabla base;
- DO ALSO sobre la tabla: cada cambio de precio deja bitácora en la misma sentencia;
- las restricciones siguen aplicando a la consulta reescrita (CHECK → 23514).
"""
import os
from decimal import Decimal as D
from pathlib import Path
import psycopg

SECRET = Path(os.environ.get('BOVI_SECRET_DIR', Path.home() / '.local/share/bovicierre-academic/secrets'))
conn = psycopg.connect(host='127.0.0.1', port=15432, dbname=os.environ.get('BOVI_DB_NAME', 'bovicierre_gold_final'), user='postgres',
                       password=(SECRET / 'admin_password').read_text().strip())
c = conn.cursor()
try:
    c.execute("""CREATE SCHEMA lab_reglas;
    CREATE TABLE lab_reglas.tarifa(ruta text PRIMARY KEY, precio numeric(14,2) NOT NULL CHECK (precio > 0));
    CREATE TABLE lab_reglas.bitacora(ruta text, anterior numeric(14,2), nuevo numeric(14,2), en timestamptz DEFAULT now());
    CREATE VIEW lab_reglas.tarifa_publica AS SELECT ruta, precio FROM lab_reglas.tarifa;
    CREATE RULE alta_por_vista AS ON INSERT TO lab_reglas.tarifa_publica DO INSTEAD INSERT INTO lab_reglas.tarifa VALUES (NEW.ruta, NEW.precio);
    CREATE RULE bitacora_precio AS ON UPDATE TO lab_reglas.tarifa WHERE OLD.precio IS DISTINCT FROM NEW.precio
      DO ALSO INSERT INTO lab_reglas.bitacora(ruta, anterior, nuevo) VALUES (OLD.ruta, OLD.precio, NEW.precio);""")
    c.execute("INSERT INTO lab_reglas.tarifa_publica VALUES ('DEMO-RUTA-LAB', 12000)")
    assert c.execute("SELECT precio FROM lab_reglas.tarifa WHERE ruta='DEMO-RUTA-LAB'").fetchone()[0] == D('12000.00')
    print('PASS TEST-41 DO INSTEAD: INSERT en la vista reescrito a la tabla base')
    c.execute("UPDATE lab_reglas.tarifa SET precio = 12500 WHERE ruta='DEMO-RUTA-LAB'")
    assert c.execute('SELECT anterior, nuevo FROM lab_reglas.bitacora').fetchall() == [(D('12000.00'), D('12500.00'))]
    print('PASS TEST-41 DO ALSO: el cambio de precio quedó en bitácora en la misma sentencia')
    c.execute('SAVEPOINT s')
    try:
        c.execute("INSERT INTO lab_reglas.tarifa_publica VALUES ('DEMO-RUTA-MALA', -1)"); raise AssertionError('CHECK no aplicó')
    except psycopg.Error as ex:
        assert ex.sqlstate == '23514', ex.sqlstate
        c.execute('ROLLBACK TO s')
    print('PASS TEST-41 la consulta reescrita respeta el CHECK (23514)')
    rules = c.execute("SELECT rulename FROM pg_rules WHERE schemaname='lab_reglas' ORDER BY 1").fetchall()
    assert [r[0] for r in rules] == ['alta_por_vista', 'bitacora_precio'], rules
finally:
    conn.rollback(); conn.close()
print('PASS TEST-41 laboratorio revertido (sin reglas en el esquema bovi)')
