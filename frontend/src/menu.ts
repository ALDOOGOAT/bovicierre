// Menú por rol (2026-11-10, tanda «menos app, más claro»).
// El servidor deja LEER cualquier pantalla a todo miembro de la sede (AccessService.authorize sin mutación); la única
// lectura exclusiva de ADMIN es Usuarios (UserController / CommandService.query). Así que el menú no protege nada:
// solo decide qué ve cada quien. Una pantalla fuera del menú sigue abriendo por su hash y por el buscador (⌘K).
// Los cinco caminos ya no van en el menú: viven en la Mesa de tratos de la Bandeja y en el buscador.
import {CAMINOS} from './caminos';

export type Grupo='hoy'|'tratos'|'dinero'|'control'|'detallado'|'ayuda';
type Escena='nota'|'corral'|'libreta'|'fierro';
export type Pantalla={id:string;titulo:string;grupo:Grupo;roles:readonly string[];escena:Escena;pista?:string};

const ESCRIBE=['ADMIN','OPERADOR'];
const COBRA=['ADMIN','CAJA'];
const TODOS=['ADMIN','OPERADOR','CAJA','AUDITOR'];

/** `titulo` es el h1 (#main-title) y el título de la pestaña; las E2E fijan Bandeja, Cartera, Nueva operación y Ayuda y tutoriales. */
export const PANTALLAS:Pantalla[]=[
    {id:'operaciones',titulo:'Bandeja',grupo:'hoy',roles:TODOS,escena:'nota',pista:'Pendientes y mesa de tratos'},
    {id:'contrapartes',titulo:'Contrapartes',grupo:'tratos',roles:['OPERADOR'],escena:'nota'},
    {id:'predios',titulo:'Predios',grupo:'tratos',roles:['OPERADOR'],escena:'nota'},
    {id:'animales',titulo:'Animales',grupo:'tratos',roles:['OPERADOR','AUDITOR'],escena:'corral'},
    {id:'inventario',titulo:'Posiciones',grupo:'tratos',roles:['OPERADOR','AUDITOR'],escena:'corral'},
    {id:'pesajes',titulo:'Tickets y pesajes',grupo:'tratos',roles:['OPERADOR','AUDITOR'],escena:'nota'},
    {id:'expediente',titulo:'Expediente',grupo:'tratos',roles:TODOS,escena:'nota'},
    {id:'cartera',titulo:'Cartera',grupo:'dinero',roles:['CAJA','AUDITOR'],escena:'libreta'},
    {id:'liquidaciones',titulo:'Liquidaciones',grupo:'dinero',roles:['CAJA','AUDITOR'],escena:'libreta'},
    {id:'gastos',titulo:'Gastos',grupo:'dinero',roles:TODOS,escena:'libreta'},
    {id:'margen',titulo:'Margen',grupo:'dinero',roles:['AUDITOR'],escena:'libreta'},
    {id:'periodos',titulo:'Periodos',grupo:'control',roles:['AUDITOR'],escena:'fierro'},
    {id:'usuarios',titulo:'Usuarios y permisos',grupo:'control',roles:[],escena:'fierro'},
    {id:'sincronizacion',titulo:'Sincronización',grupo:'control',roles:['AUDITOR'],escena:'fierro'},
    {id:'documentos',titulo:'Documentos',grupo:'control',roles:['AUDITOR'],escena:'fierro'},
    // Registro detallado: las pantallas completas que hacen lo mismo que un camino, con todos los campos a la vista.
    {id:'captura',titulo:'Nueva operación',grupo:'detallado',roles:ESCRIBE,escena:'nota'},
    {id:'movimientos',titulo:'Recepción y entrega',grupo:'detallado',roles:ESCRIBE,escena:'corral'},
    {id:'pagos',titulo:'Cobros y pagos',grupo:'detallado',roles:COBRA,escena:'libreta'},
    {id:'simulador',titulo:'Simulador',grupo:'detallado',roles:['ADMIN'],escena:'libreta'},
    {id:'ayuda',titulo:'Ayuda y tutoriales',grupo:'ayuda',roles:TODOS,escena:'fierro'},
];

/** `encabezado:false` = el grupo va sin rótulo en la barra lateral (Bandeja arriba, Ayuda al pie). */
export const GRUPOS:{id:Grupo;titulo:string;encabezado:boolean}[]=[
    {id:'hoy',titulo:'Hoy',encabezado:false},
    {id:'tratos',titulo:'Tratos y ganado',encabezado:true},
    {id:'dinero',titulo:'Dinero',encabezado:true},
    {id:'control',titulo:'Control',encabezado:true},
    {id:'detallado',titulo:'Registro detallado',encabezado:true},
    {id:'ayuda',titulo:'Ayuda',encabezado:false},
];

export const esAdmin=(roles:readonly string[])=>roles.includes('ADMIN');
export const escribe=(roles:readonly string[])=>roles.some(r=>ESCRIBE.includes(r));
export const cobra=(roles:readonly string[])=>roles.some(r=>COBRA.includes(r));

/** Pantallas del menú de este rol; ADMIN las conserva todas. */
export function menuDe(roles:readonly string[]){return PANTALLAS.filter(p=>esAdmin(roles)||p.roles.some(r=>roles.includes(r)));}
/** El servidor permite leerla (solo Usuarios exige ADMIN). */
export function permitida(id:string,roles:readonly string[]){return id!=='usuarios'||esAdmin(roles);}
/** Caminos que este rol puede empezar. */
export function caminosDe(roles:readonly string[]){return CAMINOS.filter(c=>c.roles.some(r=>roles.includes(r)));}

export const esCamino=(screen:string)=>screen.startsWith('camino-');
export const pantalla=(screen:string)=>PANTALLAS.find(p=>p.id===screen);
export function tituloDe(screen:string){return CAMINOS.find(c=>c.id===screen)?.titulo||pantalla(screen)?.titulo||'Bandeja';}
/** En un camino, el menú marca la Bandeja: el camino es un paso de la Mesa de tratos. */
export const seccionDe=(screen:string)=>esCamino(screen)?'operaciones':screen;

/** Pantallas completas que tienen un camino guiado equivalente: se ofrece «hazlo paso a paso». */
export const ALTERNOS:Record<string,string[]>={captura:['camino-compra','camino-venta'],movimientos:['camino-recibir','camino-entregar'],pagos:['camino-cobro'],liquidaciones:['camino-cobro']};

/** Preferencia local opcional (abrir/cerrar grupos); sin almacenamiento, gana el valor por defecto. */
export function leerPreferencia(clave:string):boolean|undefined{try{const v=localStorage.getItem(clave);return v===null?undefined:v==='abierto';}catch{return undefined;}}
export function guardarPreferencia(clave:string,abierto:boolean){try{localStorage.setItem(clave,abierto?'abierto':'cerrado');}catch{/* preferencia opcional */}}
