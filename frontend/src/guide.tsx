import {useCallback,useEffect,useLayoutEffect,useRef,useState,type CSSProperties,type KeyboardEvent} from 'react';
// Recorrido guiado y centro de ayuda (v4). El recorrido es un port de Proyecto_Contable/frontend/src/components/Tour.js
// (repositorio propio): pasos con voz del navegador, silenciar, progreso y saltar; aquí sin Tailwind/Radix, como diálogo
// accesible (foco atrapado, Escape, foco devuelto) y con realce del elemento real de la interfaz.

type Step={title:string;body:string;target?:string};
// 2026-11-10: el recorrido apunta a la Mesa de tratos y a los caminos (antes, a Nueva operación, Recepción y entrega y
// Liquidaciones: el modo experto). Si un destino no se ve para el rol (p. ej. una tarjeta que no le toca), la tarjeta
// del recorrido sale centrada. Las E2E fijan 7 pasos y los títulos de los dos primeros.
export const TOUR:Step[]=[
    {title:'BoviCierre en dos minutos',body:'Te muestro cómo se lleva un trato, de apuntarlo a cobrarlo. Puedes salir cuando quieras con Escape.'},
    {title:'Lo pendiente de tu sede',body:'La Bandeja empieza por lo que hay que hacer hoy: ganado por recibir, entregas pendientes y lo que hay por cobrar y por pagar, con conteos del servidor. Cada renglón te lleva a su pantalla.',target:'[aria-labelledby="task-title"]'},
    {title:'Elige qué vas a hacer',body:'En la Mesa de tratos eliges un camino: comprar, vender, recibir, entregar o cobrar. Te llevo con una pregunta por paso y nada cuenta hasta que cierras el trato.',target:'.mesa'},
    {title:'Recibe o entrega el ganado',body:'Es un paso físico aparte: marcas por arete las cabezas que llegaron o que salieron. No cambia el importe del trato.',target:'.tarjeta-camino[data-camino="camino-recibir"]'},
    {title:'Cobra o paga',body:'Apuntas el dinero, lo revisas y lo abonas a su cuenta: son pasos separados para que cada saldo quede explicado.',target:'.tarjeta-camino[data-camino="camino-cobro"]'},
    {title:'Encuentra lo que sea',body:'Con Buscar (o Control más K) llegas a un trato por su folio, a un animal por su arete o a cualquier pantalla sin recorrer el menú.',target:'.buscar-launch'},
    {title:'Ayuda siempre a la mano',body:'Las pantallas completas siguen en el menú, en Registro detallado. Aquí están los videos con subtítulos y las preguntas frecuentes; repite este recorrido cuando quieras.',target:'.sidebar a[href="#ayuda"]'},
];

function speak(text:string){
    if(typeof window==='undefined'||!('speechSynthesis' in window))return;
    window.speechSynthesis.cancel();
    const u=new SpeechSynthesisUtterance(text);const voices=window.speechSynthesis.getVoices();
    u.voice=voices.find(v=>v.lang==='es-MX')||voices.find(v=>v.lang.toLowerCase().startsWith('es'))||null;
    u.lang=u.voice?.lang||'es-MX';u.rate=1;
    window.speechSynthesis.speak(u);
}
function hush(){if(typeof window!=='undefined'&&'speechSynthesis' in window)window.speechSynthesis.cancel();}
function voicePreference(){try{return localStorage.getItem('bovi.tour.voz')!=='off';}catch{return true;}}

