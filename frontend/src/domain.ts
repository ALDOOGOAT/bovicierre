import type {components} from './generated/api-schema';
import {dinero,kilos} from './formato';
export type Money=components['schemas']['Dinero'];
export type Sede={id:string;empresa_id:string;codigo:string;nombre:string;roles:string[];capacidades?:string[];disponible?:boolean};
export type Session={usuario_id?:string;nombre?:string;usuario?:{id:string;nombre:string};sedes:Sede[]};
export type Row=Record<string,unknown> & {id?:string};
export type Page={elementos:Row[];pagina:number;tamano:number;total:number};
export function decimal(value:unknown):string {
    if(typeof value!=='string'||!/^[-]?\d+(?:\.\d+)?$/.test(value))return 'No disponible';
    const [whole,fraction]=value.split('.');
    return whole.replace(/\B(?=(\d{3})+(?!\d))/g,',')+(fraction===undefined?'':'.'+fraction);
}
/** Dinero del servidor como «47,880.00 MXN» (formato único: formato.ts). */
export function money(value:unknown):string {
    if(!value||typeof value!=='object'||!('importe' in value))return 'No disponible';
    return dinero(value);
}
/**
 * Lo que la persona escribe en un campo de dinero, peso o porcentaje → número decimal simple.
 * Acepta los formatos que la propia app muestra («$52.50», «10,000», «1,250.5», «300.000 kg», «2.5 %»):
 * quita el signo de pesos, los espacios, la unidad final y las comas que agrupan miles.
 * No adivina: una coma que no agrupa miles («52,50») se deja tal cual para que la validación la rechace;
 * nunca se convierte en punto decimal. Es solo texto: no hay aritmética de punto flotante.
 */
export function normalizarDecimal(raw:string):string {
    let v=String(raw??'').normalize('NFKC').trim();
    v=v.replace(/^\$\s*/,'').replace(/\s*(?:mxn|m\.n\.|pesos|kgs?|kilos?|%)\.?$/i,'').replace(/^\$\s*/,'').replace(/\s+/g,'');
    if(/^\d{1,3}(?:,\d{3})+(?:\.\d*)?$/.test(v))v=v.replaceAll(',','');
    if(/^\.\d/.test(v))v='0'+v;
    if(/^\d+\.$/.test(v))v=v.slice(0,-1);
    return v;
}
export type MotivoDecimal='vacio'|'negativo'|'coma_decimal'|'no_numero'|'decimales'|'grande';
/** Dígitos enteros que admite cada escala del servidor (NUMERIC de la base). */
export const enterosDe=(scale:number)=>scale===2?16:scale===3?11:scale===4?10:2;
/** Revisa un decimal escrito por la persona sin lanzar excepción; el motivo alimenta mensajes humanos. */
export function revisarDecimal(raw:string,scale:number):{ok:true;valor:string}|{ok:false;motivo:MotivoDecimal} {
    const v=normalizarDecimal(raw);
    if(!v)return {ok:false,motivo:'vacio'};
    if(/^[-−–]/.test(v))return {ok:false,motivo:'negativo'};
    if(/^\d+,\d+$/.test(v))return {ok:false,motivo:'coma_decimal'};
    if(!/^\d+(?:\.\d+)?$/.test(v))return {ok:false,motivo:'no_numero'};
    const [whole,fraction='']=v.split('.');
    if(fraction.length>scale)return {ok:false,motivo:'decimales'};
    const entero=whole.replace(/^0+(?=\d)/,'');
    if(entero.length>enterosDe(scale))return {ok:false,motivo:'grande'};
    return {ok:true,valor:`${entero}.${fraction.padEnd(scale,'0')}`};
}
/** Ejemplo que acompaña cada mensaje, en el formato que la app muestra. */
export const ejemploDe=(scale:number)=>scale===2?'1,250.50':scale===3?'4,520.5':scale===4?'52.50':'2.5';
export function mensajeDecimal(motivo:MotivoDecimal,scale:number):string {
    const ej=ejemploDe(scale);
    return ({
        vacio:`Escribe la cantidad, por ejemplo ${ej}.`,
        negativo:`Escribe la cantidad sin signo de menos, por ejemplo ${ej}.`,
        coma_decimal:`Usa punto para los decimales, por ejemplo ${ej}.`,
        no_numero:`Escribe solo la cantidad, por ejemplo ${ej}.`,
        decimales:`Usa como máximo ${scale} decimales, por ejemplo ${ej}.`,
        grande:'La cantidad es demasiado grande. Revisa que no sobren ceros.'
    } as Record<MotivoDecimal,string>)[motivo];
}
/** Texto decimal canónico para el servidor («$1,250.5» con escala 2 → «1250.50»). Lanza un Error con mensaje humano. */
export function canonicalDecimal(value:string,scale:number):string {
    const r=revisarDecimal(value,scale);
    if(!r.ok)throw new Error(mensajeDecimal(r.motivo,scale));
    return r.valor;
}
export function text(value:unknown):string {
    if(value===null||value===undefined)return 'No disponible';
    if(typeof value==='boolean')return value?'Sí':'No';
    if(typeof value==='object'&&'importe' in value)return money(value);
    if(typeof value==='object'&&'kg' in value)return kilos(value);
    if(Array.isArray(value))return value.map(text).join(' · ');
    if(typeof value==='object'&&'sistema' in value)return `${String(value.sistema)}: ${String((value as Record<string,unknown>).codigo_declarado||(value as Record<string,unknown>).codigo||'No disponible')}`;
    if(typeof value==='object')return 'Ver detalle';
    return String(value).replaceAll('_',' ');
}
export function today(date=new Date()):string{
    const parts=Object.fromEntries(new Intl.DateTimeFormat('en-CA',{timeZone:'America/Mexico_City',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(date).map(p=>[p.type,p.value]));
    return `${parts.year}-${parts.month}-${parts.day}`;
}
