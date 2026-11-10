import {createContext,useContext,useEffect,useId,useRef,useState,type FormEvent,type ReactNode} from 'react';
import {ApiError,comandoDe,createAttempt,executeAttempt,request,readPending,rememberPending,forgetPending,keepAttempt,type Attempt} from './api';
import {text,decimal,type Row,type Page} from './domain';
import {toneOf,statusColumns,type Tone} from './tone';
import {importe,esFechaIso,fechaHora} from './formato';
import {palabra} from './palabras';
import {traducirError,problemaCampo,fraseCampo,confirmacionDe,type ClaveAccion,type DatosError} from './errores';
import {reglaDecimal,errorDecimal,revisarFormulario} from './validacion';
import {avisarGuardado} from './aviso';
export function useResource<T>(path:string,revision=0){
    const [state,setState]=useState<{data?:T;etag?:string;loading:boolean;error?:Error}>({loading:true});
    const [reload,setReload]=useState(0);
    useEffect(()=>{let active=true;const controller=new AbortController();setState({loading:true});request<T>(path,{signal:controller.signal}).then(r=>{if(active)setState({data:r.data,etag:r.etag||undefined,loading:false});}).catch(error=>{if(active)setState({loading:false,error});});return()=>{active=false;controller.abort();};},[path,revision,reload]);
    return {...state,reload:()=>setReload(n=>n+1)};
}
/**
 * Lo que una pantalla le presta a sus avisos de error: a qué paso puede llevar cada acción
 * («Ir a la báscula») y datos que el servidor no repite, como el folio del ticket pendiente.
 */
export type ContextoAvisos={acciones?:Partial<Record<ClaveAccion,()=>void>>;datos?:DatosError};
export const AvisosContexto=createContext<ContextoAvisos>({});
/**
 * Aviso de error en dos líneas: qué pasó (título) y qué hacer. Si la pantalla sabe llevar al paso que lo
 * arregla, aparece el botón. Código, regla y referencia quedan plegados en «Datos para soporte».
 */
export function Notice({error,children}:{error?:Error;children?:ReactNode}){
    const ctx=useContext(AvisosContexto);
    if(!error)return null;
    const api=error instanceof ApiError?error:undefined;
    const t=api?traducirError(api.detalle(),{...api.contexto,datos:{...api.contexto.datos,...ctx.datos}}):{que:error.message,hacer:undefined,accion:undefined};
    const ir=t.accion?ctx.acciones?.[t.accion.clave]:undefined;
    const soporte=api?[api.details.regla_id&&'Regla '+api.details.regla_id,api.details.codigo&&'código '+api.details.codigo,api.details.correlation_id&&'referencia '+api.details.correlation_id].filter(Boolean).join(' · '):'';
    return <div className="notice error aviso" role="alert">
        <strong className="aviso-que">{t.que}</strong>
        {t.hacer&&<span className="aviso-hacer">{t.hacer}</span>}
        {children}
        {ir&&t.accion&&<button type="button" className="secondary aviso-accion" onClick={ir}>{t.accion.etiqueta}</button>}
        {soporte&&<details className="aviso-soporte"><summary>Datos para soporte</summary><small className="mono">{soporte}</small></details>}
    </div>;
}
/** Qué decir cuando una lista está vacía de verdad (no por un filtro): título y la siguiente acción útil. */
export type Vacio={titulo:string;texto:string};
const VACIO:Vacio={titulo:'Todo listo para empezar',texto:'Todavía no hay registros en esta sede. Usa la acción de esta pantalla para agregar el primero.'};
export function State({loading,error,empty,reload,children,vacio=VACIO}:{loading:boolean;error?:Error;empty?:boolean;reload:()=>void;children:ReactNode;vacio?:Vacio}){
    if(loading)return <div className="loading" role="status"><p>Consultando datos de la sede…</p>{[0,1,2,3].map(n=><span key={n} className="skeleton" aria-hidden="true"/>)}</div>;
    if(error)return <div className="empty"><Notice error={error}/><button className="secondary" onClick={reload}>Volver a consultar</button></div>;
    if(empty)return <div className="empty"><span className="empty-mark" aria-hidden="true"/><strong>{vacio.titulo}</strong><p>{vacio.texto}</p></div>;
    return children;
}
/** Errores por campo del último intento (del servidor o de la revisión local) y un contador para saber si ya se atendieron. */
const FieldErrors=createContext<{errores:Record<string,string>;intento:number}>({errores:{},intento:0});
const FormScope=createContext('');
/**
 * Campo con etiqueta persistente. Los de dinero, peso y porcentaje (validacion.ts) usan teclado decimal,
 * se revisan al salir del campo y, después del primer error, en cada tecla. El mensaje queda junto al campo
 * y se enlaza con aria-describedby.
 */
