# Manual de usuario de BoviCierre

Aplicación integrada local: `http://localhost:15180`. Vite `http://127.0.0.1:15173` es la alternativa de desarrollo. Este manual describe las acciones disponibles en el frontend; las evidencias usan cuentas y registros DEMO sintéticos. No se incluyen contraseñas. El administrador proporciona el acceso.

## Acceso y sede

Escribe usuario y contraseña, pulsa **Ingresar** y selecciona una sede autorizada. El encabezado mantiene la sede y el rol activos. Para cambiar de sede, pulsa su nombre; para terminar la sesión, pulsa **Salir**. Un QR abre una ficha interna y exige acceso autorizado a su sede.

En escritorio usa el menú lateral. En móvil usa **Sección** para cambiar de pantalla. **Ir al contenido** permite saltar la navegación con teclado. Las tablas extensas desplazan dentro de su propia región.

## Compra

1. Registra la contraparte y las identidades de los animales si aún no existen.
2. En **Nueva operación**, selecciona compra, contraparte y fecha del trato. Marca **Compra pendiente de recepción física** si corresponde y crea el borrador.
3. Selecciona animales y fija unidad de precio y precio unitario. Registra, si corresponden, deducción, cargos o bonificaciones pactadas. Guarda cada lote; **Añadir lote** conserva los demás.
4. Si el precio es por kg, registra una propuesta de pesaje, aprueba el ticket revisado y vincula su identificador al lote. La comparación de tickets muestra variación; no representa un descuento automático.
5. Revisa todos los lotes y **Acepta condiciones**. Reabrir condiciones crea otra propuesta y conserva versiones aceptadas.
6. En **Revisar y confirmar**, selecciona un periodo abierto y fecha de reconocimiento. **Confirmar compra** genera inventario y obligación económica según las reglas del servidor.

Confirmar no equivale a recibir ni a pagar. Si la compra quedó pendiente de recepción, copia los identificadores de posición del inventario y registra **RECEPCION** en **Recepción y entrega**.

## Contrapartes, predios y ficha del animal

**Contrapartes** registra los datos comerciales declarados. **Predios** permite alta, búsqueda y consulta paginada; ubicación, UPP y responsable son datos declarados, no una certificación sanitaria. Los campos obligatorios bloquean una captura vacía.

La ficha del animal muestra identificaciones y **Ciclos de inventario** de la sede activa, paginados de 20 en 20. Una recompra conserva el ciclo cerrado anterior y abre otro con su costo canónico del servidor. Cambiar sede o animal reinicia la consulta; no se combinan historias de distintas sedes.

## Venta

Crea un borrador de venta y selecciona posiciones disponibles. Las reservadas o no disponibles están deshabilitadas. Guarda precios y acepta las condiciones. Fija vencimiento y pulsa **Reservar posiciones**. Revisa y confirma con periodo abierto y fecha de reconocimiento.

Para la entrega física, usa **Recepción y entrega**, selecciona **ENTREGA**, copia posiciones e identificador de la venta confirmada y registra la fecha y hora. La entrega no aplica dinero a la obligación.

Una reserva puede entrar en conflicto con otra venta o vencer realmente. El servidor rechaza la confirmación sin generar liquidación; usa **Resolver conflicto y volver a capturar**, revisa la disponibilidad y registra una nueva reserva cuando corresponda.

## Corrección y comparación de pesajes

En **Tickets y pesajes**, abre una versión aprobada exacta y registra una corrección con motivo, fecha, neto y evidencia. La composición animal se conserva; escribe pesos individuales sólo si fueron medidos. Aprueba la propuesta nueva después de revisarla. El original queda en el historial como **CORREGIDO**, vinculado a la versión nueva; no se edita ni borra. Tickets con composiciones distintas muestran **No comparable** y no generan una variación ficticia.

## Liquidaciones y dinero

Abre una liquidación para revisar conceptos, total original, cargos, abonos, aplicaciones y saldo pendiente. Todos los importes vienen del servidor. El comprobante es interno; no es CFDI.

En **Cobros y pagos**, registra dirección, contraparte, importe, método, fecha y referencia. Selecciona el registro y **Valida el pago revisado** con periodo y fecha de reconocimiento. Elige una liquidación compatible y escribe el importe que deseas aplicar. El dinero registrado conserva disponible hasta su aplicación; un disponible restante puede ser anticipo o saldo a favor.

