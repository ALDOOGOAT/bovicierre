# Informe de dependencias y DAST — 13-oct-2026

Herramientas: **Trivy 0.75.0** (binario oficial con checksum verificado, base de vulnerabilidades local; no se subió código a ningún servicio) y **OWASP ZAP** (`ghcr.io/zaproxy/zaproxy:stable`, sólo contra `http://127.0.0.1:15180` con datos DEMO). Resúmenes versionados: [trivy-summary.json](../testing/evidence/security/20261013-sca/trivy-summary.json) y [zap-summary.json](../testing/evidence/security/20261013-dast/zap-summary.json). Los JSON crudos de Trivy quedan en el directorio privado `~/.local/share/bovicierre-academic/evidence-raw/`.

## Composición de software (SCA)
| Objetivo | Antes | Corrección | Después (altas/críticas) |
|---|---|---|---|
| `backend/pom.xml` | 3 críticas (Tomcat 11.0.24), 5 altas y 2 medias (Jackson 3.1.5) | `tomcat.version` 11.0.25 y `jackson-bom.version` 3.1.7 sobre el BOM de Spring Boot 4.1.1; jar desplegado verificado | 0 |
| `db/migrate/pom.xml` | 2 altas (pgjdbc 42.7.10) | pgjdbc 42.7.13 (la del backend) | 0 |
| npm (`frontend/package-lock.json`) | 0 (vite 8.0.16 desde el 12-oct) | — | 0 |
| Python (`db/requirements.txt`, `tools/dev`) | 0 | — | 0 |
| Secretos en el árbol | 0 | — | 0 |
| Imagen backend | 3 altas en `/usr/bin/pebble` (Go) de la base Temurin | se elimina `pebble`, que no se usa | 0 |
| Imagen frontend | 47 altas Alpine (nginx-unprivileged 1.29.5) | nginx-unprivileged 1.30.5-alpine fijada por digest | 0 |
| Imagen Caddy (borde) | 4 altas: Go 1.26.8 y `x/net` 0.59 (DoS HTTP/2, Range, ECH) | Caddy 2.11.7 recompilado con Go 1.27.2 y `x/net` 0.60.0 (`infra/caddy/Dockerfile`) | 0 |
| Imagen PostgreSQL 18.6 | 1 crítica y 33 altas | digest actual de `postgres:18-alpine` (misma 18.6) | 1 crítica + 24 altas sólo en `gosu` (stdlib Go) de la imagen oficial: **riesgo residual aceptado**, `gosu` sólo corre al arrancar para soltar privilegios y la base no se publica en producción |
| Imagen Pgpool (Debian bookworm) | 1 crítica y 55 altas, todas sin corrección publicada | se probó trixie: 46 altas sin corrección; no compensa cambiar de SO base antes del piloto | **riesgo residual aceptado**: componente interno sin puertos en producción; revisar en cada actualización de Debian |
| Configuración (Dockerfiles) | DS-0002: Pgpool como root | Pgpool corre con UID sin privilegios; `pool_passwd` en `/tmp` | DS-0026 (sin HEALTHCHECK) baja, informativo |

## DAST (OWASP ZAP)
| Pasada | Resultado |
|---|---|
| Baseline sin sesión (araña 3 min, pasivo) | 0 FAIL, 64 PASS, 3 avisos informativos; tras corregir: 0 FAIL, 65 PASS |
| API activa desde `openapi.yaml` (61 rutas con la sede DEMO, sesión `demo.auditor` de sólo lectura, 15 min) | 0 FAIL, 118 PASS; **13 respuestas 500** (byte nulo `%00` en búsquedas/filtros y multipart malformado) y falta de COOP/CORP/COEP |
| API activa tras correcciones | 0 FAIL, 119 PASS; 1 respuesta 502 que coincide con el reinicio del frontend durante el escaneo (verificado: la misma ruta responde 200) y avisos informativos del fallback de la SPA |

Correcciones derivadas: SF-22 (500 → 400) y SF-26 (cabeceras de aislamiento de origen). La sesión del escaneo se cerró al terminar (logout 204, después 401).

## Qué sigue sin cubrirse
DAST con rol de escritura (para no generar datos masivos), Semgrep/SAST dedicado, Gitleaks sobre todo el historial y escaneo de la VM real. Esto no equivale a «sin vulnerabilidades».