export function Field({label,name,type='text',required=true,value,onChange,options,help,error,disabled=false,placeholder='Selecciona…'}:{label:string;name:string;type?:string;required?:boolean;value:string;onChange:(value:string)=>void;options?:{value:string;label:string}[];help?:string;error?:string;disabled?:boolean;placeholder?:string}){
    const ctx=useContext(FieldErrors);const scope=useContext(FormScope);const id=scope?`${scope}-${name}`:name;
    const regla=!options&&type==='text'?reglaDecimal(name):undefined;
    const [local,setLocal]=useState<string>();const [vivo,setVivo]=useState(false);const [atendido,setAtendido]=useState(-1);
    const delIntento=ctx.intento!==atendido?ctx.errores[name]:undefined;
    const shown=error||local||delIntento;
    function revisar(v:string,alSalir:boolean){
        if(!regla)return;
        // Al salir de un campo vacío no se regaña (la persona puede estar recorriendo el formulario).
        if(alSalir&&!vivo&&!v.trim()){setLocal(undefined);return;}
        const problema=errorDecimal(v,regla,required);setLocal(problema);if(problema)setVivo(true);
    }
    function cambiar(v:string){
        onChange(v);
        const pendiente=!!delIntento;
        if(pendiente){setAtendido(ctx.intento);setVivo(true);}
        if(vivo||pendiente)revisar(v,false);
    }
    const describe=[shown&&`${id}-error`,help&&`${id}-help`].filter(Boolean).join(' ')||undefined;
    const decimalMode=regla||name.includes('importe')||name.includes('precio')||name==='neto';
    return <label className="field" htmlFor={id}><span>{label}{required?' *':''}</span>{options?<select id={id} name={name} value={value} required={required} onChange={e=>cambiar(e.target.value)} disabled={disabled} aria-invalid={!!shown} aria-describedby={describe}><option value="">{placeholder}</option>{options.map(o=><option key={o.value} value={o.value}>{o.label}</option>)}</select>:<input id={id} name={name} type={type} value={value} required={required} onChange={e=>cambiar(e.target.value)} onBlur={e=>revisar(e.target.value,true)} disabled={disabled} autoComplete={type==='password'?'current-password':name==='login'?'username':'off'} inputMode={decimalMode?'decimal':undefined} spellCheck={regla?false:undefined} aria-invalid={!!shown} aria-describedby={describe}/>}{shown&&<small className="field-error" id={`${id}-error`}>{shown}</small>}{help&&<small id={`${id}-help`}>{help}</small>}</label>;
}
/** Etiqueta visible de un campo del formulario (sin el asterisco de obligatorio). */
function etiquetaDe(el:HTMLElement|null){return el?.closest('label')?.querySelector(':scope > span')?.textContent?.replace(/\s*\*$/,'').trim()||'Este dato';}
function irAlCampo(id:string){const el=document.getElementById(id);if(el){el.focus();el.scrollIntoView?.({block:'center'});}}
/**
 * Formulario de comando. Conserva Idempotency-Key, If-Match y el reintento manual con la misma clave (nunca reintenta solo).
 * `bloqueo`: razón visible y anunciada por la que el botón principal no se puede usar todavía (p. ej. cambios sin guardar).
 * `exito`: texto del aviso de confirmación; por omisión sale del comando (errores.ts).
 */
