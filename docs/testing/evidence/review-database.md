# Revisión independiente de SQL y límites de acceso

Fecha: 2026-10-11. Revisión estática inicial del conjunto V1–V10, sin escrituras SQL, reinicios ni nuevas pruebas durante la ventana de interfaz/TEST-22. Después se verificó la corrección V11 en una ventana autorizada. Se siguió `~/.codex/skills/seguridad-bd.md`, ajustando su enfoque al modelo JDBC con roles técnicos y funciones autorizadas de este proyecto. No se presupone Supabase ni acceso SQL desde el navegador.

## Hallazgo bloqueante: versión obsoleta aceptada al cancelar o anular

**P1-01.** En [V9, `cancelar_operacion` y `anular_venta`](../../../db/migrations/V9__lector_a_captura_owner_fecha.sql#L359), líneas 359–378, se bloquea la operación mediante `FOR UPDATE`, pero no se compara `op.version_lock` con el `version_lock` recibido. La API exige `If-Match` en ambos comandos ([CoreController](../../../backend/src/main/java/mx/bovicierre/operaciones/CoreController.java#L102)); OpenAPI documenta rechazo 412 para una versión obsoleta. El bloqueo evita escrituras simultáneas, pero no verifica qué versión revisó el cliente.

Reproducción preparada, derivada del código y **no ejecutada durante esta revisión**:

1. Crear una operación de compra en borrador y consultar su ETag, por ejemplo `"1"`.
2. Editar la fecha mediante PATCH con ese ETag; la operación avanza a `"2"`.
3. Enviar POST `/operaciones/{id}/cancelar`, nueva clave de idempotencia, `If-Match: "1"` y motivo.
4. La rama de V9 comprobaba solamente que el estado fuese BORRADOR/ACORDADA; por tanto cancelaba la versión 2 en lugar de devolver 412.

En V9, para anular una venta, una versión anterior a la confirmación también pasaba la comprobación de estado cuando la venta estaba CONFIRMADA, sin entregas ni aplicaciones netas. El comando tiene efectos económicos mediante contramovimientos.

Corrección aplicada: después de obtener `op` bajo bloqueo y antes de modificar datos, rechazar inexistencia o versión distinta con `BV412`/RN-017. Se mantiene el retorno de idempotencia previo a la comprobación, como en edición/confirmación: una repetición del mismo comando ya confirmado conserva su resultado aunque su ETag original sea antiguo.

**Estado posterior: corregido y verificado.** [V11](../../../db/migrations/V11__cancelacion_anulacion_version.sql#L318) agrega las guardas bajo `FOR UPDATE` (líneas 318 y 325). La [evidencia SQL](../../../db/tests/version-guards-result.json) registra 22 llamadas para versión obsoleta y repetición exacta de cancelar, anular, acordar y reabrir. Después de liberar las ventanas, la ejecución HTTP real confirmó cancelar con versión obsoleta → 412, cancelar con versión vigente → 200, repetición exacta → mismo resultado y anular con versión obsoleta → 412. La ejecución conjunta aprobó 21 pruebas: 13 unitarias, 7 HTTP y un PostgreSQL 18.6 recién creado por Testcontainers con V1–V11, sin fallos, errores ni omisiones. Evidencia: [verification-result.json](../../../backend/verification-result.json), capturada `2026-10-11T20:44:23.432362Z`. El hallazgo histórico se conserva para explicar la corrección.

## Controles revisados

| Área | Evidencia estática | Alcance de la conclusión |
| --- | --- | --- |
| Dinero | V1 usa `numeric`, restricciones contra NaN/Infinity y CHECK de signos; V2 líneas 64–75 calcula y redondea en SQL. `fn_reparto`, V2 líneas 99–132, conserva suma y asigna el residual de centavos determinísticamente. | No hay `double` ni recálculo monetario Java en los caminos revisados. Las tres bases de reparto son explícitas. |
| Periodos | V2 líneas 55–63 exige periodo y fecha, bloquea la fila y verifica ABIERTO/rango. V9 usa esta función antes de confirmar, aplicar/revertir/reembolsar, ajustar, registrar/repartir gastos, baja y anulación. El cierre bloquea la misma fila, V9 líneas 342–350. | La escritura financiera y el cierre se excluyen mediante el mismo bloqueo. No es una nueva prueba de carrera. |
| Idempotencia | V9 líneas 53–57 inserta/bloquea la clave por empresa, sede, principal, comando y clave; rechaza una huella distinta y retorna resultado COMPLETADA antes de comprobar versiones. Líneas 384–386 registran auditoría, cola de salida y resultado en la misma función. V11 conserva este orden. | Conserva resultado y evita doble efecto mientras la transacción de llamada confirma atómicamente. |
| Bloqueos y reintentos | V9 bloquea pago antes de liquidación en aplicaciones/reversos; ajuste bloquea pagos ordenados antes de liquidación. Las posiciones se bloquean ordenadas. CommandService limita 40001/40P01 a tres intentos con espera acotada. | Las esperas de red FDW no quedan dentro de la transacción financiera. No se afirma ausencia absoluta de interbloqueos. |
| `SECURITY DEFINER` | Funciones fijan `search_path=pg_catalog` y referencian esquemas explícitos. V3 líneas 154–174 revoca PUBLIC, separa autenticación, trabajador y roles de aplicación, y asigna propietario NOLOGIN `bovi_command`. V10 líneas 19–46 selecciona recursos de una lista fija; parámetros dinámicos se enlazan o se convierten a UUID antes de citar. | No se encontró interpolación directa de texto del cliente como identificador SQL. Los roles técnicos permanecen un límite de confianza del servidor; no constituyen identidad SQL individual de cada usuario. |
| Autorización | `fn_scope` verifica empresa configurada, usuario activo, membresía y rol, además del propietario. V10 verifica membresía en consultas y ADMIN para usuarios; consulta de comando incluye principal. | UUID de un recurso no sustituye autorización. El rol de aplicación no recibe DML/DDL de negocio. |
| Proveedor | V9 líneas 2–43 separa lector A y captura del propietario; la página interna incluye contexto y huella, la captura los valida, retira contexto y genera token. Java invoca ambas llamadas con confirmación automática, sucesivamente. B elimina su servidor FDW. | La página interna no tiene una ruta de entrada pública; la credencial del servicio sigue siendo confiable. |
| Cola de salida (`outbox`) | V3 líneas 131–149 persiste la reserva temporal de entrega, intentos y próxima ejecución; el trabajador confirma su transacción local antes de invocar A. El consumidor A coteja el evento replicado y registra recepción/auditoría una sola vez. | Entrega reintentable con efecto idempotente. La revisión no simula muerte de proceso ni sustituye TEST-22. |

## Hipótesis descartada: precisión de la captura del proveedor

Se señaló inicialmente una posible comparación entre cuatro y dos decimales al registrar el gasto. **Se retira ese hallazgo.** [V4, línea 5](../../../db/migrations/V4__capturas_proveedor_dto.sql#L5) define `infra.tarifa_snapshot.precio` como `numeric(14,2)`: el INSERT de V9 convierte la fuente `12000.0050` a `12000.01` en esa columna. El JSON conserva `precio_unitario_fuente` de cuatro decimales y `HALF_UP_2`; el gasto compara contra la columna de dos decimales, coherente con Dinero. No se requiere una migración por esta hipótesis. El agente de base de datos ejecutó después la comprobación fronteriza en su ventana autorizada: [provider-precision-result.json](../../../db/tests/provider-precision-result.json), captura/aceptación/gasto B aprobados con fuente `12000.0050` y Dinero `12000.01`. Esta revisión no ejecutó ese programa de pruebas.

## Límites

La revisión inicial acredita lectura de código y DDL; no cambió roles, funciones, periodos ni servicios durante la ventana. La verificación posterior autorizada se distingue arriba. No es una certificación de producción ni demuestra ausencia absoluta de carreras. No quedan hallazgos bloqueantes confirmados abiertos en este alcance.
