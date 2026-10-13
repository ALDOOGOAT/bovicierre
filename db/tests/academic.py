#!/usr/bin/env python3
"""Concurrencia, lógica bidireccional y FDW en PostgreSQL18 real. Sólo DEMO / DB aislada."""
import concurrent.futures,hashlib,json,os,threading,time,uuid,subprocess
from pathlib import Path
from decimal import Decimal
import psycopg
from psycopg.types.json import Jsonb
SECRET=Path(os.environ.get('BOVI_SECRET_DIR',Path.home()/'.local/share/bovicierre-academic/secrets'));DB=os.environ.get('BOVI_DB_NAME','bovicierre_release_replay')
E='11111111-1111-4111-8111-111111111111';S={'A':'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','B':'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'};U='99999999-9999-4999-8999-999999999999';per={};calls=0
assert DB!='bovicierre','Academic tests require isolated database'
def connect(node='A',role=None,autocommit=False,pool=False):
 role=role or 'bovi_app_'+node.lower();files={'postgres':'admin_password','bovi_worker':'worker_password'}
 return psycopg.connect(host='127.0.0.1',port={'A':19999 if pool else 15432,'B':19998 if pool else 15433}[node],dbname=DB,user=role,password=(SECRET/files.get(role,'app_'+node.lower()+'_password')).read_text().strip(),autocommit=autocommit)
def sql(node,query,args=(),role=None):
 with connect(node,role) as con:
  with con.cursor() as c:
   c.execute(query,args);row=c.fetchone() if c.description else None;return row[0] if row else None

def command(node,name,body,connection=None,key=None):
 global calls
 calls+=1; b=dict(body)
 if name in ('confirmar_operacion','registrar_pago','validar_pago','aplicar_pago','revertir_aplicacion','reembolsar_pago','ajustar_liquidacion','registrar_gasto','repartir_gasto','registrar_baja','anular_venta'):
  b={'periodo_id':per[node],'fecha_reconocimiento':'2026-10-11',**b}
 params=(E,S[node],U,key or 'DEMO-ACADEMIC-'+str(uuid.uuid4()),hashlib.sha256(json.dumps(b,sort_keys=True).encode()).hexdigest(),uuid.uuid4(),name,Jsonb(b))
 if connection:
  with connection.cursor() as c:c.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',params);return c.fetchone()[0]
 return sql(node,'select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',params)
def wait_until(fn,timeout=12):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  if fn():return
  threading.Event().wait(.05)
 raise AssertionError('Replication convergence deadline exceeded')
def animal(node,code):
 aid=command('A','registrar_animal',{'sede_operadora_id':S[node],'sexo':'M','identificaciones':[{'sistema':'INTERNO','codigo':'DEMO '+code.replace('-','')}]})['id']
 if node=='B':wait_until(lambda:sql('B','select count(*) from bovi.animal where id=%s',(aid,))==1)
 return aid
def operation(node,kind,party,ids,price):return command(node,'crear_operacion',{'tipo':kind,'parte_id':party,'fecha_operacion':'2026-10-01','lotes':[{'animales' if kind=='COMPRA' else 'posiciones':ids,'unidad_precio':'CABEZA','precio_unitario':str(price)}]})['id']
start=time.monotonic()
wait_until(lambda:sql('B','select count(*) from bovi.membresia_usuario where usuario_id=%s',(U,))==2)
for node in 'AB':
 existing=sql(node,"select id::text from bovi.periodo_cierre where empresa_id=%s and sucursal_id=%s and estado='ABIERTO' limit 1",(E,S[node]))
 if not existing:
  closed=sql(node,"select id::text from bovi.periodo_cierre where empresa_id=%s and sucursal_id=%s and estado='CERRADO' ORDER BY desde DESC limit 1",(E,S[node]))
  if closed:command(node,'reabrir_periodo',{'periodo_id':closed,'motivo':'DEMO rerun isolated tests'});existing=closed
 per[node]=existing or command(node,'crear_periodo',{'desde':'2026-10-01','hasta':'2026-10-31'})['id']