export function CommandForm({path,build,method='POST',etag,children,label,onDone,bloqueo,exito}:{path:string;build:(form:FormData)=>unknown;method?:string;etag?:string;children:ReactNode;label:string;onDone?:(data:Row)=>void;bloqueo?:string;exito?:string}){
    const scope=useId();const [attempt,setAttempt]=useState<Attempt|undefined>(()=>readPending(path));const [busy,setBusy]=useState(false);const [error,setError]=useState<Error>();const [success,setSuccess]=useState(false);const ref=useRef<HTMLDivElement>(null);const formRef=useRef<HTMLFormElement>(null);
    const [locales,setLocales]=useState<Record<string,string>>({});const [intento,setIntento]=useState(0);
    const unresolved=!!attempt;
    const enfocar=()=>setTimeout(()=>ref.current?.focus(),0);
    async function execute(current:Attempt,retry=false){setBusy(true);setError(undefined);setLocales({});setSuccess(false);try{const {data}=await executeAttempt<Row>(current,retry);forgetPending(path);setAttempt(undefined);setSuccess(true);avisarGuardado(exito||confirmacionDe(comandoDe(current.path,current.method)),undefined,current.key);onDone?.(data);}catch(e){const err=e as Error;setError(err);setIntento(n=>n+1);if(!keepAttempt(err)){forgetPending(path);setAttempt(undefined);}enfocar();}finally{setBusy(false);}}
    function submit(e:FormEvent<HTMLFormElement>){
        e.preventDefault();if(attempt){void execute(attempt,true);return;}
        const form=e.currentTarget;const revision=revisarFormulario(form);
        if(Object.keys(revision).length){setError(undefined);setSuccess(false);setLocales(revision);setIntento(n=>n+1);enfocar();return;}
        setLocales({});
        try{const next=createAttempt(path,build(new FormData(form)),method,etag);rememberPending(next);setAttempt(next);void execute(next);}catch(e){setError(e as Error);setIntento(n=>n+1);enfocar();}
    }
    // Campos del servidor: junto al campo si existe en este formulario; si no, una frase con acción (nunca el nombre técnico).
    const campos=error instanceof ApiError?(error.details.campos||[]):[];
    const cubre=error instanceof ApiError?(error.traduccion.cubre||[]):[];
    const idDe=(campo:string)=>`${scope}-${campo}`;
    const existe=(campo:string)=>{if(typeof document==='undefined'||!formRef.current)return false;const el=document.getElementById(idDe(campo));return !!el&&formRef.current.contains(el);};
    const enCampo=campos.filter(f=>existe(f.campo));
    const sueltos=campos.filter(f=>!existe(f.campo)&&!cubre.includes(f.campo));
    const errores={...Object.fromEntries(enCampo.map(f=>[f.campo,problemaCampo(f.problema)])),...locales};
    const enlace=(campo:string,mensaje:string)=><li key={campo}><a href={'#'+idDe(campo)} onClick={ev=>{ev.preventDefault();irAlCampo(idDe(campo));}}>{etiquetaDe(typeof document!=='undefined'?document.getElementById(idDe(campo)):null)}: {mensaje}</a></li>;
    const nLocales=Object.keys(locales).length;
    const bloqueado=!unresolved&&!busy&&!!bloqueo;
    return <form ref={formRef} onSubmit={submit} className="command">
        <div ref={ref} tabIndex={-1} className="command-avisos">
            {nLocales>0&&<div className="notice error aviso" role="alert"><strong className="aviso-que">{nLocales===1?'Revisa este dato antes de seguir.':`Revisa estos ${nLocales} datos antes de seguir.`}</strong><ul className="aviso-lista">{Object.entries(locales).map(([campo,mensaje])=>enlace(campo,mensaje))}</ul></div>}
            {error&&<Notice error={error}>{(enCampo.length>0||sueltos.length>0)&&<ul className="aviso-lista">{enCampo.map(f=>enlace(f.campo,problemaCampo(f.problema)))}{sueltos.map(f=><li key={f.campo}>{fraseCampo(f.campo,f.problema)}</li>)}</ul>}</Notice>}
        </div>
        <FormScope.Provider value={scope}><FieldErrors.Provider value={{errores,intento}}><fieldset disabled={busy||unresolved}>{children}</fieldset></FieldErrors.Provider></FormScope.Provider>
        {success&&<p className="notice success" role="status">Registro confirmado por el servidor.</p>}
        {error instanceof ApiError&&error.status===409&&!busy&&<button className="secondary" type="button" onClick={()=>{forgetPending(path);setAttempt(undefined);setError(undefined);}}>Resolver conflicto y volver a capturar</button>}
        {unresolved&&!busy&&<p className="notice">La captura está protegida. Reintenta con el mismo contenido y la misma clave; no crees otro registro.</p>}
        {bloqueo!==undefined&&<p className="aviso-bloqueo" id={`${scope}-bloqueo`} role="status">{bloqueado?bloqueo:''}</p>}
        <button disabled={busy||bloqueado} aria-describedby={bloqueado?`${scope}-bloqueo`:undefined} className="primary">{busy?'Esperando respuesta…':unresolved?'Reintentar el mismo comando':label}</button>
    </form>;
}
const UUID=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
// Identificadores técnicos completos en monoespaciado; el texto no se recorta ni se sustituye.
/** Aretes del animal como etiquetas: el código es texto real; el sistema (SINIIGA, interno…) queda en el título. */
function Aretes({value}:{value:unknown}){const list=Array.isArray(value)?(value as Row[]).map(v=>({codigo:String(v.codigo_declarado||v.codigo||''),sistema:String(v.sistema||'')})):[{codigo:String(value),sistema:''}];return <span className="aretes-tabla">{list.map((a,i)=><span key={i} className={'arete-mini'+(a.sistema==='SINIIGA'?' oficial':'')} title={a.sistema||undefined}>{a.codigo}{a.sistema&&<span className="sr-only"> ({a.sistema})</span>}</span>)}</span>;}
const Nada=()=><><span className="nil" aria-hidden="true">—</span><span className="sr-only">No disponible</span></>;
// Fechas ISO del servidor siempre como «8 nov 2026» (con hora si la trae); nunca «2026-11-08T16:05:00Z».
function Cell({value,numeric}:{value:unknown;numeric?:boolean}){if(value===null||value===undefined||value==='')return <Nada/>;if(numeric&&typeof value==='string')return <>{decimal(value)}</>;if(esFechaIso(value))return <time dateTime={value}>{fechaHora(value)}</time>;const shown=text(value);return UUID.test(shown)?<span className="uuid">{shown}</span>:<>{shown}</>;}
/**
 * Pastilla de estado con forma de arete: la palabra del trato, el tono y una figura por tono (punto, aro, rombo, raya),
 * nunca solo color. `codigo` deja el código del servidor al lado en chico, donde técnicos y pruebas lo leen.
 */