export function GuidedTour({open,onClose,onStart}:{open:boolean;onClose:()=>void;onStart:()=>void}){
    const [index,setIndex]=useState(0);const [voice,setVoice]=useState(voicePreference);const [rect,setRect]=useState<DOMRect>();
    const card=useRef<HTMLDivElement>(null);const primary=useRef<HTMLButtonElement>(null);const opener=useRef<Element|null>(null);
    const step=TOUR[index];const last=index===TOUR.length-1;
    const close=useCallback(()=>{hush();onClose();},[onClose]);
    const startRef=useRef(onStart);startRef.current=onStart; // el padre recrea la función en cada render: sólo importa al abrir
    useEffect(()=>{if(open&&voice)speak(step.title+'. '+step.body);else hush();},[open,voice,step]);
    // Modal: lo de atrás queda visible (para el realce) pero inerte. Al cerrar se quita `inert` ANTES de devolver el foco
    // (el navegador ignora focus() en elementos inertes); si el botón que lo abrió ya no existe, el foco va al título.
    useEffect(()=>{if(!open)return;opener.current=document.activeElement;setIndex(0);setVoice(voicePreference());startRef.current();
        const behind=[...document.querySelectorAll('.app-shell > .sidebar, .app-shell > .workspace, .app-shell > .skip')];behind.forEach(e=>e.setAttribute('inert',''));
        return()=>{hush();behind.forEach(e=>e.removeAttribute('inert'));const back=opener.current as HTMLElement|null;(back?.isConnected?back:document.getElementById('main-title'))?.focus();};},[open]);
    useEffect(()=>{if(open)primary.current?.focus();},[open,index]);
    const measure=useCallback(()=>{const el=step.target?document.querySelector(step.target):null;const r=el?.getBoundingClientRect();setRect(r&&r.width>0&&r.height>0?r:undefined);},[step]);
    useLayoutEffect(()=>{if(!open)return;const el=step.target?document.querySelector(step.target):null;el?.scrollIntoView({block:'nearest'});measure();window.addEventListener('resize',measure);window.addEventListener('scroll',measure,true);return()=>{window.removeEventListener('resize',measure);window.removeEventListener('scroll',measure,true);};},[open,step,measure]);
    useEffect(()=>{if(!open)return;const onKey=(e:globalThis.KeyboardEvent)=>{if(e.key==='Escape'){e.preventDefault();close();}};document.addEventListener('keydown',onKey);return()=>document.removeEventListener('keydown',onKey);},[open,close]);
    if(!open)return null;
    const trap=(e:KeyboardEvent<HTMLDivElement>)=>{if(e.key!=='Tab')return;const items=[...(card.current?.querySelectorAll<HTMLElement>('button')||[])];if(!items.length)return;const first=items[0],end=items[items.length-1];
        if(e.shiftKey&&document.activeElement===first){e.preventDefault();end.focus();}else if(!e.shiftKey&&document.activeElement===end){e.preventDefault();first.focus();}};
    const toggleVoice=()=>{const next=!voice;setVoice(next);try{localStorage.setItem('bovi.tour.voz',next?'on':'off');}catch{/* preferencia opcional */}};
    // Tarjeta junto al elemento realzado: a la derecha de la barra lateral, debajo de bloques anchos o centrada (móvil/sin destino).
    const place:CSSProperties=!rect?{}:rect.left<320&&rect.width<320?{left:rect.right+24,top:Math.max(16,Math.min(rect.top-24,window.innerHeight-340))}:{left:Math.max(16,Math.min(rect.left,window.innerWidth-436)),top:rect.bottom+20<window.innerHeight-300?rect.bottom+20:Math.max(16,rect.top-320)};
    return <div className="tour-layer">
        <div className={rect?'tour-spot':'tour-dim'} style={rect?{top:rect.top-6,left:rect.left-6,width:rect.width+12,height:rect.height+12}:undefined} aria-hidden="true" onClick={close}/>
        <div ref={card} className={rect?'tour-card anchored':'tour-card'} style={place} role="dialog" aria-modal="true" aria-labelledby="tour-title" aria-describedby="tour-body" onKeyDown={trap}>
            <div className="tour-head"><p className="paso-tour">Paso {index+1} de {TOUR.length}</p><button type="button" className="tour-voice" aria-pressed={voice} onClick={toggleVoice}>Narración por voz</button></div>
            <h2 id="tour-title">{step.title}</h2>
            <p id="tour-body">{step.body}</p>
            <div className="tour-foot"><div className="tour-dots" aria-hidden="true">{TOUR.map((_,k)=><span key={k} data-on={k===index?'true':undefined}/>)}</div>
                <div className="tour-actions"><button type="button" className="secondary" onClick={close}>Saltar</button>{index>0&&<button type="button" className="secondary" onClick={()=>setIndex(index-1)}>Anterior</button>}<button ref={primary} type="button" className="primary" onClick={()=>last?close():setIndex(index+1)}>{last?'Terminar':'Siguiente'}</button></div></div>
        </div>
    </div>;
}

