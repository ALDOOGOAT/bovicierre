#!/usr/bin/env python3
"""Fallos reales sourceA/B/proveedor, SQL QA y HTTPmain; reanuda contenedores finally, sin promoción."""
import hashlib,http.cookiejar,json,os,subprocess,threading,time,urllib.error,urllib.request,uuid
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb
DB='bovicierre_release_replay';sec=Path.home()/'.local/share/bovicierre-academic/secrets';E='11111111-1111-4111-8111-111111111111';S={'A':'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','B':'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'};U='99999999-9999-4999-8999-999999999999';BASE=os.environ.get('BOVI_API_BASE','http://127.0.0.1:18080')+'/api/v1';calls=0;stopped=set();results={};jar=http.cookiejar.CookieJar();http=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def conn(node='A',role=None,auto=False):
 role=role or 'bovi_app_'+node.lower();file={'postgres':'admin_password','bovi_worker':'worker_password'}.get(role,'app_'+node.lower()+'_password')
 return psycopg.connect(host='127.0.0.1',port={'A':15432,'B':15433}[node],dbname=DB,user=role,password=(sec/file).read_text().strip(),autocommit=auto,connect_timeout=2)
def sql(node,query,args=(),role=None):
 with conn(node,role) as c:return c.execute(query,args).fetchone()[0]
def command(c,node,name,body):
 global calls
 calls+=1
 return c.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',(E,S[node],U,'DEMO-OUTAGE-'+str(uuid.uuid4()),hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest(),uuid.uuid4(),name,Jsonb(body))).fetchone()[0]
def wait(fn,timeout=40):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  try:
   if fn():return
  except (psycopg.Error,urllib.error.URLError,TimeoutError):pass
  threading.Event().wait(.05)
 raise AssertionError('Readiness deadline')
def container(node):return 'bovicierre-academic-pg-'+node.lower()+'-1'
def docker(*args):return subprocess.run(['docker',*args],capture_output=True,text=True,check=True).stdout.strip()
def verify(node):
 info=json.loads(docker('inspect',container(node)))[0];assert info['Config']['Labels']['com.docker.compose.project']=='bovicierre-academic';assert info['Config']['Labels']['com.docker.compose.service']=='pg-'+node.lower();return info
for node in ('a','b','prov'):verify(node)
def stop(node):verify(node);stopped.add(node);docker('stop','--time','5',container(node));print('Stopped own source '+node,flush=True)
def resume(node):
 docker('start',container(node));wait(lambda:subprocess.run(['docker','exec',container(node),'pg_isready','-U','postgres','-d','bovicierre'],capture_output=True).returncode==0);stopped.discard(node);print('Resumed own source '+node,flush=True)
