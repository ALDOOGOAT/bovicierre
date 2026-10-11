import {test} from 'node:test';
import assert from 'node:assert/strict';
import {replaceLot,operationAnimals} from '../src/workflow.ts';
import {ApiError,clearSession,setPrincipal,keepAttempt,rememberPending,readPending,createAttempt,executeAttempt} from '../src/api.ts';

test('editar el primer lote conserva identidad y orden de todos los demás',()=>{
    const second={numero_lote:2,animales:['animal-b'],precio_unitario:'20.0000'};
    const original=[{numero_lote:1,animales:['animal-a'],precio_unitario:'10.0000'},second];
    const result=replaceLot(original,{...original[0],precio_unitario:'11.0000'});
    assert.deepEqual(result.map(l=>[l.numero_lote,l.animales]),[[1,['animal-a']],[2,['animal-b']]]);
    assert.equal(result[1],second);assert.equal(original[0].precio_unitario,'10.0000');
    assert.deepEqual(replaceLot(result,{numero_lote:3,animales:['animal-c']}).map(l=>l.numero_lote),[1,2,3]);
});
test('venta KG conserva identidad animal y exige resolver cada posición del lote',()=>{
    const operation={tipo:'VENTA',lotes:[{numero_lote:1,animales:[],posiciones:['position-b','position-a']}]};
    const positions=[{id:'position-a',animal_id:'animal-a'},{id:'position-b',animal_id:'animal-b'},{id:'other',animal_id:'other'}];
    assert.deepEqual(operationAnimals(operation,positions),['animal-b','animal-a']);
    assert.throws(()=>operationAnimals(operation,positions.slice(0,1)),/todas las posiciones/);
    assert.deepEqual(operationAnimals({tipo:'COMPRA',lotes:[{animales:['animal-a']}]}),['animal-a']);
});
test('resultado incierto 500/502/504 y autenticación expirada conserva intención; rechazo de dominio permite corregir',()=>{
    for(const status of [0,401,408,409,425,429,500,502,503,504])assert.equal(keepAttempt(new ApiError(status)),true,String(status));
    for(const status of [400,403,404,412,413,422,428])assert.equal(keepAttempt(new ApiError(status)),false,String(status));
});
test('intención sobrevive expiración de sesión, queda aislada por principal y lookup recupera sin duplicar POST',async()=>{
    const oldStorage=globalThis.sessionStorage;const oldFetch=globalThis.fetch;
    const saved=new Map<string,string>();
    Object.defineProperty(globalThis,'sessionStorage',{configurable:true,value:{getItem:(key:string)=>saved.get(key)||null,setItem:(key:string,value:string)=>saved.set(key,value),removeItem:(key:string)=>saved.delete(key)}});
    const attempt=createAttempt('/sedes/site-a/pagos',{importe:{importe:'10.00',moneda:'MXN'}});
    try{
        setPrincipal('principal-a');rememberPending(attempt);clearSession();assert.equal(readPending(attempt.path),undefined);
        setPrincipal('principal-b');assert.equal(readPending(attempt.path),undefined);
        setPrincipal('principal-a');assert.equal(JSON.stringify(readPending(attempt.path)),JSON.stringify(attempt));
        const calls:string[]=[];globalThis.fetch=async(input,init)=>{calls.push(init?.method||'GET');return new Response(JSON.stringify({estado:'COMPLETADA',resultado:{id:'p1'}}),{status:200});};
        assert.equal((await executeAttempt<{id:string}>(readPending(attempt.path)!,true)).data.id,'p1');assert.deepEqual(calls,['GET']);
    }finally{globalThis.fetch=oldFetch;Object.defineProperty(globalThis,'sessionStorage',{configurable:true,value:oldStorage});setPrincipal(undefined);}
});
