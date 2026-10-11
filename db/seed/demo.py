#!/usr/bin/env python3
"""Semilla pequeña repetible por comandos y claves permanentes; no borra ni inserta hechos financieros."""
import hashlib,json,os,subprocess,uuid,calendar
if os.environ.get('BOVI_ENV','').strip().lower()=='production' or 'production' in {profile.strip().lower() for profile in os.environ.get('SPRING_PROFILES_ACTIVE','').split(',')}:
 raise SystemExit('Entorno production: bootstrap/semilla DEMO bloqueados antes de cualquier operación.')
from pathlib import Path
from datetime import date
import psycopg
from psycopg.types.json import Jsonb
ROOT=Path(__file__).resolve().parents[2]
SECRETS=Path(os.environ.get('BOVI_SECRET_DIR',Path.home()/'.local/share/bovicierre-academic/secrets'))
fixture=json.loads((ROOT/'data/synthetic/demo-scenarios.json').read_text());dataset=fixture['dataset'];day=date.fromisoformat(fixture['fecha'])
assert dataset.startswith('DEMO-')
label=subprocess.run(['docker','inspect','--format','{{index .Config.Labels "com.docker.compose.project"}}','bovicierre-academic-pg-a-1'],capture_output=True,text=True,check=True).stdout.strip()
if label!='bovicierre-academic':raise SystemExit('Proyecto académico exacto requerido; semilla bloqueada')
e='11111111-1111-4111-8111-111111111111';s='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';actor='99999999-9999-4999-8999-999999999999'
with psycopg.connect(host='127.0.0.1',port=19999,dbname='bovicierre',user='bovi_app_a',password=(SECRETS/'app_a_password').read_text().strip()) as connection:
 c=connection.cursor()
 c.execute('select razon_social from bovi.empresa where id=%s',(e,));company=c.fetchone()
 if not company or not company[0].startswith('DEMO '):raise SystemExit('Empresa DEMO exacta requerida')
 def query(sql,args=()):
  c.execute(sql,args);row=c.fetchone();return row[0] if row else None
 def money(value):return {'importe':value,'moneda':'MXN'}
 def command(name,step,body):
  digest=hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()
  c.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',(e,s,actor,dataset+'-'+step,digest,uuid.uuid4(),name,Jsonb(body)));return c.fetchone()[0]
 period=query("select id::text from bovi.periodo_cierre where empresa_id=%s and sucursal_id=%s and estado='ABIERTO' and %s between desde and hasta limit 1",(e,s,day))
 if not period:period=command('crear_periodo','periodo',{'desde':day.replace(day=1).isoformat(),'hasta':day.replace(day=calendar.monthrange(day.year,day.month)[1]).isoformat()})['id']
 financial={'periodo_id':period,'fecha_reconocimiento':day.isoformat()}
 party=command('crear_contraparte','parte',{'nombre':dataset+' contraparte'})['id']
 animals=[command('registrar_animal','animal-'+str(i),{'sexo':'M','identificaciones':[{'sistema':'INTERNO','codigo':dataset+' '+str(i)}]})['id'] for i in range(fixture['animales'])]
 purchase=command('crear_operacion','compra',{'tipo':'COMPRA','parte_id':party,'fecha_operacion':day.isoformat(),'lotes':[{'animales':animals,'unidad_precio':'CABEZA','precio_unitario':fixture['precio_compra_por_cabeza']}]})['id']
 command('confirmar_operacion','confirmar-compra',{'operacion_id':purchase,'version_lock':0,**financial})
 expense=command('registrar_gasto','gasto',{'operacion_id':purchase,'clasificacion':'CAPITALIZABLE','concepto':dataset+' transporte sintético','importe':money(fixture['gasto_capitalizable']),'fecha_economica':day.isoformat(),**financial})['id'];command('repartir_gasto','reparto',{'gasto_id':expense,'metodo':'POR_CABEZA',**financial})
 positions=[str(p) for p in query('select array_agg(id order by id) from bovi.posicion_inventario where empresa_id=%s and sucursal_id=%s and compra_operacion_id=%s',(e,s,purchase))]
 sale=command('crear_operacion','venta',{'tipo':'VENTA','parte_id':party,'fecha_operacion':day.isoformat(),'lotes':[{'posiciones':positions[:fixture['animales_venta']],'unidad_precio':'CABEZA','precio_unitario':fixture['precio_venta_por_cabeza']}]})['id'];command('reservar_venta','reserva',{'operacion_id':sale})
 liq=command('confirmar_operacion','confirmar-venta',{'operacion_id':sale,'version_lock':0,**financial})
 payment=command('registrar_pago','cobro',{'parte_id':party,'tipo':'COBRO','importe':money(fixture['cobro']),'metodo':'EFECTIVO','recibido_el':day.isoformat()})['id'];command('validar_pago','validar-cobro',{'pago_id':payment,**financial});command('aplicar_pago','aplicar-cobro',{'pago_id':payment,'liquidacion_id':liq['id'],'importe':money(fixture['aplicacion']),**financial})
 actual={'inventario':str(query('select sum(delta_inventario) from bovi.asiento_valoracion av join bovi.posicion_inventario p on (p.empresa_id,p.sucursal_id,p.id)=(av.empresa_id,av.sucursal_id,av.posicion_id) where p.compra_operacion_id=%s',(purchase,))),'costo_venta':str(query('select costo_vendido from bovi.v_margen_operacion where operacion_id=%s',(sale,))),'margen':str(query('select venta_neta-costo_vendido-gastos_directos from bovi.v_margen_operacion where operacion_id=%s',(sale,))),'saldo_venta':str(query('select saldo from bovi.v_saldo_liquidacion where id=%s',(liq['id'],))),'anticipo':str(query('select disponible from bovi.v_disponible_pago where id=%s',(payment,)))}
 from decimal import Decimal
 if any(Decimal(actual[k])!=Decimal(v) for k,v in fixture['esperados'].items()):raise RuntimeError('Datos DEMO cambiaron; no se sobreescribe ni corrige automáticamente')
 print(json.dumps({'dataset':dataset,'compra_id':purchase,'venta_id':sale,'pago_id':payment,'sql_verificado':actual},indent=2))
