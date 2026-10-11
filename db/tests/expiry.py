#!/usr/bin/env python3
"""TEST20: dos conexiones/barrera, espera observada por lock y vencimiento real antes de confirmar."""
import concurrent.futures,hashlib,json,os,threading,time,uuid
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb
DB=os.environ.get('BOVI_DB_NAME','bovicierre_release_replay');assert DB!='bovicierre';sec=Path.home()/'.local/share/bovicierre-academic/secrets'
E='11111111-1111-4111-8111-111111111111';S='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';U='99999999-9999-4999-8999-999999999999';calls=0

def conn(admin=False):return psycopg.connect(host='127.0.0.1',port=15432,dbname=DB,user='postgres' if admin else 'bovi_app_a',password=(sec/('admin_password' if admin else 'app_a_password')).read_text().strip())
def command(c,name,body,key=None):
 global calls
 calls+=1
 return c.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',(E,S,U,key or 'DEMO-EXPIRY-'+str(uuid.uuid4()),hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest(),uuid.uuid4(),name,Jsonb(body))).fetchone()[0]
with conn() as c:
 period=c.execute("select id::text from bovi.periodo_cierre where sucursal_id=%s and estado='ABIERTO'",(S,)).fetchone()[0];fin={'periodo_id':period,'fecha_reconocimiento':'2026-10-11'}
 party=command(c,'crear_contraparte',{'nombre':'DEMO expiry barrier'})['id'];aid=command(c,'registrar_animal',{'sexo':'M','identificaciones':[{'sistema':'INTERNO','codigo':'DEMOEXP'+uuid.uuid4().hex}]})['id'];buy=command(c,'crear_operacion',{'tipo':'COMPRA','parte_id':party,'lotes':[{'animales':[aid],'unidad_precio':'CABEZA','precio_unitario':'100'}]})['id'];command(c,'confirmar_operacion',{'operacion_id':buy,'version_lock':0,**fin});pos=str(c.execute('select id from bovi.posicion_inventario where compra_operacion_id=%s',(buy,)).fetchone()[0]);sale=command(c,'crear_operacion',{'tipo':'VENTA','parte_id':party,'lotes':[{'posiciones':[pos],'unidad_precio':'CABEZA','precio_unitario':'1600'}]})['id'];deadline=c.execute("select clock_timestamp()+interval '5 seconds'").fetchone()[0];command(c,'reservar_venta',{'operacion_id':sale,'vence_en':deadline.isoformat()})
barrier=threading.Barrier(2);shared={};start=time.monotonic();key='DEMO-EXPIRY-CONFIRM-'+str(uuid.uuid4())
def lock_holder():
 with conn(True) as c:
  c.execute('select id from bovi.posicion_inventario where id=%s for update',(pos,));barrier.wait(timeout=5)
  # Poll the actual lock wait, never guess concurrency from a delay.
  end=time.monotonic()+10
  while not c.execute("select exists(select 1 from pg_stat_activity where pid=%s and wait_event_type='Lock')",(shared['pid'],)).fetchone()[0]:
   assert time.monotonic()<end;threading.Event().wait(.005)
  shared['lock_wait_observed']=True
  while c.execute('select clock_timestamp()<%s',(deadline,)).fetchone()[0]:threading.Event().wait(.005)
  c.commit()
def confirmer():
 with conn() as c:
  shared['pid']=c.info.backend_pid;began=c.execute('select now()').fetchone()[0];assert began<deadline;barrier.wait(timeout=5)
  try:command(c,'confirmar_operacion',{'operacion_id':sale,'version_lock':0,**fin},key);c.commit();return 'UNEXPECTED_COMMIT'
  except psycopg.Error as ex:c.rollback();assert ex.sqlstate=='P0001';return json.loads(ex.diag.message_detail)['codigo']
with concurrent.futures.ThreadPoolExecutor(2) as ex:
 holder=ex.submit(lock_holder);confirmation=ex.submit(confirmer);holder.result();code=confirmation.result()
assert code=='BV403' and shared['lock_wait_observed']
with conn() as c:
 assert c.execute('select count(*) from bovi.liquidacion where operacion_id=%s',(sale,)).fetchone()[0]==0
 assert c.execute('select estado from bovi.posicion_inventario where id=%s',(pos,)).fetchone()[0]=='DISPONIBLE'
 assert c.execute('select count(*) from bovi.clave_idempotencia where clave=%s',(key,)).fetchone()[0]==0
 # KG draft can be captured before the ticket; simulator and acceptance expose missing weight.
 kg=command(c,'crear_operacion',{'tipo':'COMPRA','parte_id':party,'lotes':[{'animales':[aid],'unidad_precio':'KG','precio_unitario':'11'}]})['id']
 for mode in ('simulador','acordar_operacion'):
  c.execute('savepoint incomplete')
  try:
   if mode=='simulador':c.execute('select bovi.consultar(%s,%s,%s,%s,%s)',(E,S,U,mode,Jsonb({'id':kg})))
   else:command(c,mode,{'operacion_id':kg,'version_lock':0})
  except psycopg.Error as ex:assert ex.sqlstate=='P0001' and json.loads(ex.diag.message_detail)['codigo']=='BV013';c.execute('rollback to incomplete')
  else:raise AssertionError('Incomplete KG accepted')
 c.rollback()
result={'database':DB,'seconds':round(time.monotonic()-start,3),'command_calls':calls,'two_connections':True,'barrier':True,'lock_wait_observed':True,'tx_began_before_expiry':True,'result':'BV403','liquidacion_partial':False,'kg_incomplete_public_BV013':True}
Path('db/tests/expiry-result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS TEST20 '+json.dumps(result))
