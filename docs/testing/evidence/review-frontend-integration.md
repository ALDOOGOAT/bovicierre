# Revisión de integración frontend

BoviCierre conecta formularios autenticados mediante cookie con comandos SQL canónicos de compras, ventas, liquidaciones y pagos. La revisión siguió los controladores HTTP, la autorización de comandos, la normalización SQL, la captura por kg y los reintentos persistidos. La fase inicial fue de solo lectura; después, el coordinador autorizó las correcciones del frontend y su comprobación real.

**Estado final: seis hallazgos cerrados.** Las severidades describen los defectos originales. El frontend pasó **13 pruebas unitarias**, comprobación de tipos y build; el recorrido original de cierre pasó **9/9 E2E en23,8s**, con PostgreSQL V11 y API PID573660. La repetición integrada posterior por Caddy15180/PostgreSQL V13 pasó **15/15 E2E** y **1/1** con caída física del proveedor; las duraciones exactas por caso y los límites figuran en el resumen. Evidencia: [recorrido UI](ui/frontend-ui-tests.md), [resumen final](ui/bovicierre-ui-final-run.json) y [pruebas unitarias de las correcciones](../../../frontend/tests/workflow.test.ts). Las correcciones de backend/SQL se distinguen de las pruebas ejecutadas por este revisor.

## Debía corregirse

1. **[P1 · Cerrado] El ticket de una venta por kg perdía su composición animal.** `frontend/src/screens.tsx:13`, `frontend/src/workflow.ts:8`; DTO original `db/migrations/V8__borrador_kg_y_expiracion.sql:449`, aprobación `:128`.
   - **Función:** El formulario construye un ticket con los animales del lote seleccionado.
   - **Problema original:** El auxiliar leía solamente `lote.animales`. El DTO de una venta contiene `posiciones`, pero obtiene `animales` exclusivamente de `seleccion_compra`; por ello enviaba `animales: []`. Guardar una venta por kg, proponer su ticket y aprobarlo producía BV013 por falta de composición. Las pruebas anteriores cubrían compra por kg y venta por cabeza.
   - **Corrección y evidencia:** Cada posición de venta se resuelve a su `animal_id` canónico mediante consultas paginadas de inventario de la sede. La captura exige resolver todas las identidades. Las pruebas unitarias verifican identidad y rechazo de posiciones sin resolver. El E2E final comprobó venta de **300.000 kg**, ticket aprobado, acuerdo, reserva, confirmación por **3000.00 MXN** y persistencia tras recarga: [evidencia](ui/bovicierre-ui-regresion-kg-lotes.json).
   - **Consecuencia sin corrección:** No podía completarse una venta por peso desde la interfaz.

2. **[P1 · Cerrado] Editar un lote anterior cambiaba su orden y su identidad SQL.** `frontend/src/screens.tsx:30`; SQL original `db/migrations/V8__borrador_kg_y_expiracion.sql:71`, `:85`.
   - **Función:** Un PATCH reemplaza un lote y vuelve a enviar la composición completa de la operación.
   - **Problema original:** El constructor quitaba el lote editado y agregaba su reemplazo al final. Con lote 1=A y lote 2=B, editar el primero enviaba `[lote 2, lote 1]`; SQL asigna `numero_lote` por ordinalidad del arreglo. Sin historia intercambiaba los números; con un ticket previo rechazaba la conservación de composición. Cambiaba la relación entre animales, precios y lotes.
   - **Corrección y evidencia:** `replaceLot` conserva el orden ascendente de `numero_lote`. La prueba unitaria verifica que editar el primero conserva identidades y el objeto del lote intacto. El E2E final editó dos lotes antes y después de un pesaje aprobado; confirmó la compra por **302.00 MXN**: [evidencia](ui/bovicierre-ui-regresion-kg-lotes.json).
   - **Consecuencia sin corrección:** Una edición de precio podía reasignar lotes o bloquear un expediente con pesajes.

3. **[P1 · Cerrado] Una respuesta incierta o la expiración de sesión descartaba la clave de idempotencia.** `frontend/src/ui.tsx:26`, `frontend/src/api.ts:10`, `frontend/src/screens.tsx:56`, `:90`, `frontend/src/App.tsx:20`.
   - **Función:** El formulario protege un comando sin resolver y consulta `/comandos/{comando}/{clave}` antes de repetirlo.
   - **Problema original:** Se conservaban solamente los estados 0/409/425/503. Si una escritura confirmada recibía 500/502/504 al entregar su respuesta, se borraba el intento y se permitía crear otra clave. La expiración de sesión también borraba los intentos persistidos. Reproducción: confirmar un POST, sustituir su respuesta por 502, recargar y volver a enviar el mismo contenido.
   - **Corrección y evidencia:** Los resultados inciertos 5xx, tiempos agotados y autenticación expirada conservan cuerpo y clave. El almacenamiento pendiente se separa por principal autenticado, sede y ruta; otro usuario no carga el intento anterior. Los rechazos conocidos 400/403/404/412/413/422/428 permiten corregir la captura. Las pruebas unitarias cubren conservación, recuperación por el mismo principal, aislamiento entre usuarios y consulta sin otro POST. El E2E ejecutó un POST real 201, simuló solamente su entrega 502, recargó y recuperó el resultado con **un único POST**: [evidencia](ui/bovicierre-ui-http502.json).
   - **Consecuencia sin corrección:** Un reintento podía duplicar un pago, gasto o documento confirmado mediante una clave nueva.

