# Contexto del backend

Actualizado el 2026-10-11. Implementación ejecutable en Java 21, Spring Boot 4.1.1, Maven Wrapper 3.9.12 y JDBC, bajo `mx.bovicierre`. El servidor usa transacciones con propietario explícito A o B; no escribe directamente tablas de negocio ni calcula importes mediante coma flotante.

## Autoridades e implementación

Las reglas y oráculos están en [domain](../domain/), las decisiones en [ADR](../architecture/adr/), el contrato HTTP en [OpenAPI](../api/openapi.yaml) y el SQL físico en [db/migrations](../../db/migrations/). La definición vigente de `bovi.cmd_ejecutar` es [V13](../../db/migrations/V13__correccion_composicion_exacta.sql); reemplaza las versiones históricas de esa función. Las consultas, la composición histórica de pesajes y los informes canónicos vigentes están en [V12](../../db/migrations/V12__pesajes_reportes_canonicos.sql); los cálculos auxiliares y la comprobación de periodos proceden de V2. Se aplica la secuencia completa V1–V13 mediante la migración externa: el proceso de aplicación no contiene Flyway ni ejecuta DDL al arrancar.

Están implementados sesión y administración de usuarios/membresías, maestros, operaciones y acuerdos versionados, pesajes, reservas, inventario y movimientos, liquidaciones, pagos/aplicaciones/reversos/reembolsos, ajustes con conciliación atómica, gastos y tres métodos de reparto, periodos/cierres/reapertura, consultas e informes, archivos privados, QR local y PDF. El proveedor simulado se consulta por FDW exclusivamente en A; después se guarda una captura inmutable en el propietario de la sede, antes de cualquier transacción financiera. El trabajador de la cola de salida usa reservas temporales persistentes y consumo idempotente de muerte B→A.

La sesión JDBC reside en A con rol técnico separado. Cada solicitud autenticada y cada comando vuelven a verificar autorización vigente en A; su caída devuelve 503. Las operaciones económicas se ejecutan en el propietario de la sede. Una caída de B no cambia el propietario ni reinicia el proceso de aplicación. El navegador obtiene CSRF en `/api/v1/sesion/csrf`; login y logout también lo requieren. Cookie `BOVI_SESSION`, HttpOnly y SameSite=Lax; Secure sólo en el perfil de producción con HTTPS.

Los decimales entran como cadenas con escala explícita; los resultados financieros provienen del SQL canónico. El detalle JSON de errores PostgreSQL `P0001` se valida antes de exponer códigos BV, regla y campos públicos; no se devuelve SQL. Los errores de seguridad se escriben en UTF-8. La intención de idempotencia incluye IDs de ruta, cuerpo y versión original. Una repetición del mismo comando devuelve el resultado persistido antes de comprobar nuevamente `If-Match`; un contenido diferente devuelve 409. La guarda incorporada en V11 al cancelar y anular se conserva en V13. La corrección de pesaje exige motivo, identifica el original por la ruta y conserva su conjunto de animales; los pesos individuales desconocidos permanecen nulos.

## Ejecución y rutas

El desarrollo nativo se inicia con `./backend/run-local.sh` y escucha en `127.0.0.1:18080`. Obtiene secretos de un directorio externo privado; los documentos quedan fuera del repositorio. Las conexiones de negocio usan Pgpool A/B; autenticación usa la conexión técnica A. Para una copia coherente, el PID propio se termina mediante SIGTERM y se espera el drenaje HTTP/trabajador antes de copiar base y archivos.

El arranque académico integrado es `make academic`. Usa [application.yml](../../infra/compose/application.yml), construye las imágenes locales de backend/frontend y sirve un único origen mediante Caddy en **`http://127.0.0.1:15180`**. Rechaza el arranque si sigue activa la API nativa en 18080. Sólo Caddy publica un puerto en loopback; el servidor escucha internamente en 18080 con usuario sin privilegios. Los secretos se montan como archivos y el directorio documental privado es externo. Esta ejecución local usa HTTP; no acredita TLS ni publicación de producción.

