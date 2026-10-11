# Flujos y pantallas

Estado: frontend local implementado en `frontend/`; recorrido principal real verificado el 2026-10-11. [Manual de usuario](user-manual.md) y [evidencia UI](../testing/evidence/ui/frontend-ui-tests.md). Contrato: `docs/api/openapi.yaml`. Principios: B2B sobrio; información operativa (pendientes, diferencias, saldos, evidencia); sin gráficas ficticias; importes alineados a la derecha con "MXN"; pesos con "kg"; estados con texto + ícono (no sólo color); teclado y foco visibles; escritorio primero, captura esencial usable en móvil. La UI nunca calcula totales financieros: muestra los del servidor.

## Estados comunes de toda pantalla
| Estado | Comportamiento |
|---|---|
| Cargando | Indicador textual accesible; sin bloquear navegación |
| Vacío | Mensaje de ausencia; acciones de captura según rol |
| Error 401 | Redirigir a acceso conservando ruta |
| Error 403 / 404 | Mensaje de acceso o recurso no disponible, sin revelar datos |
| 409 / 412 conflicto | Revisar conflicto y recargar versión; no sobrescribir |
| 422 regla | Mensaje del servidor junto al campo (`campos[]`) + `regla_id` visible para soporte |
| 503 dueño no disponible | Resultado no conocido; consultar primero el mismo intento antes de reintentar |
| Datos atrasados | Corte o aviso real cuando la API lo proporciona; sin inventar antigüedad |
| Reintento | Botón con la **misma** Idempotency-Key; nunca reintento automático de comandos monetarios |