def request(path,body=None,csrf=None):
 headers={'Content-Type':'application/json'}
 if csrf:headers['X-XSRF-TOKEN']=csrf
 req=urllib.request.Request(BASE+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
 try:
  with http.open(req,timeout=12) as response:return response.status,json.loads(response.read() or '{}')
 except urllib.error.HTTPError as ex:return ex.code,json.loads(ex.read() or '{}')
def assert_http(path,status):
 got,body=request(path);assert got==status,(path,got,body)
 if status==503:assert isinstance(body.get('codigo'),str) and 'password' not in json.dumps(body).lower() and 'jdbc:' not in json.dumps(body).lower(),body
 return got
start=time.monotonic()
try:
 code,csrf=request('/sesion/csrf');assert code==200;code,_=request('/sesion/login',{'login':'demo.admin','contrasena':(sec/'demo_password').read_text().strip()},csrf['token']);assert code==204,code
 for node in 'AB':assert_http('/sedes/'+S[node]+'/operaciones',200)
 with conn() as c:
  party=str(c.execute('select id from bovi.parte limit 1').fetchone()[0]);aid=command(c,'A','registrar_animal',{'sede_operadora_id':S['B'],'sexo':'M','identificaciones':[{'sistema':'INTERNO','codigo':'DEMOOUT'+uuid.uuid4().hex[:24]}]})['id']
 wait(lambda:sql('B','select count(*) from bovi.animal where id=%s',(aid,))==1)
 with conn('B') as c:
  per=str(c.execute("select id from bovi.periodo_cierre where sucursal_id=%s and estado='ABIERTO'",(S['B'],)).fetchone()[0]);fin={'periodo_id':per,'fecha_reconocimiento':'2026-10-11'};buy=command(c,'B','crear_operacion',{'tipo':'COMPRA','parte_id':party,'lotes':[{'animales':[aid],'unidad_precio':'CABEZA','precio_unitario':'100'}]})['id'];command(c,'B','confirmar_operacion',{'operacion_id':buy,'version_lock':0,**fin});pos=str(c.execute('select id from bovi.posicion_inventario where compra_operacion_id=%s',(buy,)).fetchone()[0]);doc=command(c,'B','registrar_documento',{'tipo_documental':'OTRO','storage_key':'DEMOOUTAGEMETADATA','sha256':'d'*64,'tamano_bytes':1,'mime':'application/pdf'})['id'];command(c,'B','registrar_baja',{'posiciones':[pos],'motivo_baja':'MUERTE','documento_id':doc,**fin});event=str(c.execute("select id from bovi.evento_outbox where tipo_evento='ANIMAL_MUERTO' and payload->>'posicion_id'=%s",(pos,)).fetchone()[0])
 wait(lambda:sql('A','select count(*) from bovi.evento_outbox where id=%s',(event,))==1)
 worker=uuid.uuid4();claim=next(x for x in sql('B','select bovi.reclamar_entregas(%s,100)',(worker,),'bovi_worker') if x['id']==event)
 # Already scoped B read transaction; no finance rows locked before A outage.
 with conn('B') as authorized:
  authorized.execute('select bovi.consultar(%s,%s,%s,%s,%s)',(E,S['B'],U,'operacion',Jsonb({'id':buy}))).fetchone()
  stop('a')
  try:
   results['A_down_HTTP']={n:assert_http('/sedes/'+S[n]+'/operaciones',503) for n in 'AB'}
   try:sql('A','select bovi.consumir_muerte(%s,%s,%s,%s)',(E,S['B'],event,Jsonb(claim['payload'])),'bovi_worker')
   except psycopg.OperationalError:pass
   else:raise AssertionError('A consumer unexpectedly reachable')
   sql('B','select bovi.fallar_entrega(%s,%s)',(event,worker),'bovi_worker');retry=sql('B',"select jsonb_build_object('intentos',intentos,'lease_clear',lease_token is null,'future_retry',proximo_intento>clock_timestamp(),'error',ultimo_error) from infra.entrega_outbox where evento_id=%s",(event,),'postgres');assert retry['intentos']>=1 and retry['lease_clear'] and retry['future_retry'];results['persistent_retry_A_down']=retry
   gid=command(authorized,'B','registrar_gasto',{'operacion_id':buy,'importe':{'importe':'1.00','moneda':'MXN'},'concepto':'DEMO preauthorizedB duringAdown','clasificacion':'CAPITALIZABLE',**fin})['id'];command(authorized,'B','repartir_gasto',{'gasto_id':gid,**fin});authorized.commit();results['preauthorized_B_committed_during_A_down']=True
  finally:resume('a')
 wait(lambda:request('/sedes/'+S['A']+'/operaciones')[0]==200)
 # Claim expires by actual server clock, simulating worker process disappearing after claim.
 wait(lambda:sql('B','select proximo_intento<=clock_timestamp() from infra.entrega_outbox where evento_id=%s',(event,),'postgres'))
 abandoned=uuid.uuid4();claim=next(x for x in sql('B','select bovi.reclamar_entregas(%s,100)',(abandoned,),'bovi_worker') if x['id']==event);lease=sql('B','select lease_vence_en from infra.entrega_outbox where evento_id=%s',(event,),'postgres');assert sql('B','select bovi.reclamar_entregas(%s,100)',(uuid.uuid4(),),'bovi_worker')==[]
 wait(lambda:sql('B','select clock_timestamp()>%s',(lease,)),timeout=35)
 newworker=uuid.uuid4();claim=next(x for x in sql('B','select bovi.reclamar_entregas(%s,100)',(newworker,),'bovi_worker') if x['id']==event)
 try:sql('B','select bovi.confirmar_entrega(%s,%s)',(event,abandoned),'bovi_worker')
 except psycopg.Error as ex:assert ex.sqlstate=='P0001' and json.loads(ex.diag.message_detail)['codigo']=='BV402'
 else:raise AssertionError('Expired/old lease acknowledged')
 for _ in range(2):sql('A','select bovi.consumir_muerte(%s,%s,%s,%s)',(E,S['B'],event,Jsonb(claim['payload'])),'bovi_worker')
 sql('B','select bovi.confirmar_entrega(%s,%s)',(event,newworker),'bovi_worker');assert sql('A','select count(*) from bovi.mensaje_inbox where event_id=%s',(event,))==1;results['expired_lease_reclaimed_old_ack_denied_inbox_dedup']=True
 stop('b')
 try:results['B_down_HTTP']={'A':assert_http('/sedes/'+S['A']+'/operaciones',200),'B':assert_http('/sedes/'+S['B']+'/operaciones',503)}
 finally:resume('b')
 wait(lambda:request('/sedes/'+S['B']+'/operaciones')[0]==200)
 with conn('A',auto=True) as c:quotes=c.execute('select bovi.leer_tarifas_proveedor(%s,%s,%s,%s)',(E,S['B'],U,Jsonb({}))).fetchone()[0]
 with conn('B') as c:token=c.execute('select bovi.capturar_tarifas_proveedor(%s,%s,%s,%s)',(E,S['B'],U,Jsonb(quotes))).fetchone()[0]['elementos'][0]['snapshot_id'];command(c,'B','aceptar_tarifa',{'snapshot_id':token})
 stop('prov')
 try:
  results['provider_down_HTTP']=assert_http('/sedes/'+S['B']+'/integraciones/proveedor/tarifas',503)
  with conn('B') as c:gasto=command(c,'B','registrar_gasto',{'operacion_id':buy,'snapshot_id':token,'importe':quotes['elementos'][0]['precio'],'concepto':'DEMO acceptedoffline','clasificacion':'CAPITALIZABLE',**fin});assert gasto['snapshot_fuente_externa']['precio']==quotes['elementos'][0]['precio'];results['accepted_snapshot_gasto_survives_provider_down']=True
 finally:resume('prov')
 wait(lambda:request('/sedes/'+S['A']+'/integraciones/proveedor/tarifas')[0]==200)
 results.update({'database':DB,'command_calls':calls,'seconds':round(time.monotonic()-start,3),'tests':['TEST-22','TEST-24','TEST-25'],'labels_verified':'bovicierre-academic pg-a/pg-b/pg-prov','financial_source_transactions_closed_except_explicit_B_preauthorized':True,'main_business_facts_not_written_by_SQL_harness':True})
 Path('db/tests/outages-result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2,default=str)+'\n');print('PASS '+json.dumps(results,default=str),flush=True)
finally:
 for node in list(stopped):resume(node)