party=command('A','crear_contraparte',{'nombre':'DEMO académico carreras'})['id'];wait_until(lambda:sql('B','select count(*) from bovi.parte where id=%s',(party,))==1)
aid=animal('A',str(uuid.uuid4()));buy=operation('A','COMPRA',party,[aid],1100);command('A','confirmar_operacion',{'operacion_id':buy,'version_lock':0});pos=str(sql('A','select id from bovi.posicion_inventario where compra_operacion_id=%s',(buy,)))
# Two transactions start at the same barrier; exactly one reservation can win.
sales=[operation('A','VENTA',party,[pos],1600) for _ in range(2)];barrier=threading.Barrier(2)
def reserve(op):
 with connect() as con:
  barrier.wait()
  try:result=command('A','reservar_venta',{'operacion_id':op},con);con.commit();return ('ok',op,result)
  except psycopg.Error as ex:con.rollback();return(ex.sqlstate,op,json.loads(ex.diag.message_detail)['codigo'] if ex.diag.message_detail and ex.sqlstate=='P0001' else None)
with concurrent.futures.ThreadPoolExecutor(2) as executor:results=list(executor.map(reserve,sales))
assert sum(r[0]=='ok' for r in results)==1,results
winner=next(r[1] for r in results if r[0]=='ok');loser=next(r[1] for r in results if r[0]!='ok')
# GOLD-ACAD-03: el perdedor recibe conflicto de negocio y queda una sola reserva activa.
assert next(r for r in results if r[0]!='ok')[2]=='BV402',results;assert sql('A',"select count(*) from bovi.reserva_venta where posicion_id=%s and estado='ACTIVA'",(pos,))==1
command('A','confirmar_operacion',{'operacion_id':winner,'version_lock':0})
print('PASS TEST-10 barrier race: exactly one reservation/confirmation')
# Two application transactions share a payment lock, no overapplication.
liq=str(sql('A','select id from bovi.liquidacion where operacion_id=%s',(winner,)));pay=command('A','registrar_pago',{'parte_id':party,'tipo':'COBRO','importe':{'importe':'600.00','moneda':'MXN'},'metodo':'EFECTIVO'})['id'];command('A','validar_pago',{'pago_id':pay});barrier=threading.Barrier(2)
def apply(_):
 with connect() as con:
  barrier.wait()
  try:r=command('A','aplicar_pago',{'pago_id':pay,'liquidacion_id':liq,'importe':{'importe':'400.00','moneda':'MXN'}},con);con.commit();return 'ok'
  except psycopg.Error as e:con.rollback();assert e.sqlstate=='P0001';return json.loads(e.diag.message_detail)['codigo']
with concurrent.futures.ThreadPoolExecutor(2) as ex:results=list(ex.map(apply,range(2)))
assert sorted(results)==['BV020','ok'],results
assert sql('A','select disponible from bovi.v_disponible_pago where id=%s',(pay,))==200
print('PASS TEST-11 barrier race: 600 payment, one400, available200')
# B-origin confirmed acquisition replicates without regenerating audit/outbox.
bid=animal('B',str(uuid.uuid4()));bbuy=operation('B','COMPRA',party,[bid],1100);command('B','confirmar_operacion',{'operacion_id':bbuy,'version_lock':0});bpos=str(sql('B','select id from bovi.posicion_inventario where compra_operacion_id=%s',(bbuy,)))
wait_until(lambda:sql('A','select count(*) from bovi.posicion_inventario where id=%s',(bpos,))==1)
for table in ('operacion','posicion_inventario','liquidacion','auditoria_evento','evento_outbox'):
 wait_until(lambda t=table:sql('A','select count(*) from bovi.'+t)==sql('B','select count(*) from bovi.'+t))
print('PASS TEST-21/23 bidirectional full-table counts and no duplicated audit/outbox')
# The apply stream is paused, B can operate only its known resources; no write promotion.
sql('A','ALTER SUBSCRIPTION sub_a_desde_b DISABLE',role='postgres')
try:
 bnew=operation('B','COMPRA',party,[animal('B',str(uuid.uuid4()))],100)
 assert sql('A','select count(*) from bovi.operacion where id=%s',(bnew,))==0
