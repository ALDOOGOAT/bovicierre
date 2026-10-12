import {test} from 'node:test';
import assert from 'node:assert/strict';
import {toneOf,statusColumns} from '../src/tone.ts';

test('tono por estado no altera el valor y separa operación, entrega y pago',()=>{
    assert.equal(toneOf('CONFIRMADA'),'positive');
    assert.equal(toneOf('BORRADOR'),'attention');
    assert.equal(toneOf('ANULADA'),'critical');
    assert.equal(toneOf('PENDIENTE RECEPCION'),'attention');
    assert.equal(toneOf('VENDIDA_PENDIENTE_ENTREGA'),'progress');
    assert.equal(toneOf('valor desconocido'),'neutral');
    assert.equal(toneOf(undefined),'neutral');
    assert.equal(toneOf({importe:'1.00'}),'neutral');
    for(const column of ['estado','estado_entrega','estado_pago'])assert.ok(statusColumns.has(column));
    assert.ok(!statusColumns.has('total'));
});
