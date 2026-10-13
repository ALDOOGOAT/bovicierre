#!/usr/bin/env python3
"""GOLD-ACAD-01/02: escenarios académicos con importes ficticios fijos, independientes de otras semillas.

Rol de aplicación y bovi.cmd_ejecutar reales sobre la base aislada; cada cifra se consulta por los IDs del
escenario (no por totales globales) y todo se revierte al final. Esperados escritos a mano, no calculados
con la función evaluada.
"""
import hashlib, json, os, uuid
from decimal import Decimal as D
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb

SECRET = Path(os.environ.get('BOVI_SECRET_DIR', Path.home() / '.local/share/bovicierre-academic/secrets'))
E = '11111111-1111-4111-8111-111111111111'; S = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'; U = '99999999-9999-4999-8999-999999999999'
conn = psycopg.connect(host='127.0.0.1', port=15432, dbname=os.environ.get('BOVI_DB_NAME', 'bovicierre_gold_final'),
                       user='bovi_app_a', password=(SECRET / 'app_a_password').read_text().strip())
cur = conn.cursor(); period = None; RUN = uuid.uuid4().hex[:8]
ECONOMIC = ('confirmar_operacion', 'registrar_pago', 'validar_pago', 'aplicar_pago', 'registrar_gasto', 'repartir_gasto')


def cmd(name, body):
    if name in ECONOMIC:
        body = {'periodo_id': period, 'fecha_reconocimiento': '2026-10-11', **body}
    digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    cur.execute('select bovi.cmd_ejecutar(%s,%s,%s,%s,%s,%s,%s,%s)', (E, S, U, 'DEMO-ACAD-' + str(uuid.uuid4()), digest, uuid.uuid4(), name, Jsonb(body)))
    return cur.fetchone()[0]


def q(sql, args=()):
    cur.execute(sql, args); return cur.fetchone()[0]


def money(v): return {'importe': str(v), 'moneda': 'MXN'}
def report(op): return q("select bovi.consultar(%s,%s,%s,'reportes_margen',%s)", (E, S, U, Jsonb({'operacion_id': str(op)})))
def saldo(liq): return q('select saldo from bovi.v_saldo_liquidacion where id=%s', (liq,))
def liq_of(op): return str(q('select id from bovi.liquidacion where operacion_id=%s', (op,)))
def animal(tag): return cmd('registrar_animal', {'sexo': 'M', 'identificaciones': [{'sistema': 'INTERNO', 'codigo': f'DEMO-ACAD-{RUN}-{tag}'}]})['id']


def pay(party, kind, amount, liq):
    pid = cmd('registrar_pago', {'parte_id': party, 'tipo': kind, 'importe': money(amount), 'metodo': 'TRANSFERENCIA', 'recibido_el': '2026-10-11'})['id']
    cmd('validar_pago', {'pago_id': pid}); cmd('aplicar_pago', {'pago_id': pid, 'liquidacion_id': liq, 'importe': money(amount)})
    return pid


