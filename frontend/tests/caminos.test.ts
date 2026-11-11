import {test} from 'node:test';
import assert from 'node:assert/strict';
import {claveArete,filtrarCuentas,leerAretes,letraBascula,quitarApuntados} from '../src/caminos-util.ts';
import {errorDecimal,reglaDecimal} from '../src/validacion.ts';

test('«Apuntar varios» acepta un arete por renglón, espacios, comas y punto y coma',()=>{
    const l=leerAretes('0712345678\n0712345679, 0712345680;0712345681  0712345682\t0712345683','M');
    assert.deepEqual(l.map(x=>x.codigo),['0712345678','0712345679','0712345680','0712345681','0712345682','0712345683']);
    assert.ok(l.every(x=>x.sexo==='M'&&!x.problema));
    assert.deepEqual(l.map(x=>x.renglon),[1,2,2,2,2,2]);
});

test('ignora renglones vacíos y espacios sobrantes',()=>{
    const l=leerAretes('\n   \n  MX-001  \n\n','H');
    assert.equal(l.length,1);
    assert.equal(l[0].codigo,'MX-001');
    assert.equal(l[0].renglon,3);
    assert.equal(leerAretes('','M').length,0);
});

test('una H o M junto a un arete le cambia el sexo solo a ese arete',()=>{
    const l=leerAretes('A1 H\nA2\nm A3\nA4 hembra\nA5 Macho','M');
    assert.deepEqual(l.map(x=>[x.codigo,x.sexo]),[['A1','H'],['A2','M'],['A3','M'],['A4','H'],['A5','M']]);
    const h=leerAretes('B1\nB2 M','H');
    assert.deepEqual(h.map(x=>x.sexo),['H','M']);
    // Varios en un renglón: la marca va con el arete que la precede; si va primero, con el que la sigue.
    assert.deepEqual(leerAretes('C1 H, C2, C3 h','M').map(x=>x.sexo),['H','M','H']);
    assert.deepEqual(leerAretes('H C1 C2','M').map(x=>x.sexo),['H','M']);
    // Una marca sola no es un arete.
    assert.equal(leerAretes('H','M').length,0);
});

test('marca formato y repetidos por arete sin perder los buenos',()=>{
    const l=leerAretes('0712345678\nÑANDÚ-1\n07-1234-5678\n#45\n0712345679\n'+'9'.repeat(41),'M');
    assert.equal(l.length,6);
    assert.equal(l[0].problema,undefined);
    assert.match(l[1].problema||'',/solo letras, números y guiones/);
    assert.match(l[2].problema||'',/Repetido: ya está en el renglón 1/);
    assert.equal(leerAretes('Z9 Z9','M')[1].problema,'Repetido en este mismo renglón.');
    assert.match(l[3].problema||'',/solo letras, números y guiones/);
    assert.equal(l[4].problema,undefined);
    assert.match(l[5].problema||'',/más de 40 caracteres/);
    assert.equal(l.filter(x=>!x.problema).length,2);
    assert.equal(leerAretes('---','M')[0].problema,'Usa solo letras, números y guiones (sin acentos, ñ ni símbolos).');
});

test('la clave normaliza como el servidor (mayúsculas, sin espacios ni guiones)',()=>{
    assert.equal(claveArete('mx-07 12'),'MX0712');
    assert.equal(leerAretes('ab-1\nAB1','M')[1].problema,'Repetido: ya está en el renglón 1.');
});

test('quitarApuntados deja solo los aretes que fallaron, con su marca de sexo',()=>{
    const texto='0712345678\n0712345679 H\nA1, A2\nA3';
    assert.equal(quitarApuntados(texto,new Set(['0712345678','A1','A3'])),'0712345679 H\nA2');
    // La marca se va con su arete y se queda con el que falló.
    assert.equal(quitarApuntados('C1 H, C2 M, C3',new Set(['C1'])),'C2 M C3');
    assert.equal(quitarApuntados('H C1 C2',new Set(['C2'])),'C1 H');
    assert.equal(quitarApuntados(texto,new Set(['0712345678','0712345679','A1','A2','A3'])),'');
    assert.equal(quitarApuntados('a-1\nA1',new Set(['A1'])),'');
});

const cuentas=[
    {id:'1',direccion:'POR_COBRAR',folio:'V-2026-000007',nombre:'José González'},
    {id:'2',direccion:'POR_PAGAR',folio:'C-2026-000012',nombre:'DEMO Rancho El Ébano'},
    {id:'3',direccion:'POR_PAGAR',folio:'C-2026-000013',nombre:'José Pérez'},
    {id:'4',direccion:'POR_COBRAR',folio:'V-2026-000021',nombre:'Ganadera del Sur SA'},
];
const describe=(c:typeof cuentas[number])=>c.folio+' '+c.nombre;
const ids=(r:typeof cuentas)=>r.map(c=>c.id);

test('filtro de cuentas por sentido: «Te debe» y «Le debes»',()=>{
    assert.deepEqual(ids(filtrarCuentas(cuentas,{texto:'',sentido:''},describe)),['1','2','3','4']);
    assert.deepEqual(ids(filtrarCuentas(cuentas,{texto:'',sentido:'POR_COBRAR'},describe)),['1','4']);
    assert.deepEqual(ids(filtrarCuentas(cuentas,{texto:'',sentido:'POR_PAGAR'},describe)),['2','3']);
});

test('filtro de cuentas por folio o contraparte, sin acentos ni mayúsculas',()=>{
    assert.deepEqual(ids(filtrarCuentas(cuentas,{texto:'gonzalez',sentido:''},describe)),['1']);
    assert.deepEqual(ids(filtrarCuentas(cuentas,{texto:'JOSÉ',sentido:''},describe)),['1','3']);
    assert.deepEqual(ids(filtrarCuentas(cuentas,{texto:'c-2026-000012',sentido:''},describe)),['2']);
    assert.deepEqual(ids(filtrarCuentas(cuentas,{texto:'000013',sentido:''},describe)),['3']);
    assert.deepEqual(ids(filtrarCuentas(cuentas,{texto:'ebano rancho',sentido:''},describe)),['2']);
    assert.deepEqual(ids(filtrarCuentas(cuentas,{texto:'josé',sentido:'POR_PAGAR'},describe)),['3']);
    assert.deepEqual(ids(filtrarCuentas(cuentas,{texto:'nadie',sentido:''},describe)),[]);
    assert.deepEqual(ids(filtrarCuentas(cuentas,{texto:'   ',sentido:''},describe)),['1','2','3','4']);
});

test('la lectura de la báscula achica la letra cuando no cabe',()=>{
    assert.equal(letraBascula('438'),15);
    assert.equal(letraBascula('0'),15);
    assert.ok(letraBascula('910.500')<10);
    assert.ok(letraBascula('910.500')*7*0.62<=40.5);
    assert.ok(letraBascula('4,520.500')>=7);
});

test('un número con dos puntos pide un solo punto decimal (no «sin letras»)',()=>{
    const precio=reglaDecimal('precio_unitario')!;
    assert.equal(errorDecimal('52.5.0',precio),'Escribe un solo punto decimal, por ejemplo 52.50.');
    assert.equal(errorDecimal('52.50',precio),undefined);
    assert.match(errorDecimal('52a',precio)||'',/sin letras/);
    assert.equal(errorDecimal('1.000.50',reglaDecimal('importe')!),'Escribe un solo punto decimal, por ejemplo 1,250.50.');
});