export const VIDEOS=[
    {id:'compra',title:'Comprar ganado y confirmar el trato',body:'Cliente o proveedor, ganado por arete, precio por cabeza, revisión del cálculo del servidor y confirmación.'},
    {id:'recepcion',title:'Recibir el ganado comprado',body:'Abrir la operación confirmada, marcar los animales por arete y registrar la recepción.'},
    {id:'venta-cobro',title:'Vender, entregar y cobrar',body:'Reservar el ganado, confirmar la venta, registrar la entrega y aplicar el cobro a la liquidación.'},
    {id:'tablero',title:'Tablero, cartera y margen',body:'Pendientes de la sede, obligaciones por vencer y resultado económico con su fecha de corte.'},
];
const FAQ:[string,string][]=[
    ['¿Por qué no puedo confirmar una compra por kilo?','Una compra por kilo necesita un pesaje aprobado del lote. Registra el ticket de báscula en el paso de Pesaje, apruébalo y vuelve a confirmar.'],
    ['¿Registrar un pago ya salda la deuda?','No. Primero registras el dinero, luego lo validas y al final lo aplicas a una liquidación compatible. Así cada saldo queda explicado.'],
    ['¿Qué pasa si dos personas reservan el mismo animal?','Sólo una reserva queda activa. La otra persona ve un aviso de conflicto y puede elegir otro animal; nunca se vende dos veces.'],
    ['¿Cómo corrijo algo que ya confirmé?','Los hechos confirmados no se editan: se registra un ajuste, un reverso o una nueva versión, y el original queda en el expediente.'],
    ['¿Qué es el periodo económico?','Un mes calendario por sede. Sólo puede haber uno abierto; al cerrarlo, el servidor congela un resumen que puede reabrirse con motivo.'],
    ['¿El comprobante PDF es una factura?','No. Es un comprobante interno de la liquidación; no es un CFDI ni sustituye la facturación.'],
];

export function HelpCenter({startTour}:{startTour:()=>void}){
    return <>
        <section className="panel help-intro"><div><h2>Aprende BoviCierre en minutos</h2><p className="muted">Un recorrido de dos minutos con voz y videos cortos con subtítulos de cada tarea frecuente.</p></div><button type="button" className="primary" onClick={startTour}>Iniciar recorrido guiado</button></section>
        <section className="panel" aria-labelledby="videos-title"><div className="section-heading"><h2 id="videos-title">Videos de uso</h2><span className="badge">Subtítulos en español</span></div><p className="muted">Se grabaron antes del rediseño del 9 de noviembre de 2026: los pasos y las reglas son los mismos, pero las pantallas se ven distintas. Hoy los tratos empiezan en la Mesa de tratos de la Bandeja.</p>
            <div className="video-grid">{VIDEOS.map(v=><article className="video-card" key={v.id}><video controls preload="none" poster={`/videos/${v.id}-poster.jpg`} aria-describedby={`video-${v.id}`}><source src={`/videos/${v.id}.mp4`} type="video/mp4"/><track kind="captions" srcLang="es" label="Español" src={`/videos/${v.id}.vtt`} default/></video><h3>{v.title}</h3><p className="muted" id={`video-${v.id}`}>{v.body}</p></article>)}</div>
        </section>
        <section className="panel" aria-labelledby="faq-title"><h2 id="faq-title">Preguntas frecuentes</h2><div className="faq">{FAQ.map(([q,a])=><details key={q}><summary>{q}</summary><p>{a}</p></details>)}</div></section>
        <section className="panel narrow" aria-labelledby="keys-title"><h2 id="keys-title">Teclado y accesibilidad</h2><ul className="key-list"><li><kbd>Tab</kbd> y <kbd>Mayús</kbd>+<kbd>Tab</kbd> recorren campos y botones en orden.</li><li><kbd>Enter</kbd> envía el formulario activo; <kbd>Espacio</kbd> marca casillas de ganado.</li><li><kbd>Ctrl</kbd>+<kbd>K</kbd> (<kbd>⌘</kbd>+<kbd>K</kbd> en Mac) abre el buscador: escribe un folio, un arete, un nombre o una pantalla y elige con las flechas y <kbd>Enter</kbd>.</li><li><kbd>Esc</kbd> cierra el buscador y el recorrido guiado; el foco vuelve a donde estabas.</li><li>El enlace “Ir al contenido” aparece con el primer <kbd>Tab</kbd> de cada página.</li><li>Las animaciones se apagan si tu sistema pide reducir movimiento.</li></ul></section>
    </>;
}
