import test from 'node:test';
import assert from 'node:assert/strict';
import {agrupar,cantidad,dinero,fecha,fechaHora,importe,kilos,precio,esFechaIso} from '../src/formato.ts';
import {estadoCuenta,palabra,quienDebe,sentidoPago,conImporte,mismoImporte} from '../src/palabras.ts';
import {money,text} from '../src/domain.ts';

test('dinero: un solo formato «47,880.00 MXN», sin flotantes ni redondeo',()=>{
    assert.equal(dinero({importe:'47880.00',moneda:'MXN'}),'47,880.00 MXN');
    assert.equal(dinero({importe:'1000',moneda:'MXN'}),'1,000.00 MXN');
    // «0» y «0.00» se leen igual (antes salía «0 MXN» en los ajustes).
    assert.equal(dinero({importe:'0',moneda:'MXN'}),'0.00 MXN');
    assert.equal(dinero({importe:'0.00'}),'0.00 MXN');
    assert.equal(dinero({importe:'-1500.5',moneda:'MXN'}),'−1,500.50 MXN');
    assert.equal(dinero({importe:'123456789012.34',moneda:'MXN'}),'123,456,789,012.34 MXN');
    // Más decimales que la escala: se quitan solo los ceros; un dígito real nunca se redondea aquí.
    assert.equal(dinero({importe:'10.5000'}),'10.50 MXN');
    assert.equal(dinero({importe:'10.125'}),'10.125 MXN');
    assert.equal(dinero(undefined),'No disponible');
    assert.equal(dinero({importe:'abc'}),'No disponible');
    assert.equal(importe({importe:'37880.00'}),'37,880.00');
    // money() y text() de domain usan el mismo formateador; las E2E buscan «1,000.00 MXN».
    assert.equal(money({importe:'1000.00',moneda:'MXN'}),'1,000.00 MXN');
    assert.equal(text({importe:'900',moneda:'MXN'}),'900.00 MXN');
});

test('kilos: separador de miles y la escala de la báscula, sin ceros basura',()=>{
    assert.equal(kilos({kg:'912.00000000000000000000000'}),'912.000 kg');
    assert.equal(kilos({kg:'4520.5'}),'4,520.500 kg');
    assert.equal(kilos('100.000'),'100.000 kg');
    assert.equal(kilos({kg:'1234567.1234'}),'1,234,567.1234 kg');
    assert.equal(kilos({kg:'-10.000'}),'−10.000 kg');
    assert.equal(kilos(undefined),'No disponible');
    assert.equal(text({kg:'110.000'}),'110.000 kg');
});

test('cantidad y precio de un concepto según su unidad',()=>{
    assert.equal(cantidad('912.00000000000000000000000','KG'),'912.000 kg');
    assert.equal(cantidad('3.000','CABEZA'),'3 cabezas');
    assert.equal(cantidad('1.000','CABEZA'),'1 cabeza');
    assert.equal(cantidad('1000','MXN'),'1,000.00 MXN');
    assert.equal(precio('52.5000','KG'),'52.50 MXN por kg');
    assert.equal(precio('47.1250','KG'),'47.125 MXN por kg');
    assert.equal(precio('14500.0000','CABEZA'),'14,500.00 MXN por cabeza');
    assert.equal(precio(52.5),'52.50 MXN');
    assert.equal(agrupar('007.5',2),'7.50');
    assert.equal(agrupar('-0.00',2),'0.00');
    assert.equal(agrupar('1e5'),undefined);
});

test('fechas legibles en la zona de México; nunca ISO',()=>{
    assert.equal(fecha('2026-11-08'),'8 nov 2026');
    assert.equal(fecha('2026-11-09T04:42:23.879265+00:00'),'8 nov 2026');
    assert.match(fechaHora('2026-11-08T16:05:00Z'),/^8 nov 2026, 10:05/);
    assert.equal(fechaHora('2026-11-08'),'8 nov 2026');
    assert.equal(fecha(null),'Sin fecha');
    assert.equal(fecha('mañana','sin fecha'),'sin fecha');
    assert.ok(esFechaIso('2026-11-08'));
    assert.ok(esFechaIso('2026-11-10T07:09:23.676423+00:00'));
    assert.ok(!esFechaIso('C-2026-000007'));
    assert.ok(!esFechaIso('2026'));
});

test('estados y códigos en palabras del trato',()=>{
    assert.equal(palabra('POR_PAGAR'),'Por pagar');
    assert.equal(palabra('VALIDADO'),'Validado');
    assert.equal(palabra('REGISTRADO'),'Por validar');
    assert.equal(palabra('BORRADOR'),'Borrador');
    assert.equal(palabra('ACORDADA'),'Acordada');
    assert.equal(palabra('PENDIENTE_RECEPCION'),'Por recibir');
    assert.equal(palabra('PENDIENTE RECEPCION'),'Por recibir');
    assert.equal(palabra('PROPIETARIO'),'Leído en el nodo de esta sede');
    assert.equal(palabra('ASINCRONA'),'Copia en segundos');
    // Código desconocido: legible sin inventar significado; nombres y folios no se tocan.
    assert.equal(palabra('ALGO_NUEVO'),'Algo nuevo');
    assert.equal(palabra('C-2026-000007'),'C-2026-000007');
    assert.equal(palabra('DEMO-2026-10-V1 contraparte'),'DEMO-2026-10-V1 contraparte');
    assert.equal(palabra(undefined),'No disponible');
    assert.equal(quienDebe('POR_COBRAR'),'Te debe');
    assert.equal(quienDebe('POR_PAGAR'),'Le debes');
    assert.equal(sentidoPago('COBRO'),'Te pagó');
    assert.equal(sentidoPago('PAGO'),'Le pagaste');
});

test('estado de una cuenta: solo compara lo que dio el servidor',()=>{
    const hoy='2026-11-10';
    const m=(importe:string)=>({importe,moneda:'MXN'});
    assert.deepEqual(estadoCuenta({saldo:m('0.00'),total:m('1000.00')},hoy),{palabra:'Saldada',tono:'positive'});
    assert.deepEqual(estadoCuenta({saldo:m('37880.00'),total:m('47880.00')},hoy),{palabra:'Abonada en parte',tono:'progress'});
    assert.deepEqual(estadoCuenta({saldo:m('3000.00'),total:m('3000.00')},hoy),{palabra:'Pendiente',tono:'attention'});
    assert.deepEqual(estadoCuenta({saldo:m('3000.00'),total:m('3000.00'),vence_el:'2026-11-01'},hoy),{palabra:'Vencida',tono:'critical'});
    assert.deepEqual(estadoCuenta({saldo:m('3000.00'),total:m('3000.00'),vence_el:'2026-11-10'},hoy),{palabra:'Pendiente',tono:'attention'});
    assert.deepEqual(estadoCuenta({},hoy),{palabra:'Sin saldo informado',tono:'neutral'});
    assert.ok(conImporte(m('0.01')));
    assert.ok(!conImporte(m('0')));
    assert.ok(mismoImporte(m('3000'),m('3000.00')));
    assert.ok(!mismoImporte(m('3000.00'),m('3000.01')));
});
