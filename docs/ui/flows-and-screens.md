# Flujos y pantallas

Estado: base preparada para TASK-J-001/J-002 (responsable: Jared). Contrato: `docs/api/openapi.yaml`. Principios: B2B sobrio; información operativa (pendientes, diferencias, saldos, evidencia); sin gráficas ficticias; importes alineados a la derecha con "MXN"; pesos con "kg"; estados con texto + ícono (no sólo color); teclado y foco visibles; escritorio primero, captura esencial usable en móvil. La UI nunca calcula totales financieros: muestra los del servidor.

## Estados comunes de toda pantalla
| Estado | Comportamiento |
|---|---|
| Cargando | Esqueleto; sin bloquear navegación |
| Vacío | Mensaje + acción principal ("Registrar primera compra") |
| Error 401 | Redirigir a acceso conservando ruta |
| Error 403 / 404 | "No tienes acceso a este recurso" (sin revelar existencia) |
| 409 conflicto | "Otra persona cambió este registro" + Recargar; no sobrescribir |
| 422 regla | Mensaje del servidor junto al campo (`campos[]`) + `regla_id` visible para soporte |
| 503 dueño no disponible | "La sede no está disponible; no se registró nada. Reintentar" |
| Datos atrasados | Banda "Datos consolidados al HH:MM (antigüedad N min)" cuando `antiguedad_replica_segundos` > 0 |
| Reintento | Botón con la **misma** Idempotency-Key; nunca reintento automático de comandos monetarios |

## Pantallas
| # | Pantalla | Campos / contenido | Permisos | Componentes | API | Casos especiales |
|---|---|---|---|---|---|---|
| 1 | Acceso y selección de sede | login, contraseña; lista de sedes con roles y disponibilidad | Público → sesión | Formulario, lista | /sesion/* | Sede no disponible marcada; sin login si A cae |
| 2 | Bandeja de operaciones | folio, tipo, contraparte, estado, entrega, pendientes (pesaje, liquidación, entrega, pago, documento) | OPE, CAJ, AUD (lectura) | Tabla paginada, filtros, chips de pendiente | GET operaciones | Orden estable por fecha+folio |
| 3 | Contrapartes y predios | nombre, tipo, RFC, teléfono; predio, UPP declarada | OPE (alta), AUD (lectura) | Búsqueda, formulario | contrapartes | Alta se escribe en A: si A cae, 503 |
| 4 | Ficha del animal | identificaciones (vigentes e históricas), situación, ciclos con costo y estado | Todos | Línea de tiempo de ciclos | animales/{id} | PENDIENTE_CONVERGENCIA visible; MUERTO bloquea recompra |
| 5 | Inventario y selección para venta | posiciones por estado, reservada (derivado), costo vigente | OPE | Tabla con selección múltiple | inventario/posiciones | Posición reservada por otra venta: deshabilitada con motivo |
| 6 | Captura compra/venta por pasos | 1 contraparte · 2 lotes y animales/posiciones · 3 condiciones por lote (kg/cabeza, precio, pesaje base, deducción pactada) · 4 pesajes · 5 revisión y confirmar | OPE | Stepper, autosave de borrador con If-Match | operaciones, pesajes, confirmar | Conflicto version_lock; confirmar deshabilitado hasta cumplir RN-017 con lista de faltantes |
| 7 | Comparación de tickets | pesaje A vs B, variación kg y %, composición | OPE | Tabla comparativa | pesajes | "No comparable: composición distinta" (RN-014); variación ≠ descuento |
| 8 | Detalle de liquidación | conceptos con fórmula, costo, gastos, ajustes, aplicaciones, saldo, documentos, estado de entrega **separado** | Todos | Desglose, tabla de aplicaciones | liquidaciones/{id} | Margen PROVISIONAL etiquetado |
| 9 | Cobros/pagos y aplicación | pago, disponible, obligaciones compatibles con saldo | CAJ | Formulario + tabla de aplicación | pagos, aplicaciones | Excede saldo → 422 en campo; anticipo visible como "saldo a favor" |
| 10 | Expediente y línea temporal | hechos ordenados: alta, pesajes, versiones, confirmación, movimientos, pagos, ajustes, revisiones | Todos | Timeline con enlaces | varios | Rótulo "Revisión administrativa registrada" |
| 11 | Cartera | contraparte, saldo, vencimiento, días vencida | CAJ, AUD | Tabla filtrable | reportes/cartera | Corte y antigüedad visibles |
| 12 | Margen e inventario | venta, costo vendido, gastos directos, margen, pérdidas | ADM, AUD | Tabla + totales | reportes/margen | Etiquetas PROVISIONAL / ACTUALIZADO / CERRADO |
| 13 | Usuarios y permisos | usuario, sede, rol, vigencia | ADM | Tabla editable | (pendiente de contrato) | Cambios en A |
| 14 | Incidencias de sincronización | "Sede B sin sincronizar desde HH:MM", acciones sugeridas | ADM | Lista de avisos | (operación técnica) | Sin mostrar hosts, Pgpool ni SQL |
| 15 | Simulador de margen | precio compra/venta, kg, gastos | OPE | Formulario + resultado | preview (pendiente) | "Simulación: no registra nada" |

## Recorrido principal para wireframes (J-002)
Compra (6) → Pesajes (6.4, 7) → Confirmar → Recepción → Inventario (5) → Venta (6) con reserva → Confirmar → Liquidación (8) → Cobro y aplicación (9) → Entrega → Expediente (10). Excepciones a dibujar: reserva vencida, ticket no comparable, aplicación excedida, sede no disponible, bonificación después del pago (GOLD-07).

## Offline (extra)
Sólo borradores locales marcados "Borrador sin enviar"; nunca confirmar, reservar ni aplicar sin conexión con el dueño.
