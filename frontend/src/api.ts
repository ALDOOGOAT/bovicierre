import {traducirError,fraseError,type ContextoError,type DetalleError,type Traduccion} from './errores';
export type DetallesApi={codigo?:string;mensaje?:string;regla_id?:string;correlation_id?:string;campos?:{campo:string;problema:string}[]};
/**
 * Error de la API con su traducción al lenguaje del tratante (ver errores.ts).
 * `message` es la frase completa «qué pasó + qué hacer»; `contexto.escritura` distingue un comando de una consulta:
 * solo un comando de escritura promete conservar la captura o reintentar con la misma clave.
 */
export class ApiError extends Error {
    readonly traduccion:Traduccion;
    constructor(public status:number,public details:DetallesApi={},public contexto:ContextoError={}){
        const traduccion=traducirError({status,...details},contexto);
        super(fraseError(traduccion));
        this.traduccion=traduccion;
    }
    /** Datos del error para volver a traducirlo con lo que sabe la pantalla (p. ej. el folio del ticket). */
    detalle():DetalleError{return {status:this.status,...this.details};}
}
let csrf='';
let csrfHeader='X-CSRF-TOKEN';
let principal:string|undefined;
export function setPrincipal(id:string|undefined){principal=id;}
export function clearSession(){csrf='';principal=undefined;if(typeof window!=='undefined')window.dispatchEvent(new Event('session-cleared'));}
export function keepAttempt(error:Error){return !(error instanceof ApiError)||error.status===0||error.status===401||error.status===408||error.status===409||error.status===425||error.status===429||error.status>=500;}
export async function refreshCsrf(){const {data}=await request<{token:string;headerName:string}>('/sesion/csrf');if(!['X-CSRF-TOKEN','X-XSRF-TOKEN'].includes(data.headerName))throw new Error('Cabecera CSRF no reconocida.');csrf=data.token;csrfHeader=data.headerName;}
export async function request<T>(path:string,options:RequestInit={}):Promise<{data:T;etag:string|null}>{
    const headers=new Headers(options.headers);
    if(options.body&&!headers.has('Content-Type')&&typeof options.body==='string')headers.set('Content-Type','application/json');
    if(options.method&&options.method!=='GET'&&csrf)headers.set(csrfHeader,csrf);
    const escritura=!!options.method&&options.method!=='GET';
    const contexto:ContextoError={escritura,comando:escritura?comandoDe(path,options.method!):undefined};
    let response:Response;
    try{response=await fetch('/api/v1'+path,{...options,headers,credentials:'same-origin'});}catch{throw new ApiError(0,{},contexto);}
    if(!response.ok){const detail=await response.json().catch(()=>({}));if(response.status===401)window.dispatchEvent(new Event('session-expired'));throw new ApiError(response.status,detail,contexto);}
    let data:unknown;try{data=response.status===204?undefined:await response.json();}catch{throw new ApiError(0,{},contexto);}
    return {data:data as T,etag:response.headers.get('ETag')};
}
export type Attempt={path:string;method:string;body:string|undefined;key:string;etag?:string};
export function createAttempt(path:string,body:unknown,method='POST',etag?:string):Attempt{return {path,body:body===undefined?undefined:JSON.stringify(body),method,key:crypto.randomUUID(),etag};}
export async function executeAttempt<T>(attempt:Attempt,checkResult=false){if(checkResult){const prior=await commandResult<T>(attempt);if(prior.completed)return {data:prior.data as T,etag:null};}return request<T>(attempt.path,{method:attempt.method,body:attempt.body,headers:{'Idempotency-Key':attempt.key,...(attempt.etag?{'If-Match':attempt.etag}:{})}});}

const commandPrefix='bovi:pending:';
const storageKey=(path:string)=>principal?commandPrefix+principal+':'+path:undefined;
export function readPending(path:string):Attempt|undefined{try{const key=storageKey(path);const saved=key?sessionStorage.getItem(key):null;return saved?JSON.parse(saved):undefined;}catch{return undefined;}}
export function rememberPending(attempt:Attempt){try{const key=storageKey(attempt.path);if(key)sessionStorage.setItem(key,JSON.stringify(attempt));}catch{/* shortcut: storage may be unavailable, the mounted form still preserves its retry. */}}
export function forgetPending(path:string){try{const key=storageKey(path);if(key)sessionStorage.removeItem(key);}catch{/* shortcut: unavailable tab storage has no stored retry to remove. */}}

/** Nombre del comando de escritura para traducir errores y elegir la confirmación (incluye el inicio de sesión). */
export function comandoDe(path:string,method='POST'):string|undefined{return path==='/sesion/login'?'iniciar_sesion':commandName({path,method});}
export function commandName(attempt:Pick<Attempt,'path'|'method'>):string|undefined{
    const pieces=attempt.path.split('/');const resource=pieces[3];const action=pieces[5];
    const actions:Record<string,string>={confirmar:'confirmar_operacion',acordar:'acordar_operacion',revisiones:'registrar_revision',pesajes:'registrar_pesaje',aprobar:'aprobar_pesaje',correcciones:'corregir_pesaje',reservas:'reservar_venta',liberar:'liberar_reserva',reparto:'repartir_gasto',validar:'validar_pago',aplicaciones:'aplicar_pago',reverso:'revertir_aplicacion',reembolsos:'reembolsar_pago',ajustes:'ajustar_liquidacion',cierre:'cerrar_periodo',cerrar:'cerrar_periodo',reabrir:'reabrir_periodo',membresias:'asignar_membresia'};
    if(resource==='integraciones'&&pieces[6]==='aceptaciones')return 'aceptar_tarifa';
    if(action)return action==='reabrir'&&resource==='operaciones'?'reabrir_operacion':actions[action];
    if(attempt.method==='PATCH'&&resource==='operaciones')return 'editar_operacion';
    if(attempt.method==='PATCH'&&resource==='usuarios')return 'actualizar_usuario';
    return ({contrapartes:'crear_contraparte',predios:'crear_predio',animales:'registrar_animal',operaciones:'crear_operacion',gastos:'registrar_gasto',pagos:'registrar_pago',documentos:'registrar_documento',periodos:'crear_periodo',usuarios:'crear_usuario',movimientos:'registrar_movimiento'} as Record<string,string>)[resource==='inventario'?pieces[4]:resource];
}
export async function commandResult<T>(attempt:Attempt):Promise<{completed:boolean;data?:T}>{
    const command=commandName(attempt);if(!command)return {completed:false};
    const site=attempt.path.split('/')[2];try{const {data}=await request<{estado:string;resultado:T}>(`/sedes/${site}/comandos/${command}/${attempt.key}`);if(data.estado==='COMPLETADA')return {completed:true,data:data.resultado};if(data.estado==='EN_CURSO')throw new ApiError(425,{mensaje:'El servidor todavía está procesando este comando.'},{escritura:true,comando:command});throw new ApiError(0,{},{escritura:true,comando:command});}catch(e){if(e instanceof ApiError&&e.status===404)return {completed:false};if(e instanceof ApiError&&!e.contexto.escritura)throw new ApiError(e.status,e.details,{escritura:true,comando:command});throw e;}
}
