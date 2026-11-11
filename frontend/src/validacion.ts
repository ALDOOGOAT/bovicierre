// Validación de los campos de dinero, peso y porcentaje (2026-11-10, tanda «Que no se rompa»).
// Mensajes estilo GOV.UK: dicen qué escribir y dan un ejemplo en el formato que la propia app muestra.
// La pantalla solo revisa el formato; el servidor sigue siendo la única fuente de importes y totales.
import * as z from 'zod/mini';
import {ejemploDe, enterosDe, normalizarDecimal} from './domain';

export type ReglaDecimal = {
  /** Decimales que guarda el servidor (2 dinero, 3 kg, 4 precio unitario, 6 porcentaje). */
  escala: number;
  /** Qué escribir, en segunda persona y sin punto final: «el precio pactado». */
  que: string;
  /** Unidad que se nombra en el mensaje: «en pesos», «en kilos». */
  unidad?: string;
};

/** Campos conocidos por nombre. El nombre del campo es el mismo que viaja al servidor. */
const REGLAS: [RegExp, ReglaDecimal][] = [
  [/^precio_unitario$/, {escala: 4, que: 'el precio pactado', unidad: 'en pesos'}],
  [/^neto$/, {escala: 3, que: 'el peso neto del ticket', unidad: 'en kilos'}],
  [/^peso_.+$/, {escala: 3, que: 'el peso medido', unidad: 'en kilos'}],
  [/^(importe|monto)$/, {escala: 2, que: 'el importe', unidad: 'en pesos'}],
  [/^asignacion_\d+$/, {escala: 2, que: 'el importe de esta cabeza', unidad: 'en pesos'}],
  [/^cargos_pactados$/, {escala: 2, que: 'los cargos', unidad: 'en pesos'}],
  [/^bonificaciones_pactadas$/, {escala: 2, que: 'los descuentos', unidad: 'en pesos'}],
  [/^deduccion_pct$/, {escala: 6, que: 'el porcentaje de merma', unidad: 'sin el signo %'}],
];

export function reglaDecimal(name: string): ReglaDecimal | undefined {
  return REGLAS.find(([patron]) => patron.test(name))?.[1];
}

const fraseEjemplo = (r: ReglaDecimal) => `por ejemplo ${ejemploDe(r.escala)}`;

/** Esquema Zod de un campo decimal: entra el texto tal como se escribió, sale el texto canónico para el servidor. */
export function esquemaDecimal(r: ReglaDecimal, requerido = true) {
  const ej = fraseEjemplo(r);
  const escribe = `Escribe ${r.que}${r.unidad ? ' ' + r.unidad : ''}, ${ej}.`;
  return z.pipe(
    z.string().check(
      z.overwrite((v) => normalizarDecimal(v)),
      z.refine((v) => !requerido || v !== '', {error: escribe, abort: true}),
      z.refine((v) => v === '' || !/^[-−–]/.test(v), {error: `Escribe ${r.que} sin signo de menos, ${ej}.`, abort: true}),
      z.refine((v) => v === '' || !/^\d+,\d+$/.test(v), {error: `Usa punto para los decimales, ${ej}.`, abort: true}),
      // «52.5.0» no tiene letras: el problema es el segundo punto.
      z.refine((v) => v === '' || !/^[\d.]*\.[\d.]*\.[\d.]*$/.test(v), {error: `Escribe un solo punto decimal, ${ej}.`, abort: true}),
      z.refine((v) => v === '' || /^\d+(?:\.\d+)?$/.test(v), {error: `Escribe solo el número, sin letras, ${ej}.`, abort: true}),
      z.refine((v) => (v.split('.')[1] || '').length <= r.escala, {error: `Usa como máximo ${r.escala} decimales, ${ej}.`, abort: true}),
      z.refine((v) => v.split('.')[0].replace(/^0+(?=\d)/, '').length <= enterosDe(r.escala), {
        error: r.escala === 6 ? `Escribe un porcentaje menor que 100, ${ej}.` : 'La cantidad es demasiado grande. Revisa que no sobren ceros.',
        abort: true,
      }),
    ),
    z.transform((v) => {
      if (v === '') return '';
      const [entero, fraccion = ''] = v.split('.');
      return `${entero.replace(/^0+(?=\d)/, '')}.${fraccion.padEnd(r.escala, '0')}`;
    }),
  );
}

/** Primer problema del valor escrito, o `undefined` si está bien. Un campo opcional vacío está bien. */
export function errorDecimal(valor: string, r: ReglaDecimal, requerido = true): string | undefined {
  const resultado = esquemaDecimal(r, requerido).safeParse(valor);
  return resultado.success ? undefined : resultado.error.issues[0]?.message;
}

/** Revisa todos los campos decimales conocidos de un formulario antes de enviarlo. */
export function revisarFormulario(form: HTMLFormElement): Record<string, string> {
  const errores: Record<string, string> = {};
  for (const el of Array.from(form.elements)) {
    if (!(el instanceof HTMLInputElement) || el.disabled || !el.name || el.type === 'hidden') continue;
    const r = reglaDecimal(el.name);
    if (!r) continue;
    const problema = errorDecimal(el.value, r, el.required);
    if (problema) errores[el.name] = problema;
  }
  return errores;
}
