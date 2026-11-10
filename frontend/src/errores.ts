// Traducción de errores del servidor al lenguaje del tratante (2026-11-10, tanda «Que no se rompa»).
// Cada error responde dos preguntas: qué pasó y qué hacer. El código, la regla y la referencia
// quedan para soporte (letra chica plegada), nunca como título. Se tutea y se usan las palabras del trato.
// Fuentes de la tabla: RAISE EXCEPTION de db/migrations (codigo + regla_id + campos) y ApiErrors.java.

export type DetalleError = {
  status: number;
  codigo?: string;
  mensaje?: string;
  regla_id?: string;
  correlation_id?: string;
  campos?: {campo: string; problema: string}[];
};
/** Pasos a los que un aviso puede llevar; cada pantalla registra los que tiene. */
export type ClaveAccion = 'bascula' | 'precio' | 'ganado' | 'apartar' | 'recargar';
export type DatosError = {
  /** Folio del ticket de báscula que falta aprobar, si la pantalla lo conoce. */
  folio_ticket?: string;
};
export type ContextoError = {
  /** Comando de escritura que se intentó (`acordar_operacion`, `registrar_pago`…); ausente en consultas. */
  comando?: string;
  escritura?: boolean;
  datos?: DatosError;
};
export type Traduccion = {
  que: string;
  hacer?: string;
  accion?: {clave: ClaveAccion; etiqueta: string};
  /** Campos del servidor que este mensaje ya explica (no se repiten como lista). */
  cubre?: string[];
};

type Entrada = {
  codigo?: string;
  regla?: string;
  comando?: string[];
  campo?: string;
  t: (c: ContextoError, d: DetalleError) => Traduccion;
};

const IR_BASCULA = {clave: 'bascula', etiqueta: 'Ir a la báscula'} as const;
const IR_PRECIO = {clave: 'precio', etiqueta: 'Ir al precio'} as const;
const RECARGAR = {clave: 'recargar', etiqueta: 'Recargar el trato'} as const;
const CONFIRMAR = ['confirmar_operacion'];

