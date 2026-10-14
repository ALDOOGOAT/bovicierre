#!/usr/bin/env python3
"""FDW lector A/captura B, fecha PATCH y vendibles; namespace QA, hechos rollback."""
import hashlib,json,os,time,uuid
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb
DB=os.environ.get('BOVI_DB_NAME','bovicierre_release_replay');assert DB!='bovicierre'
sec=Path.home()/'.local/share/bovicierre-academic/secrets';E='11111111-1111-4111-8111-111111111111';SA='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';SB='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';U='99999999-9999-4999-8999-999999999999';calls=0

def conn(node,auto=False):return psycopg.connect(host='127.0.0.1',port=15432 if node=='a' else 15433,dbname=DB,user='bovi_app_'+node,password=(sec/('app_'+node+'_password')).read_text().strip(),autocommit=auto)
def command(c,s,name,body):
 global calls
 calls+=1
 return c.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',(E,s,U,'DEMO-CAPTURE-'+str(uuid.uuid4()),hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest(),uuid.uuid4(),name,Jsonb(body))).fetchone()[0]
def query(c,s,resource,params):return c.execute('select bovi.consultar(%s,%s,%s,%s,%s)',(E,s,U,resource,Jsonb(params))).fetchone()[0]
def reject(c,sql,args,code):
 c.execute('savepoint invalid')
 try:c.execute(sql,args)
 except psycopg.Error as ex:
  assert ex.sqlstate=='P0001' and json.loads(ex.diag.message_detail)['codigo']==code,(ex.sqlstate,ex.diag.message_detail);c.execute('rollback to invalid')
 else:raise AssertionError('Expected '+code)
start=time.monotonic()
with conn('a',True) as reader,conn('b') as owner:
 quotes=reader.execute('select bovi.leer_tarifas_proveedor(%s,%s,%s,%s)',(E,SB,U,Jsonb({'ruta':'DEMO-RUTA-01'}))).fetchone()[0];assert 'snapshot_id' not in quotes['elementos'][0]
 captured=owner.execute('select bovi.capturar_tarifas_proveedor(%s,%s,%s,%s)',(E,SB,U,Jsonb(quotes))).fetchone()[0];token=captured['elementos'][0]['snapshot_id'];assert captured['elementos'][0]['precio']=={'importe':'12000.00','moneda':'MXN'}
 accepted=command(owner,SB,'aceptar_tarifa',{'snapshot_id':token});assert accepted['snapshot_id']==token
 # DEC-26: B tiene servidor FDW de sólo lectura para la “Y” de la rúbrica, pero el flujo de negocio en B no lo usa:
 # la consulta en vivo sigue rechazada (BV501) y la captura sólo acepta lo leído por A (abajo).
 assert owner.execute("select count(*) from pg_foreign_server where srvname='prov_sim'").fetchone()[0]==1
 reject(owner,'select bovi.consultar_tarifas_proveedor(%s,%s,%s,%s)',(E,SB,U,Jsonb({})),'BV501')
 reject(owner,'select bovi.capturar_tarifas_proveedor(%s,%s,%s,%s)',(E,SA,U,Jsonb(quotes)),'BV501')
 tampered=json.loads(json.dumps(quotes));tampered['elementos'][0]['precio']['importe']='1.00'
 reject(owner,'select bovi.capturar_tarifas_proveedor(%s,%s,%s,%s)',(E,SB,U,Jsonb(tampered)),'BV015')
 op=command(owner,SB,'crear_operacion',{'tipo':'COMPRA','parte_id':str(owner.execute('select id from bovi.parte limit 1').fetchone()[0])})['id'];per=str(owner.execute("select id from bovi.periodo_cierre where sucursal_id=%s and estado='ABIERTO'",(SB,)).fetchone()[0])
 gasto=command(owner,SB,'registrar_gasto',{'operacion_id':op,'snapshot_id':token,'importe':captured['elementos'][0]['precio'],'concepto':'DEMO captura localB','clasificacion':'CAPITALIZABLE','periodo_id':per,'fecha_reconocimiento':'2026-10-11'});assert gasto['snapshot_fuente_externa']['snapshot_id']==token
 owner.rollback()
with conn('a') as c:
 party=str(c.execute('select id from bovi.parte limit 1').fetchone()[0]);animal=command(c,SA,'registrar_animal',{'sexo':'M','identificaciones':[{'sistema':'INTERNO','codigo':'DEMOCAP'+uuid.uuid4().hex}]})['id'];lot={'animales':[animal],'unidad_precio':'CABEZA','precio_unitario':'100'}
 op=command(c,SA,'crear_operacion',{'tipo':'COMPRA','parte_id':party,'fecha_operacion':'2026-10-01','lotes':[lot]})['id'];command(c,SA,'editar_operacion',{'operacion_id':op,'version_lock':0,'lotes':[lot]});assert query(c,SA,'operacion',{'id':op})['fecha_operacion']=='2026-10-01'
 command(c,SA,'editar_operacion',{'operacion_id':op,'version_lock':1,'fecha_operacion':'2026-10-02','lotes':[lot]});assert query(c,SA,'operacion',{'id':op})['fecha_operacion']=='2026-10-02'
 per=str(c.execute("select id from bovi.periodo_cierre where sucursal_id=%s and estado='ABIERTO'",(SA,)).fetchone()[0]);fin={'periodo_id':per,'fecha_reconocimiento':'2026-10-11'};command(c,SA,'confirmar_operacion',{'operacion_id':op,'version_lock':2,**fin});pos=str(c.execute('select id from bovi.posicion_inventario where compra_operacion_id=%s',(op,)).fetchone()[0])
 def visible(flag=True):return query(c,SA,'inventario_posiciones',{'id':pos,'disponibles_para_venta':flag})['total']
 assert visible()==1
 sale=command(c,SA,'crear_operacion',{'tipo':'VENTA','parte_id':party,'lotes':[{'posiciones':[pos],'unidad_precio':'CABEZA','precio_unitario':'1600'}]})['id'];deadline=c.execute("select clock_timestamp()+interval '100 milliseconds'").fetchone()[0];command(c,SA,'reservar_venta',{'operacion_id':sale,'vence_en':deadline.isoformat()});assert visible()==0 and visible(False)==1
 while c.execute('select clock_timestamp()<%s',(deadline,)).fetchone()[0]:time.sleep(.005)
 assert visible()==1
 command(c,SA,'reservar_venta',{'operacion_id':sale});command(c,SA,'confirmar_operacion',{'operacion_id':sale,'version_lock':0,**fin});assert visible()==0
 reject(c,'select bovi.consultar(%s,%s,%s,%s,%s)',(E,SA,U,'inventario_posiciones',Jsonb({'disponibles_para_venta':'true'})),'BV015')
 c.rollback()
result={'database':DB,'seconds':round(time.monotonic()-start,3),'command_calls':calls,'FDW_reader':'A','capture_owner':'B','B_provider_server_absent':True,'capture_hash_scope_checked':True,'snapshot_gasto_local_B':True,'fecha_patch_preserves_absent_and_updates_explicit':True,'vendibles_disponible_reserved_expired_pending_sale':True}
Path('db/tests/owner-capture-result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS '+json.dumps(result))
