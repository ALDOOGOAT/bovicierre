# Modelo de amenazas — BoviCierre (revisión estática)

- Fecha: 2026-10-12. Rama: `feature/uiux-qa-claude`.
- Revisor: agente `bovi-backend-security` (Claude). Es una revisión **estática de código**: solo lectura, sin ejecutar Docker, make, arneses de BD, escaneos ni ataques.
- Alcance: navegador → Caddy (`infra/`) → Spring Boot (`backend/src/main/java/mx/bovicierre/`) → JDBC → funciones, roles y permisos SQL (`db/migrations/V1..V13`, `db/bootstrap/`) → archivos (`evidencia/`) → CSV/PDF/QR (`reportes/`, `evidencia/`) → FDW/outbox → frontend (`frontend/src/`) → herramientas de agente (`tools/claude/`, `tools/dev/`).
- **Limitación:** esta revisión no demuestra que no haya vulnerabilidades. Cada control descrito aquí se afirma por lectura de código y queda pendiente de confirmar con las pruebas dinámicas propuestas, que deben ejecutarse **solo contra la instancia local**. Los hallazgos están en `docs/security/findings.md`.
- Las referencias a OWASP ASVS 5.0 (capítulos V1–V16) y a WSTG se citan solo por capítulo, como marco de la prueba propuesta.

## 1. Activos

| Activo | Dónde vive | Por qué importa |
|---|---|---|
| Hechos económicos confirmados (operación, liquidación, pago, aplicación, gasto, cierre) | BD A/B, `bovi.*` | Integridad e inmutabilidad (regla no negociable) |
| Credenciales de usuario (`hash_contrasena` bcrypt) | `bovi.usuario` (A, replicado) | Toma de cuentas |
| Sesiones (`infra.spring_session`) y token CSRF | pg-a, por medio de `bovi_auth` | Secuestro de sesión |
| Membresías y roles por sede | `bovi.membresia_usuario` | Autorización horizontal y vertical |
| Documentos privados (PDF/PNG/JPEG) | `BOVI_DOCUMENTS_DIR`, direccionados por SHA-256 | Confidencialidad entre sedes |
| Datos maestros con PII (RFC, teléfono de contrapartes) | `bovi.parte` | Privacidad |
| Secretos de roles SQL y FDW | `BOVI_SECRET_DIR` (fuera del repo), variables de entorno del contenedor y catálogos `pg_user_mapping`/`pg_subscription` | Movimiento lateral |
| Reportes exportables (CSV, PDF de comprobante, QR) | Generados al vuelo | Fuga de datos, inyección de fórmulas |
| Herramientas de agente (plugin y MCP) | `tools/claude/`, `tools/dev/` | Integridad de la evidencia y del flujo de desarrollo |

## 2. Actores

| Actor | Capacidad esperada según el código |
|---|---|
| Anónimo | Solo `/api/v1/sesion/csrf`, `/sesion/login` y `/salud` (`SecurityConfiguration.java:28`). Sin acceso al QR, CSV, PDF ni documentos (todos exigen sesión). |
| ADMIN de sede | Todo dentro de su sede, más usuarios, membresías, periodos, anulación y revisión (`CommandService.java:38-40`, `V13:9`). |
| OPERADOR | Comandos operativos (operación, pesaje, gasto, documento, tarifa). No toca pagos ni usuarios. |
| CAJA | Pagos, aplicaciones, reembolsos y validación. Puede leer toda la sede. |
| AUDITOR | Solo lectura: `authorize(...,mutation=true)` lo excluye (`AccessService.java:39-40`). |
| Usuario de otra sede | Sin membresía vigente en la sede del path, debe recibir 403 (`AccessService.java:36-37`, `V12:434`). Sí ve los maestros de la empresa (SF-13). |
| Usuario bloqueado o con membresía revocada | Se revalida en cada petición (`SecurityConfiguration.java:39`, `AccessService.java:26-29`). |
| Rol SQL limitado (`bovi_app_a/b`, `bovi_auditor`, `bovi_worker`, `bovi_auth`) | Solo EXECUTE sobre las funciones concedidas (`V3:165-177`). Pero `bovi_app_*` tiene SELECT sobre todas las tablas `bovi` y suministra el actor a `cmd_ejecutar` (SF-09). |
| Agente de desarrollo (Claude/MCP) | Lee y escribe el repo. El plugin solo observa (`register.ts`). El MCP de Chrome navega sitios externos (SF-17). |