/** De lo más específico a lo más general: gana la primera entrada que coincide. */
export const TABLA_ERRORES: Entrada[] = [
  // ── Báscula y precio por kilo (RN-012..014) ─────────────────────────────
  {
    codigo: 'BV013',
    regla: 'RN-014',
    campo: 'pesaje_base_id',
    t: (c) => ({
      que: c.datos?.folio_ticket ? `Falta aprobar el ticket ${c.datos.folio_ticket}.` : 'Falta aprobar el pesaje del lote.',
      hacer: 'El precio es por kilo: primero aprueba el ticket de la báscula y después vuelve a intentarlo.',
      accion: IR_BASCULA,
      cubre: ['pesaje_base_id'],
    }),
  },
  {
    codigo: 'BV013',
    regla: 'RN-014',
    t: () => ({
      que: 'El ticket de báscula no pesa las mismas cabezas del lote.',
      hacer: 'Corrige el ticket para que lleve exactamente las cabezas del trato, o cambia las cabezas y vuelve a pesar.',
      accion: IR_BASCULA,
    }),
  },
  {
    codigo: 'BV013',
    regla: 'RN-013',
    comando: ['aprobar_pesaje'],
    t: () => ({
      que: 'Este ticket ya no se puede aprobar.',
      hacer: 'Puede que ya esté aprobado o que se haya corregido. Recarga para ver cómo quedó.',
      accion: RECARGAR,
    }),
  },
  {
    codigo: 'BV013',
    regla: 'RN-013',
    campo: 'animales',
    t: () => ({
      que: 'La corrección debe pesar las mismas cabezas que el ticket original.',
      hacer: 'Deja las mismas cabezas y cambia solo el peso o el folio.',
      cubre: ['animales'],
    }),
  },
  {
    codigo: 'BV013',
    regla: 'RN-013',
    campo: 'corrige_a_id',
    t: () => ({
      que: 'La corrección tiene que ser del mismo trato y del mismo lote.',
      hacer: 'Abre el ticket original desde su trato y corrígelo ahí.',
      cubre: ['corrige_a_id'],
    }),
  },
  {
    codigo: 'BV013',
    t: () => ({
      que: 'El ticket de báscula no está listo para esto.',
      hacer: 'Revisa que el ticket esté aprobado y que pese las mismas cabezas del lote.',
    }),
  },
  // ── Condiciones y cierre del trato (RN-017) ─────────────────────────────
  {
    codigo: 'BV015',
    regla: 'RN-017',
    comando: ['acordar_operacion'],
    t: () => ({
      que: 'Todavía no hay condiciones guardadas.',
      hacer: 'Guarda primero las cabezas y el precio del lote; después acéptalas.',
      accion: IR_PRECIO,
    }),
  },
  {
    codigo: 'BV015',
    regla: 'RN-017',
    comando: CONFIRMAR,
    t: (c) => ({
      que: 'Al trato le falta algo para cerrarse.',
      hacer: c.datos?.folio_ticket
        ? `Si el precio es por kilo, aprueba el ticket ${c.datos.folio_ticket}; revisa también que cada lote tenga cabezas y precio.`
        : 'Revisa que cada lote tenga cabezas y precio y, si es por kilo, su pesaje aprobado.',
      accion: IR_BASCULA,
    }),
  },
  {
    codigo: 'BV015',
    regla: 'RN-017',
    comando: ['reservar_venta', 'liberar_reserva'],
    t: () => ({
      que: 'Solo se apartan cabezas de una venta abierta.',
      hacer: 'Esta venta ya se cerró o se canceló. Recarga para ver cómo quedó.',
      accion: RECARGAR,
    }),
  },
  {
    codigo: 'BV015',
    regla: 'RN-017',
    comando: ['ajustar_liquidacion'],
    t: () => ({que: 'No encontramos esa liquidación.', hacer: 'Vuelve a abrirla desde Liquidaciones.'}),
  },
  {
    codigo: 'BV015',
    regla: 'RN-017',
    t: () => ({que: 'Faltan datos del trato para hacer esto.', hacer: 'Revisa las cabezas, el precio y el pesaje, y vuelve a intentarlo.'}),
  },
  {
    codigo: 'BV015',
    regla: 'RN-013',
    t: () => ({
      que: 'Falta el motivo de la corrección.',
      hacer: 'Escribe por qué corriges el ticket, en no más de 200 letras.',
      cubre: ['motivo'],
    }),
  },
  {
    codigo: 'BV015',
    regla: 'RN-023',
    t: () => ({
      que: 'El cierre no cuadra con su desglose y no se guardó.',
      hacer: 'No se movió nada. Avisa al administrador con los datos para soporte de abajo.',
      cubre: ['total'],
    }),
  },
  {
    codigo: 'BV015',
    regla: 'RN-035',
    t: () => ({
      que: 'La tarifa del proveedor no corresponde a este gasto.',
      hacer: 'Vuelve a consultar la tarifa, acéptala y usa el mismo importe.',
    }),
  },
  {
    codigo: 'BV015',
    regla: 'RN-037',
    t: () => ({que: 'La versión del documento no es válida.', hacer: 'Vuelve a subir el archivo como versión nueva.'}),
  },
  {
    codigo: 'BV015',
    regla: 'RN-001',
    campo: 'contrasena',
    t: () => ({que: 'La contraseña no se pudo guardar así.', hacer: 'Escribe otra contraseña y vuelve a intentarlo.', cubre: ['contrasena']}),
  },
  {
    codigo: 'BV015',
    regla: 'RN-001',
    t: () => ({que: 'La búsqueda o el filtro no es válido.', hacer: 'Usa una búsqueda más corta o quita el filtro.'}),
  },
  {
    codigo: 'BV015',
    regla: 'RN-020',
    t: () => ({que: 'El filtro de cabezas no es válido.', hacer: 'Quita el filtro y vuelve a buscar.'}),
  },
  {
    codigo: 'BV015',
    regla: 'RN-029',
    t: () => ({que: 'El filtro de la cartera no es válido.', hacer: 'Quita el filtro y vuelve a consultar.'}),
  },
  {
    codigo: 'BV015',
    regla: 'RN-034',
    t: () => ({que: 'Solo se aceptan pesos mexicanos (MXN).', hacer: 'Escribe el importe en pesos.'}),
  },
  // ── Registros firmes, costos y dinero ──────────────────────────────────
  {
    codigo: 'BV010',
    t: () => ({que: 'Ese dato ya no se puede cambiar.', hacer: 'Si hay un error, registra una corrección; el original se conserva.'}),
  },
  {
    codigo: 'BV011',
    t: () => ({
      que: 'Alguna cabeza no tiene su arete vigente o está dada de baja.',
      hacer: 'Revisa los aretes del trato en Animales antes de seguir.',
    }),
  },
  {
    codigo: 'BV016',
    t: () => ({
      que: 'Esto ya quedó firme y no se puede cambiar.',
      hacer: 'Si hay que corregir, reabre las condiciones o registra un ajuste; el original se conserva.',
    }),
  },
  {
    codigo: 'BV018',
    regla: 'RN-013',
    t: () => ({
      que: 'Faltan los pesos individuales de las cabezas.',
      hacer: 'Para repartir por peso, cada cabeza necesita su peso medido en el ticket. Elige otro método de reparto.',
      cubre: ['metodo'],
    }),
  },
  {
    codigo: 'BV018',
    campo: 'asignaciones',
    t: () => ({
      que: 'Los importes por cabeza no suman el gasto completo.',
      hacer: 'Escribe un importe para cada cabeza; juntos deben sumar el gasto.',
      cubre: ['asignaciones'],
    }),
  },
  {
    codigo: 'BV018',
    t: () => ({
      que: 'El gasto no se puede repartir así.',
      hacer: 'Revisa que la compra ya esté cerrada y que el gasto no se haya repartido antes.',
    }),
  },
  {
    codigo: 'BV020',
    comando: ['aplicar_pago'],
    t: () => ({
      que: 'El abono es mayor que lo que se debe o que el dinero disponible.',
      hacer: 'Revisa que el dinero esté validado y escribe un importe igual o menor; lo que sobre queda disponible.',
    }),
  },
  {
    codigo: 'BV020',
    comando: ['reembolsar_pago'],
    t: () => ({que: 'El reembolso es mayor que el dinero disponible.', hacer: 'Escribe un importe igual o menor al disponible.'}),
  },
  {
    codigo: 'BV020',
    campo: 'reaplicar_pagos',
    t: () => ({
      que: 'Ese abono toca una cuenta que ya tiene pagos aplicados.',
      hacer: 'Marca «Conciliar ajuste y aplicaciones en una sola operación» y vuelve a registrarlo.',
      cubre: ['reaplicar_pagos'],
    }),
  },
  {
    codigo: 'BV020',
    t: () => ({
      que: 'El movimiento de dinero no cuadra con el saldo.',
      hacer: 'Revisa que el dinero esté validado y que el importe no pase del saldo ni del disponible.',
    }),
  },
  {
    codigo: 'BV021',
    t: () => ({
      que: 'Ese dinero no corresponde a esa cuenta.',
      hacer: 'Un cobro se abona a lo que te deben y un pago a lo que debes, de la misma persona.',
    }),
  },
  {
    codigo: 'BV022',
    t: () => ({que: 'Ese abono ya se revirtió o no existe.', hacer: 'Recarga el historial del pago.', cubre: ['aplicacion_id']}),
  },
  {
    codigo: 'BV023',
    t: (_c, d) => ({que: d.mensaje || 'El archivo no se pudo guardar.', hacer: 'Sube un PDF, PNG o JPEG de menos de 20 MiB.'}),
  },
  {
    codigo: 'BV024',
    t: () => ({
      que: 'Para dar de baja una cabeza hace falta evidencia y que no esté en un trato.',
      hacer: 'Adjunta el documento y libera el apartado antes de registrar la baja.',
    }),
  },
  {
    codigo: 'BV025',
    t: () => ({
      que: 'La fecha no cae en un periodo abierto.',
      hacer: 'Elige una fecha dentro del periodo abierto o pide al administrador que lo abra en Control → Periodos.',
      cubre: ['periodo_id', 'fecha_reconocimiento', 'desde', 'hasta'],
    }),
  },
  {
    codigo: 'BV026',
    t: () => ({
      que: 'Ese movimiento no corresponde a estas cabezas.',
      hacer: 'Revisa que las cabezas estén pendientes de recibir o de entregar.',
      cubre: ['posiciones'],
    }),
  },
  // ── Concurrencia, apartados y versiones ─────────────────────────────────
  {
    codigo: 'BV402',
    comando: ['editar_operacion', 'crear_operacion'],
    t: () => ({que: 'Las cabezas de este trato están apartadas.', hacer: 'Libera el apartado antes de cambiar el trato.'}),
  },
  {
    codigo: 'BV402',
    t: () => ({
      que: 'Alguna cabeza ya está apartada en otro trato o ya no está disponible.',
      hacer: 'Recarga y elige otras cabezas.',
      cubre: ['posiciones'],
    }),
  },
  {
    codigo: 'BV403',
    t: () => ({
      que: 'La reserva venció o alguna cabeza ya no está disponible.',
      hacer: 'Vuelve a apartar las cabezas y cierra de nuevo.',
    }),
  },
  {
    codigo: 'BV404',
    t: () => ({
      que: 'No encontramos ese registro en esta sede.',
      hacer: 'Puede que sea de otra sede o que ya no exista. Vuelve a la lista y búscalo de nuevo.',
    }),
  },
  {
    codigo: 'BV405',
    t: () => ({
      que: 'Ese intento ya se usó con otros datos.',
      hacer: 'Usa «Resolver conflicto y volver a capturar» para empezar de nuevo; no se duplica nada.',
    }),
  },
  {
    codigo: 'BV409',
    t: (c) => ({
      que: 'Otra persona guardó al mismo tiempo.',
      hacer: c.escritura ? 'Reintenta el mismo comando: usa la misma clave y no se duplica.' : 'Vuelve a consultar.',
    }),
  },
  {
    codigo: 'BV412',
    t: () => ({
      que: 'Otra persona cambió este registro.',
      hacer: 'Recarga antes de continuar para ver la versión nueva y vuelve a capturar.',
      accion: RECARGAR,
      cubre: ['version_lock'],
    }),
  },
  {
    codigo: 'BV501',
    t: (c) => ({
      que: 'La sede no está disponible.',
      hacer: c.escritura ? 'Conservamos la captura para reintentar.' : 'Vuelve a consultar en un momento.',
    }),
  },
];

