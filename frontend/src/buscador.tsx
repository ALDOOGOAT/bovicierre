// Buscador de la libreta (⌘K / Ctrl+K) — 2026-11-10, tanda «menos app, más claro».
// cmdk aporta el combobox accesible (flechas, Enter, aria-activedescendant); el diálogo es un <dialog> nativo en modo
// modal: lo de atrás queda inerte, Escape lo cierra (evento cancel) y el navegador devuelve el foco a quien lo abrió.
// El filtro es propio (subcadena sin acentos, palabra por palabra): para alguien no técnico es más predecible que el
// difuso de cmdk y deja ordenar primero lo que viene del servidor. La búsqueda remota usa los `q` que la API ya tiene
// (operaciones, animales y contrapartes: búsqueda literal acotada, 200 caracteres); no hay endpoint nuevo.
import {Command} from 'cmdk';
import {useCallback,useEffect,useMemo,useRef,useState,type KeyboardEvent,type ReactNode} from 'react';
import {request} from './api';
import {type Page,type Row,text} from './domain';
import {NavIcon} from './brand';
import {toneOf} from './tone';
import {GRUPOS,PANTALLAS,caminosDe,escribe,menuDe,permitida} from './menu';

type Go=(next:string,row?:Row)=>void;
const mac=typeof navigator!=='undefined'&&/Mac|iPhone|iPad|iPod/.test(navigator.userAgent);

// Palabras del trato con las que alguien buscaría cada pantalla o camino (sin acentos: se normaliza al comparar).
const CLAVES:Record<string,string>={
    'camino-compra':'comprar compra trato proveedor borrador nuevo',
    'camino-venta':'vender venta trato comprador apartar',
    'camino-recibir':'recibir recepcion llegaron llegada corral',
    'camino-entregar':'entregar entrega salieron salida camion',
    'camino-cobro':'cobrar pagar cobro pago abono abonar dinero caja',
    operaciones:'inicio hoy pendientes mesa tratos operaciones',
    contrapartes:'clientes proveedores compradores vendedores directorio telefono',
    predios:'ranchos origen upp',
    animales:'aretes cabezas ganado siniiga qr ficha',
    inventario:'posiciones existencias corral disponible costo',
    pesajes:'bascula tickets kilos peso',
    expediente:'historial hechos evidencia folio',
    cartera:'saldos deudas me deben debo vencimientos cuentas por cobrar por pagar',
    liquidaciones:'cuentas obligaciones saldo comprobante',
    gastos:'costos flete alimento',
    margen:'ganancia utilidad resultado',
    periodos:'cortes mes cierre reabrir',
    usuarios:'permisos roles accesos contrasena',
    sincronizacion:'replicacion sedes nodos',
    documentos:'archivos pdf evidencias',
    captura:'operacion formulario completo experto borrador',
    movimientos:'recepcion entrega formulario completo',
    pagos:'cobros pagos dinero validar aplicar formulario completo',
    simulador:'calculo simular borrador',
    ayuda:'tutoriales videos preguntas recorrido teclado',
};
const normal=(s:string)=>s.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
function coincide(consulta:string,...textos:(string|undefined)[]){const pajar=normal(textos.filter(Boolean).join(' '));return normal(consulta).split(/\s+/).filter(Boolean).every(p=>pajar.includes(p));}