## 3. Fronteras de confianza y puntos de entrada

1. **Navegador ↔ Caddy** (`127.0.0.1:15180`, `infra/compose/application.yml:32`): HTTP en local y TLS en el ejemplo de producción. Caddy solo añade `nosniff`, `Referrer-Policy` y (en producción) HSTS.
2. **Caddy ↔ backend :18080 / frontend nginx :8080**: red interna de Compose, sin puertos publicados.
3. **Spring ↔ PostgreSQL**: pools `ownerA/ownerB` (rol de app por medio de Pgpool), `authDataSource` (rol `bovi_auth` directo a pg-a), `workerA/B` (`DatabaseConfiguration.java`). Todas las llamadas usan parámetros JDBC `?`.
4. **Funciones SECURITY DEFINER (`bovi_command`)**: aquí ocurre la escalada de privilegio controlada. `cmd_ejecutar` y `consultar` revalidan la membresía, pero confían en `p_actor`.
5. **Nodo A ↔ proveedor (FDW)**: servidor `prov_sim` fijo, rol `bovi_fdw_read` de solo SELECT.
6. **Disco de documentos**: raíz `0700`, nombres = SHA-256.
7. **Agente ↔ Internet** (MCP de Chrome) y **agente ↔ repo** (hooks del plugin).

Puntos de entrada HTTP: `SessionController` (csrf/login/logout/actual/salud), `CoreController` (listas, detalle, creación, acciones, `PATCH` de operaciones), `UserController`, `DocumentController` (multipart/descarga/revisión), `AnimalQrController`, `SettlementController` (PDF), `CsvController`, `ProviderController`, `DiagnosticsController`. Fuera de HTTP: `OutboxWorker` (planificado), `CleanupMain` (CLI local), scripts de bootstrap.

## 4. Controles por amenaza (SEC-01 … SEC-16)

### SEC-01 Inyección SQL (login, búsqueda, folio, ids, filtros, paginación, orden)
- **Control presente:**
  - Todo el SQL de Java usa `JdbcTemplate` con `?`: `AccessService.java:18,27,32` y `CommandService.java:48,81`.
  - Ids validados como `UUID` en el path y en `validateIdFilter` (`CoreController.java:87-94`).
  - Paginación limitada a 1..100 en Java (`CoreController.java:81-82`, `ProviderController.java:24`) y en SQL (`V12:435`).
  - En `consultar`, los valores del usuario viajan por `USING $6/$7/$8`. La búsqueda `q` se limita a 200 caracteres y escapa `\ % _` (`V12:477-478`).
  - `estado` y `tipo` pasan por lista blanca (`V12:495`). `ORDER BY` es fijo (`t.id`/`t.operacion_id`).
  - `operacion_id` se pasa por `quote_literal(...::uuid)` (`V12:508`).