export function Estado({value,tono,codigo,children}:{value?:unknown;tono?:Tone;codigo?:boolean;children?:ReactNode}){
    const v=typeof value==='string'?value:'';
    return <span className="estado"><span className="badge" data-tone={tono||toneOf(v)}>{children??palabra(v)}</span>{codigo&&v&&<code className="estado-codigo">{text(v)}</code>}</span>;
}
/** Conteo animado de un número entero ya entregado por el servidor (no se usa para dinero). Respeta movimiento reducido. */
export function CountUp({value}:{value:number}){
    const reduced=()=>typeof matchMedia==='function'&&matchMedia('(prefers-reduced-motion: reduce)').matches;
    const [shown,setShown]=useState(()=>reduced()?value:0);
    useEffect(()=>{if(reduced()){setShown(value);return;}let raf=0;const start=performance.now();const tick=(t:number)=>{const k=Math.min(1,(t-start)/700);setShown(Math.round(value*(1-Math.pow(1-k,4))));if(k<1)raf=requestAnimationFrame(tick);};raf=requestAnimationFrame(tick);return()=>cancelAnimationFrame(raf);},[value]);
    return <>{shown}</>;
}
// Importe con la moneda en menor tamaño; el texto conserva «1,000.00 MXN» para lectores y pruebas. El dinero no se anima.
export function Amount({value}:{value:unknown}){const i=importe(value);if(i===undefined)return <>No disponible</>;const m=value&&typeof value==='object'&&'moneda' in value?(value as {moneda?:unknown}).moneda:undefined;const moneda=typeof m==='string'&&m?m:'MXN';return <>{i} <span className="unit">{moneda}</span></>;}
/**
 * Columna de una tabla. `palabras`: el código del servidor en palabras (palabras.ts); `codigo`: además, el código en chico.
 * `ref`: referencia técnica tenue al final (el UUID completo queda en el texto; a la vista se recorta).
 * `render`: celda propia (dinero con contexto, quién debe, folio).
 */