type Resultados={q:string;cargando:boolean;fallo:boolean;tratos:Row[];animales:Row[];partes:Row[]};
const SIN:Resultados={q:'',cargando:false,fallo:false,tratos:[],animales:[],partes:[]};
/** Tratos, aretes y contrapartes de la sede que contienen el texto (5 de cada uno; se espera 250 ms entre teclas). */
function useBusqueda(base:string,consulta:string):Resultados{
    const [r,setR]=useState<Resultados>(SIN);
    useEffect(()=>{const q=consulta.trim().slice(0,200);if(q.length<2){setR(SIN);return;}
        setR(prev=>({...prev,q,cargando:true}));const control=new AbortController();
        const espera=setTimeout(async()=>{const qs='?'+new URLSearchParams({pagina:'1',tamano:'5',q});
            const [o,a,p]=await Promise.allSettled(['/operaciones','/animales','/contrapartes'].map(ruta=>request<Page>(base+ruta+qs,{signal:control.signal})));
            if(control.signal.aborted)return;const filas=(x:PromiseSettledResult<{data:Page}>)=>x.status==='fulfilled'?x.value.data.elementos||[]:[];
            setR({q,cargando:false,fallo:[o,a,p].every(x=>x.status==='rejected'),tratos:filas(o),animales:filas(a),partes:filas(p)});},250);
        return()=>{clearTimeout(espera);control.abort();};},[base,consulta]);
    return r;
}

function Lupa(){return <svg className="icono-lupa" viewBox="0 0 20 20" aria-hidden="true"><path d="M8.6 15.2a6.6 6.6 0 1 0 0-13.2 6.6 6.6 0 0 0 0 13.2zM13.4 13.4L18 18"/></svg>;}
function Voz(){return <svg className="nav-icon" viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><path d="M3 8h3l4-3v10l-4-3H3zM13 7.5c1 .8 1.5 1.6 1.5 2.5s-.5 1.7-1.5 2.5M15.5 5c1.7 1.4 2.5 3 2.5 5s-.8 3.6-2.5 5"/></svg>;}
function Renglon({value,icono,titulo,detalle,pista,onSelect,forceMount}:{value:string;icono:ReactNode;titulo:ReactNode;detalle?:ReactNode;pista?:string;onSelect:()=>void;forceMount?:boolean}){
    return <Command.Item value={value} onSelect={onSelect} forceMount={forceMount}>{icono}<span className="buscador-texto"><strong>{titulo}</strong>{detalle&&<small>{detalle}</small>}</span>{pista&&<span className="buscador-pista">{pista}</span>}</Command.Item>;
}
const aretes=(v:unknown)=>(Array.isArray(v)?v as Row[]:[]).map(x=>({codigo:String(x.codigo_declarado||x.codigo||''),oficial:x.sistema==='SINIIGA'})).filter(x=>x.codigo);

