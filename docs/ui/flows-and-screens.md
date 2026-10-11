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

## Liquidación → pago → aplicación: primera mejora documental

Preparado el 2026-10-11 para TASK-J-002/J-012/J-013; **sin frontend implementado ni prueba visual**. [Referencias, observaciones y límites](references.md). Objetivo: OPE entiende el cierre y CAJ aplica dinero sin confundir confirmación, entrega y saldo. No modifica fórmulas, permisos ni estados del dominio.

### Detalle de liquidación (pantalla 8)

Orden de lectura y navegación:

1. Folio, contraparte, sede y dirección «Por cobrar»/«Por pagar». Separar estado de operación, estado de entrega y saldo pendiente; no sintetizarlos en «Completado».
2. Saldo pendiente en MXN, vencimiento y siguiente acción según permiso. CAJ: «Registrar cobro»/«Registrar pago»; acceso al pago disponible cuando la consulta exista. OPE/AUD: lectura y expediente según autorización, sin acción de caja.
3. Desglose: conceptos con cantidad/unidad/precio/importe, total original, cargos, abonos, aplicaciones netas y saldo. Sólo valores canónicos del servidor; no construir totales en JavaScript. Conservar distinción entre costo/margen y obligación.
4. Aplicaciones y ajustes con vínculos al expediente; estado físico de entrega en bloque separado. Comprobante rotulado «Comprobante interno · no es CFDI».

Si el servidor no entrega un dato, mostrar «No disponible» con explicación técnica en documentación, nunca cero ni un valor simulado. Los wireframes y mocks llevan «DEMO · datos sintéticos».

### Caja (pantalla 9)

| Paso | Contenido y acción | Resultado visible |
|---|---|---|
| Registrar | Contraparte y dirección preseleccionadas desde el contexto; importe, método, fecha y referencia. «Registrar cobro/pago» llama `registrarPago`. | Mostrar identificador, estado real y disponible devueltos. «Pago registrado; pendiente de aplicar» cuando corresponda. No anunciar obligación saldada. |
| Elegir | Seleccionar pago y obligaciones compatibles con empresa, sede, contraparte, moneda y dirección (RN-030). Mostrar disponible del pago y saldo de cada obligación con encabezados explícitos. | Lista vacía: «No hay liquidaciones compatibles con saldo»; el dinero conserva su disponible. No inventar obligaciones para completarla. |
| Aplicar | Etiqueta «Importe a aplicar» por obligación; revisión de destinos e importes; acción «Aplicar pago». El servidor valida RN-029; la UI no sustituye la validación ni decide el saldo final. | `aplicarPago` devuelve pago actualizado; recargar las liquidaciones afectadas y mostrar sus saldos reales. Disponible restante: «Saldo a favor / anticipo», según dirección. |
| Continuar | Enlace «Volver a liquidación» y acceso al expediente. | Entrega y operación mantienen sus propios estados; pagar no confirma una operación ni registra entrega. |

Cada comando conserva su propia clave de idempotencia mientras contenido e intención no cambien (RN-032); registrar y aplicar son comandos distintos. Deshabilitar duplicación mientras se espera, conservando el texto de la acción. Ante resultado incierto de red, no mostrar éxito ni cero: permitir reintento del mismo comando/contenido con la misma clave. Si el usuario cambia el contenido después de resolver el intento anterior, corresponde una nueva intención/clave. Un 409 por clave usada con otro contenido requiere resolver el conflicto, no ocultarlo generando claves automáticamente.

422: conservar entradas y enlazar el mensaje del servidor al campo mediante `aria-describedby`; mostrar `regla_id`. Tras envío fallido, enfocar un resumen de errores con enlaces a los campos; conservar errores inline y anunciarlos sin duplicación. No mover el foco en cada validación al salir del campo. 409: aviso y recarga explícita de saldos, sin sobreescribir ni reaplicar automáticamente. 503: conservar la captura para reintento siguiendo el estado devuelto por la API. Éxito: anunciar el resultado y actualizar desde el servidor antes de permitir otra aplicación.

### Contrato pendiente, sin conectividad simulada

El OpenAPI actual define `detalleLiquidacion`, `registrarPago` y `aplicarPago`; `Pago` incluye `estado`, `aplicado`, `reembolsado` y `disponible`. No define todavía consultas para listar/recuperar pagos disponibles ni obligaciones compatibles, ni el comando de validación del pago que contempla UC-09. `Liquidacion` no incluye listas detalladas de ajustes/aplicaciones ni estados de entrega. Resolver estos huecos con el responsable del contrato antes de integrar la pantalla; usar respuestas DEMO identificadas para wireframes, sin afirmar que ya existe backend conectado. No se añaden endpoints en esta mejora.

### Criterios para implementar y verificar

| Caso | Resultado esperado (pendiente de ejecución) |
|---|---|
| GOLD-04A / TEST-04 | Obligación DEMO 1,000.00, pago 600.00, aplicaciones 400.00 y 200.00: saldo 400.00, disponible 0.00 MXN. Reintentar no duplica; aplicar 0.01 más recibe error. |
| GOLD-04B / TEST-04 | Pago DEMO 1,200.00 aplicado por 1,000.00: saldo 0.00, disponible 200.00 MXN; entrega mantiene su estado previo. |
| GOLD-07 / TEST-07 | Bonificación posterior a pago: preservar original y mostrar reverso, nueva aplicación y ajuste; disponible 100.00 antes del reembolso, 0.00 después. No ofrecer editar/borrar hechos. |
| TEST-11/12 | La API rechaza aplicación incompatible/sobreaplicación y conflicto de idempotencia; errores junto al destino afectado sin perder entradas. |
| 390 px | Una columna; rótulos y moneda visibles; nombres largos envuelven; tablas extensas con desplazamiento identificado dentro de su región, sin desbordar toda la página. Acción accesible sin tapar campos con teclado virtual. |
| 768 / 1440 px | Resumen y detalle con orden de lectura estable; importes alineados; el panel de aplicación conserva contexto sin ocultar desglose ni expediente. |
| Teclado y estados | Completar sin ratón; foco visible; resumen de errores con enlaces; anunciar carga/error/éxito sin mover foco inesperadamente. Al volver, restaurar foco en la acción de origen. No depender de animación; respetar movimiento reducido. |

Estos criterios amplían el diseño, **no son pruebas pasadas**. Registrar capturas, consola, navegación y comandos reales en `docs/testing/evidence.md` cuando exista aplicación ejecutable.
