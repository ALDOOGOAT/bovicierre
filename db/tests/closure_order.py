#!/usr/bin/env python3
"""GOLD10 coste-primero: barrera + espera Lock observada, corte incluye reconocimiento comprometido."""
import concurrent.futures,hashlib,json,os,threading,time,uuid
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb
DB=os.environ.get('BOVI_DB_NAME','bovicierre_release_replay');assert DB!='bovicierre';sec=Path.home()/'.local/share/bovicierre-academic/secrets';E='11111111-1111-4111-8111-111111111111';S='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';U='99999999-9999-4999-8999-999999999999';calls=0

def conn():return psycopg.connect(host='127.0.0.1',port=15432,dbname=DB,user='bovi_app_a',password=(sec/'app_a_password').read_text().strip())
def command(c,name,body):
 global calls
 calls+=1
 return c.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',(E,S,U,'DEMO-CLOSURE-'+str(uuid.uuid4()),hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest(),uuid.uuid4(),name,Jsonb(body))).fetchone()[0]
with conn() as c:
 per=str(c.execute("select id from bovi.periodo_cierre where sucursal_id=%s and estado='ABIERTO'",(S,)).fetchone()[0]);party=str(c.execute('select id from bovi.parte limit 1').fetchone()[0]);aid=command(c,'registrar_animal',{'sexo':'M','identificaciones':[{'sistema':'INTERNO','codigo':'DEMOCLOSE'+uuid.uuid4().hex[:24]}]})['id'];buy=command(c,'crear_operacion',{'tipo':'COMPRA','parte_id':party,'lotes':[{'animales':[aid],'unidad_precio':'CABEZA','precio_unitario':'100'}]})['id'];fin={'periodo_id':per,'fecha_reconocimiento':'2026-10-11'};command(c,'confirmar_operacion',{'operacion_id':buy,'version_lock':0,**fin});before=c.execute('select sum(delta_inventario) from bovi.asiento_valoracion where sucursal_id=%s',(S,)).fetchone()[0]
barrier=threading.Barrier(2);shared={};start=time.monotonic()
def cost_writer():
 with conn() as c:
  gid=command(c,'registrar_gasto',{'operacion_id':buy,'importe':{'importe':'7.00','moneda':'MXN'},'clasificacion':'CAPITALIZABLE','concepto':'DEMO COST FIRST','fecha_economica':'2027-02-01',**fin})['id'];command(c,'repartir_gasto',{'gasto_id':gid,**fin});barrier.wait(timeout=5)
  end=time.monotonic()+5
  while not c.execute("select exists(select 1 from pg_stat_activity where pid=%s and wait_event_type='Lock')",(shared['pid'],)).fetchone()[0]:
   assert time.monotonic()<end;threading.Event().wait(.005)
  shared['lock_wait_observed']=True;c.commit();return gid
def closer():
 with conn() as c:
  shared['pid']=c.info.backend_pid;barrier.wait(timeout=5);r=command(c,'cerrar_periodo',{'periodo_id':per,'motivo':'DEMO COST FIRST barrier'});c.commit();return r
with concurrent.futures.ThreadPoolExecutor(2) as ex:
 writer=ex.submit(cost_writer);closer_future=ex.submit(closer);gid=writer.result();closed=closer_future.result()
with conn() as c:
 after=c.execute('select sum(delta_inventario) from bovi.asiento_valoracion where sucursal_id=%s',(S,)).fetchone()[0];assert after==before+7;assert str(after)==closed['totales']['inventario'];frozen=c.execute('select totales from bovi.cierre_periodo_version where periodo_id=%s and numero_version=%s',(per,closed['numero_version'])).fetchone()[0];command(c,'reabrir_periodo',{'periodo_id':per,'motivo':'DEMO preserve immutable closedversion'});assert frozen==c.execute('select totales from bovi.cierre_periodo_version where periodo_id=%s and numero_version=%s',(per,closed['numero_version'])).fetchone()[0]
result={'database':DB,'command_calls':calls,'seconds':round(time.monotonic()-start,3),'two_connections_barrier':True,'period_lock_wait_observed':shared['lock_wait_observed'],'order':'cost_first_commit_then_close','inventory_before':str(before),'inventory_after':str(after),'closure_inventory':closed['totales']['inventario'],'documentary_date':'2027-02-01','recognition_date':'2026-10-11','old_closure_immutable_after_reopen':True};Path('db/tests/closure-order-result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS TEST09/GOLD10 '+json.dumps(result))
