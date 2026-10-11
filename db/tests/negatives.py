#!/usr/bin/env python3
"""TEST12/13/14/16/17: negativas SQL reales, namespaces QA únicamente."""
import concurrent.futures,hashlib,json,os,threading,uuid
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb
DB=os.environ.get('BOVI_DB_NAME','bovicierre_release_replay');assert DB!='bovicierre';secret=Path.home()/'.local/share/bovicierre-academic/secrets'
E='11111111-1111-4111-8111-111111111111';A='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';B='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';U='99999999-9999-4999-8999-999999999999';calls=0;results={}
def connect(admin=False):return psycopg.connect(host='127.0.0.1',port=15432,dbname=DB,user='postgres' if admin else 'bovi_app_a',password=(secret/('admin_password' if admin else 'app_a_password')).read_text().strip())
def command(c,name,body,site=A,company=E):
 global calls
 calls+=1
 return c.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',(company,site,U,'DEMO-NEGATIVE-'+str(uuid.uuid4()),hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest(),uuid.uuid4(),name,Jsonb(body))).fetchone()[0]
barrier=threading.Barrier(2);identifier='DEMOID'+uuid.uuid4().hex

def duplicate(site):
 with connect() as c:
  barrier.wait()
  try:record=command(c,'registrar_animal',{'sede_operadora_id':site,'sexo':'M','identificaciones':[{'sistema':'INTERNO','codigo':identifier if site==A else 'demoid-'+identifier[6:]}]},site);c.commit();return 'OK'
  except psycopg.Error as ex:c.rollback();return ex.sqlstate
with concurrent.futures.ThreadPoolExecutor(2) as ex:states=list(ex.map(duplicate,[A,B]))
assert sorted(states)==['23505','OK'];results['TEST-13']={'two_connections_barrier':True,'states':states,'canonical_writer':'A for both site scopes'}
with connect() as c:
 assert c.execute('select count(*) from bovi.animal_identificacion where codigo_normalizado=%s',(identifier.upper(),)).fetchone()[0]==1
 party=str(c.execute('select id from bovi.parte where empresa_id=%s limit 1',(E,)).fetchone()[0]);foreign=str(c.execute('select id from bovi.posicion_inventario where sucursal_id=%s limit 1',(B,)).fetchone()[0])
 cases=[('foreign_site_fk','crear_operacion',{'tipo':'VENTA','parte_id':party,'lotes':[{'unidad_precio':'CABEZA','precio_unitario':'10','posiciones':[foreign]}]},'23503',E),('foreign_company_scope','crear_contraparte',{'nombre':'DEMO rejected'},'42501',str(uuid.uuid4())),('nonfinite_money','registrar_pago',{'parte_id':party,'tipo':'COBRO','metodo':'EFECTIVO','importe':{'importe':'NaN','moneda':'MXN'}},'23514',E)]
 for label,name,body,state,company in cases:
  c.execute('savepoint denied')
  try:command(c,name,body,company=company)
  except psycopg.Error as ex:assert ex.sqlstate==state,(label,ex.sqlstate);results[label]=state;c.execute('rollback to denied')
  else:raise AssertionError(label+' was accepted')
 for label,sql in [('disable_trigger','ALTER TABLE bovi.liquidacion DISABLE TRIGGER ALL'),('replica_mode',"SET session_replication_role='replica'")]:
  c.execute('savepoint denied')
  try:c.execute(sql)
  except psycopg.Error as ex:assert ex.sqlstate=='42501';results[label]='42501';c.execute('rollback to denied')
  else:raise AssertionError(label+' was accepted')
 c.rollback()
with connect() as c:
 aid=str(c.execute('select id from bovi.animal where empresa_id=%s and sede_operadora_id=%s limit 1',(E,A)).fetchone()[0]);party=str(c.execute('select id from bovi.parte where empresa_id=%s limit 1',(E,)).fetchone()[0])
 op=command(c,'crear_operacion',{'tipo':'COMPRA','parte_id':party,'lotes':[{'unidad_precio':'KG','precio_unitario':'10','animales':[aid]}]})['id'];ticket=command(c,'registrar_pesaje',{'operacion_id':op,'numero_lote':1,'modo':'NETO_REPORTADO','neto':{'kg':'1.000'},'ticket_folio':'DEMO guard immutable','bascula':'DEMO QA','animales':[{'animal_id':aid}]})['id'];command(c,'aprobar_pesaje',{'pesaje_id':ticket})
with connect(True) as c:
 c.execute('set role bovi_command')
 for table,expression,where in [('liquidacion','total=total','true'),('contrato_version','estado=estado',"estado='ACEPTADA'"),('condicion_lote','precio_unitario=precio_unitario',"EXISTS(SELECT 1 FROM bovi.contrato_version cv WHERE (cv.empresa_id,cv.sucursal_id,cv.operacion_id,cv.numero_version)=(bovi.condicion_lote.empresa_id,bovi.condicion_lote.sucursal_id,bovi.condicion_lote.operacion_id,bovi.condicion_lote.numero_version) AND cv.estado='ACEPTADA')"),('pesaje','neto_kg=neto_kg',"estado='APROBADO'")]:
  c.execute('savepoint immutable')
  try:c.execute('UPDATE bovi.'+table+' SET '+expression+' WHERE '+where)
  except psycopg.Error as ex:assert ex.sqlstate=='P0001' and json.loads(ex.diag.message_detail)['codigo']=='BV016';results['immutable_'+table]='BV016';c.execute('rollback to immutable')
  else:
   # Existing QA has CABEZA-only committed fixtures; no approved weighing is not a passing test.
   results['immutable_'+table]='NO_FIXTURE_UNTESTED'
 c.rollback()
Path('db/tests/negatives-result.json').write_text(json.dumps({'database':DB,'command_calls':calls,'results':results,'scope':'SQL direct; does not certify HTTP error mapping'},indent=2)+'\n');print('PASS SQL negatives '+json.dumps(results))
