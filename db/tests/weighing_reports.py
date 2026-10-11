#!/usr/bin/env python3
"""V12 QA: tickets exactos, motivos e idempotencia; informes y cierre histórico sin tocar main."""
import calendar,hashlib,json,time,uuid
from pathlib import Path
from datetime import date,timedelta
import psycopg
from psycopg.types.json import Jsonb
DB='bovicierre_release_replay';E='11111111-1111-4111-8111-111111111111';S='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';U='99999999-9999-4999-8999-999999999999';calls=0;checks=[];start=time.monotonic()
secret=Path.home()/'.local/share/bovicierre-academic/secrets'
def conn(db=DB):return psycopg.connect(host='127.0.0.1',port=15432,dbname=db,user='bovi_app_a',password=(secret/'app_a_password').read_text().strip())
def command(c,name,body,key=None):
 global calls
 calls+=1
 return c.execute('SELECT bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',(E,S,U,key or 'DEMO-V12-'+str(uuid.uuid4()),hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest(),uuid.uuid4(),name,Jsonb(body))).fetchone()[0]
def query(c,resource,body):return c.execute('SELECT bovi.consultar(%s,%s,%s,%s,%s)',(E,S,U,resource,Jsonb(body))).fetchone()[0]
def reject(c,name,body,code,key=None):
 c.execute('SAVEPOINT invalid');before=c.execute('SELECT count(*) FROM bovi.auditoria_evento').fetchone()[0]
 try:command(c,name,body,key)
 except psycopg.Error as ex:
  assert ex.sqlstate=='P0001' and json.loads(ex.diag.message_detail)['codigo']==code
  c.execute('ROLLBACK TO invalid')
 else:raise AssertionError('Comando inválido aceptado: '+name)
 assert c.execute('SELECT count(*) FROM bovi.auditoria_evento').fetchone()[0]==before
 c.execute('RELEASE invalid')
def money(amount):return {'importe':str(amount),'moneda':'MXN'}
def animal(c):return command(c,'registrar_animal',{'sexo':'M','identificaciones':[{'sistema':'INTERNO','codigo':'DEMO V12 '+uuid.uuid4().hex[:24]}]})['id']
def review(c,operation):return command(c,'registrar_revision',{'operacion_id':operation,'criterio':'DEMO V12 revisión sintética','resultado':'SIN_OBSERVACIONES','documentos':[]})
def cycle(c,party,fin,price=100,saleprice=150,direct=5):
 aid=animal(c);buy=command(c,'crear_operacion',{'tipo':'COMPRA','parte_id':party,'lotes':[{'animales':[aid],'unidad_precio':'CABEZA','precio_unitario':str(price)}]})['id'];command(c,'confirmar_operacion',{'operacion_id':buy,'version_lock':0,**fin});review(c,buy)
 pos=str(c.execute('SELECT id FROM bovi.posicion_inventario WHERE compra_operacion_id=%s',(buy,)).fetchone()[0]);sale=command(c,'crear_operacion',{'tipo':'VENTA','parte_id':party,'lotes':[{'posiciones':[pos],'unidad_precio':'CABEZA','precio_unitario':str(saleprice)}]})['id'];command(c,'reservar_venta',{'operacion_id':sale});liq=command(c,'confirmar_operacion',{'operacion_id':sale,'version_lock':0,**fin})['id'];review(c,sale)
 gasto=command(c,'registrar_gasto',{'operacion_id':sale,'clasificacion':'DIRECTO_VENTA','concepto':'DEMO V12','importe':money(direct),**fin})['id'];command(c,'repartir_gasto',{'gasto_id':gasto,'metodo':'POR_CABEZA',**fin});return buy,sale,liq
