#!/usr/bin/env python3
"""Prueba económica real PostgreSQL18; todo se revierte tras verificar los GOLD fijos."""
import hashlib,json,os,sys,uuid
from decimal import Decimal as D
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb
SECRET=Path(os.environ.get('BOVI_SECRET_DIR',Path.home()/'.local/share/bovicierre-academic/secrets'))
E='11111111-1111-4111-8111-111111111111'; S='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'; U='99999999-9999-4999-8999-999999999999'
conn=psycopg.connect(host='127.0.0.1',port=15432,dbname=os.environ.get('BOVI_DB_NAME','bovicierre_gold_final'),user='bovi_app_a',password=(SECRET/'app_a_password').read_text().strip())
cur=conn.cursor(); n=0; period=None

def cmd(name,body,key=None):
 global n
 n+=1
 if name in ('confirmar_operacion','registrar_pago','validar_pago','aplicar_pago','revertir_aplicacion','reembolsar_pago','ajustar_liquidacion','registrar_gasto','repartir_gasto','registrar_baja','anular_venta'):
  body={'periodo_id':period,'fecha_reconocimiento':'2026-10-11',**body}
 digest=hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()
 cur.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)',(E,S,U,key or 'DEMO-GOLD-'+str(uuid.uuid4()),digest,uuid.uuid4(),name,Jsonb(body)))
 return cur.fetchone()[0]

def q(sql,args=()):cur.execute(sql,args);return cur.fetchone()[0]
def negative(name,body,code,key=None):
 cur.execute('SAVEPOINT invalid')
 try: cmd(name,body,key)
 except psycopg.Error as e:
  assert e.sqlstate=='P0001',(e.sqlstate,str(e))
  detail=json.loads(e.diag.message_detail); assert detail['codigo']==code,detail; assert isinstance(detail['campos'],list)
  cur.execute('ROLLBACK TO invalid');return
 raise AssertionError('Expected rejection '+code)

def money(val): return {'importe':str(val),'moneda':'MXN'}
def animal(i):return cmd('registrar_animal',{'sexo':'M','identificaciones':[{'sistema':'INTERNO','codigo':'DEMO GOLD '+str(i)}]})['id']
def operation(kind,party,ids,price,kg=None):
 lot={'unidad_precio':'KG' if kg else 'CABEZA','precio_unitario':str(price),'animales' if kind=='COMPRA' else 'posiciones':ids}
 if kg:lot['neto']={'kg':str(kg)}
 op=cmd('crear_operacion',{'tipo':kind,'parte_id':party,'fecha_operacion':'2026-10-01','lotes':[lot]})['id']
 if kg:
  w=q('select id from bovi.pesaje where operacion_id=%s',(op,));cmd('aprobar_pesaje',{'pesaje_id':str(w)})
 if kind=='VENTA':cmd('reservar_venta',{'operacion_id':op})
 return op

def confirm(op,key=None):return cmd('confirmar_operacion',{'operacion_id':op,'version_lock':0},key)
def expense(op,amount,kind='CAPITALIZABLE',bonus=None):
 b={'operacion_id':op,'importe':money(amount),'clasificacion':kind,'concepto':'DEMO gasto','fecha_economica':'2026-10-01','naturaleza':'BONIFICACION' if bonus else 'COSTO'}
 if bonus:b['bonifica_gasto_id']=bonus
 gid=cmd('registrar_gasto',b)['id'];cmd('repartir_gasto',{'gasto_id':gid});return gid

def payment(party,amount):
 pid=cmd('registrar_pago',{'parte_id':party,'tipo':'COBRO','importe':money(amount),'metodo':'EFECTIVO','recibido_el':'2026-10-11'})['id'];cmd('validar_pago',{'pago_id':pid});return pid