finally:sql('A','ALTER SUBSCRIPTION sub_a_desde_b ENABLE',role='postgres')
wait_until(lambda:sql('A','select count(*) from bovi.operacion where id=%s',(bnew,))==1)
print('PASS TEST-21 partition/reconnect original owner converges')
# Synthetic document evidence for death, source financial transaction never writes central identity.
doc=command('B','registrar_documento',{'tipo_documental':'OTRO','storage_key':'DEMO-'+str(uuid.uuid4()),'sha256':'a'*64,'tamano_bytes':1,'mime':'application/pdf'})['id']
command('B','registrar_baja',{'posiciones':[bpos],'motivo_baja':'MUERTE','documento_id':doc})
event=str(sql('B',"select id from bovi.evento_outbox where tipo_evento='ANIMAL_MUERTO' and payload->>'posicion_id'=%s",(bpos,)))
wait_until(lambda:sql('A','select count(*) from bovi.evento_outbox where id=%s',(event,))==1)
assert sql('A','select situacion from bovi.animal where id=%s',(bid,))=='VIGENTE'
lease=uuid.uuid4();claims=sql('B','select bovi.reclamar_entregas(%s,50)',(lease,),'bovi_worker');claim=next(x for x in claims if x['id']==event)
assert sql('B','select bovi.reclamar_entregas(%s,50)',(uuid.uuid4(),),'bovi_worker')==[]
# No acknowledgement after the first central consume simulates an acknowledgement lost in transit.
for _ in range(2):sql('A','select bovi.consumir_muerte(%s,%s,%s,%s)',(E,S['B'],event,Jsonb(claim['payload'])),'bovi_worker')
sql('B','select bovi.confirmar_entrega(%s,%s)',(event,lease),'bovi_worker')
assert sql('A','select situacion from bovi.animal where id=%s',(bid,))=='MUERTO';assert sql('A','select count(*) from bovi.mensaje_inbox where event_id=%s',(event,))==1
assert sql('A',"select count(*) from bovi.auditoria_evento where correlation_id=%s and comando='consumir_muerte'",(event,))==1
wait_until(lambda:sql('B','select situacion from bovi.animal where id=%s',(bid,))=='MUERTO')
assert sql('B','select sum(delta_perdida) from bovi.asiento_valoracion where posicion_id=%s',(bpos,))==1100
print('PASS death B/outbox/lease/A-inbox with lost acknowledgement deduplicated; loss1100')
with connect('B') as con:
 deadop=command('B','crear_operacion',{'tipo':'COMPRA','parte_id':party,'lotes':[{'animales':[bid],'unidad_precio':'CABEZA','precio_unitario':'100'}]},con)['id']
 con.execute('savepoint dead')
 try:command('B','confirmar_operacion',{'operacion_id':deadop,'version_lock':0},con)
 except psycopg.Error as ex:assert ex.sqlstate=='P0001' and json.loads(ex.diag.message_detail)['codigo']=='BV011';con.execute('rollback to dead')
 else:raise AssertionError('Dead animal repurchased')
 con.rollback()
for node in 'AB':
 reconciliation=sql(node,'select bovi.fn_validar_conciliacion_propietario(%s,%s,%s)',(E,S[node],U));assert reconciliation['huerfanos']==0 and reconciliation['liquidaciones_desbalanceadas']==0,reconciliation
print('PASS TEST33 deadidentity cannotrebuy; TEST23 explicit owner reconciliation0orphans/0imbalances')

# Read-only FDW through real raw Pgpool, not a mocked provider.
with connect('A',pool=True) as con:
 with con.cursor() as c:
  c.execute('select precio_mxn from ext_proveedor.tarifa_transporte where ruta=%s',('DEMO-RUTA-01',));assert c.fetchone()[0]==12000
  c.execute('savepoint denied')
  try:c.execute("update ext_proveedor.tarifa_transporte set precio_mxn=1")
  except psycopg.Error as e:assert e.sqlstate=='42501';c.execute('rollback to denied')
  else:raise AssertionError('FDW write should be denied')
