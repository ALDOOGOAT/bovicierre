// Marca e iconografía originales de BoviCierre (SVG en línea, sin dependencias ni assets externos).
/** Fierro «B en Caja Abierta» (2026-11-11): la B dentro de un corral con la puerta abierta a la derecha.
 *  Se lee como un fierro de herrar: «Caja B». Trazo parejo y la panza de la B sin tocar el asta, como hierro forjado. */
export function BrandMark({size=36}:{size?:number}){
    return <svg className="brand-mark" aria-hidden="true" viewBox="0 0 100 100" width={size} height={size}>
        <rect width="100" height="100" rx="22" fill="currentColor"/>
        <g transform="translate(14 14) scale(.72)" fill="none" stroke="var(--brand-mark-ink,#F2C230)" strokeWidth="9" strokeLinecap="round" strokeLinejoin="round">
            <path d="M80 40V18H20V82H80V60"/>
            <path d="M38 32V68M38 32H51A9 9 0 0 1 51 50M51 50H53A9 9 0 0 1 53 68H38"/>
        </g>
    </svg>;
}
export function Brand({subtitle='GANADO EN PIE'}:{subtitle?:string}){
    return <div className="brand"><BrandMark/><span>BoviCierre<small>{subtitle}</small></span></div>;
}
const paths:Record<string,string>={'camino-compra':'M7 3.5h6l2 2.5v9.5a1.5 1.5 0 0 1-1.5 1.5h-7A1.5 1.5 0 0 1 5 15.5V6zM10 7.5h.01M7.5 12h5','camino-venta':'M3 16h14M5 16V9l5-4 5 4v7M8.5 16v-4h3v4','camino-recibir':'M3 4v13M17 4v13M3 7h14M3 11h14M3 15h14M3 15L17 7','camino-entregar':'M2 6h9v7H2zM11 9h3.5L17 11.5V13h-6M5 15.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zM14 15.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z','camino-cobro':'M3 6h14v9H3zM3 9h14M6 12.5h3M13 12.5h1',
    operaciones:'M3 13l2.5-7h9L17 13M3 13v3.5h14V13M3 13h4l1 2h4l1-2h4',
    captura:'M10 4v12M4 10h12',
    contrapartes:'M7.5 9a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM3 16c0-2.5 2-4.5 4.5-4.5S12 13.5 12 16M13.5 4.3a2.5 2.5 0 0 1 0 4.4M14.5 11.8c1.5.6 2.5 2.2 2.5 4.2',
    predios:'M10 17s5-4.6 5-8.5a5 5 0 0 0-10 0C5 12.4 10 17 10 17zM10 10.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4z',
    pesajes:'M10 4v12M5 16h10M4 7h12M4 7l-2 5h4zM16 7l-2 5h4z',
    expediente:'M3 6.5V15a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8a1 1 0 0 0-1-1h-6L8.5 5H4a1 1 0 0 0-1 1.5z',
    inventario:'M10 3l7 3.5-7 3.5-7-3.5zM3 10l7 3.5 7-3.5M3 13.5L10 17l7-3.5',
    animales:'M4 4h6.5L16 9.5 10.5 15 4 8.5zM7.2 7.2h.01',
    movimientos:'M2 6h9v7H2zM11 9h3.5L17 11.5V13h-6M5 15.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zM14 15.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z',
    liquidaciones:'M5 3h10v14l-2.5-1.5L10 17l-2.5-1.5L5 17zM7.5 7h5M7.5 10h5',
    pagos:'M3 6h13a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H3zM3 6l9-2.5V6M13 11h.01',
    gastos:'M10 3v14M13.5 6H8.5a2 2 0 0 0 0 4h3a2 2 0 0 1 0 4H6',
    cartera:'M6 4h8v13H6zM8 7.5h4M8 10.5h4M8 13.5h2.5',
    margen:'M3 15l4.5-4.5 3 3L17 7M12.5 7H17v4.5',
    simulador:'M5 3h10v14H5zM7.5 6h5M7.5 10h.01M10 10h.01M12.5 10h.01M7.5 13h.01M10 13h.01M12.5 13h.01',
    periodos:'M4 5h12v11H4zM4 8.5h12M7.5 3v3M12.5 3v3',
    usuarios:'M10 3l6 2.5v4c0 3.6-2.6 6.4-6 7.5-3.4-1.1-6-3.9-6-7.5v-4zM7.5 10l1.8 1.8L13 8',
    sincronizacion:'M15.5 8A6 6 0 0 0 4.6 6.6M4.5 12a6 6 0 0 0 10.9 1.4M15.5 4v4h-4M4.5 16v-4h4',
    documentos:'M6 3h5.5L15 6.5V17H6zM11 3v4h4M8.5 10.5h4M8.5 13.5h4',ayuda:'M10 17.5a7.5 7.5 0 1 0 0-15 7.5 7.5 0 0 0 0 15zM7.9 7.7a2.2 2.2 0 0 1 4.3.8c0 1.5-2.2 1.8-2.2 3.2M10 14.3v.2'
};
export function NavIcon({name}:{name:string}){
    return <svg className="nav-icon" aria-hidden="true" viewBox="0 0 20 20" width="18" height="18"><path d={paths[name]||paths.documentos}/></svg>;
}
export function initials(name:string){return name.replace(/^DEMO\s+/i,'').split(/\s+/).filter(Boolean).slice(0,2).map(w=>w[0]!.toUpperCase()).join('')||'U';}