try:
    period = cmd('crear_periodo', {'desde': '2026-10-01', 'hasta': '2026-10-31'})['id']
    # GOLD-ACAD-01: compra 2×$10,000, transporte $2,000 por cabeza, pago total, venta de 1 a $16,000, cobro $4,000.
    proveedor = cmd('crear_contraparte', {'nombre': f'DEMO ACAD proveedor {RUN}'})['id']
    comprador = cmd('crear_contraparte', {'nombre': f'DEMO ACAD comprador {RUN}'})['id']
    a1, a2 = animal('A1'), animal('A2')
    buy = cmd('crear_operacion', {'tipo': 'COMPRA', 'parte_id': proveedor, 'fecha_operacion': '2026-10-01', 'requiere_recepcion': True,
                                  'lotes': [{'unidad_precio': 'CABEZA', 'precio_unitario': '10000', 'animales': [a1, a2]}]})['id']
    cmd('confirmar_operacion', {'operacion_id': buy, 'version_lock': 0})
    buy_liq = liq_of(buy)
    assert q('select total from bovi.liquidacion where id=%s', (buy_liq,)) == D('20000.00')
    cur.execute('select animal_id,id from bovi.posicion_inventario where compra_operacion_id=%s', (buy,))
    pos = {str(r[0]): str(r[1]) for r in cur.fetchall()}
    assert q("select count(*) from bovi.posicion_inventario where compra_operacion_id=%s and estado='PENDIENTE_RECEPCION'", (buy,)) == 2
    cmd('registrar_movimiento', {'tipo': 'RECEPCION', 'posiciones': list(pos.values()), 'ocurrido_en': '2026-10-02T10:00:00Z'})
    assert q("select count(*) from bovi.posicion_inventario where compra_operacion_id=%s and estado='DISPONIBLE'", (buy,)) == 2
    gasto = cmd('registrar_gasto', {'operacion_id': buy, 'importe': money('2000.00'), 'clasificacion': 'CAPITALIZABLE', 'concepto': 'DEMO transporte',
                                     'fecha_economica': '2026-10-02', 'naturaleza': 'COSTO'})['id']
    cmd('repartir_gasto', {'gasto_id': gasto, 'metodo': 'POR_CABEZA'})
    for p in pos.values():
        assert q('select coalesce(sum(importe),0) from bovi.asignacion_costo where posicion_id=%s', (p,)) == D('11000.00')
    pay(proveedor, 'PAGO', '20000.00', buy_liq)
    sold, kept = pos[a1], pos[a2]
    sale = cmd('crear_operacion', {'tipo': 'VENTA', 'parte_id': comprador, 'fecha_operacion': '2026-10-05',
                                   'lotes': [{'unidad_precio': 'CABEZA', 'precio_unitario': '16000', 'posiciones': [sold]}]})['id']
    cmd('reservar_venta', {'operacion_id': sale})  # vence_en por defecto: ahora + 15 min
    cmd('confirmar_operacion', {'operacion_id': sale, 'version_lock': 0})
    sale_liq = liq_of(sale)
    cmd('registrar_movimiento', {'tipo': 'ENTREGA', 'posiciones': [sold], 'operacion_id': sale, 'ocurrido_en': '2026-10-06T09:00:00Z'})
    pay(comprador, 'COBRO', '4000.00', sale_liq)
    rep = report(sale)
    got = {
        'animales_disponibles': q("select count(*) from bovi.posicion_inventario where compra_operacion_id=%s and estado='DISPONIBLE'", (buy,)),
        'valor_inventario_restante': q('select sum(delta_inventario) from bovi.asiento_valoracion where posicion_id in (%s,%s)', (sold, kept)),
        'venta_reconocida': D(rep['venta_neta']['importe']),
        'costo_vendido': D(rep['costo_vendido']['importe']),
        'margen_venta': D(rep['margen']['importe']),
        'cobro_aplicado': q("select sum(importe) from bovi.aplicacion_pago where liquidacion_id=%s and naturaleza='APLICACION'", (sale_liq,)),
        'saldo_comprador': saldo(sale_liq),
        'saldo_proveedor': saldo(buy_liq),
    }
    expected = {'animales_disponibles': 1, 'valor_inventario_restante': D('11000.00'), 'venta_reconocida': D('16000.00'), 'costo_vendido': D('11000.00'),
                'margen_venta': D('5000.00'), 'cobro_aplicado': D('4000.00'), 'saldo_comprador': D('12000.00'), 'saldo_proveedor': D('0.00')}
    assert got == expected, (got, expected)
    # Entregar y cobrar no duplican venta, deuda ni costo: una sola liquidación por operación.
    assert q('select count(*) from bovi.liquidacion where operacion_id in (%s,%s)', (buy, sale)) == 2
    print('PASS GOLD-ACAD-01', json.dumps({k: str(v) for k, v in got.items()}, ensure_ascii=False))

    # GOLD-ACAD-02: compra por peso, ticket neto 500 kg × $60/kg = $30,000; sin aprobar no confirma.
    k1, k2 = animal('K1'), animal('K2')
    kg = cmd('crear_operacion', {'tipo': 'COMPRA', 'parte_id': proveedor, 'fecha_operacion': '2026-10-07',
                                 'lotes': [{'unidad_precio': 'KG', 'precio_unitario': '60', 'animales': [k1, k2], 'neto': {'kg': '500.000'}}]})['id']
    ticket = str(q('select id from bovi.pesaje where operacion_id=%s', (kg,)))
    assert q('select estado from bovi.pesaje where id=%s', (ticket,)) == 'PROPUESTA'
    assert q('select count(*) from bovi.pesaje_animal where pesaje_id=%s and peso_individual_kg is not null', (ticket,)) == 0
    cur.execute('SAVEPOINT sin_aprobar')
    try:
        cmd('confirmar_operacion', {'operacion_id': kg, 'version_lock': 0})
        raise AssertionError('Confirmó una compra por kg con pesaje sin aprobar')
    except psycopg.Error as ex:
        detail = json.loads(ex.diag.message_detail or '{}')
        assert ex.sqlstate == 'P0001' and detail.get('codigo') == 'BV015' and detail.get('regla_id') == 'RN-017' and 'pesajes pendientes' in detail.get('mensaje', ''), (ex.sqlstate, detail)
        cur.execute('ROLLBACK TO sin_aprobar')
    assert q('select count(*) from bovi.liquidacion where operacion_id=%s', (kg,)) == 0
    cmd('aprobar_pesaje', {'pesaje_id': ticket})
    cmd('confirmar_operacion', {'operacion_id': kg, 'version_lock': 0})
    assert q('select total from bovi.liquidacion where operacion_id=%s', (kg,)) == D('30000.00')
    print('PASS GOLD-ACAD-02 pesaje sin aprobar → BV015/RN-017 sin liquidación; aprobado → 30000.00')
finally:
    conn.rollback(); conn.close()
print('PASS GOLD-ACAD escenarios revertidos')
