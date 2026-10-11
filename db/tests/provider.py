#!/usr/bin/env python3
"""Captura FDW aceptada, precio posterior y scopes; DB aislada, sin modificar fuente main."""
import hashlib,json,os,uuid
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb
secret=Path(os.environ.get('BOVI_SECRET_DIR',Path.home()/'.local/share/bovicierre-academic/secrets'));db=os.environ.get('BOVI_DB_NAME','bovicierre_release_replay');assert db!='bovicierre'
e='11111111-1111-4111-8111-111111111111';s='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';a='99999999-9999-4999-8999-999999999999'
def connect(port,user,file):return psycopg.connect(host='127.0.0.1',port=port,dbname=db,user=user,password=(secret/file).read_text().strip())
with connect(15432,'bovi_app_a','app_a_password') as connection,connect(15434,'postgres','admin_password') as source:
 c=connection.cursor()
 def command(name,body,actor=a,key=None):
  c.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',(e,s,actor,key or 'DEMO-PROVIDER-'+str(uuid.uuid4()),hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest(),uuid.uuid4(),name,Jsonb(body)));return c.fetchone()[0]
 c.execute('select bovi.consultar_tarifas_proveedor(%s,%s,%s,%s)',(e,s,a,Jsonb({'ruta':'DEMO-RUTA-01'})));capture=c.fetchone()[0]['elementos'][0];token=capture['snapshot_id'];assert capture['fuente']=='DEMO_PROVEEDOR_SIMULADO'
 accepted=command('aceptar_tarifa',{'snapshot_id':token});assert accepted['snapshot_id']==token
 source.execute("update proveedor.tarifa_transporte set precio_mxn=99999,version=version+1 where ruta='DEMO-RUTA-01'");source.commit()
 try:
  c.execute("select id::text from bovi.periodo_cierre where empresa_id=%s and sucursal_id=%s and estado='ABIERTO'",(e,s));r=c.fetchone();per=r[0] if r else command('crear_periodo',{'desde':'2026-10-01','hasta':'2026-10-31'})['id']
  party=command('crear_contraparte',{'nombre':'DEMO fuente temporal'})['id'];op=command('crear_operacion',{'tipo':'COMPRA','parte_id':party})['id']
  body={'operacion_id':op,'snapshot_id':token,'importe':capture['precio'],'clasificacion':'DIRECTO_VENTA','concepto':'DEMO tarifa aceptada','periodo_id':per,'fecha_reconocimiento':'2026-10-11','fecha_economica':'2027-02-01'}
  # Capitalizable/directo classifications validated at reparto, registration retains documentary date.
  body['clasificacion']='CAPITALIZABLE';key='DEMO-PROVIDER-IDEM-'+str(uuid.uuid4());g=command('registrar_gasto',body,key=key);repeat=command('registrar_gasto',body,key=key);assert g==repeat and g['gasto_id']==g['id'];assert g['snapshot_fuente_externa']['precio']==capture['precio'];assert g['importe']['importe']=='12000.00'
  c.execute('savepoint bad')
  try:command('aceptar_tarifa',{'snapshot_id':token},actor='89999999-9999-4999-8999-999999999999')
  except psycopg.Error as ex:assert ex.sqlstate=='P0001' and json.loads(ex.diag.message_detail)['codigo']=='BV404';c.execute('rollback to bad')
  else:raise AssertionError('Cross-principal token accepted')
  c.execute('savepoint badamount')
  try:command('registrar_gasto',{**body,'importe':{'importe':'99999.00','moneda':'MXN'}})
  except psycopg.Error as ex:assert ex.sqlstate=='P0001';c.execute('rollback to badamount')
  else:raise AssertionError('Changed tariff overwrote frozen capture')
  print('PASS V4 FDW capture12000 retained after provider99999; exact replay fullgasto; tokenprincipal/price denial')
 finally:
  source.execute("update proveedor.tarifa_transporte set precio_mxn=12000,version=version-1 where ruta='DEMO-RUTA-01'");source.commit();connection.rollback()