- **Sin verificar:** las ramas de `consultar` con SQL estático que no se leyeron completas (`reparto_gasto`, `fn_reporte`).
- **Prueba dinámica:** WSTG-INPV-05. Enviar `q`, `estado`, `tipo`, `pagina`, `tamano`, `orden` y `operacion_id` con cargas `' OR 1=1--`, `%`, `_`, `\` y 201 caracteres. Esperado: 400/422, nunca 500 y ningún cambio en el `total`. ASVS V1.

### SEC-02 SQL dinámico en PL/pgSQL
- **Control presente:**
  - `format()` usa `%I` para la tabla (`V12:509-511`), con `tab` tomado de un `CASE` cerrado.
  - Los `%s` solo concatenan fragmentos constantes del propio código (`filtro`, columnas extra).
  - En `fn_validar_conciliacion_propietario` (`V3:43-44`) se concatenan `regclass` (salida citada) y columnas por `%I`.
  - Los DDL de triggers (`V2:43-49`) son de migración.
- **Sin verificar:** relaciones no calificadas en funciones definer con `search_path=pg_catalog` (SF-08).
- **Prueba:** test SQL (Testcontainers) que recorra `pg_proc` y falle si una función `prosecdef` contiene `EXECUTE` con `%s` aplicado a una variable derivada de un parámetro. Revisión con `plpgsql_check`.

### SEC-03 Acceso horizontal por sede y recurso
- **Control presente:**
  - `AccessService.authorize` exige membresía vigente en la sede del path y usuario ACTIVO (`AccessService.java:34-43`).
  - `consultar` lo revalida en SQL (`V12:434`) y añade `t.sucursal_id=$2` a las tablas locales (`V12:506`). Los detalles se filtran por `(e,s,id)`.
  - Operación, pago, liquidación y gasto pasan por `consultar`.
  - El QR consulta el animal antes de generarse (`AnimalQrController.java:21`). El PDF consulta la liquidación (`SettlementController.java:20`). La descarga de documentos obtiene el SHA solo de un documento de la sede (`DocumentController.java:42-46`). El CSV usa `query` (`CsvController.java:25`).
  - Las FK compuestas `(empresa_id, sucursal_id, …)` impiden cruzar referencias (p. ej. `V1:885-889`).
- **Sin verificar / hallazgos:**
  - `actualizar_usuario` no limita al usuario destino por sede (SF-01).
  - Los maestros se ven en toda la empresa (SF-13).
  - Un `registrar_documento` invocado con un `sha256` ajeno (SF-15) hoy no es alcanzable.
- **Prueba:** WSTG-ATHZ-04 (IDOR). Usar un usuario sintético con membresía solo en DEMO-B. Pedir GET `/sedes/A/...` y `/sedes/B/operaciones/{id de A}`, `/documentos/{id de A}/contenido`, `/liquidaciones/{id de A}/comprobante`, `/animales/{id de A}/qr` y `/reportes/cartera/csv` de A. Esperado: 403 o 404. ASVS V8.

### SEC-04 Escalada de rol y asignación masiva
- **Control presente:**
  - El servidor rechaza `empresa_id`, `sucursal_id`, `actor_id`, `nodo_dueno`, `sede_operadora_id`, `nodo_origen` y `version_lock` en el cuerpo (`CoreController.java:32-33`), y además `hash_contrasena` en usuarios (`UserController.java:25`).
  - Los totales calculados se rechazan (`JsonSupport.decimals`).
  - La matriz de roles se aplica dos veces: Java (`CommandService.java:38-40`) y SQL (`V13:9`).
  - Una membresía fuera de la sede se rechaza (`V13` en `asignar_membresia`).
  - `estado` de usuario tiene `CHECK (ACTIVO|BLOQUEADO)` (`V1:62`).
- **Sin verificar:** que el ADMIN de B no bloquee usuarios de A (SF-01). Hay divergencia Java/SQL en `crear_periodo` (SF-14).
- **Prueba:** como OPERADOR, CAJA y AUDITOR, POST `/usuarios`, `/usuarios/{id}/membresias` con `rol_codigo=ADMIN`, `/periodos` y `/operaciones/{id}/anular`. Esperado: 403. Como ADMIN, intentar `{"sucursal_id":"<otra>"}`. Esperado: 400.

### SEC-05 CSRF (login y comandos)
- **Control presente:**
  - El repositorio CSRF vive en la sesión, con la cabecera `X-XSRF-TOKEN` (`SecurityConfiguration.java:26,29`). El login **no** se excluye de CSRF, lo que protege contra login CSRF.
  - Tras el login se regenera el token (`SessionController.java:50`).
  - `SameSite=Lax` y `HttpOnly` (`application.yml:9-10`). No hay CORS configurado (solo mismo origen).
  - El frontend envía la cabecera solo en métodos distintos de GET (`frontend/src/api.ts:16`).
  - No se encontraron GET con efectos.
- **Sin verificar:** comportamiento con `Origin` ajeno y con multipart sin cabecera.
- **Prueba:** WSTG-SESS-05. POST de login, logout, comando y multipart sin token o con token de otra sesión. Esperado: 403 `AUTH403`. ASVS V3 y V7.

### SEC-06 Sesiones
- **Control presente:**
  - Contra fijación de sesión: `changeSessionId()` (`SessionController.java:44-45`).
  - Logout con `invalidate()`, también protegido por CSRF (`SessionController.java:53-58`).
  - Expiración por inactividad de 30 min (`application.yml:23`).
  - Usuario bloqueado: se revalida en cada petición (`SecurityConfiguration.java:39` → `AccessService.current`).
  - Membresía revocada: `authorize` y `fn_scope`/`consultar` lo revalidan.
  - `secure=true` en el perfil de producción (`application-production.yml:5`).
- **Sin verificar:**
  - No hay timeout absoluto.
  - La cookie es `secure=false` fuera de producción.
  - Se crean sesiones anónimas en JDBC por `/sesion/csrf` (SF-03).
  - No hay concurrencia máxima de sesiones.
- **Prueba:** WSTG-SESS-03/06/07. Comparar la cookie antes y después del login. Reutilizar la cookie tras el logout (esperado 401). Bloquear o revocar la membresía con otra sesión ADMIN y repetir la petición (esperado 401/403 inmediato). Esperar más de 30 min. ASVS V7.

### SEC-07 XSS
- **Control presente:**
  - No hay `dangerouslySetInnerHTML`, `innerHTML` ni `eval` en `frontend/src`.
  - Los `href` construidos son rutas `/api/v1` con prefijo fijo o anclas `#` (`App.tsx:29,41`, `screens.tsx:34,43,47,77`).
  - El SVG QR se genera en el servidor con contenido fijo y se carga como `<img>` (`App.tsx:59`).
  - Las respuestas API son JSON o `problem+json`.
