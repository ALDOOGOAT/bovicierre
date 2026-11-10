// Códigos del servidor en palabras del trato (2026-11-10, tanda «Dinero legible»).
// El código sigue viajando y guardándose igual; aquí solo se decide cómo se lee en pantalla.
// Donde una prueba o una persona técnica necesita el código (expediente, sincronización, posiciones), se muestra al lado.
import type { Row } from './domain';
import { agrupar } from './formato';

const PALABRAS: Record<string, string> = {
  // Trato
  BORRADOR: 'Borrador', ACORDADA: 'Acordada', CONFIRMADA: 'Cerrada', CANCELADA: 'Cancelada', ANULADA: 'Anulada',
  COMPRA: 'Compra', VENTA: 'Venta',
  // Entrega física y ganado
  PENDIENTE: 'Pendiente', PARCIAL: 'Parcial', COMPLETA: 'Completa',
  DISPONIBLE: 'Disponible', PENDIENTE_RECEPCION: 'Por recibir', VENDIDA_PENDIENTE_ENTREGA: 'Vendida, por entregar',
  CERRADA_VENTA: 'Vendida y entregada', BAJA: 'Dada de baja', VIGENTE: 'Vigente',
  CONVERGENTE: 'Visible en ambas sedes', PENDIENTE_CONVERGENCIA: 'Llegando a la otra sede', DISPONIBLE_LOCAL: 'Solo en esta sede',
  RECEPCION: 'Recepción', ENTREGA: 'Entrega', MUERTE: 'Muerte', PERDIDA: 'Pérdida',
  // Báscula y condiciones
  PROPUESTA: 'Propuesta', APROBADO: 'Aprobado', CORREGIDO: 'Corregido', ACEPTADA: 'Aceptada', SUSTITUIDA: 'Sustituida',
  KG: 'kg', CABEZA: 'cabeza', MXN: 'MXN', NETO_REPORTADO: 'Neto del ticket',
  BASE: 'Precio pactado', CARGO: 'Cargo', ABONO: 'Abono', BONIFICACION: 'Bonificación', DEDUCCION: 'Deducción',
  // Dinero
  POR_COBRAR: 'Por cobrar', POR_PAGAR: 'Por pagar',
  COBRO: 'Cobro recibido', PAGO: 'Pago entregado',
  REGISTRADO: 'Por validar', VALIDADO: 'Validado', REVERTIDO: 'Revertido',
  NORMAL: 'Normal', REEMBOLSO: 'Reembolso', APLICACION: 'Abono aplicado', REVERSO: 'Abono revertido',
  EFECTIVO: 'Efectivo', TRANSFERENCIA: 'Transferencia', CHEQUE: 'Cheque', OTRO: 'Otro',
  PRECIO_GANADO: 'Precio del ganado', BONIFICACION_COMERCIAL: 'Bonificación comercial',
  COSTO: 'Costo', CAPITALIZABLE: 'Se suma al costo del ganado', DIRECTO_VENTA: 'Gasto directo de la venta',
  POR_CABEZA: 'Por cabeza', POR_PESO_MEDIDO: 'Por peso medido', IMPORTE_INDIVIDUAL: 'Importe por cabeza',
  INVENTARIO: 'Costo del inventario', COSTO_VENTA: 'Costo de la venta',
  // Reportes y control
  ACTUALIZADO: 'Al día', PROVISIONAL: 'Provisional', CERRADO: 'Cerrado', ABIERTO: 'Abierto', REABIERTO: 'Reabierto',
  CIERRE: 'Cierre', REAPERTURA: 'Reapertura',
  PROPIETARIO: 'Leído en el nodo de esta sede', REPLICA: 'Leído de la copia (réplica)',
  ASINCRONA: 'Copia en segundos', SIN_OBSERVACIONES: 'Sin observaciones', CON_OBSERVACIONES: 'Con observaciones', RECHAZADA: 'Rechazada',
  ACTIVO: 'Activo', BLOQUEADO: 'Bloqueado', REVOCADO: 'Revocado',
  ADMIN: 'Administración', OPERADOR: 'Operador', CAJA: 'Caja', AUDITOR: 'Auditoría',
  FISICA: 'Persona física', MORAL: 'Persona moral', M: 'Macho', H: 'Hembra',
  TICKET_BASCULA: 'Ticket de báscula', CONTRATO: 'Contrato', GUIA_MOVILIZACION: 'Guía de movilización',
  COMPROBANTE_PAGO: 'Comprobante de pago', IDENTIFICACION: 'Identificación',
  REVISION_ADMINISTRATIVA_PENDIENTE: 'la revisión administrativa de los documentos',
};