/** Respuesta por estado HTTP cuando el código no está en la tabla. */
function porEstado(d: DetalleError, c: ContextoError): Traduccion | undefined {
  const w = !!c.escritura;
  switch (d.status) {
    case 0:
      return w
        ? {que: 'No se pudo conocer el resultado.', hacer: 'Reintenta el mismo comando para comprobarlo: usa la misma clave y no se duplica.'}
        : {que: 'No hubo respuesta de la sede.', hacer: 'Revisa la conexión y vuelve a consultar.'};
    case 401:
      return c.comando === 'iniciar_sesion'
        ? {que: 'El usuario o la contraseña no coinciden.', hacer: 'Revísalos y vuelve a intentar.'}
        : {que: 'La sesión terminó.', hacer: 'Ingresa de nuevo para seguir.'};
    case 403:
      return {que: 'Tu rol no permite hacer esto en esta sede.', hacer: 'Pídeselo a quien tenga ese permiso o al administrador.'};
    case 404:
      return {que: 'No encontramos ese registro en esta sede.', hacer: 'Puede que sea de otra sede o que ya no exista. Vuelve a la lista.'};
    case 408:
      return {que: 'La sede tardó demasiado en responder.', hacer: w ? 'Reintenta el mismo comando; no se duplica.' : 'Vuelve a consultar.'};
    case 412:
      return {que: 'Otra persona cambió este registro.', hacer: 'Recarga antes de continuar.', accion: RECARGAR};
    case 425:
      return {que: d.mensaje || 'El servidor todavía está procesando este comando.', hacer: 'Espera un momento y vuelve a consultar el mismo intento.'};
    case 428:
      return {que: 'Falta la versión del registro.', hacer: 'Recarga antes de continuar.', accion: RECARGAR};
    case 429:
      return {que: d.mensaje || 'Demasiados intentos seguidos.', hacer: 'Espera un momento y vuelve a intentar.'};
    case 502:
    case 503:
    case 504:
      return w
        ? {que: 'La sede no está disponible.', hacer: 'Conservamos la captura para reintentar.'}
        : {que: 'La sede no está disponible por ahora.', hacer: 'Vuelve a consultar en un momento.'};
  }
  if (d.status >= 500)
    return w
      ? {que: 'La sede no pudo procesar la solicitud.', hacer: 'Reintenta el mismo comando; si se repite, avisa a soporte con los datos de abajo.'}
      : {que: 'La sede no pudo responder la consulta.', hacer: 'Vuelve a consultar en un momento.'};
  return undefined;
}

