"""Genera DDL desde el catálogo lógico; la migración resultante es la autoridad de ejecución."""
from pathlib import Path
import runpy
root = Path(__file__).resolve().parents[2]
tables = runpy.run_path(str(root / 'tools/esquema/esquema.py'))['TABLAS']
for _, name, cols, fks, uks in tables:
    if name=='infra.entrega_outbox':
        for field in [('lease_token','uuid',set()),('lease_vence_en','timestamptz',set())]:
            if not any(c[0]==field[0] for c in cols): cols.append(field)
    if name == 'pago' and not any(c[0]=='naturaleza' for c in cols): cols.append(('naturaleza','varchar(10)',{'NN'}))
    if name in ('pago','aplicacion_pago','gasto_operacion','ajuste_liquidacion'):
        if not any(c[0]=='periodo_id' for c in cols):
            cols.append(('periodo_id','uuid',{'NN'}))
            fks.append((['empresa_id','sucursal_id','periodo_id'],'periodo_cierre',['empresa_id','sucursal_id','id']))
        if not any(c[0]=='fecha_reconocimiento' for c in cols): cols.append(('fecha_reconocimiento','date',{'NN'}))
        if name=='pago':
            for c in cols:
                if c[0] in ('periodo_id','fecha_reconocimiento'): c[2].discard('NN')