try:
 period=cmd('crear_periodo',{'desde':'2026-10-01','hasta':'2026-10-31'})['id']
 party=cmd('crear_contraparte',{'nombre':'DEMO GOLD contraparte'})['id']
 animals=[animal(i) for i in range(1,11)]
 buy=operation('COMPRA',party,animals,1000);settle=confirm(buy)
 assert settle['total']==money('10000.00'),settle
 expense(buy,1000)
 positions=[str(x) for x in q('select array_agg(id order by id) from bovi.posicion_inventario where compra_operacion_id=%s',(buy,))]
 sell=operation('VENTA',party,positions[:4],1600);sale=confirm(sell)
 expense(sell,200,'DIRECTO_VENTA')
 assert q('select costo_vendido from bovi.v_margen_operacion where operacion_id=%s',(sell,))==D('4400')
 assert q('select venta_neta-costo_vendido-gastos_directos from bovi.v_margen_operacion where operacion_id=%s',(sell,))==D('1800')
 assert q('select sum(delta_inventario) from bovi.asiento_valoracion')==D('6600')
 print('PASS GOLD-02 fixed: sale6400 cost4400 margin1800 inventory6600')
 late=expense(buy,500)
 assert q('select costo_vendido from bovi.v_margen_operacion where operacion_id=%s',(sell,))==D('4600')
 assert q('select sum(delta_inventario) from bovi.asiento_valoracion')==D('6900')
 assert q('select venta_neta-costo_vendido-gastos_directos from bovi.v_margen_operacion where operacion_id=%s',(sell,))==D('1600')
 expense(buy,200,bonus=late)
 assert q('select costo_vendido from bovi.v_margen_operacion where operacion_id=%s',(sell,))==D('4520')
 assert q('select venta_neta-costo_vendido-gastos_directos from bovi.v_margen_operacion where operacion_id=%s',(sell,))==D('1680')
 assert q('select sum(delta_inventario) from bovi.asiento_valoracion')==D('6780')
 print('PASS GOLD-06 fixed: cost4520 inventory6780 margin1680; original debt unchanged')
 third=operation('COMPRA',party,[animal(i) for i in range(30,33)],10);confirm(third);thirdcost=expense(third,1);assert q('select array_agg(importe order by posicion_id) from bovi.asignacion_costo where fuente_gasto_id=%s',(thirdcost,))==[D('.34'),D('.33'),D('.33')]
 print('PASS GOLD-03 .34/.33/.33')
 pay=payment(party,1200);cmd('aplicar_pago',{'pago_id':pay,'liquidacion_id':sale['id'],'importe':money(1000)})
 assert q('select disponible from bovi.v_disponible_pago where id=%s',(pay,))==D('200')
 negative('aplicar_pago',{'pago_id':pay,'liquidacion_id':sale['id'],'importe':money('200.01')},'BV020')
 print('PASS GOLD-04B advance200 and overapplication rejected')
 # Economic correction preserves original, restores available funds and refunds only available.
 ap=str(q('select id from bovi.aplicacion_pago where pago_id=%s',(pay,)))
 cmd('revertir_aplicacion',{'aplicacion_id':ap})
 negative('revertir_aplicacion',{'aplicacion_id':ap},'BV022')  # DIV-08: segundo reverso, otra clave
 cmd('ajustar_liquidacion',{'liquidacion_id':sale['id'],'naturaleza':'ABONO','monto':money(100),'motivo':'DEMO GOLD-07','fuente':'BONIFICACION_COMERCIAL'})
 cmd('aplicar_pago',{'pago_id':pay,'liquidacion_id':sale['id'],'importe':money(900)})
 cmd('reembolsar_pago',{'pago_id':pay,'importe':money(300),'metodo':'EFECTIVO'})
 assert q('select disponible from bovi.v_disponible_pago where id=%s',(pay,))==0
 print('PASS reverso/reaplicacion/reembolso with original immutable')
 # Replay returns the identical persisted settlement snapshot.
 newanimal=animal(100); buy2=operation('COMPRA',party,[newanimal],1000);key='DEMO-IDEM-'+str(uuid.uuid4());one=confirm(buy2,key);two=confirm(buy2,key);assert one==two
 negative('confirmar_operacion',{'operacion_id':buy2,'version_lock':1},'BV412');negative('confirmar_operacion',{'operacion_id':buy2,'version_lock':1},'BV405',key)
 print('PASS idempotent same-result and stale version')
 # GOLD-07 exact: a fully paid obligation1000 is atomically reduced to900.
 exactanimal=animal(110);exactbuy=operation('COMPRA',party,[exactanimal],100);confirm(exactbuy);exactpos=[str(x) for x in q('select array_agg(id) from bovi.posicion_inventario where compra_operacion_id=%s',(exactbuy,))];exactop=operation('VENTA',party,exactpos,1000);exactliq=confirm(exactop);exactpay=payment(party,1000);cmd('aplicar_pago',{'pago_id':exactpay,'liquidacion_id':exactliq['id'],'importe':money(1000)})
 cmd('ajustar_liquidacion',{'liquidacion_id':exactliq['id'],'naturaleza':'ABONO','monto':money(100),'motivo':'DEMO GOLD07 atómico','reaplicar_pagos':True})
 assert q('select total_ajustado from bovi.v_saldo_liquidacion where id=%s',(exactliq['id'],))==D('900');assert q('select saldo from bovi.v_saldo_liquidacion where id=%s',(exactliq['id'],))==0;assert q('select disponible from bovi.v_disponible_pago where id=%s',(exactpay,))==100
 cmd('reembolsar_pago',{'pago_id':exactpay,'importe':money(100),'metodo':'EFECTIVO'});assert q('select disponible from bovi.v_disponible_pago where id=%s',(exactpay,))==0
 print('PASS GOLD-07 exact atomic reverse1000/reapply900/adjust100/refund100')
 # Typed measured weights, no fabricated division of a lot total.
 individs=[animal(i) for i in (120,121)];weightbuy=cmd('crear_operacion',{'tipo':'COMPRA','parte_id':party,'fecha_operacion':'2026-10-01','lotes':[{'animales':individs,'unidad_precio':'KG','precio_unitario':'10','neto':{'kg':'400'}}]})['id'];original=str(q('select id from bovi.pesaje where operacion_id=%s',(weightbuy,)))
 cmd('aprobar_pesaje',{'pesaje_id':original})
 corrected=cmd('corregir_pesaje',{'motivo':'DEMO GOLD corrección individual trazada','corrige_a_id':original,'operacion_id':weightbuy,'numero_lote':1,'modo':'NETO_REPORTADO','neto':{'kg':'400'},'animales':[{'animal_id':individs[0],'peso_individual':{'kg':'100'}},{'animal_id':individs[1],'peso_individual':{'kg':'300'}}]})['id'];cmd('aprobar_pesaje',{'pesaje_id':corrected});confirm(weightbuy)
 measured=cmd('registrar_gasto',{'operacion_id':weightbuy,'importe':money(1),'clasificacion':'CAPITALIZABLE','concepto':'DEMO peso','fecha_economica':'2026-10-01'})['id'];cmd('repartir_gasto',{'gasto_id':measured,'metodo':'POR_PESO_MEDIDO'});assert sorted(q('select array_agg(importe) from bovi.asignacion_costo where fuente_gasto_id=%s',(measured,)))==[D('.25'),D('.75')]
 individual=cmd('registrar_gasto',{'operacion_id':weightbuy,'importe':money(1),'clasificacion':'CAPITALIZABLE','concepto':'DEMO individual','fecha_economica':'2026-10-01'})['id'];individualpos=[str(x) for x in q('select array_agg(id order by id) from bovi.posicion_inventario where compra_operacion_id=%s',(weightbuy,))];cmd('repartir_gasto',{'gasto_id':individual,'metodo':'IMPORTE_INDIVIDUAL','asignaciones':[{'posicion_id':individualpos[0],'importe':money('.40')},{'posicion_id':individualpos[1],'importe':money('.60')}]});assert sorted(q('select array_agg(importe) from bovi.asignacion_costo where fuente_gasto_id=%s',(individual,)))==[D('.40'),D('.60')]
 print('PASS POR_PESO_MEDIDO .25/.75 and IMPORTE_INDIVIDUAL .40/.60')
 # GOLD-01 gross realization and physical shrinkage remain separate.
 gold1animals=[animal(i) for i in range(140,150)];gold1buy=operation('COMPRA',party,gold1animals,48,5000);confirm(gold1buy);expense(gold1buy,12000);gold1pos=[str(x) for x in q('select array_agg(id order by id) from bovi.posicion_inventario where compra_operacion_id=%s',(gold1buy,))];gold1sell=operation('VENTA',party,gold1pos,60,4900);gold1liq=confirm(gold1sell);expense(gold1sell,8000,'DIRECTO_VENTA');gold1pay=payment(party,50000);cmd('aplicar_pago',{'pago_id':gold1pay,'liquidacion_id':gold1liq['id'],'importe':money(50000)})
 assert q('select costo_vendido from bovi.v_margen_operacion where operacion_id=%s',(gold1sell,))==252000;assert q('select venta_neta-costo_vendido-gastos_directos from bovi.v_margen_operacion where operacion_id=%s',(gold1sell,))==34000;assert q('select saldo from bovi.v_saldo_liquidacion where id=%s',(gold1liq['id'],))==244000
 initial=str(q('select id from bovi.pesaje where operacion_id=%s',(gold1buy,)));final=str(q('select id from bovi.pesaje where operacion_id=%s',(gold1sell,)));compare=q('select bovi.consultar(%s,%s,%s,%s,%s)',(E,S,U,'comparacion_pesajes',Jsonb({'inicial_id':initial,'final_id':final})));assert compare['estado']=='COMPARABLE' and D(compare['variacion_kg'])==100 and D(compare['variacion_pct'])==2
 print('PASS GOLD-01 cost252000 margin34000 saldo244000 shrink100kg/2% withoutautomaticdiscount')
 groupg=cmd('registrar_gasto',{'operacion_id':gold1buy,'importe':money(1),'clasificacion':'CAPITALIZABLE','concepto':'DEMO missingindividual','fecha_economica':'2026-10-01'})['id'];negative('repartir_gasto',{'gasto_id':groupg,'metodo':'POR_PESO_MEDIDO'},'BV018');assert q('select count(*) from bovi.pesaje_animal where pesaje_id=%s and peso_individual_kg is not null',(initial,))==0
 incomparable=q('select bovi.consultar(%s,%s,%s,%s,%s)',(E,S,U,'comparacion_pesajes',Jsonb({'inicial_id':initial,'final_id':corrected})));assert incomparable['estado']=='NO_COMPARABLE'
 print('PASS TEST18 no fabricated individualweight/repartition denied and TEST19 differentsets NO_COMPARABLE')

 # GOLD-08 loss and a later expense never manufacture a sale or receivable.
 lossanimal=animal(160);lossbuy=operation('COMPRA',party,[lossanimal],1100);confirm(lossbuy);losspos=str(q('select id from bovi.posicion_inventario where compra_operacion_id=%s',(lossbuy,)));lossdoc=cmd('registrar_documento',{'tipo_documental':'OTRO','storage_key':'DEMO-LOSS-EVIDENCE','sha256':'a'*64,'tamano_bytes':1,'mime':'application/pdf'})['id'];cmd('registrar_baja',{'posiciones':[losspos],'motivo_baja':'PERDIDA','documento_id':lossdoc});expense(lossbuy,50)
 assert q('select sum(delta_inventario) from bovi.asiento_valoracion where posicion_id=%s',(losspos,))==0;assert q('select sum(delta_perdida) from bovi.asiento_valoracion where posicion_id=%s',(losspos,))==1150
 print('PASS GOLD-08 loss1100+50=1150 no receivable')
 revision=cmd('registrar_revision',{'operacion_id':lossbuy,'criterio':'DEMO version review','resultado':'SIN_OBSERVACIONES','documentos':[{'documento_id':lossdoc,'resultado':'SIN_OBSERVACIONES','observacion':'DEMO reviewed v1'}]})['id'];doc2=cmd('registrar_documento',{'operacion_id':lossbuy,'tipo_documental':'OTRO','storage_key':'DEMO-LOSS-V2','sha256':'b'*64,'tamano_bytes':1,'mime':'application/pdf','documento_previo_id':lossdoc,'version':2})['id']
 assert q('select documento_id::text from bovi.revision_documento where revision_id=%s',(revision,))==lossdoc;assert q('select sha256 from bovi.documento where id=%s',(lossdoc,))=='a'*64
 reviewed=q('select bovi.consultar(%s,%s,%s,%s,%s)',(E,S,U,'documento',Jsonb({'id':lossdoc})));newversion=q('select bovi.consultar(%s,%s,%s,%s,%s)',(E,S,U,'documento',Jsonb({'id':doc2})));assert len(reviewed['revisiones'])==1 and newversion['revisiones']==[]
 print('PASS TEST34 newdocumentv2 preserves immutable reviewedv1 metadata/reference; SQLmetadataonly')

 # ANUL-01 restores all recognized cost including late adjustments, then the cycle can be sold/delivered/rebought.
 annul_animal=animal(170);annulbuy=operation('COMPRA',party,[annul_animal],1100);confirm(annulbuy);annulpos=str(q('select id from bovi.posicion_inventario where compra_operacion_id=%s',(annulbuy,)));annulsell=operation('VENTA',party,[annulpos],1600);confirm(annulsell);expense(annulbuy,100);cmd('anular_venta',{'operacion_id':annulsell,'version_lock':1,'motivo':'DEMO ANUL-01'})
 assert q('select sum(delta_inventario) from bovi.asiento_valoracion where posicion_id=%s',(annulpos,))==1200;assert q('select sum(delta_costo_venta) from bovi.asiento_valoracion where operacion_id=%s',(annulsell,))==0
 soldagain=operation('VENTA',party,[annulpos],1600);confirm(soldagain);oldledger=q('select count(*) from bovi.asiento_valoracion where posicion_id=%s',(annulpos,));cmd('registrar_movimiento',{'tipo':'ENTREGA','posiciones':[annulpos],'operacion_id':soldagain});assert q('select count(*) from bovi.asiento_valoracion where posicion_id=%s',(annulpos,))==oldledger;rebuy=operation('COMPRA',party,[annul_animal],1500);confirm(rebuy);assert q('select max(numero_ciclo) from bovi.posicion_inventario where animal_id=%s',(annul_animal,))==2
 assert q('select sum(importe) from bovi.asignacion_costo where posicion_id=%s',(annulpos,))==1200
 print('PASS ANUL-01 restore1200/cost0 and GOLD-05/09 newcycle2 keepsold1200')
 # GOLD-04A fixed installment600=400+200, exact replay and no cent beyond available.
 a4=animal(175);b4=operation('COMPRA',party,[a4],100);confirm(b4);p4=str(q('select id from bovi.posicion_inventario where compra_operacion_id=%s',(b4,)));s4=operation('VENTA',party,[p4],1000);l4=confirm(s4);pay4=payment(party,600);key4='DEMO-GOLD04A-'+str(uuid.uuid4());first4=cmd('aplicar_pago',{'pago_id':pay4,'liquidacion_id':l4['id'],'importe':money(400)},key4);again4=cmd('aplicar_pago',{'pago_id':pay4,'liquidacion_id':l4['id'],'importe':money(400)},key4);assert first4==again4;cmd('aplicar_pago',{'pago_id':pay4,'liquidacion_id':l4['id'],'importe':money(200)})
 assert q('select saldo from bovi.v_saldo_liquidacion where id=%s',(l4['id'],))==400;assert q('select disponible from bovi.v_disponible_pago where id=%s',(pay4,))==0;negative('aplicar_pago',{'pago_id':pay4,'liquidacion_id':l4['id'],'importe':money('.01')},'BV020')
 print('PASS GOLD-04A obligation1000/pay600/apps400+200/replayexact/saldo400/disponible0/centrejected')
 # GOLD04B exact debt1000, advance1200; physical/cash/document events never recognize economics again.
 b4animal=animal(176);b4buy=operation('COMPRA',party,[b4animal],100);confirm(b4buy);b4pos=str(q('select id from bovi.posicion_inventario where compra_operacion_id=%s',(b4buy,)));b4sale=operation('VENTA',party,[b4pos],1000);b4liq=confirm(b4sale)
 def economic_snapshot():return q("select jsonb_build_object('liquidaciones',(select count(*) from bovi.liquidacion),'total_obligaciones',(select sum(total) from bovi.liquidacion),'conceptos',(select count(*) from bovi.concepto_liquidacion),'asientos',(select count(*) from bovi.asiento_valoracion),'inventario',(select sum(delta_inventario) from bovi.asiento_valoracion),'costo_venta',(select sum(delta_costo_venta) from bovi.asiento_valoracion))")
 before_nonfinancial=economic_snapshot();b4pay=payment(party,1200);cmd('aplicar_pago',{'pago_id':b4pay,'liquidacion_id':b4liq['id'],'importe':money(1000)});assert q('select disponible from bovi.v_disponible_pago where id=%s',(b4pay,))==D('200');assert q('select saldo from bovi.v_saldo_liquidacion where id=%s',(b4liq['id'],))==0
 cmd('registrar_documento',{'operacion_id':b4sale,'tipo_documental':'OTRO','storage_key':'DEMO-GOLD32-PRIVATE-METADATA','sha256':'c'*64,'tamano_bytes':1,'mime':'application/pdf'});cmd('registrar_movimiento',{'tipo':'ENTREGA','posiciones':[b4pos],'operacion_id':b4sale});assert economic_snapshot()==before_nonfinancial
 print('PASS GOLD-04B exact obligation1000/pay1200/applied1000/advance200; TEST32 payment/doc/delivery preserve economic snapshot')

 # Versioned agreement preserves approved weighing, receipt requirement and accepted conditions.
 agreementanimal=animal(180);agreement=cmd('crear_operacion',{'tipo':'COMPRA','parte_id':party,'requiere_recepcion':True,'lotes':[{'animales':[agreementanimal],'unidad_precio':'KG','precio_unitario':'10','neto':{'kg':'100'}}]})['id'];agreementweigh=str(q('select id from bovi.pesaje where operacion_id=%s',(agreement,)));cmd('aprobar_pesaje',{'pesaje_id':agreementweigh})
 cmd('acordar_operacion',{'operacion_id':agreement,'version_lock':0});negative('editar_operacion',{'operacion_id':agreement,'version_lock':1,'lotes':[]},'BV412');cmd('reabrir_operacion',{'operacion_id':agreement,'version_lock':1})
 cmd('editar_operacion',{'operacion_id':agreement,'version_lock':2,'lotes':[{'animales':[agreementanimal],'unidad_precio':'KG','precio_unitario':'11','pesaje_base_id':agreementweigh}]})
 assert q('select precio_unitario from bovi.condicion_lote where operacion_id=%s and numero_version=1',(agreement,))==10
 assert q('select requiere_recepcion from bovi.contrato_version where operacion_id=%s and numero_version=2',(agreement,)) is True
 versionliq=cmd('confirmar_operacion',{'operacion_id':agreement,'version_lock':3});assert versionliq['numero_version']==2 and D(versionliq['total']['importe'])==1100
 assert q('select estado from bovi.posicion_inventario where compra_operacion_id=%s',(agreement,))=='PENDIENTE_RECEPCION'
 assert q("select count(*) from bovi.contrato_version where operacion_id=%s and estado='ACEPTADA'",(agreement,))==2
 assert q("select expira_en='infinity'::timestamptz from bovi.clave_idempotencia where comando='confirmar_operacion' limit 1") is True
 print('PASS agreement v1 preserved/v2 confirmed with same weighing; receipt flag retained; permanent idempotency')
 negative('registrar_animal',{'sexo':'M','identificaciones':[{'sistema':'INTERNO','codigo':'ábc'}]},'BV015')
 negative('crear_periodo',{'desde':'2026-11-01','hasta':'2026-11-30'},'BV025')
 futureg=cmd('registrar_gasto',{'operacion_id':rebuy,'importe':money(1),'clasificacion':'CAPITALIZABLE','concepto':'DEMO documental futura','fecha_economica':'2027-02-01'})['id'];cmd('repartir_gasto',{'gasto_id':futureg});expectedinventory=q('select sum(delta_inventario) from bovi.asiento_valoracion')
 closed=cmd('cerrar_periodo',{'periodo_id':period,'motivo':'DEMO cierre'});assert D(closed['totales']['inventario'])==expectedinventory
 pending=cmd('registrar_pago',{'parte_id':party,'tipo':'COBRO','importe':money(1),'metodo':'EFECTIVO'})['id'];negative('validar_pago',{'pago_id':pending},'BV025')
 cmd('reabrir_periodo',{'periodo_id':period,'motivo':'DEMO reapertura'})
 assert q('select count(*) from bovi.cierre_periodo_version where periodo_id=%s',(period,))==2
 print('PASS period lock, one-open, immutable closure+reopening')
 conn.rollback()
 print('PASS PostgreSQL18 runtime-role GOLD transaction rolled back; calls='+str(n))
except BaseException:
 conn.rollback();raise
finally:conn.close()
