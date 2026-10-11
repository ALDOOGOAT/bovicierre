import type {components} from './generated/api-schema';
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
export function money(value:unknown):string {
    if(!value||typeof value!=='object'||!('importe' in value))return 'No disponible';
    const data=value as Money;
    return `${decimal(data.importe)} ${data.moneda||'MXN'}`;
}
export function canonicalDecimal(value:string,scale:number):string {
    if(!new RegExp(`^\\d{1,${scale===2?16:scale===3?11:scale===4?10:2}}(?:\\.\\d{1,${scale}})?$`).test(value))throw new Error(`Escribe un decimal positivo con hasta ${scale} decimales.`);
    const [whole,fraction='']=value.split('.');
    return `${whole.replace(/^0+(?=\d)/,'')}.${fraction.padEnd(scale,'0')}`;
}
export function text(value:unknown):string {
    if(value===null||value===undefined)return 'No disponible';
    if(typeof value==='boolean')return value?'Sí':'No';
    if(typeof value==='object'&&'importe' in value)return money(value);
    if(typeof value==='object'&&'kg' in value)return `${decimal((value as {kg:string}).kg)} kg`;
    if(Array.isArray(value))return value.map(text).join(' · ');
    if(typeof value==='object'&&'sistema' in value)return `${String(value.sistema)}: ${String((value as Record<string,unknown>).codigo_declarado||(value as Record<string,unknown>).codigo||'No disponible')}`;
    if(typeof value==='object')return 'Ver detalle';
    return String(value).replaceAll('_',' ');
}
export function today(date=new Date()):string{
    const parts=Object.fromEntries(new Intl.DateTimeFormat('en-CA',{timeZone:'America/Mexico_City',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(date).map(p=>[p.type,p.value]));
    return `${parts.year}-${parts.month}-${parts.day}`;
}