4. **[P1 · Cerrado] FDW de la sede B leía al proveedor desde B en vez del lector A requerido.** Ubicación original `backend/src/main/java/mx/bovicierre/shared/CommandService.java:64`, `db/bootstrap/bootstrap.py:68`; requisito `docs/database/replication-and-fdw.md:59`.
   - **Función:** Las tarifas se consultan externamente, se capturan localmente y se aceptan antes de referenciarlas desde un gasto.
   - **Problema original:** La ruta usaba `jdbc.get(scope.owner())` y el bootstrap instalaba la conexión externa en ambos nodos. Seleccionar B leía al proveedor desde B. Cambiar solamente la llamada al nodo A habría fallado por la guarda de propietario y habría dejado la captura no replicada en el nodo incorrecto.
   - **Corrección y evidencia:** El backend consulta `leer_tarifas_proveedor` exclusivamente en A y después llama `capturar_tarifas_proveedor` en el propietario de la sede; V9 separa ambas funciones. El coordinador de backend reportó comprobación HTTP de lectura A → captura/aceptación B → gasto B. La suite final de backend pasó **21 pruebas: 13 unitarias, 7 HTTP y 1 PostgreSQL real de Testcontainers**: [resultado](../../../backend/verification-result.json). Este revisor comprobó el código final; no repitió las pruebas de nodos ni caídas.
   - **Consecuencia sin corrección:** Se incumplía la topología requerida; un cambio parcial habría roto la aceptación de tarifas en B.

5. **[P2 · Cerrado] Guardar un lote sobrescribía la fecha declarada del trato con la fecha actual.** SQL original `db/migrations/V8__borrador_kg_y_expiracion.sql:24`, `:79`; llamada `frontend/src/screens.tsx:30`.
   - **Función:** Guardar condiciones modifica un borrador existente.
   - **Problema original:** El cuerpo contenía lotes y preferencia de recepción, sin `fecha_operacion`. SQL inicializaba `f` con la fecha actual y escribía `fecha_operacion=f`. Un borrador fechado 2026-10-01, editado el 2026-10-11, cambiaba de fecha sin una edición explícita.
   - **Corrección y evidencia:** V9, línea 102, conserva `op.fecha_operacion` salvo que la petición incluya una nueva fecha. Corrección SQL del coordinador, comprobada en el código final por este revisor. El cierre de este hallazgo se basa en esa corrección; no se presenta como reproducción HTTP independiente de una fecha histórica.
   - **Consecuencia sin corrección:** Una edición normal alteraba un hecho operativo histórico del expediente.

6. **[P2 · Cerrado] El filtro booleano HTTP no llegaba al predicado SQL tipado.** `docs/api/openapi.yaml:835`, `backend/src/main/java/mx/bovicierre/operaciones/CoreController.java:58`, `db/migrations/V10__filtro_posiciones_vendibles.sql:74`.
   - **Función:** `GET /inventario/posiciones` declara `disponibles_para_venta` como booleano.
   - **Problema original:** V8 ignoraba el filtro. V10 agregó un predicado que exige un booleano JSON, pero el controlador seguía enviando todos los parámetros como cadenas. `?disponibles_para_venta=true` llegaba como `"true"` y producía BV015/422. Una prueba SQL con booleano nativo no comprobaba la conversión HTTP.
   - **Corrección y evidencia:** El controlador final acepta solamente los literales `true`/`false`, los convierte a booleano JSON y rechaza valores inválidos. El coordinador reportó **HTTP 200 para ambos valores válidos y 400 para uno inválido**, incluidos en la suite final de 21 pruebas: [resultado](../../../backend/verification-result.json). El cliente se regeneró desde OpenAPI 0.2.0. Los parámetros `q` cambiaban durante la revisión y no se reportaron como defectos obsoletos.
   - **Consecuencia sin corrección:** Una consulta válida del contrato recibía 422 y el filtro no podía utilizarse por HTTP.

## Conviene corregir

Sin hallazgos adicionales en esta categoría.

## Opcional

Sin hallazgos adicionales en esta categoría.

## No comprobado en esta revisión

- No se ejecutaron navegador, base de datos, reinicios, migraciones ni escrituras HTTP durante la fase inicial de solo lectura. Las pruebas UI posteriores fueron autorizadas y se distinguen arriba.
- No se repitieron de forma independiente las21 pruebas históricas del backend ni la reproducción HTTP de una fecha histórica o caídas de nodos A/B. La prueba posterior del proveedor sí verificó GET503 y recuperación200 por UI con stop/start físico del coordinador; no se atribuye a esta revisión una prueba de failover.
- No se realizó una auditoría completa de penetración, pruebas de entradas arbitrarias ni medición de rendimiento por encima de 100 entradas en selectores. Las guardas de API y principal/empresa/sede SQL se siguieron estáticamente; no se declara certificación de seguridad.

## Cierre y evidencia final

Los seis hallazgos tienen corrección. Los hallazgos 1–3 se verificaron mediante pruebas unitarias y recorrido UI real. Los hallazgos 4–6 cuentan con correcciones del coordinador de backend/SQL y la evidencia indicada; sus comprobaciones no se atribuyen a este revisor.

La novena prueba retuvo un GET del expediente B, cambió mediante el selector a A y comprobó cancelación real `net::ERR_ABORTED`, sin expediente ni captura animal de B: [evidencia de aislamiento](ui/bovicierre-ui-scope-cancel.json). El cierre original fue **9 E2E y13 unitarias PASS**, seguido de repetición integrada **15+1 E2E PASS** y13 unitarias; [resumen](ui/bovicierre-ui-final-run.json). La corrida previa encontró un supuesto incorrecto del harness documental al superar 20 registros; la prueba final utiliza la búsqueda real por UUID.

**Dictamen: no quedan bloqueadores confirmados abiertos en este alcance.** Las capturas usan datos DEMO sintéticos; no se guardaron cookies, credenciales ni trazas privadas.