function coincide(e: Entrada, d: DetalleError, c: ContextoError) {
  if (e.codigo && e.codigo !== d.codigo) return false;
  if (e.regla && e.regla !== d.regla_id) return false;
  if (e.comando && (!c.comando || !e.comando.includes(c.comando))) return false;
  if (e.campo && !(d.campos || []).some((f) => f.campo === e.campo)) return false;
  return true;
}

/** Qué pasó y qué hacer, en palabras del tratante. Nunca devuelve el código como título. */
export function traducirError(d: DetalleError, c: ContextoError = {}): Traduccion {
  // Los estados de transporte (sin respuesta, sede caída, sesión) mandan sobre cualquier código.
  if (d.status === 0 || d.status === 401 || d.status === 503) return porEstado(d, c)!;
  const entrada = d.codigo ? TABLA_ERRORES.find((e) => coincide(e, d, c)) : undefined;
  if (entrada) return entrada.t(c, d);
  // BV400 y demás mensajes propios del backend ya son específicos: se conservan.
  if (d.codigo === 'BV400' && d.mensaje) return {que: d.mensaje, hacer: 'Corrige ese dato y vuelve a intentarlo.'};
  const estado = porEstado(d, c);
  if (estado) return estado;
  if (d.mensaje) return {que: d.mensaje};
  return {que: 'No se pudo completar.', hacer: c.escritura ? 'Revisa los datos y vuelve a intentarlo.' : 'Vuelve a consultar.'};
}

