// Utilidades puras de los caminos guiados (2026-11-10, tanda «Camino de compra fluido»).
// Sin React ni red: se prueban en tests/caminos.test.ts. Ningún importe se calcula aquí.

export type Sexo = 'M' | 'H';

/** Un arete leído de «Apuntar varios»: el código tal como se escribió, su clave normalizada y su problema si lo hay. */
export type LineaArete = {
  codigo: string;
  /** Mayúsculas sin espacios ni guiones: la misma normalización que el servidor (bovi.fn_codigo). */
  clave: string;
  sexo: Sexo;
  /** Renglón del texto (1, 2, 3…) para decir dónde está el problema. */
  renglon: number;
  problema?: string;
};

const SEPARA = /[\s,;]+/;
const MARCA_SEXO = /^(m|h|macho|hembra|machos|hembras)$/i;
const CODIGO = /^[A-Za-z0-9-]+$/;
export const MAX_ARETE = 40;

export const claveArete = (codigo: string) => codigo.toUpperCase().replace(/[\s-]/g, '');
const sexoDeMarca = (m: string): Sexo => (m[0].toLowerCase() === 'h' ? 'H' : 'M');

/**
 * Lee lo que se pegó o escribió en «Apuntar varios»: un arete por renglón, o varios separados por espacios, comas o
 * punto y coma. Una H o una M junto a un arete le cambia el sexo: la marca va con el arete que la precede en el renglón
 * («0712 H») o, si va primero, con el que la sigue («H 0712»). Los demás usan `porDefecto`.
 * Los problemas (formato, repetido) se marcan por arete sin descartar los buenos.
 */
export function leerAretes(texto: string, porDefecto: Sexo): LineaArete[] {
  const lineas: LineaArete[] = [];
  const vistos = new Map<string, number>();
  texto.split(/\r?\n/).forEach((renglon, i) => {
    const piezas = renglon.trim().split(SEPARA).filter(Boolean);
    const sexos = sexosPorPieza(piezas, porDefecto);
    piezas.forEach((codigo, j) => {
      if (MARCA_SEXO.test(codigo)) return;
      const sexo = sexos[j];
      const clave = claveArete(codigo);
      let problema: string | undefined;
      if (codigo.length > MAX_ARETE) problema = `Tiene más de ${MAX_ARETE} caracteres. Revisa que no se hayan juntado dos aretes.`;
      else if (!CODIGO.test(codigo) || !/[A-Za-z0-9]/.test(codigo)) problema = 'Usa solo letras, números y guiones (sin acentos, ñ ni símbolos).';
      else if (vistos.has(clave)) problema = vistos.get(clave) === i + 1 ? 'Repetido en este mismo renglón.' : `Repetido: ya está en el renglón ${vistos.get(clave)}.`;
      if (!problema) vistos.set(clave, i + 1);
      lineas.push({codigo, clave, sexo, renglon: i + 1, problema});
    });
  });
  return lineas;
}

/** A qué pieza (arete) pertenece cada marca H/M del renglón: a la anterior; si va primero, a la siguiente. */
function duenosDeMarcas(piezas: string[]): Map<number, number> {
  const duenos = new Map<number, number>();
  piezas.forEach((p, j) => {
    if (!MARCA_SEXO.test(p)) return;
    let k = j - 1;
    while (k >= 0 && MARCA_SEXO.test(piezas[k])) k--;
    if (k < 0) {
      k = j + 1;
      while (k < piezas.length && MARCA_SEXO.test(piezas[k])) k++;
    }
    if (k < piezas.length) duenos.set(j, k);
  });
  return duenos;
}

function sexosPorPieza(piezas: string[], porDefecto: Sexo): Sexo[] {
  const sexos = piezas.map(() => porDefecto);
  duenosDeMarcas(piezas).forEach((arete, marca) => (sexos[arete] = sexoDeMarca(piezas[marca])));
  return sexos;
}

/** Quita del texto los aretes que ya se apuntaron y deja los que fallaron (cada uno con su marca), para corregirlos sin volver a escribir todo. */
export function quitarApuntados(texto: string, apuntados: Set<string>): string {
  return texto
    .split(/\r?\n/)
    .map((renglon) => {
      const piezas = renglon.trim().split(SEPARA).filter(Boolean);
      const marcaDe = new Map<number, string>();
      duenosDeMarcas(piezas).forEach((arete, marca) => marcaDe.set(arete, piezas[marca]));
      return piezas
        .map((p, j) => (MARCA_SEXO.test(p) || apuntados.has(claveArete(p)) ? '' : marcaDe.has(j) ? `${p} ${marcaDe.get(j)}` : p))
        .filter(Boolean)
        .join(' ');
    })
    .filter(Boolean)
    .join('\n');
}

export type Sentido = '' | 'POR_COBRAR' | 'POR_PAGAR';

/** Minúsculas sin acentos ni espacios dobles, para buscar «gonzalez» y encontrar «González». */
export const normalizarBusqueda = (s: string) =>
  s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/\s+/g, ' ').trim();

/**
 * Filtra las cuentas por sentido («Te debe» = POR_COBRAR, «Le debes» = POR_PAGAR) y por texto: cada palabra escrita
 * debe aparecer en el folio o en el nombre de la contraparte (`describe`), sin importar acentos ni mayúsculas.
 */
export function filtrarCuentas<T extends Record<string, unknown>>(
  cuentas: T[],
  filtro: {texto: string; sentido: Sentido},
  describe: (cuenta: T) => string,
): T[] {
  const palabras = normalizarBusqueda(filtro.texto).split(' ').filter(Boolean);
  return cuentas.filter((c) => {
    if (filtro.sentido && c.direccion !== filtro.sentido) return false;
    if (!palabras.length) return true;
    const donde = normalizarBusqueda(describe(c));
    return palabras.every((p) => donde.includes(p));
  });
}

/** Tamaño de letra de la pantalla de la báscula para que la lectura quepa (≈40 unidades del dibujo). */
export function letraBascula(lectura: string, ancho = 40, maximo = 15, minimo = 7): number {
  const n = Math.max(1, lectura.length);
  const cabe = ancho / (n * 0.62);
  return Math.round(Math.min(maximo, Math.max(minimo, cabe)) * 10) / 10;
}