def q(t): return t if '.' in t else 'bovi.'+t
out=['-- 42 tablas / 83 FK; PostgreSQL 18. Los defaults no sustituyen validaciones de comandos.','CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA public;','CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;','CREATE SCHEMA IF NOT EXISTS bovi AUTHORIZATION bovi_owner;','CREATE SCHEMA IF NOT EXISTS infra AUTHORIZATION bovi_owner;','ALTER SCHEMA infra OWNER TO bovi_owner;', 'GRANT USAGE ON SCHEMA public TO bovi_owner;', 'SET search_path = bovi, infra, public;', 'SET ROLE bovi_owner;']
checks={
'empresa':["estado IN ('ACTIVA','SUSPENDIDA')"],
'sucursal':["nodo_dueno IN ('A','B')", "codigo ~ '^[A-Z0-9-]+$'"],
'rol_aplicacion':["codigo IN ('ADMIN','OPERADOR','CAJA','AUDITOR')"],
'usuario':["estado IN ('ACTIVO','BLOQUEADO')",'login_normalizado = lower(btrim(login_normalizado))'],
'parte':["tipo_persona IN ('FISICA','MORAL')"],
'animal':["sexo IN ('M','H')", "situacion IN ('VIGENTE','IDENTIDAD_EN_REVISION','MUERTO')"],
'animal_identificacion':["sistema IN ('SINIIGA','SINIDA','INTERNO','OTRO')","estado IN ('VIGENTE','INACTIVA','EN_REVISION')",'vigente_hasta IS NULL OR vigente_hasta >= vigente_desde','(evidencia_sucursal_id IS NULL) = (evidencia_documento_id IS NULL)'],
'operacion':["tipo IN ('COMPRA','VENTA')", "moneda = 'MXN'", "estado IN ('BORRADOR','ACORDADA','CONFIRMADA','CANCELADA','ANULADA')", "estado_entrega IN ('PENDIENTE','PARCIAL','COMPLETA')", "estado NOT IN ('CONFIRMADA','ANULADA') OR numero_version_aceptada IS NOT NULL",'version_lock >= 0'],
'folio_contador':["tipo IN ('COMPRA','VENTA')",'ultimo > 0'],
'contrato_version':["estado IN ('PROPUESTA','ACEPTADA','SUPERADA')", "politica_redondeo = 'HALF_UP_2'",'numero_version > 0'],
'lote_operacion':['numero_lote > 0'],
'condicion_lote':["unidad_precio IN ('KG','CABEZA')",'precio_unitario > 0','deduccion_pct >= 0 AND deduccion_pct < 100','cargos_pactados >= 0 AND bonificaciones_pactadas >= 0',"(unidad_precio = 'KG' AND base_pesaje = 'PESAJE' AND pesaje_base_id IS NOT NULL) OR (unidad_precio = 'CABEZA' AND base_pesaje = 'NINGUNA' AND pesaje_base_id IS NULL)"],
'pesaje':["modo IN ('BRUTO_TARA','NETO_REPORTADO')",'neto_kg > 0',"(modo = 'BRUTO_TARA' AND bruto_kg IS NOT NULL AND tara_kg IS NOT NULL AND tara_kg >= 0 AND tara_kg <= bruto_kg AND neto_kg = bruto_kg - tara_kg) OR (modo = 'NETO_REPORTADO' AND bruto_kg IS NULL AND tara_kg IS NULL)","estado IN ('PROPUESTA','APROBADO','CORREGIDO')","fuente IN ('MANUAL','CSV','OCR','FDW')"],
'pesaje_animal':['peso_individual_kg IS NULL OR peso_individual_kg > 0'],
'seleccion_compra':["tipo_operacion = 'COMPRA'"], 'seleccion_venta':["tipo_operacion = 'VENTA'"],
'posicion_inventario':["estado IN ('PENDIENTE_RECEPCION','DISPONIBLE','VENDIDA_PENDIENTE_ENTREGA','CERRADA_VENTA','BAJA')",'numero_ciclo > 0',"(estado = 'BAJA') = (motivo_baja IS NOT NULL)","motivo_baja IS NULL OR motivo_baja IN ('PERDIDA','MUERTE')","(estado IN ('BAJA','CERRADA_VENTA')) = (cerrada_en IS NOT NULL)"],
'reserva_venta':["estado IN ('ACTIVA','CONSUMIDA','LIBERADA','EXPIRADA')",'vence_en > creada_en'],
'movimiento_inventario':["tipo IN ('RECEPCION','ENTREGA','BAJA','REVERSO')"],
'periodo_cierre':["estado IN ('ABIERTO','CERRADO')", "desde = date_trunc('month',desde)::date AND hasta = (desde + interval '1 month' - interval '1 day')::date"],
'cierre_periodo_version':["tipo IN ('CIERRE','REAPERTURA')",'numero_version > 0',"length(btrim(motivo)) > 0"],
'liquidacion':["direccion IN ('POR_PAGAR','POR_COBRAR')",'total >= 0'],
'concepto_liquidacion':["tipo IN ('BASE','CARGO','BONIFICACION','DEDUCCION')","unidad IN ('KG','CABEZA','MXN')", "(tipo IN ('BASE','CARGO') AND importe >= 0) OR (tipo IN ('BONIFICACION','DEDUCCION') AND importe <= 0)"],
'ajuste_liquidacion':["naturaleza IN ('CARGO','ABONO')",'monto > 0',"length(btrim(motivo)) > 0", "fuente IN ('PRECIO_GANADO','BONIFICACION_COMERCIAL','ANULACION','OTRO')"],
'gasto_operacion':["naturaleza IN ('COSTO','BONIFICACION')", "clasificacion IN ('CAPITALIZABLE','DIRECTO_VENTA','OTRO')", 'importe > 0',"estado IN ('BORRADOR','APROBADO')","(naturaleza = 'BONIFICACION') = (bonifica_gasto_id IS NOT NULL)"],
'asignacion_costo':['num_nonnulls(fuente_liquidacion_id,fuente_gasto_id,fuente_ajuste_id) = 1','(fuente_liquidacion_id IS NULL) = (fuente_numero_concepto IS NULL)',"metodo IN ('IMPORTE_INDIVIDUAL','POR_CABEZA','POR_PESO_MEDIDO')",'base_valor > 0','importe <> 0'],
'asiento_valoracion':["clase IN ('ADQUISICION','VENTA','COSTO_TARDIO_INVENTARIO','COSTO_TARDIO_VENTA','COSTO_TARDIO_PERDIDA','BAJA','ANULACION_VENTA')","sentido IN ('AUMENTO','DISMINUCION')","sentido = 'AUMENTO' OR clase LIKE 'COSTO_TARDIO_%'",'importe > 0'],
'pago':["tipo IN ('COBRO','PAGO')", "naturaleza IN ('NORMAL','REEMBOLSO')", "moneda = 'MXN'",'importe > 0',"metodo IN ('TRANSFERENCIA','EFECTIVO','CHEQUE','OTRO')","estado IN ('REGISTRADO','VALIDADO','REVERTIDO')","estado = 'REGISTRADO' OR (periodo_id IS NOT NULL AND fecha_reconocimiento IS NOT NULL)","(naturaleza = 'REEMBOLSO') = (pago_origen_id IS NOT NULL)"],
'aplicacion_pago':['importe > 0',"naturaleza IN ('APLICACION','REVERSO')","(naturaleza = 'REVERSO') = (reverso_de_id IS NOT NULL)"],
'documento':["sha256 ~ '^[0-9a-f]{64}$'",'tamano_bytes BETWEEN 1 AND 20971520',"mime IN ('application/pdf','image/jpeg','image/png')",'version > 0'],
'revision_administrativa':['num_nonnulls(operacion_id,identificacion_id) = 1',"resultado IN ('SIN_OBSERVACIONES','CON_OBSERVACIONES','RECHAZADA')"],
'clave_idempotencia':["estado IN ('EN_CURSO','COMPLETADA')","hash_peticion ~ '^[0-9a-f]{64}$'", "expira_en >= creada_en + interval '30 days'"],
'infra.nodo_config':["nodo IN ('A','B')"],
'infra.entrega_outbox':['intentos >= 0'],
'infra.importacion_fuente':['filas_leidas >= 0 AND filas_error >= 0',"fuente IN ('CSV','OCR','FDW')"]}
gen={
'delta_inventario':"CASE clase WHEN 'ADQUISICION' THEN importe WHEN 'VENTA' THEN -importe WHEN 'BAJA' THEN -importe WHEN 'ANULACION_VENTA' THEN importe WHEN 'COSTO_TARDIO_INVENTARIO' THEN CASE sentido WHEN 'AUMENTO' THEN importe ELSE -importe END ELSE 0 END",
'delta_costo_venta':"CASE clase WHEN 'VENTA' THEN importe WHEN 'ANULACION_VENTA' THEN -importe WHEN 'COSTO_TARDIO_VENTA' THEN CASE sentido WHEN 'AUMENTO' THEN importe ELSE -importe END ELSE 0 END",
'delta_perdida':"CASE clase WHEN 'BAJA' THEN importe WHEN 'COSTO_TARDIO_PERDIDA' THEN CASE sentido WHEN 'AUMENTO' THEN importe ELSE -importe END ELSE 0 END"}
for _,t,cols,fks,uks in tables:
    items=[]
    for n,typ,marks in cols:
        s=n+' '+typ.replace(' GEN','')
        if 'GEN' in typ: s += ' GENERATED ALWAYS AS ('+gen[n]+') STORED'
        else:
            if n == 'id' and typ == 'uuid': s+=' DEFAULT uuidv7()'
            if n in ('creado_en','registrado_en','subido_en','abierta_en','ocurrido_en','recibido_en','creada_en','aplicada_en','pesado_en'): s+=' DEFAULT now()'
            if n in ('version_lock','deduccion_pct','cargos_pactados','bonificaciones_pactadas','intentos'): s+=' DEFAULT 0'
            if n == 'es_sintetico': s+=' DEFAULT true'
            if n == 'vigente': s+=' DEFAULT true'
            if n == 'moneda': s+=" DEFAULT 'MXN'"
        if 'NN' in marks: s+=' NOT NULL'
        if typ.startswith('numeric'): s+=f" CHECK ({n} NOT IN ('NaN','Infinity','-Infinity'))"
        if n == 'nodo_origen': s+=" CHECK (nodo_origen IN ('A','B'))"
        items.append(s)
    items.append('PRIMARY KEY ('+', '.join(n for n,_,m in cols if 'PK' in m)+')')
    for uk in uks: items.append('UNIQUE ('+', '.join(uk)+')')
    for check in checks.get(t,[]): items.append('CHECK ('+check+')')
    out.append('CREATE TABLE '+q(t)+' (\n    '+',\n    '.join(items)+'\n);')