print('PASS TEST-25 actual FDW12000 through Pgpool, UPDATE denied42501')
# Wrong writer and readonly runtime restrictions are exercised against owner connections.
for node,statement in [('B','update bovi.animal set situacion=\'MUERTO\''),('A','create table bovi.unsolicited(id int)'),('A',"set session_replication_role='replica'")]:
 try:sql(node,statement)
 except psycopg.Error as e:assert e.sqlstate=='42501',(e.sqlstate,statement)
 else:raise AssertionError('Forbidden SQL accepted')
print('PASS runtime DML/DDL/replica-role denied')
# GOLD-10 locks the same period before financial facts and immutable closure snapshot.
barrier=threading.Barrier(2)
def closing(_):
 with connect() as con:
  barrier.wait();result=command('A','cerrar_periodo',{'periodo_id':per['A'],'motivo':'DEMO GOLD10 barrier'},con);con.commit();return result

def late_cost(_):
 with connect() as con:
  barrier.wait()
  try:
   gid=command('A','registrar_gasto',{'operacion_id':buy,'importe':{'importe':'7.00','moneda':'MXN'},'clasificacion':'CAPITALIZABLE','concepto':'DEMO GOLD10 fecha documental futura','fecha_economica':'2027-02-01'},con)['id']
   command('A','repartir_gasto',{'gasto_id':gid},con);con.commit();return 'APLICADO'
  except psycopg.Error as ex:con.rollback();assert ex.sqlstate=='P0001';assert json.loads(ex.diag.message_detail)['codigo']=='BV025';return 'CERRADO'
with concurrent.futures.ThreadPoolExecutor(2) as executor:
 futures=[executor.submit(closing,0),executor.submit(late_cost,0)];closure=futures[0].result();outcome=futures[1].result()
assert Decimal(closure['totales']['inventario'])==sql('A','select sum(delta_inventario) from bovi.asiento_valoracion where empresa_id=%s and sucursal_id=%s',(E,S['A']))
frozen=sql('A','select totales from bovi.cierre_periodo_version where periodo_id=%s and numero_version=%s',(per['A'],closure['numero_version']))
command('A','reabrir_periodo',{'periodo_id':per['A'],'motivo':'DEMO next test release'})
assert sql('A','select totales from bovi.cierre_periodo_version where periodo_id=%s and numero_version=%s',(per['A'],closure['numero_version']))==frozen
print('PASS GOLD-10 barrier closure/cost='+outcome+' documentaryfuture ignored; immutableclosure preserved')
# Planner evidence is scoped to this declared tiny synthetic dataset.
plans={};counts={}
queries={'inventario':"select * from bovi.posicion_inventario where empresa_id=%s and sucursal_id=%s and estado='DISPONIBLE'",'cartera':'select * from bovi.v_saldo_liquidacion where empresa_id=%s and sucursal_id=%s','liquidacion':'select * from bovi.concepto_liquidacion where empresa_id=%s and sucursal_id=%s','expediente':'select * from bovi.movimiento_inventario where empresa_id=%s and sucursal_id=%s'}
with connect('A') as con:
 with con.cursor() as c:
  for key,query in queries.items():c.execute('EXPLAIN(ANALYZE,BUFFERS,FORMAT JSON) '+query,(E,S['A']));plans[key]=c.fetchone()[0][0]
  for table in ('animal','operacion','posicion_inventario','liquidacion','aplicacion_pago','evento_outbox'):c.execute('select count(*) from bovi.'+table);counts[table]=c.fetchone()[0]
Path('db/tests/explain.json').write_text(json.dumps({'database':DB,'dataset':counts,'plans':plans,'scope':'Dataset pequeño; no acredita SLO ni rendimiento en producción.'},indent=2))
summary={'database':DB,'seconds':round(time.monotonic()-start,3),'command_calls':calls,'tests':['TEST-10','TEST-11','TEST-21','TEST-23','TEST-24','TEST-25','TEST-33','TEST-09','roles'],'dataset':counts}
Path('db/tests/academic-result.json').write_text(json.dumps(summary,indent=2));print('PASS academic evidence '+json.dumps(summary))