export type Columna={key:string;label:string;money?:boolean;numeric?:boolean;palabras?:boolean;codigo?:boolean;ref?:boolean;render?:(row:Row)=>ReactNode};
/** Nombre de lo que abre el botón «Abrir …» para lectores de pantalla: nunca el UUID. */
function nombreFila(row:Row,i:number){
    if(row.folio)return text(row.folio);
    if(row.ticket_folio)return 'ticket '+text(row.ticket_folio);
    if(row.nombre)return text(row.nombre);
    if(row.concepto)return text(row.concepto);
    return 'renglón '+(i+1);
}
function Flecha(){return <svg className="abrir-flecha" viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" focusable="false"><path d="M3 8h9.5M8.5 4l4 4-4 4" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></svg>;}
function celda(c:Columna,row:Row):ReactNode{
    const v=row[c.key];
    if(c.render)return c.render(row);
    if(c.ref)return typeof v==='string'&&v?<span className="uuid ref" title={v}>{v}</span>:<Nada/>;
    if((c.key==='identificacion'||c.key==='identificaciones')&&v)return <Aretes value={v}/>;
    if(statusColumns.has(c.key)&&typeof v==='string')return <Estado value={v} codigo={c.codigo}/>;
    if(c.palabras&&typeof v==='string'&&v)return <>{palabra(v)}{c.codigo&&<code className="estado-codigo">{text(v)}</code>}</>;
    return <Cell value={v} numeric={c.numeric}/>;
}
/**
 * Tabla de registros. `onSelect` agrega la acción «Abrir»: al final («Detalle») o, con `abrirEn`, en la primera celda
 * —el folio o la fecha se vuelven el botón— para que no se esconda detrás del desplazamiento horizontal.
 * `nombre` dice qué se abre («liquidación C-2026-000007»); el botón siempre empieza por «Abrir».
 */
export function DataTable({rows,columns,onSelect,nombre=nombreFila,abrirEn,etiqueta='Registros de la sede',clase}:{rows:Row[];columns:Columna[];onSelect?:(row:Row)=>void;nombre?:(row:Row,i:number)=>string;abrirEn?:string;etiqueta?:string;clase?:string}){
    const enCelda=!!onSelect&&!!abrirEn&&columns.some(c=>c.key===abrirEn);
    const claseTd=(c:Columna)=>c.ref?'ref-celda':c.money||c.numeric?'numeric':['tipo','direccion','unidad','unidad_precio','naturaleza'].includes(c.key)?'short-value':'';
    return <div className={'table-region'+(clase?' '+clase:'')} role="region" aria-label={etiqueta} tabIndex={0}><table><thead><tr>{columns.map(c=><th className={c.money||c.numeric?'numeric':c.ref?'ref-celda':''} key={c.key} scope="col">{c.label}</th>)}{onSelect&&!enCelda&&<th scope="col">Detalle</th>}</tr></thead><tbody>{rows.map((row,index)=><tr key={String(row.id||index)}>{columns.map(c=><td className={claseTd(c)} key={c.key}>{enCelda&&c.key===abrirEn?<button type="button" className="abrir-fila" aria-label={'Abrir '+nombre(row,index)} onClick={()=>onSelect!(row)}><span className="abrir-contenido">{celda(c,row)}</span><Flecha/></button>:celda(c,row)}</td>)}{onSelect&&!enCelda&&<td><button type="button" className="text-button" onClick={()=>onSelect(row)}>Abrir<span className="sr-only"> {nombre(row,index)}</span></button></td>}</tr>)}</tbody></table></div>;
}
type Opcion=string|{value:string;label:string};
/**
 * Lista paginada del servidor con búsqueda y filtros. `buscar` puede traducir lo escrito antes de consultar
 * (p. ej. un folio a la referencia de su operación); `render` reemplaza la tabla genérica por una propia.
 */
export function List({path,columns=[],revision=0,onSelect,filters=[],nombre,abrirEn,render,buscar,etiquetaBusqueda='Buscar en esta lista',vacio,etiqueta}:{path:string;columns?:Columna[];revision?:number;onSelect?:(row:Row)=>void;filters?:{name:string;label:string;options:Opcion[]}[];nombre?:(row:Row,i:number)=>string;abrirEn?:string;render?:(rows:Row[])=>ReactNode;buscar?:(q:string)=>Promise<string>|string;etiquetaBusqueda?:string;vacio?:Vacio;etiqueta?:string}){
    const [page,setPage]=useState(1);const [query,setQuery]=useState('');const [search,setSearch]=useState('');const [values,setValues]=useState<Record<string,string>>({});const qs=new URLSearchParams({pagina:String(page),tamano:'20',...(search?{q:search}:{}),...Object.fromEntries(Object.entries(values).filter(([,value])=>value))});const res=useResource<Page>(path+(path.includes('?')?'&':'?')+qs.toString(),revision);
    async function enviar(e:FormEvent<HTMLFormElement>){e.preventDefault();const q=query.trim();let valor=q;if(q&&buscar){try{valor=await buscar(q);}catch{valor=q;}}setSearch(valor);setPage(1);}
    const opcion=(o:Opcion)=>typeof o==='string'?{value:o,label:palabra(o)}:o;
    return <><form className="list-filters" aria-label="Buscar y filtrar registros" onSubmit={e=>void enviar(e)}><Field name="q" label={etiquetaBusqueda} type="search" required={false} value={query} onChange={setQuery}/>{filters.map(f=><Field key={f.name} name={f.name} label={f.label} required={false} value={values[f.name]||''} placeholder="Todos" onChange={value=>{setValues(current=>({...current,[f.name]:value}));setPage(1);}} options={f.options.map(opcion)}/>)}<button className="secondary" type="submit">Buscar</button></form><State {...res} empty={!search&&!Object.values(values).some(Boolean)&&!res.data?.elementos?.length} vacio={vacio}>{res.data&&<>{res.data.elementos.length?(render?render(res.data.elementos):<DataTable rows={res.data.elementos} columns={columns} onSelect={onSelect} nombre={nombre} abrirEn={abrirEn} etiqueta={etiqueta}/>):<p className="notice">No hay resultados con estos criterios. Cambia la búsqueda o los filtros.</p>}</>}</State>{res.data&&<div className="pagination"><span>{res.data.total} registros · Página {page}</span><div><button className="secondary" disabled={page===1} onClick={()=>setPage(p=>p-1)}>Anterior</button><button className="secondary" disabled={page*20>=res.data.total} onClick={()=>setPage(p=>p+1)}>Siguiente</button></div></div>}</>;
}