/** Texto plano de una traducción (para `Error.message` y lectores de pantalla). */
export const fraseError = (t: Traduccion) => (t.hacer ? `${t.que} ${t.hacer}` : t.que);

// ── Errores de campo enviados por el servidor ─────────────────────────────
const NOMBRES: Record<string, string> = {
  pesaje_base_id: 'el pesaje aprobado del lote',
  periodo_id: 'el periodo',
  fecha_reconocimiento: 'la fecha',
  monto: 'el importe',
  importe: 'el importe',
  motivo: 'el motivo',
  posiciones: 'las cabezas',
  animales: 'las cabezas pesadas',
  asignaciones: 'los importes por cabeza',
  metodo: 'el método de reparto',
  total: 'el total',
  version_lock: 'la versión del registro',
  version: 'la versión del documento',
  contrasena: 'la contraseña',
  corrige_a_id: 'el ticket original',
  aplicacion_id: 'el abono',
  reaplicar_pagos: 'la conciliación de pagos',
  desde: 'el inicio del periodo',
  hasta: 'el fin del periodo',
  q: 'la búsqueda',
  estado: 'el filtro de estado',
  tipo: 'el filtro de tipo',
  direccion: 'el filtro de dirección',
  vencida: 'el filtro de vencidas',
  disponibles_para_venta: 'el filtro de disponibles',
};
const PROBLEMAS: Record<string, string> = {
  faltante: 'falta',
  invalido: 'no es válido',
  requerido_1_200: 'escribe entre 1 y 200 letras',
  obsoleta: 'otra persona lo cambió',
  reservada: 'ya está apartado en otro trato',
  composicion_distinta: 'debe llevar las mismas cabezas que el original',
  composicion_contexto_distinto: 'debe ser del mismo trato y lote',
  descuadrado: 'no cuadra con su desglose',
  ya_revertida: 'ya se revirtió',
};

