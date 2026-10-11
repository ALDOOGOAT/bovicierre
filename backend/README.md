# Backend BoviCierre

Java 21, Spring Boot 4.1.1, Maven Wrapper 3.9.12. El BOM administra JDBC, Security y Spring Session 4.1.1. Los cálculos monetarios y comandos viven en PostgreSQL; la API no recibe totales ni escribe tablas de negocio directamente.

```bash
./mvnw verify
./run-local.sh
```

El arranque local escucha `127.0.0.1:18080`. `run-local.sh` obtiene secretos externos generados por el bootstrap académico en `$HOME/.local/share/bovicierre-academic/secrets`; no contiene contraseñas. `BOVI_SECRETS_DIR` o `BOVI_SECRET_DIR` permiten indicar otro directorio. Configuración por entorno: `BOVI_DB_A_URL`, `BOVI_DB_B_URL`, `BOVI_AUTH_URL`, sus usuarios/contraseñas, `BOVI_DOCUMENTS_DIR`, `BOVI_API_PORT`. Las URL de negocio por defecto usan Pgpool A `19999`, B `19998`; autenticación usa A `15432` con su rol técnico separado. Perfil `production` marca la cookie Secure y requiere HTTPS.

La sesión JDBC sólo reside en A, mediante `bovi_auth`. Ese rol tiene DML exclusivamente en las tablas de sesión; los roles de negocio invocan `bovi.cmd_ejecutar` y `bovi.consultar`. Cada solicitud autenticada vuelve a verificar el usuario en A y cada acción verifica la membresía actual. A no disponible produce 503; no hay cambio automático de propietario.

Al terminar cada comando, el registro escribe un mensaje JSON con `comando`, `correlation_id`, `nodo_dueno`, `duracion_ms`, `resultado` y, si falla, código público. Las consultas de negocio que duran al menos un segundo escriben `CONSULTA_LENTA` con recurso, propietario y duración. No incluye cuerpos, claves de idempotencia, hashes, archivos, contraseñas ni texto SQL. `GET /api/v1/sedes/{sedeId}/integraciones/diagnostico`, sólo ADMIN con autorización vigente, expone contadores del proceso (éxitos, errores y duración total de comandos; consultas, errores, duración y consultas lentas), snapshot Hikari de conexiones activas/inactivas/en espera/máximo y el corte SQL de sincronización de esa sede. Los contadores se reinician al arrancar y no son transaccionales ni una bitácora económica. `/api/v1/salud` comprueba conectividad de A/B/autorización. No hay exportador de métricas, histograma de latencias ni retraso individual por stream.

Antes de login se consulta `GET /api/v1/sesion/csrf`; devuelve `{token,headerName}` y `Cache-Control: no-store`. Login, logout y todos los comandos requieren ese encabezado. Login rota el identificador de sesión y el CSRF; consultar nuevamente el token después de login. Cookie `BOVI_SESSION`, HttpOnly, SameSite=Lax. Idempotency-Key de 16–80 caracteres; If-Match fuerte (`"1"`) en edición/confirmación. El hash incluye comando, IDs de ruta, cuerpo y versión, con orden canónico de objetos JSON.

Para las pruebas HTTP reales se necesita el servicio arrancado y las migraciones/seed académicos aplicados:

```bash
BOVI_API_IT=true BOVI_TEST_PASSWORD_FILE="$HOME/.local/share/bovicierre-academic/secrets/demo_password" ./mvnw test
```

Las pruebas HTTP quedan explícitamente omitidas sin esa variable; las pruebas unitarias no dependen de una base. No se usa H2. El runner SQL en `db/tests/` verifica GOLD y restricciones con PostgreSQL real.

Los archivos admiten PDF, PNG y JPEG por firma inicial y un máximo de 20 MiB, se guardan fuera de recursos web con SHA-256 y se descargan tras verificar el scope, como adjuntos. La firma identifica el formato, no constituye un análisis antimalware. Las cargas usan staging UUID privado y publicación atómica del SHA-256. El bloqueo por hash se mantiene hasta terminar el comando SQL y su commit; el resultado documental completo se guarda para replay. Las versiones enlazan al documento previo y las revisiones señalan IDs exactos. Un fallo SQL puede dejar contenido sin referencia durante al menos 24 horas.

`./cleanup-documents.sh` sólo diagnostica huérfanos de más de 24 horas. `./cleanup-documents.sh --execute` elimina los candidatos revisados en esa ejecución: ambos nodos deben responder que el SHA-256 no tiene referencia, y el bloqueo compartido excluye las cargas activas. Nunca borra contenido reciente, referenciado, bloqueado o con una consulta fallida. El comando usa el rol worker, no arranca API ni schedulers.

Los QR se generan localmente como SVG mediante ZXing y conservan autenticación/scope. Los CSV usan valores canónicos de SQL y neutralizan fórmulas de hojas de cálculo; el PDF de liquidación no crea nuevos hechos económicos.

`run-local.sh` guarda PID Java y registro en `~/.local/share/bovicierre-academic/run` (o `BOVI_RUNTIME_DIR`). Para una copia coherente, terminar ese PID propio mediante SIGTERM y esperar su salida: HTTP y scheduler tienen drenaje de 30 segundos. Después de terminar, comprobar que no quedan transacciones financieras activas antes de copiar base y archivos. Reiniciar con `./run-local.sh`; no se usa SIGSTOP.

El Dockerfile construye con Java 21 y Wrapper y ejecuta como UID/GID 1000. El entrypoint admite `BOVI_DB_A_PASSWORD_FILE`, `BOVI_DB_B_PASSWORD_FILE`, `BOVI_AUTH_PASSWORD_FILE` y `BOVI_WORKER_PASSWORD_FILE`. El contenedor escucha internamente en `0.0.0.0`; publicar sólo en loopback corresponde al Compose local. No contiene Flyway ni intenta DDL al arrancar.

Prueba fresca separada con un único PostgreSQL 18.6 efímero, migraciones reales y comprobación del rol runtime:

```bash
BOVI_TC_IT=true ./mvnw -Dtest=PostgresContainerTest test
```

Testcontainers 2.0.5 viene del BOM de Spring Boot. Esta prueba se omite sin la variable explícita; no depende de los puertos académicos.

La consulta FDW del proveedor simulado se lee siempre en A mediante una conexión autocommit. Después de terminar esa consulta, otra conexión autocommit guarda la cotización técnica en el propietario de la sede, A o B, antes de cualquier bloqueo financiero. El token se acepta con `POST /integraciones/proveedor/tarifas/aceptaciones`; un gasto puede referir ese `snapshot_id`, con importe igual al monto canónico aceptado. La fuente original de cuatro decimales y la política de redondeo se conservan en SQL; Java no redondea ni reconstruye el snapshot.
