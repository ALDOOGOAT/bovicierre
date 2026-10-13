# Plan y matriz de pruebas de seguridad (SEC-01..16)

Alcance: sólo la instancia local BoviCierre (`127.0.0.1:15180`, contenedores `bovicierre-academic-*`) con datos sintéticos DEMO. Nunca redes de terceros, otros contenedores ni sitios de referencia. Referencias: OWASP WSTG (diseño de pruebas) y ASVS (requisitos), aplicados sólo donde se indica; no se declara conformidad ASVS. Modelo de amenazas: [threat-model.md](threat-model.md). Resultados: [findings.md](findings.md).

| ID | Prueba | Cómo | Resultado 12-oct-2026 |
|---|---|---|---|
| SEC-01 | SQLi en búsqueda/filtros/paginación + nombre legítimo con apóstrofe | `tests/security/sec_dynamic.py` (6 payloads en `q`, 4 en filtros, verificación de conteo antes/después) | PASS 12/12 |
| SEC-02 | SQL dinámico en PL/pgSQL | Revisión estática (`EXECUTE`/`format`) | Sin `%s` con entrada de usuario según el agente; SF-08 corregido en V14 |
| SEC-03 | Acceso horizontal por sede/recurso (operación, expediente, pago, QR, CSV, cartera, escritura) y ADMIN de otra sede (SF-01) | Usuario sintético con una sola sede | PASS (403/404, 0 efectos); SF-01 corregido |
| SEC-04 | Escalada de rol / mass assignment / autobloqueo | Operador crea usuario o se asigna ADMIN; cuerpo con `empresa_id`/`sucursal_id`/`id` | PASS |
| SEC-05 | CSRF en comandos y login | Sin token, token falso, verificación de no persistencia | PASS 4/4 |
| SEC-06 | Sesión: rotación, logout, error uniforme, membresía revocada en caliente, TTL | Cookies reales `BOVI_SESSION` | PASS |
| SEC-07 | XSS almacenado | Nombre con `<img onerror>`: la API responde JSON; React escapa (sin `dangerouslySetInnerHTML`, revisión estática) | PASS parcial (no se ejecutó navegador sobre ese registro) |
| SEC-08 | Archivos (firma/tamaño/traversal/descarga) | Revisión estática; `PrivateDocumentsTest` 5/5 | Dinámico de subida políglota **no ejecutado** |
| SEC-09 | CSV fórmulas, QR anónimo | CSV de cartera, QR sin sesión | PASS (ASCII); SF-12 Unicode abierto |
| SEC-10 | Abuso de login, sesiones anónimas, paginación extrema, cuerpo grande | 12 intentos fallidos, 100 GET `/sesion/csrf`, `tamano`/`pagina` extremos, JSON 3 MB | PASS tras SF-02/03/05 |
| SEC-11 | Cabeceras, CORS, cookies, errores sin stack/SQL, UNIQUE→409 | `curl`/runner | PASS tras SF-04/SF-20 |
| SEC-12 | Roles SQL (superuser, DDL, DML financiero, replicación) | `db/tests/security.sql` en A y B dentro de `make verify-sql` | PASS ("runtime DML/DDL/replica-role denied") |
| SEC-13 | SECURITY DEFINER y sombreado `pg_temp` | `db/tests/security.sql` (catálogo de `proconfig`, ACL de base, `CREATE TEMP TABLE` como `bovi_auditor`) | PASS en A/B y en restauración V14; SF-08 corregido |
| SEC-14 | FDW sólo lectura, secretos | `make verify-sql` (TEST-25: UPDATE denegado 42501); revisión estática | PASS FDW; SF-18 abierto |
| SEC-15 | Dependencias y exposición de puertos | Trivy (Maven, npm, Python, imágenes) y `docker ps`; producción sin puertos de BD | COMPLETO 13-oct: ver SEC-18 y [dependency-report](dependency-report.md) |
| SEC-17 | DAST con OWASP ZAP | Baseline pasivo y escaneo activo de la API desde OpenAPI con sesión de sólo lectura, sólo local | 0 FAIL; 13×500 corregidos (SF-22); COOP/CORP/COEP añadidas (SF-26) |
| SEC-18 | SCA de código e imágenes | Trivy fs + imágenes desplegadas | 0 altas/críticas en código, backend, frontend y Caddy; residual aceptado en PostgreSQL (`gosu`) y Pgpool (Debian sin corrección) |
| SEC-16 | Cadena de herramientas del agente | Revisión del plugin propio, MCP y skills | SF-17 corregido; MCP de navegador/`npx -y` documentados |

Repetición: `python3 tests/security/sec_dynamic.py --out docs/testing/evidence/security/<run>/dynamic.json` (requiere la app levantada; crea usuarios/registros DEMO SEC; 12 intentos fallidos sobre un login inexistente, no bloquea cuentas reales).