/** Mensaje junto al campo («Falta este dato.»), sin nombres técnicos. */
export function problemaCampo(problema: string): string {
  const p = PROBLEMAS[problema];
  if (!p) return 'Revisa este dato.';
  if (problema === 'faltante') return 'Falta este dato.';
  if (problema === 'invalido') return 'Este dato no es válido. Revísalo.';
  return p.charAt(0).toUpperCase() + p.slice(1) + '.';
}

/** Frase con acción para un campo del servidor que no existe en este formulario. */
export function fraseCampo(campo: string, problema: string): string {
  const nombre = NOMBRES[campo] || 'un dato de este registro';
  const p = PROBLEMAS[problema] || 'necesita revisión';
  const frase = problema === 'faltante' ? `Falta ${nombre}.` : `${nombre.charAt(0).toUpperCase() + nombre.slice(1)}: ${p}.`;
  return `${frase} Revísalo en su paso y vuelve a intentarlo.`;
}

// ── Confirmaciones (lo que dice el aviso de éxito) ────────────────────────
const CONFIRMACIONES: Record<string, string> = {
  crear_operacion: 'Trato empezado como borrador.',
  editar_operacion: 'Condiciones del trato guardadas.',
  acordar_operacion: 'Acuerdo guardado como versión fija.',
  reabrir_operacion: 'Condiciones reabiertas para editar.',
  registrar_pesaje: 'Ticket de báscula apuntado.',
  aprobar_pesaje: 'Pesaje aprobado.',
  corregir_pesaje: 'Corrección del ticket guardada.',
  confirmar_operacion: 'Trato cerrado.',
  reservar_venta: 'Cabezas apartadas.',
  liberar_reserva: 'Apartado liberado.',
  registrar_pago: 'Dinero apuntado.',
  validar_pago: 'Dinero revisado y validado.',
  aplicar_pago: 'Abono aplicado a la cuenta.',
  revertir_aplicacion: 'Abono revertido; el original se conserva.',
  reembolsar_pago: 'Reembolso apuntado.',
  ajustar_liquidacion: 'Ajuste registrado.',
  registrar_gasto: 'Gasto apuntado.',
  repartir_gasto: 'Gasto repartido entre las cabezas.',
  crear_contraparte: 'Contraparte dada de alta.',
  crear_predio: 'Predio guardado.',
  registrar_animal: 'Arete registrado.',
  registrar_movimiento: 'Movimiento del corral apuntado.',
  registrar_documento: 'Documento guardado.',
  crear_periodo: 'Periodo creado.',
  cerrar_periodo: 'Periodo cerrado.',
  reabrir_periodo: 'Periodo reabierto.',
  crear_usuario: 'Usuario creado.',
  actualizar_usuario: 'Usuario actualizado.',
  asignar_membresia: 'Permiso asignado.',
  aceptar_tarifa: 'Tarifa aceptada para el gasto.',
};
export const confirmacionDe = (comando?: string) => (comando && CONFIRMACIONES[comando]) || 'Guardado.';