/**
 * Un código del servidor en palabras («POR_PAGAR» → «Por pagar»). Un código desconocido se lee en minúsculas
 * con mayúscula inicial; cualquier otro texto (nombres, folios) se devuelve tal cual.
 */
export function palabra(valor: unknown): string {
  if (valor === null || valor === undefined || valor === '') return 'No disponible';
  if (typeof valor === 'boolean') return valor ? 'Sí' : 'No';
  const s = String(valor).trim();
  const clave = s.toUpperCase().replace(/\s+/g, '_');
  if (PALABRAS[clave]) return PALABRAS[clave];
  if (/^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$|^[A-Z]{4,}$/.test(s)) {
    const t = s.replaceAll('_', ' ').toLowerCase();
    return t.charAt(0).toUpperCase() + t.slice(1);
  }
  return s;
}

/** Quién le debe a quién, en palabras del tratante (como en el camino de cobro). */
export const quienDebe = (direccion: unknown) => (direccion === 'POR_COBRAR' ? 'Te debe' : direccion === 'POR_PAGAR' ? 'Le debes' : 'No disponible');

/** Hacia dónde se movió el dinero de un pago: entra (cobro) o sale (pago). */
export const sentidoPago = (tipo: unknown) => (tipo === 'COBRO' ? 'Te pagó' : tipo === 'PAGO' ? 'Le pagaste' : 'No disponible');

export type EstadoCuenta = { palabra: string; tono: 'positive' | 'progress' | 'attention' | 'critical' | 'neutral' };

/** Centavos exactos de un importe del servidor; solo para comparar, nunca para calcular un total. */
function centavos(v: unknown): bigint | undefined {
  const s = agrupar(v && typeof v === 'object' && 'importe' in v ? (v as { importe: unknown }).importe : v, 2);
  if (s === undefined) return undefined;
  const limpio = s.replace(/[,−]/g, '');
  if (!/^\d+\.\d{2}$/.test(limpio)) return undefined;
  const c = BigInt(limpio.replace('.', ''));
  return s.startsWith('−') ? -c : c;
}

/**
 * Estado de una cuenta (liquidación) dicho con lo que el servidor ya entregó: saldo, total y vencimiento.
 * Solo compara; no suma ni resta.
 */
export function estadoCuenta(l: Row, hoy: string): EstadoCuenta {
  const saldo = centavos(l.saldo);
  const total = centavos(l.total);
  if (saldo === undefined) return { palabra: 'Sin saldo informado', tono: 'neutral' };
  if (saldo <= 0n) return { palabra: 'Saldada', tono: 'positive' };
  const vence = typeof l.vence_el === 'string' ? l.vence_el : '';
  if (vence && vence < hoy) return { palabra: 'Vencida', tono: 'critical' };
  if (total !== undefined && saldo < total) return { palabra: 'Abonada en parte', tono: 'progress' };
  return { palabra: 'Pendiente', tono: 'attention' };
}

/** ¿El importe del servidor es mayor que cero? */
export const conImporte = (v: unknown) => (centavos(v) ?? 0n) > 0n;
/** ¿Dos importes del servidor son iguales al centavo? */
export const mismoImporte = (a: unknown, b: unknown) => {
  const x = centavos(a);
  return x !== undefined && x === centavos(b);
};
