// Tono visual de un estado devuelto por la API. Sólo cambia color/ícono; el texto visible sigue siendo el valor real.
export type Tone='positive'|'progress'|'attention'|'critical'|'neutral';
const tones:Record<Tone,string[]>={
    positive:['CONFIRMADA','DISPONIBLE','ACTIVO','APROBADO','VALIDADO','COMPARABLE','SIN_OBSERVACIONES','ENTREGADA','RECIBIDA','PAGADA','CERRADA_VENTA','CERRADO','APLICADO','ACEPTADA','COMPLETA','DISPONIBLE_LOCAL','CONVERGENTE'],
    progress:['ACORDADA','PROPUESTA','REGISTRADO','ABIERTO','VENDIDA_PENDIENTE_ENTREGA','PARCIAL','PROVISIONAL','EN_PROCESO','ACTUALIZADO'],
    attention:['BORRADOR','PENDIENTE','PENDIENTE_RECEPCION','POR_COBRAR','POR_PAGAR','CON_OBSERVACIONES','VENCIDA','REABIERTO','PENDIENTE_CONVERGENCIA','SUSTITUIDA'],
    critical:['CANCELADA','ANULADA','RECHAZADA','BLOQUEADO','NO_COMPARABLE','MUERTE','PERDIDA','FALLIDO','REVERSO','INDISPONIBLE'],
    neutral:['BAJA','REVOCADO','OTRO']
};
const index=new Map(Object.entries(tones).flatMap(([tone,values])=>values.map(v=>[v,tone as Tone])));
export function toneOf(value:unknown):Tone{
    if(typeof value!=='string')return 'neutral';
    return index.get(value.trim().toUpperCase().replaceAll(' ','_'))||'neutral';
}
// Columnas cuyos valores son estados y se presentan como insignia.
export const statusColumns=new Set(['estado','estado_entrega','estado_pago','situacion','estado_convergencia','estado_revision','resultado']);