| Ruta completa | Acceso y resultado |
| --- | --- |
| `GET /api/v1/salud` | Público. Comprueba disponibilidad de A, B y autorización A por separado; no publica credenciales. |
| `GET /api/v1/sedes/{sedeId}/integraciones/diagnostico` | Sólo ADMIN vigente. Contadores del proceso, snapshot Hikari real y corte SQL de sincronización de la sede. AUDITOR recibe 403. |
| `GET /api/v1/sedes/{sedeId}/comandos/{comando}/{clave}` | Autenticado y limitado a sede/principal; permite consultar el resultado de una respuesta perdida antes de repetir. |

Los registros de comandos son mensajes JSON con comando, correlación, propietario, duración y resultado/código público; no incluyen cuerpos, claves, hashes, contraseñas ni SQL. Las consultas de al menos 1000 ms registran recurso, propietario y duración. El diagnóstico expone conexiones activas/inactivas/en espera/máximo y contadores de éxitos, errores y duración; los contadores se reinician al arrancar y no sustituyen auditoría económica.

## Evidencia comprobada

La ejecución final vigente pasó **24 pruebas**, sin fallos, errores ni omisiones: **15 unitarias + 8 HTTP reales por Caddy15180 + 1 Testcontainers** con un PostgreSQL 18.6 recién creado y las migraciones V1–V13. [verification-result-v13.json](../../backend/verification-result-v13.json), capturado `2026-10-11T21:41:45.192202Z`, conserva el comando, resultados, hashes de fuentes y la imagen ejecutada. Incluye sesión/CSRF/autorización vigente, idempotencia, compra/venta/pago, archivos privados, captura A→B, identificadores ASCII, filtros tipados, diagnóstico ADMIN y versiones obsoletas. La ampliación comprueba composición original y motivo de pesajes, rechazo de cambios de conjunto con rollback y exportación CSV de cartera, margen e inventario con contenido e importes canónicos.

El resultado **histórico V11 de 21 pruebas** (13 unitarias + 7 HTTP nativas18080 + 1 Testcontainers V1–V11) permanece en [verification-result.json](../../backend/verification-result.json), capturado `2026-10-11T20:44:23.432362Z`. No es la ejecución final por Caddy ni se ha reescrito como si hubiera cubierto V13.

```bash
BOVI_API_IT=true BOVI_TC_IT=true \
  BOVI_API_TEST_URL=http://127.0.0.1:15180/api/v1 \
  BOVI_TEST_PASSWORD_FILE="$HOME/.local/share/bovicierre-academic/secrets/demo_password" \
  ./backend/mvnw -q -f backend/pom.xml verify
```

El coordinador ejecutó `make academic` con salida 0 y validó 17 intercambios de sesión/lecturas, diagnóstico y salud contra15180 con V13: [contract-read-v13.json](../testing/evidence/contract-read-v13.json), sin errores de esquema en las respuestas registradas. Esta prueba de contrato no cubre todas las rutas ni sustituye los escenarios económicos. La [revisión SQL](../testing/evidence/review-database.md) conserva el hallazgo de versión obsoleta, su corrección V11 y la hipótesis descartada sobre precisión del proveedor.

## Límites y continuidad

Los archivos admiten PDF/PNG/JPEG por firma inicial y máximo de 20 MiB; no hay análisis antimalware. La publicación documental usa staging privado, movimiento atómico y bloqueo por huella hasta confirmar SQL. La limpieza diagnostica por defecto y sólo elimina contenido sin referencia, de más de 24 horas, con ambos nodos disponibles y sin carga activa. El PDF usa texto WinAnsi y no incrusta una fuente Unicode completa.

No se indujo artificialmente una consulta lenta en la verificación final. No hay histograma de latencias, exportador de métricas ni retraso individual por flujo de replicación; la sincronización ofrece un corte agregado. El [benchmark SQL V13](../../db/tests/benchmark-result.json) mide 800 lecturas mediante Pgpool con caché caliente en QA separada; excluye HTTP y carga escritora, por lo que no acredita latencia de la API ni capacidad comercial. Los resultados corresponden al conjunto DEMO y no acreditan TLS, CI remoto ni aceptación humana de todos los escenarios. La [restauración final V13](../testing/evidence/recovery/restore-v13.json) comprobó firmas, archivos, sesiones invalidadas y replay en el mismo host; no demuestra PITR ni recuperación frente a pérdida física del host. Conservar esas evidencias sin confundirlas con la ejecución histórica nativa de 21 pruebas.
