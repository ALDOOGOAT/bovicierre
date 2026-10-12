# Hallazgos de seguridad — campaña UI/UX + QA (S2)

Fecha 2026-10-12, rama local `feature/uiux-qa-claude`. Fuentes: revisión estática del agente `bovi-backend-security` (Claude Opus, sólo lectura; contexto en [threat-model.md](threat-model.md)) y pruebas dinámicas propias `tests/security/sec_dynamic.py` contra `127.0.0.1:15180` con datos DEMO. Severidades provisionales. **Ni la revisión ni las pruebas demuestran ausencia de vulnerabilidades**; sólo cubren lo ejecutado.

Estados: ABIERTO_ESTATICO (sólo lectura) · CONFIRMADO (reproducido) · CORREGIDO (corrección + prueba antes/después) · RIESGO_ACEPTADO (con motivo) · NO_REPRODUCIDO.

| ID | Sev. | Componente | Evidencia | Estado | Corrección / decisión | Prueba |
|---|---|---|---|---|---|---|
| SF-01 | media | `actualizar_usuario` (V13:26) vía `UserController` | ADMIN de una sede podía bloquear/renombrar a cualquier usuario de la empresa | CORREGIDO (Java) | `AccessService.member`: el destino debe tener membresía en la sede del path (404 si no); se impide el autobloqueo. La función SQL sigue sin comprobarlo → defensa sólo en API (ver SF-09) | `sec_dynamic.py` casos SF-01 |
| SF-02 | media | Login | Sin límite de intentos; confirmado: 25 fallos seguidos → sólo 401 | CORREGIDO | `LoginThrottle`: 10 fallos/15 min por login y 50 por origen → 429 + `Retry-After`; se evalúa antes de bcrypt; en memoria (una instancia) | `LoginThrottleTest` 3/3; dinámico: 10×401 y luego 429, otro usuario entra |
| SF-03 | media | `/sesion/csrf` anónimo | Confirmado: 100 GET sin cookie → +97/+100 filas en `infra.spring_session`, TTL 30 min | CORREGIDO (mitigación) | Sesión anónima con TTL 300 s; tope de 600 sesiones nuevas por origen cada 15 min (429 + `Retry-After`); al iniciar sesión vuelve a 1800 s. El crecimiento por petición persiste dentro de esos límites | `sec_dynamic.py`: TTL anónimo 300 s, autenticado 1800 s; `LoginThrottleTest.topeDeSesionesAnonimasPorOrigen` |
| SF-04 | baja | Cabeceras SPA | Sin CSP/XFO/Permissions-Policy (confirmado con `curl -I`) | CORREGIDO | Caddy local y ejemplo de producción: CSP `default-src 'self'…; frame-ancestors 'none'`, `X-Frame-Options DENY`, `Permissions-Policy` | Dinámico PASS; E2E 16/16 con 0 violaciones CSP en consola |
| SF-05 | baja | Cuerpo JSON | Sin límite: 3 MB llegaban a Spring (422) | CORREGIDO | Caddy `request_body` 1 MB para JSON en `/api/*`; multipart conserva 22 MB (Spring 20 MB) | Dinámico: 3 MB → 413, `/salud` 200 |
| SF-06 | baja (posible) | Documentos | `getBytes`/`readAllBytes` de hasta 20 MiB en memoria | ABIERTO_ESTATICO | Streaming y límite de concurrencia (pendiente; no se ejecutó la prueba de 60 descargas) | — |
| SF-07 | baja | Documentos | CAJA escribe el archivo en disco antes del rechazo del comando | ABIERTO_ESTATICO | Verificar rol antes de `stage` | — |
| SF-08 | baja (posible) | SQL definer | `search_path=pg_catalog` sin `pg_temp` final; catálogos no calificados; TEMP no revocado a PUBLIC | ABIERTO_ESTATICO | Migración V14 con `SET search_path=pg_catalog,pg_temp` + `REVOKE TEMP` + prueba de catálogo (pendiente S2+) | — |
| SF-09 | media | Confianza en credencial `bovi_app_*` | SELECT sobre todo `bovi` sin RLS; `p_actor` lo envía el llamador | RIESGO_ACEPTADO provisional | El diseño confía en la API como único llamador (ADR de dos escritores). Mitigación: credencial sólo en el contenedor backend. Requiere decisión humana (RLS/contexto de actor) | — |
| SF-10 | baja (posible) | Login | Señuelo bcrypt coste 12 vs semilla coste 10 → posible enumeración por tiempo | ABIERTO_ESTATICO | Igualar coste / rehash al iniciar sesión | — |
| SF-11 | baja | Migraciones | Flyway corre como `postgres` | ABIERTO_ESTATICO | `bovi_migrator` + `SET ROLE bovi_owner` | — |
| SF-12 | info | CSV | Prefijo `'` en negativos; variantes Unicode `＝`/`＋` no cubiertas | ABIERTO_ESTATICO | NFKC + no prefijar decimales válidos | Dinámico: fórmulas ASCII neutralizadas (PASS) |
| SF-13 | info | Maestros | Contrapartes/predios/animales/usuarios visibles entre sedes | PENDIENTE_HUMANO | Coherente con "maestros en A, una empresa por despliegue"; confirmar con la regla de negocio | — |
| SF-14 | info | Roles | `crear_periodo`: Java exige ADMIN, SQL permite OPERADOR | ABIERTO_ESTATICO | Tabla única de permisos por comando | — |
| SF-15 | info | Documentos SQL | `registrar_documento` confía en el `sha256` del payload | ABIERTO_ESTATICO | No alcanzable hoy desde HTTP | — |
| SF-16 | info | API documentos | Respuesta incluye `storage_key` | ABIERTO_ESTATICO | Quitar del DTO | — |
| SF-17 | info | Plugin propio `bovicierre-workbench` | Regex de verificación satisfecha por `echo verify-sql` | CORREGIDO | Regex anclados al inicio del comando | `claude plugin test` 6/6 con casos `echo`/`grep` |
| SF-18 | info | Secretos | Secretos en env de contenedor; mapping FDW legible por `bovi_app_a`; `secure:false` local | ABIERTO_ESTATICO | `configtree:`, mapping restringido, fallo de arranque en producción sin `Secure` | — |
| SF-20 | media | Traducción de errores SQL | UNIQUE inline de V1 con nombre autogenerado (`*_key`) → 500 BV500 en lugar de 409 (DIV-01). Reproducido por la prueba de carga (08:48:32 UTC) | CORREGIDO | `ApiErrors` traduce `23505` con sufijo `_key` a 409 BV401 sin detalle SQL | `ContractTest`; `sec_dynamic.py` casos DIV-01 → 409 |
| SF-21 | alta (sólo dev) | `vite` 8.0.3 | GHSA-4w7w-66w2-5vf9, GHSA-v2wj-q39q-566r: afectan al servidor de desarrollo | CORREGIDO | `vite@8.0.16` | `npm audit`; build/unitarias/E2E repetidos |
| SF-19 | info | Frontend | Intentos pendientes (`bovi:pending:`) permanecen en `sessionStorage` tras logout | RIESGO_ACEPTADO | Purgarlos permitiría recapturar un comando de resultado incierto (duplicado económico, regla 8). `sessionStorage` es por pestaña y por principal; no contiene contraseña ni archivos | — |

## Pruebas dinámicas (resumen)
Primera ejecución: 48/56 PASS ([dynamic-before-fixes.json](../testing/evidence/security/20261012T0234/dynamic-before-fixes.json)). De los 8 FAIL, 4 eran defectos del propio test (nombre de cookie `BOVI_SESSION`, `Accept` del QR SVG, 422 como rechazo válido de enum) y 4 hallazgos reales (SF-02, SF-04×2, SF-05). Tras las correcciones y los casos nuevos (SF-01, SF-03, DIV-01): **63/63 PASS** ([dynamic.json](../testing/evidence/security/20261012T0234/dynamic.json)).

Cobertura **no ejecutada**: ZAP/DAST autenticado, Semgrep/Gitleaks/Trivy/escáner Maven (no instalados; ver [dependency-report.md](dependency-report.md)), subida políglota de archivos, sombreado `pg_temp`, descargas concurrentes de 20 MiB, enumeración por tiempo.

## Salida
Ningún hallazgo crítico/alto **confirmado y no mitigado dentro del alcance ejecutado**. Abiertos: 1 media aceptada provisionalmente (SF-09, requiere decisión humana), bajas/info estáticas sin reproducir. Esto no es una certificación de seguridad ni habilita un piloto por sí mismo.
