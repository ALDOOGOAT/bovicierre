#!/usr/bin/env python3
"""IfMatch cancel/anular/acordar/reabrir; 412 sin efectos y replay original tras commit nuevoestado."""
import hashlib,json,os,time,uuid
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb
DB=os.environ.get('BOVI_DB_NAME','bovicierre_release_replay');assert DB!='bovicierre';sec=Path.home()/'.local/share/bovicierre-academic/secrets';E='11111111-1111-4111-8111-111111111111';S='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';U='99999999-9999-4999-8999-999999999999';calls=0

def conn():return psycopg.connect(host='127.0.0.1',port=15432,dbname=DB,user='bovi_app_a',password=(sec/'app_a_password').read_text().strip())
def command(c,name,body,key=None):
 global calls
 calls+=1
 return c.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',(E,S,U,key or 'DEMO-VERSION-'+str(uuid.uuid4()),hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest(),uuid.uuid4(),name,Jsonb(body))).fetchone()[0]
def reject(c,name,body):
 key='DEMO-VERSION-REJECT-'+str(uuid.uuid4());before=c.execute('select count(*) from bovi.auditoria_evento').fetchone()[0];c.execute('savepoint invalid')
 try:command(c,name,body,key)
 except psycopg.Error as ex:assert ex.sqlstate=='P0001' and json.loads(ex.diag.message_detail)['codigo']=='BV412';c.execute('rollback to invalid')
 else:raise AssertionError('Stale accepted '+name)
 assert c.execute('select count(*) from bovi.clave_idempotencia where clave=%s',(key,)).fetchone()[0]==0;assert c.execute('select count(*) from bovi.auditoria_evento').fetchone()[0]==before
start=time.monotonic();replays=[]
with conn() as c:
 party=str(c.execute('select id from bovi.parte limit 1').fetchone()[0]);per=str(c.execute("select id from bovi.periodo_cierre where sucursal_id=%s and estado='ABIERTO'",(S,)).fetchone()[0]);fin={'periodo_id':per,'fecha_reconocimiento':'2026-10-11'};aid=command(c,'registrar_animal',{'sexo':'M','identificaciones':[{'sistema':'INTERNO','codigo':'DEMOVER'+uuid.uuid4().hex[:24]}]})['id'];lot={'animales':[aid],'unidad_precio':'CABEZA','precio_unitario':'100'}
 cancel=command(c,'crear_operacion',{'tipo':'COMPRA','parte_id':party,'lotes':[lot]})['id'];command(c,'editar_operacion',{'operacion_id':cancel,'version_lock':0,'lotes':[lot]});c.commit();reject(c,'cancelar_operacion',{'operacion_id':cancel,'version_lock':0});assert c.execute('select estado from bovi.operacion where id=%s',(cancel,)).fetchone()[0]=='BORRADOR';body={'operacion_id':cancel,'version_lock':1};key='DEMO-CANCEL-REPLAY-'+str(uuid.uuid4());first=command(c,'cancelar_operacion',body,key);c.commit();replays.append(('cancelar_operacion',body,key,first))
 buy=command(c,'crear_operacion',{'tipo':'COMPRA','parte_id':party,'lotes':[lot]})['id'];command(c,'confirmar_operacion',{'operacion_id':buy,'version_lock':0,**fin});pos=str(c.execute('select id from bovi.posicion_inventario where compra_operacion_id=%s',(buy,)).fetchone()[0]);sale=command(c,'crear_operacion',{'tipo':'VENTA','parte_id':party,'lotes':[{'posiciones':[pos],'unidad_precio':'CABEZA','precio_unitario':'1000'}]})['id'];command(c,'reservar_venta',{'operacion_id':sale});command(c,'confirmar_operacion',{'operacion_id':sale,'version_lock':0,**fin});c.commit();reject(c,'anular_venta',{'operacion_id':sale,'version_lock':0,'motivo':'DEMO stale',**fin});assert c.execute('select estado from bovi.operacion where id=%s',(sale,)).fetchone()[0]=='CONFIRMADA';body={'operacion_id':sale,'version_lock':1,'motivo':'DEMO valid',**fin};key='DEMO-ANNUL-REPLAY-'+str(uuid.uuid4());first=command(c,'anular_venta',body,key);c.commit();replays.append(('anular_venta',body,key,first))
 agreement=command(c,'crear_operacion',{'tipo':'COMPRA','parte_id':party,'lotes':[lot]})['id'];command(c,'editar_operacion',{'operacion_id':agreement,'version_lock':0,'lotes':[lot]});reject(c,'acordar_operacion',{'operacion_id':agreement,'version_lock':0});body={'operacion_id':agreement,'version_lock':1};key='DEMO-AGREE-REPLAY-'+str(uuid.uuid4());first=command(c,'acordar_operacion',body,key);c.commit();replays.append(('acordar_operacion',body,key,first));reject(c,'reabrir_operacion',{'operacion_id':agreement,'version_lock':1});body={'operacion_id':agreement,'version_lock':2};key='DEMO-REOPEN-REPLAY-'+str(uuid.uuid4());first=command(c,'reabrir_operacion',body,key);c.commit();replays.append(('reabrir_operacion',body,key,first))
with conn() as c:
 for name,body,key,first in replays:assert command(c,name,body,key)==first
 assert c.execute('select estado from bovi.operacion where id=%s',(cancel,)).fetchone()[0]=='CANCELADA';assert c.execute('select estado from bovi.operacion where id=%s',(sale,)).fetchone()[0]=='ANULADA';assert c.execute('select estado from bovi.posicion_inventario where id=%s',(pos,)).fetchone()[0]=='DISPONIBLE'
result={'database':DB,'command_calls':calls,'seconds':round(time.monotonic()-start,3),'stale_412_no_idem_or_audit_effect':['cancelar_operacion','anular_venta','acordar_operacion','reabrir_operacion'],'exact_replay_after_commit_before_current_version_check':[x[0] for x in replays]};Path('db/tests/version-guards-result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS '+json.dumps(result))
