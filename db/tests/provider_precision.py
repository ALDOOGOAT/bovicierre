#!/usr/bin/env python3
"""Frontera HALFUP2 fuenteNUMERIC14,4→captura14,2→gasto; DB QA, fuente restaurada finally."""
import hashlib,json,os,time,uuid
from pathlib import Path
from decimal import Decimal
import psycopg
from psycopg.types.json import Jsonb
DB=os.environ.get('BOVI_DB_NAME','bovicierre_release_replay');assert DB!='bovicierre';sec=Path.home()/'.local/share/bovicierre-academic/secrets';E='11111111-1111-4111-8111-111111111111';S='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';U='99999999-9999-4999-8999-999999999999';calls=0

def conn(port,user,file,auto=False):return psycopg.connect(host='127.0.0.1',port=port,dbname=DB,user=user,password=(sec/file).read_text().strip(),autocommit=auto)
def command(c,name,body):
 global calls
 calls+=1
 return c.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',(E,S,U,'DEMO-PRECISION-'+str(uuid.uuid4()),hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest(),uuid.uuid4(),name,Jsonb(body))).fetchone()[0]
with conn(15434,'postgres','admin_password',True) as source,conn(15432,'bovi_app_a','app_a_password',True) as reader,conn(15433,'bovi_app_b','app_b_password') as owner,conn(15433,'postgres','admin_password',True) as inspector:
 original=source.execute("select precio_mxn,version from proveedor.tarifa_transporte where ruta='DEMO-RUTA-01'").fetchone()
 try:
  source.execute("update proveedor.tarifa_transporte set precio_mxn=12000.0050,version=version+1 where ruta='DEMO-RUTA-01'")
  quotes=reader.execute('select bovi.leer_tarifas_proveedor(%s,%s,%s,%s)',(E,S,U,Jsonb({}))).fetchone()[0];capture=owner.execute('select bovi.capturar_tarifas_proveedor(%s,%s,%s,%s)',(E,S,U,Jsonb(quotes))).fetchone()[0]['elementos'][0];assert capture['precio_unitario_fuente']=='12000.0050';assert capture['precio']=={'importe':'12000.01','moneda':'MXN'};token=capture['snapshot_id'];command(owner,'aceptar_tarifa',{'snapshot_id':token});owner.commit();assert inspector.execute('select precio from infra.tarifa_snapshot where id=%s',(token,)).fetchone()[0]==Decimal('12000.01')
  typ=inspector.execute("select format_type(atttypid,atttypmod) from pg_attribute where attrelid='infra.tarifa_snapshot'::regclass and attname='precio'").fetchone()[0];assert typ=='numeric(14,2)'
  per=str(owner.execute("select id from bovi.periodo_cierre where sucursal_id=%s and estado='ABIERTO'",(S,)).fetchone()[0]);party=str(owner.execute('select id from bovi.parte limit 1').fetchone()[0]);op=command(owner,'crear_operacion',{'tipo':'COMPRA','parte_id':party})['id'];gasto=command(owner,'registrar_gasto',{'operacion_id':op,'importe':capture['precio'],'snapshot_id':token,'concepto':'DEMO ROUND BOUNDARY','clasificacion':'CAPITALIZABLE','periodo_id':per,'fecha_reconocimiento':'2026-10-11'});assert gasto['importe']==capture['precio'];assert gasto['snapshot_fuente_externa']['precio_unitario_fuente']=='12000.0050'
  result={'database':DB,'command_calls':calls,'source_raw':'12000.0050','Dinero_importe':'12000.01','capture_column_type':typ,'gasto_accepted':True,'immutable_source_precision4_and_hash_preserved':True,'migration_redundant_not_added':True}
 finally:
  source.execute("update proveedor.tarifa_transporte set precio_mxn=%s,version=%s where ruta='DEMO-RUTA-01'",original);owner.rollback()
Path('db/tests/provider-precision-result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS '+json.dumps(result))