with conn() as c:
 assert c.execute('SELECT current_database()').fetchone()[0]==DB
 assert c.execute('SHOW server_version_num').fetchone()[0].startswith('18')
 name='DEMO-V12-'+uuid.uuid4().hex;party=command(c,'crear_contraparte',{'nombre':name})['id'];a1=animal(c);a2=animal(c)
 op=command(c,'crear_operacion',{'tipo':'COMPRA','parte_id':party,'lotes':[{'animales':[a1,a2],'unidad_precio':'KG','precio_unitario':'10','base_pesaje':'NETO'}]})['id']
 ticket=command(c,'registrar_pesaje',{'operacion_id':op,'numero_lote':1,'modo':'NETO_REPORTADO','neto':{'kg':'300.000'},'animales':[{'animal_id':a1,'peso_individual':{'kg':'100.000'}},{'animal_id':a2}]})['id'];command(c,'aprobar_pesaje',{'pesaje_id':ticket})
 body={'corrige_a_id':ticket,'operacion_id':op,'numero_lote':1,'modo':'NETO_REPORTADO','neto':{'kg':'301.000'},'animales':[{'animal_id':a1,'peso_individual':{'kg':'101.000'}},{'animal_id':a2}],'motivo':'DEMO corrección de lectura'}
 for invalid in ({**body,'animales':[{'animal_id':a1}]},{**body,'animales':body['animales']+[{'animal_id':str(uuid.uuid4())}]},{**body,'motivo':' '},{**body,'numero_lote':2},{**body,'operacion_id':str(uuid.uuid4())}):reject(c,'corregir_pesaje',invalid,'BV015' if invalid['motivo']==' ' else 'BV013')
 assert c.execute('SELECT estado FROM bovi.pesaje WHERE id=%s',(ticket,)).fetchone()[0]=='APROBADO'
 key='DEMO-V12-CORRECTION-'+str(uuid.uuid4());new=command(c,'corregir_pesaje',body,key);assert new['motivo_correccion']==body['motivo'] and new['corrige_a_id']==ticket
 assert command(c,'corregir_pesaje',body,key)==new
 reject(c,'corregir_pesaje',{**body,'motivo':'Otro motivo'},'BV405',key)
 tickets=query(c,'operacion_pesajes',{'id':op})['elementos'];old=next(t for t in tickets if t['id']==ticket);fresh=next(t for t in tickets if t['id']==new['id']);assert old['estado']=='CORREGIDO' and fresh==new
 expected={a1:{'kg':'100.000'},a2:None};assert {x['animal_id']:x['peso_individual'] for x in old['animales']}==expected
 assert {x['animal_id']:x['peso_individual'] for x in fresh['animales']}=={a1:{'kg':'101.000'},a2:None}
 assert query(c,'operacion',{'id':op})['pesajes']==tickets
 assert c.execute("SELECT cambio FROM bovi.auditoria_evento WHERE entidad_id=%s AND comando='corregir_pesaje'",(new['id'],)).fetchone()[0]==new
 assert c.execute('SELECT resultado FROM bovi.clave_idempotencia WHERE clave=%s',(key,)).fetchone()[0]==new
 assert c.execute('SELECT estado FROM bovi.pesaje WHERE id=%s',(ticket,)).fetchone()[0]=='CORREGIDO'
 checks.append('V13 rechaza subset/superset antes mutar original; ticket original inmutable, composición exacta y NULL individual; motivo auditado; primer DTO/replay exacto/conflicto409/contexto rechazado')
 period=c.execute("SELECT id,desde,hasta FROM bovi.periodo_cierre WHERE empresa_id=%s AND sucursal_id=%s AND estado='ABIERTO'",(E,S)).fetchone();assert period
 fin={'periodo_id':str(period[0]),'fecha_reconocimiento':str(period[1])};buy,sale,liq=cycle(c,party,fin)
 c1=query(c,'reportes_cartera',{'q':name,'pagina':1,'tamano':1});c2=query(c,'reportes_cartera',{'q':name,'pagina':2,'tamano':1});assert c1['total']==c2['total']==2 and len(c1['filas'])==len(c2['filas'])==1 and c1['filas'][0]['liquidacion_id']!=c2['filas'][0]['liquidacion_id']
 assert c1['fuente_consulta']=='PROPIETARIO' and c1['antiguedad_replica_segundos']==0 and c1['filas'][0]['dias_vencida'] is None
 assert query(c,'reportes_cartera',{'q':name,'direccion':'POR_COBRAR'})['total']==1
 assert query(c,'reportes_cartera',{'q':name,'vencida':True})['total']==0
 m=query(c,'reportes_margen',{'q':name,'tamano':1});assert [m[x]['importe'] for x in ('venta_neta','costo_vendido','gastos_directos','margen','perdidas')]==['150.00','100.00','5.00','45.00','0.00'];assert m['etiqueta']=='ACTUALIZADO'
 filtered=query(c,'reportes_margen',{'operacion_id':sale});assert filtered['margen']['importe']=='45.00'
 late=command(c,'registrar_gasto',{'operacion_id':buy,'clasificacion':'CAPITALIZABLE','concepto':'DEMO costo tardío','importe':money('10.00'),**fin})['id'];command(c,'repartir_gasto',{'gasto_id':late,'metodo':'POR_CABEZA',**fin});assert query(c,'reportes_margen',{'operacion_id':sale})['margen']['importe']=='35.00'
 checks.append('Cartera wrapper paginado/dirección/vencida; margen total completo y costo tardío filtrado por venta')
 # GOLD06: consulta canónica filtrada, mismos importes fijos de la especificación.
 animals=[animal(c) for _ in range(10)]
 gb=command(c,'crear_operacion',{'tipo':'COMPRA','parte_id':party,'lotes':[{'animales':animals,'unidad_precio':'CABEZA','precio_unitario':'1000'}]})['id'];command(c,'confirmar_operacion',{'operacion_id':gb,'version_lock':0,**fin})
 def expense(operation,amount,kind='CAPITALIZABLE',bonus=None):
  payload={'operacion_id':operation,'clasificacion':kind,'concepto':'DEMO GOLD06 reporte','importe':money(amount),'naturaleza':'BONIFICACION' if bonus else 'COSTO',**fin}
  if bonus:payload['bonifica_gasto_id']=bonus
  gid=command(c,'registrar_gasto',payload)['id'];command(c,'repartir_gasto',{'gasto_id':gid,'metodo':'POR_CABEZA',**fin});return gid
 expense(gb,'1000.00');positions=[str(x[0]) for x in c.execute('SELECT id FROM bovi.posicion_inventario WHERE compra_operacion_id=%s ORDER BY id LIMIT 4',(gb,)).fetchall()]
 gs=command(c,'crear_operacion',{'tipo':'VENTA','parte_id':party,'lotes':[{'posiciones':positions,'unidad_precio':'CABEZA','precio_unitario':'1600'}]})['id'];command(c,'reservar_venta',{'operacion_id':gs});command(c,'confirmar_operacion',{'operacion_id':gs,'version_lock':0,**fin});expense(gs,'200.00','DIRECTO_VENTA');late=expense(gb,'500.00')
 assert query(c,'reportes_margen',{'operacion_id':gs})['margen']['importe']=='1600.00'
 expense(gb,'200.00',bonus=late);assert query(c,'reportes_margen',{'operacion_id':gs})['margen']['importe']=='1680.00'
 checks.append('GOLD06 margen canónico por venta: tardío500→1600 y bonificación200→1680, sin dobleconteo')

 # Cierre actual, siguiente mes exclusivo en esta transacción QA; todo rollback al terminar.
 command(c,'cerrar_periodo',{'periodo_id':str(period[0]),'motivo':'DEMO V12 aislamiento próximo periodo'})
 nextdate=period[2]+timedelta(days=1);last=date(nextdate.year,nextdate.month,calendar.monthrange(nextdate.year,nextdate.month)[1]);np=command(c,'crear_periodo',{'desde':str(nextdate),'hasta':str(last)})['id'];nf={'periodo_id':np,'fecha_reconocimiento':str(nextdate)}
 party2=command(c,'crear_contraparte',{'nombre':name+' cierre'})['id'];buy2,sale2,liq2=cycle(c,party2,nf,200,300,10)
 close=command(c,'cerrar_periodo',{'periodo_id':np,'motivo':'DEMO V12 cierre histórico de margen'})
 closed=query(c,'reportes_margen',{'periodo_id':np});assert closed['etiqueta']=='CERRADO' and closed['margen']['importe']=='90.00' and closed['numero_version_cierre']==close['numero_version']
 after=last+timedelta(days=1);ap=command(c,'crear_periodo',{'desde':str(after),'hasta':str(date(after.year,after.month,calendar.monthrange(after.year,after.month)[1]))})['id'];af={'periodo_id':ap,'fecha_reconocimiento':str(after)}
 late=command(c,'registrar_gasto',{'operacion_id':buy2,'clasificacion':'CAPITALIZABLE','concepto':'DEMO costo posterior','importe':money('20.00'),**af})['id'];command(c,'repartir_gasto',{'gasto_id':late,'metodo':'POR_CABEZA',**af})
 assert query(c,'reportes_margen',{'periodo_id':np})==closed
 assert query(c,'reportes_margen',{'operacion_id':sale2})['margen']['importe']=='70.00'
 assert query(c,'reportes_margen',{'periodo_id':np,'operacion_id':sale2})['etiqueta']=='PROVISIONAL'
 assert c.execute('SELECT totales FROM bovi.cierre_periodo_version WHERE periodo_id=%s AND tipo=\'CIERRE\'',(np,)).fetchone()[0]['reporte_margen']==close['totales']['reporte_margen']
 checks.append('Cierre V12 snapshot margen90 inmutable tras costo20 mes posterior; margen vivo70; filtro sin cierre inventado')
 c.rollback()
# Sólo lectura main: compatibilidad real de cierres históricos existentes.
legacy=[]
with conn('bovicierre') as c:
 for row in c.execute("SELECT p.id FROM bovi.periodo_cierre p JOIN bovi.cierre_periodo_version v ON (v.empresa_id,v.sucursal_id,v.periodo_id)=(p.empresa_id,p.sucursal_id,p.id) WHERE p.empresa_id=%s AND p.sucursal_id=%s AND p.estado='CERRADO' AND v.tipo='CIERRE' AND NOT(v.totales ? 'reporte_margen') LIMIT 1",(E,S)).fetchall():legacy.append(str(row[0]))
result={'estado':'PASS','database':DB,'sql_commands':calls,'seconds':round(time.monotonic()-start,3),'migration':'V13','tests':checks,'rollback_all_QA_facts':True,'legacy_closed_main_readonly_ids':legacy,'legacy_runtime_query_pending_main_V12':bool(legacy)}
Path('db/tests/weighing-reports-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('PASS '+json.dumps(result,ensure_ascii=False))
