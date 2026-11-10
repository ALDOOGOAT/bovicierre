import {test} from 'node:test';
import assert from 'node:assert/strict';
import {canonicalDecimal,normalizarDecimal,revisarDecimal} from '../src/domain.ts';
import {errorDecimal,esquemaDecimal,reglaDecimal} from '../src/validacion.ts';

test('normaliza los formatos que la app muestra sin convertir a número binario',()=>{
    assert.equal(normalizarDecimal('$52.50'),'52.50');
    assert.equal(normalizarDecimal('10,000'),'10000');
    assert.equal(normalizarDecimal('1,250.5'),'1250.5');
    assert.equal(normalizarDecimal('  $ 1,000.00 MXN '),'1000.00');
    assert.equal(normalizarDecimal('300.000 kg'),'300.000');
    assert.equal(normalizarDecimal('2.5 %'),'2.5');
    assert.equal(normalizarDecimal('1 250.50'),'1250.50');
    assert.equal(normalizarDecimal('.5'),'0.5');
    assert.equal(normalizarDecimal('52.'),'52');
    // Una coma que no agrupa miles no se adivina: queda para que la validación la rechace.
    assert.equal(normalizarDecimal('52,50'),'52,50');
    assert.equal(normalizarDecimal('1,00'),'1,00');
});

test('canonicalDecimal acepta $, comas de miles y espacios; conserva la escala exacta',()=>{
    assert.equal(canonicalDecimal('$52.50',4),'52.5000');
    assert.equal(canonicalDecimal('10,000',2),'10000.00');
    assert.equal(canonicalDecimal('1,250.5',3),'1250.500');
    assert.equal(canonicalDecimal('9,007,199,254,740,993.01',2),'9007199254740993.01');
    assert.equal(canonicalDecimal('007',2),'7.00');
});

test('los rechazos explican qué escribir con un ejemplo, sin jerga',()=>{
    assert.throws(()=>canonicalDecimal('52,50',2),/Usa punto para los decimales, por ejemplo 1,250\.50\./);
    assert.throws(()=>canonicalDecimal('-5',2),/sin signo de menos/);
    assert.throws(()=>canonicalDecimal('1.001',2),/como máximo 2 decimales/);
    assert.throws(()=>canonicalDecimal('abc',4),/por ejemplo 52\.50/);
    assert.throws(()=>canonicalDecimal('100',6),/demasiado grande/);
    assert.deepEqual(revisarDecimal('1,2,3',2),{ok:false,motivo:'no_numero'});
    assert.deepEqual(revisarDecimal('',2),{ok:false,motivo:'vacio'});
});

test('esquemas Zod por campo: mensajes estilo GOV.UK y salida canónica',()=>{
    const precio=reglaDecimal('precio_unitario')!;
    assert.equal(precio.escala,4);
    assert.equal(errorDecimal('',precio),'Escribe el precio pactado en pesos, por ejemplo 52.50.');
    assert.equal(errorDecimal('52,50',precio),'Usa punto para los decimales, por ejemplo 52.50.');
    assert.equal(errorDecimal('$52.50',precio),undefined);
    assert.equal(esquemaDecimal(precio).parse('$52.50'),'52.5000');
    assert.equal(esquemaDecimal(reglaDecimal('importe')!).parse('10,000'),'10000.00');
    assert.equal(errorDecimal('',reglaDecimal('cargos_pactados')!,false),undefined);
    assert.equal(errorDecimal('150',reglaDecimal('deduccion_pct')!,false),'Escribe un porcentaje menor que 100, por ejemplo 2.5.');
    assert.equal(errorDecimal('4,520.5 kg',reglaDecimal('neto')!),undefined);
    assert.equal(reglaDecimal('peso_0b8a-uuid')?.escala,3);
    assert.equal(reglaDecimal('asignacion_3')?.escala,2);
    assert.equal(reglaDecimal('bonifica_gasto_id'),undefined);
    assert.equal(reglaDecimal('unidad_precio'),undefined);
});
