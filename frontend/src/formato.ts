// Un solo formateador de dinero, kilos, precios y fechas (2026-11-10, tanda «Dinero legible»).
// La pantalla nunca recalcula: recibe el decimal del servidor como texto, lo agrupa por miles y fija su escala
// (2 en dinero, 3 en kilos) sin pasar por punto flotante. Si el servidor manda más decimales que la escala, solo se
// quitan los ceros sobrantes; un dígito distinto de cero se muestra tal cual (aquí nunca se redondea).
// Formato visible del dinero: «47,880.00 MXN» (las E2E lo fijan en .settlement-summary, Cartera y ciclos del animal).
// Kilos con la escala de la báscula: «4,520.500 kg» (las E2E leen «100.000» en el historial de tickets).

const DECIMAL = /^[-−]?\d+(?:\.\d+)?$/;

/**
 * Decimal del servidor agrupado por miles: «47880» con escala 2 → «47,880.00»; «912.00000000» con escala 3 → «912.000».
 * Sin escala conserva los decimales que vengan. `undefined` si el valor no es un decimal.
 */
export function agrupar(valor: unknown, escala?: number): string | undefined {
  const s = typeof valor === 'number' && Number.isFinite(valor) ? String(valor) : typeof valor === 'string' ? valor.trim() : '';
  if (!DECIMAL.test(s)) return undefined;
  const negativo = /^[-−]/.test(s);
  const [entero, fraccion = ''] = s.replace(/^[-−]/, '').split('.');
  let f = fraccion;
  if (escala !== undefined) {
    if (f.length < escala) f = f.padEnd(escala, '0');
    else if (f.length > escala && /^0*$/.test(f.slice(escala))) f = f.slice(0, escala);
  }
  const e = entero.replace(/^0+(?=\d)/, '').replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  const cero = /^0*$/.test(entero + f);
  return (negativo && !cero ? '−' : '') + e + (f ? '.' + f : '');
}

const importeDe = (v: unknown) => (v && typeof v === 'object' && 'importe' in v ? (v as { importe: unknown }).importe : v);
function monedaDe(v: unknown) {
  const m = v && typeof v === 'object' && 'moneda' in v ? (v as { moneda?: unknown }).moneda : undefined;
  return typeof m === 'string' && m ? m : 'MXN';
}

/** Importe sin moneda («47,880.00»), de un `Dinero` o de un decimal suelto. */
export const importe = (v: unknown) => agrupar(importeDe(v), 2);

/** Dinero completo: «47,880.00 MXN». «No disponible» si el servidor no lo dio. */
export function dinero(v: unknown, vacio = 'No disponible'): string {
  const i = importe(v);
  return i === undefined ? vacio : `${i} ${monedaDe(v)}`;
}

/** Peso de báscula: «4,520.500 kg», de `{kg}` o de un decimal suelto. */
export function kilos(v: unknown, vacio = 'No disponible'): string {
  const k = v && typeof v === 'object' && 'kg' in v ? (v as { kg: unknown }).kg : v;
  const t = agrupar(k, 3);
  return t === undefined ? vacio : `${t} kg`;
}

/** Cantidad de un concepto según su unidad: «3 cabezas», «912.000 kg», «1,000.00 MXN». */
export function cantidad(v: unknown, unidad: unknown): string {
  if (unidad === 'KG') return kilos(v);
  if (unidad === 'MXN') return dinero(v);
  const n = agrupar(v, unidad === 'CABEZA' ? 0 : undefined);
  if (n === undefined) return 'No disponible';
  return unidad === 'CABEZA' ? `${n} ${n === '1' ? 'cabeza' : 'cabezas'}` : n;
}

/**
 * Precio unitario pactado sin ceros sobrantes: «52.5000» → «52.50 MXN por kg»; «47.1250» → «47.125 MXN por kg».
 * Siempre al menos dos decimales, como se dice un precio en voz alta.
 */
export function precio(v: unknown, unidad?: unknown): string {
  const s = agrupar(importeDe(v));
  if (s === undefined) return 'No disponible';
  const [e, f = ''] = s.split('.');
  const recorte = f.replace(/0+$/, '');
  const fr = recorte.length <= 2 ? f.slice(0, 2).padEnd(2, '0') : recorte;
  const por = unidad === 'KG' ? ' por kg' : unidad === 'CABEZA' ? ' por cabeza' : '';
  return `${e}.${fr} MXN${por}`;
}

const SOLO_DIA = /^\d{4}-\d{2}-\d{2}$/;
const ISO = /^\d{4}-\d{2}-\d{2}(?:[T ][\d:.]+(?:Z|[+-]\d{2}:?\d{2})?)?$/;
const DIA = new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium', timeZone: 'America/Mexico_City' });
const DIA_HORA = new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'America/Mexico_City' });

/** ¿Es una fecha ISO del servidor («2026-11-08» o «2026-11-08T16:05:00Z»)? */
export const esFechaIso = (v: unknown): v is string => typeof v === 'string' && ISO.test(v) && !isNaN(new Date(v).getTime());

function aFecha(v: unknown): Date | undefined {
  if (typeof v !== 'string' || !v) return undefined;
  // Un día suelto se lee a mediodía UTC para que la zona horaria no lo mueva al día anterior.
  const d = SOLO_DIA.test(v) ? new Date(v + 'T12:00:00Z') : new Date(v);
  return isNaN(d.getTime()) ? undefined : d;
}

/** Día legible: «8 nov 2026». */
export function fecha(v: unknown, vacio = 'Sin fecha'): string {
  const d = aFecha(v);
  return d ? DIA.format(d) : vacio;
}

/** Día y hora: «8 nov 2026, 10:05 a.m.»; un día sin hora se queda en «8 nov 2026». */
export function fechaHora(v: unknown, vacio = 'Sin fecha'): string {
  if (typeof v === 'string' && SOLO_DIA.test(v)) return fecha(v, vacio);
  const d = aFecha(v);
  return d ? DIA_HORA.format(d) : vacio;
}