- **Sin verificar:** no hay CSP (SF-04). El renderizado de campos libres (nombre, motivo, folio) se apoya en el escape por defecto de React.
- **Prueba:** WSTG-CLNT-01 / INPV-01. Crear una contraparte, un folio o un motivo con `<img src=x onerror=alert(1)>` y `javascript:alert(1)`, y comprobar en el navegador real que no se ejecuta. Revisar `Content-Type` del SVG. ASVS V3.

### SEC-08 Archivos
- **Control presente:**
  - Firma por contenido: PDF, PNG y JPEG (`PrivateDocuments.java:110-115`).
  - Tamaño de 1 B a 20 MiB (`PrivateDocuments.java:65`, `application.yml:29-30`).
  - Nombre saneado y truncado a 160 caracteres (`PrivateDocuments.java:79-80`). La ruta sale solo de un SHA-256 validado con regex y `NOFOLLOW_LINKS` (`PrivateDocuments.java:116-119`).
  - Integridad verificada en la descarga (`:121-122`). Raíz con permisos `0700`/`0600`.
  - Versionado validado en SQL (`V13:318`).
  - La descarga sale como `application/octet-stream` con `attachment`, nombre fijo y `nosniff` (`DocumentController.java:46`).
- **Sin verificar / hallazgos:**
  - El archivo se publica antes de verificar el rol del comando (SF-07).
  - Hay lectura completa a memoria (SF-06).
  - Un PDF o JPEG políglota se acepta (mitigado por `attachment`).
- **Prueba:** WSTG-BUSL-08/09. Subir HTML renombrado `.pdf` (esperado 422), un PDF de 20 MiB + 1 B (413), un nombre `../../x` y otro con caracteres de control, un políglota PDF/HTML (debe descargarse, no renderizarse) y una subida como CAJA (esperado 403 **sin** archivo nuevo en disco). ASVS V5.

### SEC-09 CSV, PDF y QR
- **Control presente:**
  - En CSV, las celdas que empiezan por `= + - @` (tras quitar espacios), TAB, CR o LF llevan el prefijo `'`, y todas van entre comillas (`CsvController.java:34-37`). Límite de 10 000 filas (`:30`).
  - El PDF escapa `\ ( )` y caracteres de control (`SettlementPdf.java:30`).
  - El QR solo codifica `/?sede=…#animales/…` y exige sesión y acceso al animal. Un anónimo no ve QR ni PDF.
- **Sin verificar:** variantes de fórmula (SF-12).
- **Prueba:** crear una contraparte `=HYPERLINK("http://x")`, `+1+1`, `@SUM(1)`, `\t=1` o `＝1`, exportar y abrir en LibreOffice sin conexión. Un anónimo pide GET del QR, PDF o CSV: esperado 401.

### SEC-10 Abuso de login y peticiones grandes
- **Control presente:**
  - `@Size(max=80/72)` y 72 bytes UTF-8 en el login (`SessionController.java:39,78`).
  - Bcrypt de coste 12 y hash señuelo para usuarios inexistentes (`SecurityConfiguration.java:24`, `SessionController.java:35,41`).
  - `tamano ≤ 100`, límite multipart, 10 000 filas en CSV.
- **Sin verificar / hallazgos:**
  - No hay rate limiting ni bloqueo (SF-02).
  - No hay límite de cuerpo JSON (SF-05).
  - Hay una diferencia de coste bcrypt con la semilla (SF-10).
  - `pagina` no tiene máximo (un OFFSET grande se mapea a 422 por desbordamiento).