## Pantallas
| # | Pantalla | Campos / contenido | Permisos | Componentes | API | Casos especiales |
|---|---|---|---|---|---|---|
| 1 | Acceso y selección de sede | login, contraseña; lista de sedes con roles y disponibilidad | Público → sesión | Formulario, lista | /sesion/* | Sede no disponible marcada; sin login si A cae |
| 2 | Bandeja de operaciones | folio, tipo, contraparte, estado, entrega, pendientes (pesaje, liquidación, entrega, pago, documento) | OPE, CAJ, AUD (lectura) | Tabla paginada, búsqueda q, filtros estado/tipo y estados textuales | GET operaciones | Orden estable por fecha+folio |
| 3 | Contrapartes | nombre, tipo, RFC, teléfono | OPE (alta), AUD (lectura) | Tabla con búsqueda q y formulario | contrapartes | Alta se escribe en A: si A cae, 503 |
| 4 | Ficha del animal | identificaciones (vigentes e históricas), situación, ciclos con costo y estado | Todos | Identificaciones y tabla de ciclos paginada (20), costo SQL | animales/{id}; inventario/posiciones?q=animal | PENDIENTE_CONVERGENCIA visible; MUERTO bloquea recompra |
| 5 | Inventario y selección para venta | posiciones por estado, reservada (derivado), costo vigente | OPE | Tabla con selección múltiple; CSV toda la sede | inventario/posiciones; reportes/inventario/csv | Posición reservada por otra venta: deshabilitada con motivo |
| 6 | Captura compra/venta por pasos | 1 contraparte · 2 lotes y animales/posiciones · 3 condiciones por lote (kg/cabeza, precio, pesaje base, deducción pactada) · 4 pesajes · 5 revisión y confirmar | OPE | Pasos y guardado explícito con If-Match | operaciones, pesajes, confirmar | If-Match; servidor valida RN-017; acuerdo explícito y reapertura versionada |
| 7 | Comparación de tickets | pesaje A vs B, variación kg y %, composición | OPE | Tabla comparativa, historial y corrección de versión aprobada con motivo | pesajes; pesajes/{id}/correcciones | "No comparable: composición distinta" (RN-014); variación ≠ descuento |
| 8 | Detalle de liquidación | conceptos con fórmula, costo, gastos, ajustes, aplicaciones, saldo, documentos, estado de entrega **separado** | Todos | Desglose, tabla de aplicaciones | liquidaciones/{id} | Margen PROVISIONAL etiquetado |
| 9 | Cobros/pagos y aplicación | pago, disponible, obligaciones compatibles con saldo | CAJ | Formulario + tabla de aplicación | pagos, aplicaciones | Excede saldo → 422 en campo; anticipo visible como "saldo a favor" |
| 10 | Expediente y línea temporal | hechos ordenados: alta, pesajes, versiones, confirmación, movimientos, pagos, ajustes, revisiones | Todos | Timeline con enlaces | varios | Rótulo "Hechos registrados por el servidor" |
| 11 | Cartera | contraparte, saldo, vencimiento, días vencida | CAJ, AUD | Búsqueda, vencimiento, tabla paginada y CSV toda la sede | reportes/cartera; reportes/cartera/csv | Corte, fuente y antigüedad desconocida explícita |
| 12 | Margen e inventario | venta, costo vendido, gastos directos, margen, pérdidas | ADM, AUD | Importes canónicos agregados y CSV toda la sede | reportes/margen; reportes/margen/csv | Etiquetas PROVISIONAL / ACTUALIZADO / CERRADO |
| 13 | Usuarios y permisos | usuario, sede, rol, vigencia | ADM | Tabla editable | usuarios y membresias | Cambios en A |
| 14 | Incidencias de sincronización | nodo, estado, pendientes, avisos y corte informado | ADM | Lista de avisos | GET sincronizacion | Sin mostrar hosts, Pgpool ni SQL |
| 15 | Simulador de margen | lotes y cálculo canónico de operación | OPE | Formulario + resultado | GET operaciones/{id}/simulador | "Simulación: no registra nada" |

## Recorrido principal implementado
Compra (6) → Pesajes (6.4, 7) → Confirmar → Recepción → Inventario (5) → Venta (6) con reserva → Confirmar → Liquidación (8) → Cobro y aplicación (9) → Entrega → Expediente (10). Estados que comprobar: reserva vencida, ticket no comparable, aplicación excedida, sede no disponible, bonificación después del pago (GOLD-07).

## Conexión e intento pendiente
No hay captura offline. Un comando de resultado desconocido conserva clave y contenido por principal y sede en sessionStorage; tras recarga consulta el lookup autenticado antes de reintentar. Errores 5xx y expiración de sesión conservan el intento; al recuperar sesión sólo el mismo principal puede cargarlo. Cambiar de sede desmonta el expediente y cancela sus GET pendientes. Contraseña y archivo binario no persisten. Sin conexión no se anuncia confirmación, reserva ni aplicación.

## Liquidación → pago → aplicación: primera mejora documental

Implementado el 2026-10-11 para TASK-J-002/J-012/J-013; [recorrido real y capturas](../testing/evidence/ui/frontend-ui-tests.md). [Referencias, observaciones y límites](references.md). Objetivo: OPE entiende el cierre y CAJ aplica dinero sin confundir confirmación, entrega y saldo. No modifica fórmulas, permisos ni estados del dominio.

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

### Antecedente histórico del contrato antes de implementar

Este párrafo conserva la observación histórica anterior a implementar; el contrato vigente ya incluye listado, detalle y validación de pagos y sus consultas conectadas. En aquel checkpoint, el OpenAPI definía `detalleLiquidacion`, `registrarPago` y `aplicarPago`; `Pago` incluye `estado`, `aplicado`, `reembolsado` y `disponible`. No define todavía consultas para listar/recuperar pagos disponibles ni obligaciones compatibles, ni el comando de validación del pago que contempla UC-09. `Liquidacion` no incluye listas detalladas de ajustes/aplicaciones ni estados de entrega. Resolver estos huecos con el responsable del contrato antes de integrar la pantalla; usar respuestas DEMO identificadas para wireframes, sin afirmar que ya existe backend conectado. No se añaden endpoints en esta mejora.

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

## Vistas adicionales implementadas

| Vista | Contenido | Permiso de escritura | API |
|---|---|---|---|
| Predios | Nombre, ubicación, UPP declarada, responsable; búsqueda y paginación | OPERADOR | predios |
| Recepción y entrega | Posiciones, movimiento, fecha y venta; baja con evidencia | OPERADOR; BAJA ADMIN | inventario/movimientos |
| Gastos | COSTO/BONIFICACION, origen, reconocimiento y reparto por cabeza/peso/importe individual | OPERADOR | gastos y reparto |
| Periodos | Alta, versiones inmutables, cierre y reapertura con motivo | ADMIN | periodos y versiones |
| Documentos | Carga PDF/PNG/JPEG, metadatos, descarga y revisión | Según sede autorizada | documentos |

El menú móvil usa selector nativo agrupado; escritorio usa navegación lateral. Las tablas desplazan en su región. Acceso, captura y formularios tienen etiquetas, foco y errores asociados. El QR usa URL interna autorizada; no se genera mediante servicios externos.

## Resultado final del recorrido local

El cierre integrado con Caddy15180 y PostgreSQL V13 aprobó **15/15 E2E** y una prueba adicional de caída física del proveedor **1/1**, sin skips ni retries. Incluye el flujo completo a 390 px sólo mediante teclado, predios, entrega/recompra con ciclos históricos, corrección de pesajes y comparación incompatible, conflicto/expiración real de reservas y descarga CSV. Los CSV exportan toda la sede autorizada y no el filtro local; los ciclos se consultan con paginación de 20 y costo SQL. Los formularios reales aprobaron compra/venta/pago/abono atómico/reembolso/documentos/QR, resultado desconocido recuperado por lookup, rol auditor, gastos con pesos individuales y tarifas FDW, acuerdos versionados y periodo actual cerrado/reabierto. El acuerdo KG incompleto devuelve 422 y enfoca el error antes de permitir continuar con un ticket aprobado. Los filtros q/estado/tipo consultan SQL y respetan la paginación. [Resultados y capturas](../testing/evidence/ui/frontend-ui-tests.md).