export function Buscador({base,sedeNombre,roles,go,pausado,startTour,cambiarSede}:{base:string;sedeNombre:string;roles:string[];go:Go;pausado:boolean;startTour:()=>void;cambiarSede:()=>void}){
    const [open,setOpen]=useState(false);const [q,setQ]=useState('');const [sel,setSel]=useState('');
    const dialog=useRef<HTMLDialogElement>(null);const trigger=useRef<HTMLButtonElement>(null);const input=useRef<HTMLInputElement>(null);const navegando=useRef(false);
    const res=useBusqueda(base,open?q:'');
    useEffect(()=>{const onKey=(e:globalThis.KeyboardEvent)=>{if(!(e.metaKey||e.ctrlKey)||e.altKey||e.shiftKey||e.key.toLowerCase()!=='k')return;if(pausado&&!dialog.current?.open)return;e.preventDefault();if(dialog.current?.open)dialog.current.close();else setOpen(true);};
        document.addEventListener('keydown',onKey);return()=>document.removeEventListener('keydown',onKey);},[pausado]);
    useEffect(()=>{const d=dialog.current;if(open&&d&&!d.open){d.showModal();input.current?.focus();}},[open]);
    // Al llegar resultados del servidor, el primero queda marcado: es lo que se buscó (un folio, un arete).
    const primero=res.tratos[0]?.id?'trato '+res.tratos[0].id:res.animales[0]?.id?'arete '+res.animales[0].id:res.partes[0]?.id?'parte '+res.partes[0].id:'';
    useEffect(()=>{if(primero)setSel(primero);},[primero]);
    const alCerrar=()=>{setOpen(false);setQ('');setSel('');if(navegando.current){navegando.current=false;return;}
        // El navegador devuelve el foco a quien abrió el diálogo; si ese elemento ya no existe, vuelve al botón.
        if(!document.activeElement||document.activeElement===document.body)trigger.current?.focus();};
    const elegir=useCallback((accion:()=>void)=>{navegando.current=true;dialog.current?.close();accion();
        requestAnimationFrame(()=>{if(!document.activeElement||document.activeElement===document.body)document.getElementById('main-title')?.focus();});},[]);
    const atrapar=(e:KeyboardEvent<HTMLDialogElement>)=>{if(e.key!=='Tab')return;const items=[...e.currentTarget.querySelectorAll<HTMLElement>('input,button:not(:disabled)')];if(!items.length)return;const first=items[0],end=items[items.length-1];
        if(e.shiftKey&&document.activeElement===first){e.preventDefault();end.focus();}else if(!e.shiftKey&&document.activeElement===end){e.preventDefault();first.focus();}};

    const consulta=q.trim();const buscando=consulta.length>0;
    const propias=useMemo(()=>new Set(menuDe(roles).map(p=>p.id)),[roles]);
    const grupoDe=(id:string)=>GRUPOS.find(g=>g.id===PANTALLAS.find(p=>p.id===id)?.grupo)?.titulo;
    const caminos=caminosDe(roles).filter(c=>!buscando||coincide(consulta,c.titulo,c.desc,CLAVES[c.id]));
    // Sin texto: solo el menú de este rol. Con texto: todo lo que el servidor le deja leer, marcando lo de fuera del menú.
    const pantallas=PANTALLAS.filter(p=>permitida(p.id,roles)&&(buscando?coincide(consulta,p.titulo,p.pista,grupoDe(p.id),CLAVES[p.id]):propias.has(p.id)));
    const acciones=[{id:'tour',titulo:'Recorrido guiado con voz',detalle:'Dos minutos por la Bandeja y la Mesa de tratos',run:startTour,icono:<Voz/>,claves:'ayuda tutorial voz'},
        {id:'sede',titulo:'Cambiar de sede',detalle:'Cada sede lleva su propia libreta',run:cambiarSede,icono:<NavIcon name="predios"/>,claves:'sucursal otra sede'}].filter(a=>!buscando||coincide(consulta,a.titulo,a.detalle,a.claves));
    const servidor=res.tratos.length+res.animales.length+res.partes.length;const locales=caminos.length+pantallas.length+acciones.length;
    const corta=consulta.length===1;const esperando=consulta.length>=2&&(res.cargando||res.q!==consulta.slice(0,200));
    const estado=!buscando?'':corta?'Sigue escribiendo para buscar también en tratos, aretes y contrapartes.':esperando?`Buscando «${consulta}» en la libreta de ${sedeNombre}…`:res.fallo?'No se pudo buscar en la sede ahora mismo; las pantallas sí están aquí.':servidor?`${servidor} ${servidor===1?'coincidencia':'coincidencias'} en ${sedeNombre}.`:locales?`Ningún trato, arete ni contraparte con «${consulta}».`:`Nada con «${consulta}» en ${sedeNombre}. Prueba con el folio, el número de arete o el nombre.`;
    const puedeEscribir=escribe(roles);

    return <>
        <button ref={trigger} type="button" className="buscar-launch" onClick={()=>setOpen(true)} aria-haspopup="dialog" aria-keyshortcuts={mac?'Meta+K':'Control+K'}><Lupa/><span className="buscar-texto">Buscar…</span><kbd className="buscar-atajo" aria-hidden="true">{mac?'⌘ K':'Ctrl K'}</kbd></button>
        <dialog ref={dialog} className="paleta" aria-label="Buscar en la libreta de la sede" onClose={alCerrar} onKeyDown={atrapar} onClick={e=>{if(e.target===e.currentTarget)e.currentTarget.close();}}>
            {open&&<Command label="Busca un folio, un arete, un nombre o una pantalla" shouldFilter={false} loop vimBindings={false} value={sel} onValueChange={setSel}>
                <div className="buscador-cabeza"><Lupa/><Command.Input ref={input} value={q} onValueChange={setQ} placeholder="Folio, arete, nombre o pantalla" maxLength={200} enterKeyHint="go" autoCapitalize="none" spellCheck={false}/><button type="button" className="buscador-cerrar" onClick={()=>dialog.current?.close()}>Cerrar<kbd aria-hidden="true">Esc</kbd></button></div>
                <Command.List>
                    {res.tratos.length>0&&<Command.Group heading="Tratos" forceMount>{res.tratos.map(o=>{const abierto=puedeEscribir&&['BORRADOR','ACORDADA'].includes(String(o.estado));const venta=o.tipo==='VENTA';
                        return <Renglon key={String(o.id)} forceMount value={'trato '+o.id} icono={<NavIcon name={venta?'camino-venta':'camino-compra'}/>} titulo={<span className="mono">{text(o.folio)}</span>} detalle={<>{venta?'Venta a ':'Compra a '}{text(o.contraparte)} <span className="badge" data-tone={toneOf(o.estado)}>{text(o.estado)}</span></>} pista={abierto?'Continuar':'Expediente'} onSelect={()=>elegir(()=>go(abierto?(venta?'camino-venta':'camino-compra'):'expediente',o))}/>;})}</Command.Group>}
                    {res.animales.length>0&&<Command.Group heading="Aretes" forceMount>{res.animales.map(a=><Renglon key={String(a.id)} forceMount value={'arete '+a.id} icono={<NavIcon name="animales"/>} titulo={<span className="aretes-tabla">{aretes(a.identificaciones).map((x,i)=><span key={i} className={'arete-mini'+(x.oficial?' oficial':'')}>{x.codigo}</span>)}</span>} detalle={[a.sexo==='H'?'Hembra':a.sexo==='M'?'Macho':'',a.situacion?text(a.situacion):''].filter(Boolean).join(' · ')||undefined} pista="Ficha" onSelect={()=>elegir(()=>go('animales',{id:String(a.id)}))}/>)}</Command.Group>}
                    {res.partes.length>0&&<Command.Group heading="Contrapartes" forceMount>{res.partes.map(p=><Renglon key={String(p.id)} forceMount value={'parte '+p.id} icono={<NavIcon name="contrapartes"/>} titulo={text(p.nombre)} detalle={[p.telefono,p.rfc].filter(Boolean).map(String).join(' · ')||undefined} pista="Directorio" onSelect={()=>elegir(()=>go('contrapartes'))}/>)}</Command.Group>}
                    {caminos.length>0&&<Command.Group heading="Empezar un camino">{caminos.map(c=><Renglon key={c.id} value={c.id} icono={<NavIcon name={c.id}/>} titulo={c.titulo} detalle={c.desc} onSelect={()=>elegir(()=>go(c.id))}/>)}</Command.Group>}
                    {pantallas.length>0&&<Command.Group heading="Ir a">{pantallas.map(p=><Renglon key={p.id} value={'ir '+p.id} icono={<NavIcon name={p.id}/>} titulo={p.titulo} detalle={p.pista} pista={propias.has(p.id)?grupoDe(p.id):'Consulta'} onSelect={()=>elegir(()=>go(p.id))}/>)}</Command.Group>}
                    {acciones.length>0&&<Command.Group heading="Otras acciones">{acciones.map(a=><Renglon key={a.id} value={'accion '+a.id} icono={a.icono} titulo={a.titulo} detalle={a.detalle} onSelect={()=>elegir(a.run)}/>)}</Command.Group>}
                </Command.List>
                <p className="buscador-estado" role="status">{estado}</p>
                <div className="buscador-pie" aria-hidden="true"><span><kbd>↑</kbd><kbd>↓</kbd> moverte</span><span><kbd>Enter</kbd> abrir</span><span><kbd>Esc</kbd> cerrar</span></div>
            </Command>}
        </dialog>
    </>;
}