- **Prueba:** WSTG-ATHN-03. 50 logins fallidos por minuto contra `demo.operador` (esperado: throttling o bloqueo). Medir latencias de usuarios existentes e inexistentes. POST de 50 MB JSON. `pagina=2147483647`. ASVS V6.

### SEC-11 Cabeceras, CORS, cookies y errores
- **Control presente:**
  - Los valores por defecto de Spring Security siguen activos en `/api` (`X-Frame-Options: DENY`, `nosniff`, `Cache-Control: no-store`). No hay `headers().disable()`.
  - Caddy añade `nosniff`, `Referrer-Policy` y quita `Server` (`Caddyfile.local:7-11`). En producción, HSTS (`Caddyfile.production.example:10`).
  - CORS ausente (mismo origen).
  - Cookie `HttpOnly`, `SameSite=Lax` y `Secure` en producción.
  - Los errores salen como `problem+json` genérico: SQLState mapeado y P0001 con lista blanca de código, regla y campos (`ApiErrors.java:40-83`), más `BV500` genérico. No hay Actuator.
- **Sin verificar:** falta CSP y anti-framing en la SPA (SF-04). La página `/error` de Spring ante una excepción no mapeada (p. ej. `IllegalStateException` en `CoreController.java:121`) usa los valores por defecto de Boot (sin traza, pero sin confirmar).
- **Prueba:** WSTG-CONF-07/12, CLNT-09. `curl -I` a `/`, `/assets/*` y `/api/v1/salud`. Cargar la SPA en un `<iframe>` local. Forzar 500 y comprobar que la respuesta no trae traza ni SQL. ASVS V3, V13 y V16.

### SEC-12 Roles SQL
- **Control presente:**
  - Roles creados sin atributos elevados: los valores por defecto son NOSUPERUSER, NOBYPASSRLS y NOCREATEDB (`01_roles.sql:3`). Solo `bovi_repl` tiene REPLICATION y `bovi_migrator` es NOINHERIT.
  - Las tablas pertenecen a `bovi_owner` (NOLOGIN).
  - `REVOKE ALL ON ALL FUNCTIONS … FROM PUBLIC` y EXECUTE solo por función (`V3:165-177`). Las funciones nuevas revocan explícitamente (`V4:436`, `V8:21`, `V9:39`, `V12:9,70`).
  - `bovi.usuario` concede SELECT por columnas sin el hash (`V3:159-160`).
  - `REVOKE ALL ON SCHEMA public FROM PUBLIC`.
- **Sin verificar / hallazgos:**
  - `bovi_app_*` tiene SELECT sobre todo `bovi` y no hay RLS (SF-09).
  - Las migraciones corren como `postgres` (SF-11).
  - TEMP no se revoca a PUBLIC (SF-08).
- **Prueba:** consulta en la instancia local: `SELECT rolname,rolsuper,rolbypassrls,rolcreaterole,rolcreatedb FROM pg_roles WHERE rolname LIKE 'bovi%'`. Además, `SELECT p.oid::regprocedure, p.proacl FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='bovi' AND (p.proacl IS NULL OR p.proacl::text LIKE '%=X/%')` (ACL nula o EXECUTE a PUBLIC). Esperado: 0 filas. ASVS V13 y V15.

### SEC-13 Funciones SECURITY DEFINER
- **Control presente:**
  - Todas las definer fijan `SET search_path = pg_catalog` y calificaron sus objetos con `bovi.`/`infra.`/`public.`.
  - El propietario es `bovi_command` (NOLOGIN): bucle `V3:171` y `ALTER OWNER` explícitos (`V4:434`, `V9:37-38`, `V12:8,69`).
  - Las definer públicas revalidan la membresía (`fn_scope`, `V12:434`).
- **Sin verificar:** falta `pg_temp` explícito al final y hay relaciones de catálogo no calificadas (SF-08). Cualquier definer futura creada como `postgres` sin `ALTER OWNER` (SF-11).
- **Prueba:** test que liste `prosecdef` con `proowner<>'bovi_command'::regrole` o `proconfig` sin `search_path`. Esperado: 0. Con `bovi_auditor`, `CREATE TEMP TABLE pg_constraint(...)` y luego llamar a `fn_validar_conciliacion_propietario`. Esperado: no se usa la tabla temporal.

