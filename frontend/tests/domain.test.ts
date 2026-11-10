import {test} from 'node:test';
import assert from 'node:assert/strict';
import {canonicalDecimal,decimal,money,today} from '../src/domain.ts';
import {createAttempt,executeAttempt,ApiError} from '../src/api.ts';
import {renderToStaticMarkup} from 'react-dom/server';
import {createElement} from 'react';
import {Field} from '../src/ui.tsx';
test('importe exacto grande y centavos conservados sin conversión binaria',()=>{
    assert.equal(decimal('9007199254740993.01'),'9,007,199,254,740,993.01');
    assert.equal(money({importe:'240000.00',moneda:'MXN'}),'240,000.00 MXN');
    assert.equal(money(undefined),'No disponible');
    assert.equal(decimal('0.000'),'0.000');
});
test('captura decimal canónica rechaza exponentes, negativos y precisión excesiva',()=>{
    assert.equal(canonicalDecimal('048.5',4),'48.5000');
    assert.equal(canonicalDecimal('0',2),'0.00');
    // 2026-11-10: «1,000» es el formato que la propia app muestra; ahora se acepta como mil (ver decimales.test.ts).
    assert.equal(canonicalDecimal('1,000',2),'1000.00');
    for(const invalid of ['1e5','-5','1.001','NaN','52,50','Infinity',''])assert.throws(()=>canonicalDecimal(invalid,2));
});
test('reintento conserva clave, contenido y If-Match aun si cambia el objeto original',async()=>{
    const original={importe:{importe:'600.00',moneda:'MXN'}};
    const attempt=createAttempt('/sedes/A/pagos',original,'POST','"3"');
    original.importe.importe='999.00';
    const calls:RequestInit[]=[];const old=globalThis.fetch;
    globalThis.fetch=async(_input,init)=>{calls.push(init!);if(calls.length===1)throw new TypeError('fallo de red');return new Response(JSON.stringify({id:'p1'}),{status:201,headers:{'Content-Type':'application/json'}});};
    try{await assert.rejects(executeAttempt(attempt),e=>e instanceof ApiError&&e.status===0);await executeAttempt(attempt);assert.equal(calls[0].body,calls[1].body);assert.ok(String(calls[1].body).includes('600.00'));assert.equal(new Headers(calls[0].headers).get('Idempotency-Key'),new Headers(calls[1].headers).get('Idempotency-Key'));assert.equal(new Headers(calls[1].headers).get('If-Match'),'"3"');assert.equal(calls[1].credentials,'same-origin');}finally{globalThis.fetch=old;}
});
test('error de campo tiene etiqueta, relación accesible y contraseña permite gestores',()=>{
    const html=renderToStaticMarkup(createElement(Field,{label:'Importe',name:'importe',value:'',onChange:()=>{},error:'Importe excedido'}));
    assert.ok(html.includes('for="importe"'));assert.ok(html.includes('aria-invalid="true"'));assert.ok(html.includes('aria-describedby="importe-error"'));assert.ok(html.includes('id="importe-error"'));
    const password=renderToStaticMarkup(createElement(Field,{label:'Contraseña',name:'contrasena',type:'password',value:'',onChange:()=>{}}));assert.ok(password.includes('autoComplete="current-password"'));
});
test('CSRF usa la cabecera entregada por el backend y se mantiene fuera de persistencia',async()=>{
    const {refreshCsrf,request}=await import('../src/api.ts');const calls:RequestInit[]=[];const old=globalThis.fetch;
    globalThis.fetch=async(_input,init)=>{calls.push(init!);return new Response(JSON.stringify(calls.length===1?{token:'csrf-test',headerName:'X-XSRF-TOKEN'}:{ok:true}),{status:200,headers:{'Content-Type':'application/json'}});};
    try{await refreshCsrf();await request('/sesion/login',{method:'POST',body:JSON.stringify({login:'example',contrasena:'test'})});assert.equal(new Headers(calls[1].headers).get('X-XSRF-TOKEN'),'csrf-test');}finally{globalThis.fetch=old;}
});

test('fecha económica predeterminada usa día de Ciudad de México después de las 18 h',()=>{assert.equal(today(new Date('2026-10-12T01:00:00Z')),'2026-10-11');assert.equal(today(new Date('2026-10-12T07:00:00Z')),'2026-10-12');});
test('resultado incierto consulta primero el comando y recupera el resultado sin nuevo POST',async()=>{
    const attempt=createAttempt('/sedes/sede-a/pagos',{importe:{importe:'600.00',moneda:'MXN'}});const old=globalThis.fetch;const calls:{url:string;method?:string}[]=[];
    globalThis.fetch=async(input,init)=>{calls.push({url:String(input),method:init?.method});return new Response(JSON.stringify({estado:'COMPLETADA',resultado:{id:'p1',disponible:{importe:'600.00',moneda:'MXN'}}}),{status:200,headers:{'Content-Type':'application/json'}});};
    try{const result=await executeAttempt<{id:string}>(attempt,true);assert.equal(result.data.id,'p1');assert.equal(calls.length,1);assert.ok(calls[0].url.includes('/comandos/registrar_pago/'+attempt.key));assert.equal(calls[0].method,undefined);}finally{globalThis.fetch=old;}
});
test('comando en curso conserva el intento y evita volver a enviarlo',async()=>{
    const attempt=createAttempt('/sedes/sede-a/operaciones/op-a/confirmar',{});const old=globalThis.fetch;let calls=0;
    globalThis.fetch=async()=>{calls++;return new Response(JSON.stringify({estado:'EN_CURSO'}),{status:200,headers:{'Content-Type':'application/json'}});};
    try{await assert.rejects(executeAttempt(attempt,true),e=>e instanceof ApiError&&e.status===425);assert.equal(calls,1);}finally{globalThis.fetch=old;}
});
test('formularios simultáneos no comparten identificadores de campo',async()=>{
    const {CommandForm}=await import('../src/ui.tsx');const {Fragment}=await import('react');
    const form=(path:string)=>createElement(CommandForm,{path,build:()=>({}),label:'Guardar',children:createElement(Field,{label:'Importe',name:'importe',value:'',onChange:()=>{}})});
    const html=renderToStaticMarkup(createElement(Fragment,null,form('/sedes/a/pagos'),form('/sedes/a/liquidaciones/l1/ajustes')));
    const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);assert.equal(ids.length,new Set(ids).size);
});