Para una bonificación posterior al pago, el administrador abre la liquidación, registra **ABONO**, importe y motivo, y marca **Conciliar ajuste y aplicaciones en una sola operación**. El servidor conserva los originales, registra los reversos y reaplica dentro de la misma transacción. El excedente queda disponible; usa **Registrar reembolso** para documentar su salida. El recorrido DEMO verificado pagó 1,000 MXN, abonó 100 MXN y terminó con aplicaciones netas de 900 MXN y saldo cero.

## Gastos y periodos

En **Gastos** puedes consultar tarifas del proveedor, elegir una versión y **Aceptar tarifa para este gasto**. El gasto conserva esa tarifa y su importe capturado; la consulta está identificada como proveedor DEMO simulado. También puedes capturar un gasto sin tarifa.

**Gastos** permite registrar costo o bonificación, clasificación, origen, documento, fecha declarada, periodo y reconocimiento. Una bonificación identifica el gasto original. Abre un gasto para consultar y aprobar el reparto **por cabeza**, **por peso medido** o **importe individual**. En el último caso escribe cada importe por posición; la suma exacta se valida en el servidor.

El administrador crea periodos en **Periodos**, consulta versiones de cierre y registra cierre o reapertura con motivo. Los hechos económicos necesitan un periodo abierto y una fecha explícita; cerrar un periodo no modifica sus hechos originales.

## Reportes y exportación

**Cartera** permite buscar, filtrar por vencimiento y avanzar por páginas. **Margen** muestra el agregado canónico de toda la sede. Ambos conservan corte, fuente y estado de consolidación informados; una antigüedad desconocida se declara sin afirmar actualización.

**Exportar CSV de toda la sede**, disponible en cartera, margen e inventario, descarga el conjunto autorizado de la sede activa. No aplica la búsqueda ni el filtro visible de la tabla. La exportación conserva importes del servidor; si alcanza el límite de exportación, muestra el rechazo de la API.

## Documentos y control

**Documentos** admite PDF, PNG o JPEG de hasta 20 MiB y vínculo opcional a una operación. El contenido se descarga con autorización. El expediente muestra hechos y evidencia conservada. El simulador consulta el cálculo de una operación sin confirmar. Cartera, margen y sincronización muestran lo que informa el servidor; un dato ausente se presenta como **No disponible**.

En **Usuarios y permisos**, el administrador crea usuarios, modifica su estado y asigna o retira un rol por sede. Un auditor consulta los registros y no tiene controles de escritura.

## Resultado incierto y errores

Si se pierde la respuesta, el formulario bloquea la captura y conserva el intento de ese usuario y sede, incluso ante un error de servidor o sesión expirada. Al ingresar de nuevo con el mismo usuario puedes recuperarlo; otro usuario no carga ese intento. **Reintentar el mismo comando** consulta primero el resultado registrado y mantiene la misma clave y contenido. Recargar no genera una intención nueva. Para archivos o contraseñas, se conserva sólo una huella; puede ser necesario seleccionar el mismo archivo o volver a escribir los mismos datos.

Ante un conflicto de versión, recarga el registro y revisa la versión vigente antes de editar. Los errores de dominio muestran regla, referencia y campos afectados. Si la sede está indisponible, espera y consulta el mismo intento; no asumas que el comando falló por completo.

## Evidencia y alcance

Se verificaron en Chrome con ventana visible el recorrido compra → inventario → venta → liquidación → cobro → bonificación atómica → reembolso, la recarga, documento y QR; también auditor de lectura y recuperación de respuesta perdida. Hay capturas de 390, 768 y 1440 px sin desbordamiento global, obtenidas con la Intel integrada y OpenGL real. También se verificaron venta por kg con composición animal, edición de dos lotes antes y después de un ticket aprobado, recuperación de HTTP 502 tras escritura confirmada, tarifas FDW, tres métodos de reparto, acuerdo incompleto con error y foco, dos versiones aceptadas y cierre/reapertura del periodo actual. La creación positiva del siguiente periodo se valida en GOLD QA aislado; no se adelantó el calendario de la sede de demostración. El cambio de sede cancela las consultas pendientes: también se verificó B → A sin mostrar el expediente ni los animales anteriores. El cierre integrado por Caddy pasó 15 recorridos y una prueba adicional de caída física del proveedor (503 y recuperación 200 con captura conservada). El flujo compra → recepción → reserva/venta → cobro/aplicación a 390 px se completó sólo con teclado, sin ratón ni locator.focus. También se verificaron predios, recompra/entrega, corrección de pesaje y CSV real. [Resultados completos](../testing/evidence/ui/frontend-ui-tests.md). No se declara prueba en teléfono físico, lector de pantalla ni certificación WCAG global.