### SEC-14 FDW, SSRF y secretos
- **Control presente:**
  - El servidor FDW está fijado en el bootstrap (`host 'pg-prov'`) con el rol `bovi_fdw_read` de solo SELECT.
  - En `leer_tarifas_proveedor`, `ruta` es un literal parametrizado y la función exige ADMIN u OPERADOR en el maestro A (`V9:2-16`).
  - No hay URL controlada por el usuario en ningún punto (no se encontró `HttpClient`, `URL` ni `dblink`).
  - Secretos fuera del repo (`setup-secrets.sh`, `umask 077`). `.gitignore` cubre `.env*`, `secrets/` y claves. El grep de patrones de secreto sobre los archivos versionados no dio coincidencias. El bootstrap redacta secretos en los errores.
- **Sin verificar:** las contraseñas FDW y de suscripción quedan en catálogos y las de los roles en el entorno del proceso (SF-18). Los logs de PostgreSQL no se revisaron (no hay `log_statement` configurado).
- **Prueba:** `gitleaks detect` o `trufflehog git file://.` sobre todo el historial. Como `bovi_app_a`, `SELECT * FROM pg_user_mappings`. `docker inspect` del backend sin contraseñas.

### SEC-15 Exposición de dependencias y contenedores
- **Control presente:**
  - Todos los puertos publicados están ligados a `127.0.0.1` (`compose.academic.yml:19,24,29,33,40`; `infra/compose/application.yml:32`). En producción se resetean (`production.example.yml:5-14`).
  - El backend escucha en `127.0.0.1` por defecto (`application.yml:3`).
  - Contenedores sin root (`user: 1000`, `nginx-unprivileged`), Caddy `read_only` y `mem_limit`.
  - Imágenes postgres, caddy y temurin fijadas por digest.
  - Spring Boot 4.1.1, ZXing 3.5.4. Sin Actuator.
- **Sin verificar:** CVEs de dependencias (no se ejecutó SCA sin red). `node:24.21.0-alpine` y `nginx-unprivileged:1.29.5-alpine` están fijados por tag, no por digest. `pool_hba.conf` admite `0.0.0.0/0` con scram (solo red interna).
- **Prueba:** `./mvnw org.owasp:dependency-check-maven:check`, `npm audit --omit=dev`, `trivy image bovicierre-backend:local` y `ss -ltnp` en el host para confirmar que no hay escucha en `0.0.0.0`.

### SEC-16 Herramientas de agente (plugin `tools/claude`, MCP)
- **Control presente:**
  - El plugin `bovicierre-workbench` solo observa. Se activa solo con el remote, el marcador y la ausencia de STOP (`logic.ts:91-97`). No bloquea, no ejecuta shell y no usa red (`register.ts`).
  - `relativeTo` rechaza `/../` (`logic.ts:155-158`).
  - `checkpoint.py` invoca `git` con argv, sin shell, y escribe con `O_EXCL 0600`.
  - El MCP de Chrome está fijado en `chrome-devtools-mcp@1.10.1`, con perfil dedicado y sin estadísticas (`tools/dev/chrome_devtools.sh:10-12`).
- **Sin verificar / hallazgos:** la evidencia se marca como satisfecha por coincidencia de texto del comando. `npx -y` no fija las dependencias transitivas. El contenido web externo entra al contexto del agente (SF-17).
- **Prueba:** un test unitario de `satisfied()` con `echo verify-sql` (hoy lo satisface). Revisar el `npm ls` del paquete MCP en caché.

## 5. Pruebas dinámicas prioritarias (solo instancia local)

1. IDOR y cruce de sede con un usuario sintético de membresía única (SEC-03, SF-01).
2. CSRF y sesión: login, comando y multipart sin token, cookie tras logout, bloqueo y revocación en caliente (SEC-05/06).
3. Fuerza bruta y peticiones grandes: logins fallidos en ráfaga, flood de `/sesion/csrf` midiendo `count(*)` de `infra.spring_session`, JSON de 50 MB (SF-02/03/05).
4. Subida maliciosa y descarga: políglota, rol CAJA y comprobación de disco, concurrencia de descargas de 20 MiB con `mem_limit 1g` (SEC-08, SF-06/07).
5. Auditoría de catálogo SQL: ACL, propietarios y `proconfig` de las definer, atributos de rol y prueba de sombreado con `pg_temp` (SEC-12/13, SF-08/11).
