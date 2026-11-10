import {test} from 'node:test';
import assert from 'node:assert/strict';
import {traducirError,fraseCampo,problemaCampo,confirmacionDe,TABLA_ERRORES} from '../src/errores.ts';
import {ApiError,comandoDe} from '../src/api.ts';

const UUID=/[0-9a-f]{8}-[0-9a-f]{4}/i;

test('RN-014 sin pesaje aprobado dice qué ticket falta y lleva a la báscula',()=>{
    const d={status:422,codigo:'BV013',regla_id:'RN-014',correlation_id:'0b8a2f1e-1111-4222-8333-444455556666',campos:[{campo:'pesaje_base_id',problema:'invalido'}]};
    const t=traducirError(d,{comando:'acordar_operacion',escritura:true,datos:{folio_ticket:'T-0042'}});
    assert.equal(t.que,'Falta aprobar el ticket T-0042.');
    assert.equal(t.accion?.clave,'bascula');
    assert.deepEqual(t.cubre,['pesaje_base_id']);
    const sinFolio=traducirError({...d,campos:[{campo:'pesaje_base_id',problema:'faltante'}]},{comando:'acordar_operacion',escritura:true});
    assert.equal(sinFolio.que,'Falta aprobar el pesaje del lote.');
    assert.ok(!UUID.test(t.que+t.hacer)&&!/RN-|BV0/.test(t.que+t.hacer));
});

test('BV015/RN-017 «Acuerdo sin condiciones» pide guardar las condiciones primero',()=>{
    const t=traducirError({status:422,codigo:'BV015',regla_id:'RN-017',campos:[]},{comando:'acordar_operacion',escritura:true});
    assert.equal(t.que,'Todavía no hay condiciones guardadas.');
    assert.match(t.hacer!,/Guarda primero/);
    assert.equal(t.accion?.clave,'precio');
    const cierre=traducirError({status:422,codigo:'BV015',regla_id:'RN-017'},{comando:'confirmar_operacion',escritura:true});
    assert.equal(cierre.que,'Al trato le falta algo para cerrarse.');
});

test('BV013 en aprobar y corregir pesaje, y reglas de dinero, se traducen al trato',()=>{
    assert.equal(traducirError({status:422,codigo:'BV013',regla_id:'RN-013'},{comando:'aprobar_pesaje',escritura:true}).que,'Este ticket ya no se puede aprobar.');
    assert.match(traducirError({status:422,codigo:'BV013',regla_id:'RN-013',campos:[{campo:'animales',problema:'composicion_distinta'}]},{comando:'corregir_pesaje'}).que,/mismas cabezas/);
    assert.match(traducirError({status:409,codigo:'BV020',regla_id:'RN-029'},{comando:'aplicar_pago',escritura:true}).que,/abono es mayor/);
    assert.match(traducirError({status:409,codigo:'BV402',regla_id:'RN-018'},{comando:'reservar_venta',escritura:true}).que,/apartada en otro trato/);
    // Contrato E2E (additional.spec): el aviso de reserva vencida contiene «La reserva venció».
    assert.match(traducirError({status:409,codigo:'BV403',regla_id:'RN-019'},{comando:'confirmar_operacion',escritura:true}).que,/^La reserva venció/);
    assert.match(traducirError({status:422,codigo:'BV025',regla_id:'RN-039'},{escritura:true}).que,/periodo abierto/);
});

test('la tabla cubre las reglas de las migraciones y ningún título expone códigos',()=>{
    const codigos=['BV010','BV011','BV013','BV015','BV016','BV018','BV020','BV021','BV022','BV023','BV024','BV025','BV026','BV402','BV403','BV404','BV405','BV409','BV412','BV501'];
    for(const codigo of codigos)assert.ok(TABLA_ERRORES.some(e=>e.codigo===codigo),'falta '+codigo);
    for(const e of TABLA_ERRORES){const t=e.t({escritura:true,datos:{}},{status:422,codigo:e.codigo});assert.ok(t.que&&!/BV\d|RN-\d|_id\b/.test(t.que+(t.hacer||'')),t.que);}
});

test('sin respuesta: el texto de reintento solo aparece en comandos de escritura',()=>{
    const escritura=traducirError({status:0},{escritura:true,comando:'crear_contraparte'});
    assert.equal(escritura.que,'No se pudo conocer el resultado.');
    const consulta=traducirError({status:0},{});
    assert.equal(consulta.que,'No hubo respuesta de la sede.');
    assert.ok(!/comando|captura/i.test(consulta.que+consulta.hacer));
    assert.match(traducirError({status:503},{escritura:true}).hacer!,/Conservamos la captura para reintentar/);
    assert.ok(!/Conservamos la captura/.test(fraseOf(traducirError({status:503},{}))));
    assert.equal(traducirError({status:401},{comando:'iniciar_sesion',escritura:true}).que,'El usuario o la contraseña no coinciden.');
});
const fraseOf=(t:{que:string;hacer?:string})=>t.que+' '+(t.hacer||'');

test('ApiError arma el mensaje desde la traducción y distingue lectura de escritura',async()=>{
    const old=globalThis.fetch;
    globalThis.fetch=async()=>{throw new TypeError('sin red');};
    try{
        const {request}=await import('../src/api.ts');
        await assert.rejects(request('/sedes/a/operaciones?pagina=1'),e=>e instanceof ApiError&&e.status===0&&e.message.startsWith('No hubo respuesta de la sede.'));
        await assert.rejects(request('/sedes/a/contrapartes',{method:'POST',body:'{}'}),e=>e instanceof ApiError&&e.message.startsWith('No se pudo conocer el resultado.')&&e.contexto.comando==='crear_contraparte');
    }finally{globalThis.fetch=old;}
    assert.equal(comandoDe('/sedes/a/operaciones/o/acordar'),'acordar_operacion');
    assert.equal(comandoDe('/sesion/login'),'iniciar_sesion');
});

test('errores de campo sin nombres técnicos y confirmaciones por comando',()=>{
    assert.equal(problemaCampo('faltante'),'Falta este dato.');
    assert.equal(problemaCampo('requerido_1_200'),'Escribe entre 1 y 200 letras.');
    assert.equal(problemaCampo('desconocido'),'Revisa este dato.');
    const frase=fraseCampo('pesaje_base_id','faltante');
    assert.equal(frase,'Falta el pesaje aprobado del lote. Revísalo en su paso y vuelve a intentarlo.');
    assert.ok(!frase.includes('pesaje_base_id'));
    assert.ok(!fraseCampo('campo_raro','x').includes('campo_raro'));
    assert.equal(confirmacionDe('acordar_operacion'),'Acuerdo guardado como versión fija.');
    assert.equal(confirmacionDe(undefined),'Guardado.');
    // El aviso de éxito nunca repite el texto que buscan las E2E en la página.
    for(const c of ['editar_operacion','crear_contraparte','registrar_pago'])assert.ok(!confirmacionDe(c).includes('Registro confirmado por el servidor'));
});