for _,t,cols,fks,uks in tables:
    for i,(loc,ref,rc) in enumerate(fks,1):
        out.append(f"ALTER TABLE {q(t)} ADD CONSTRAINT fk_{t.replace('.','_')}_{i} FOREIGN KEY ({', '.join(loc)}) REFERENCES {q(ref)} ({', '.join(rc)}) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;")
for t,cols in [('parte','empresa_id,rfc'),('gasto_operacion','empresa_id,sucursal_id,proveedor_parte_id,referencia_origen'),('documento','clave_almacenamiento'),('documento','empresa_id,sucursal_id,documento_previo_id'),('pesaje','empresa_id,sucursal_id,corrige_a_id'),('aplicacion_pago','empresa_id,sucursal_id,reverso_de_id'),('ajuste_liquidacion','empresa_id,sucursal_id,revierte_ajuste_id'),('movimiento_inventario','empresa_id,sucursal_id,reverso_de_id')]:
    out.append(f'CREATE UNIQUE INDEX uk_{t}_{cols.split(",")[-1]} ON bovi.{t} ({cols});')
for t,cols,where in [('posicion_inventario','empresa_id,animal_id',"estado IN ('PENDIENTE_RECEPCION','DISPONIBLE','VENDIDA_PENDIENTE_ENTREGA')"),('reserva_venta','empresa_id,sucursal_id,posicion_id',"estado = 'ACTIVA'"),('animal_identificacion','empresa_id,animal_id,sistema',"estado = 'VIGENTE'")]: out.append(f'CREATE UNIQUE INDEX uk_{t}_activo ON bovi.{t} ({cols}) WHERE {where};')
out += ["CREATE UNIQUE INDEX uk_nodo_unico ON infra.nodo_config ((true));","ALTER TABLE bovi.periodo_cierre ADD CONSTRAINT periodo_no_solapado EXCLUDE USING gist (empresa_id WITH =, sucursal_id WITH =, daterange(desde,hasta,'[]') WITH &&);",'RESET ROLE;']
(root/'db/migrations/V1__esquema.sql').write_text('\n\n'.join(out)+'\n')
assert len(tables)==42 and sum(len(t[3]) for t in tables)==83
print('V1 generado: 42 tablas, 83 FK')
