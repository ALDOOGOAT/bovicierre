# Informe de dependencias — 12-oct-2026

| Ecosistema | Herramienta | Resultado | Estado |
|---|---|---|---|
| npm (frontend) | `npm audit` (registro npm, árbol de 123 paquetes; 5 de producción) | Antes: 1 alto (`vite` 8.0.3, directo, dev) + 1 bajo (`esbuild` 0.27.7, transitivo, dev). Después de fijar `vite@8.0.16`: 1 bajo. `npm audit --omit=dev`: 0 | COMPLETO para npm ([json previo](../testing/evidence/security/20261012T0234/npm-audit.json)) |
| Maven (backend) | — (OWASP Dependency-Check/OSV no instalados) | 11 dependencias directas listadas (`dependency:list`): Spring Boot 4.1.1 starters (webmvc, security, validation, jdbc, session-jdbc), PostgreSQL JDBC 42.7.13, ZXing 3.5.4, Testcontainers 2.0.5 (test) | **INCOMPLETO**: sin base de vulnerabilidades consultada. No equivale a "0 vulnerabilidades" |
| Python (herramientas de prueba/semilla) | — (pip-audit no instalado) | `psycopg[binary]==3.3.2`, `PyYAML==6.0.1`; no son dependencias del producto | INCOMPLETO |
| Imágenes de contenedor | — (Trivy no instalado) | Bases fijadas en Dockerfiles (`node:24.21.0-alpine`, `nginx-unprivileged:1.29.5-alpine`, etc.) | INCOMPLETO |
| Secretos en Git | búsqueda propia de los valores de `~/.local/share/bovicierre-academic/secrets/*` sobre los archivos preparados para commit | 0 coincidencias en cada commit de la campaña | Parcial (no es Gitleaks sobre el historial completo) |

## Triage
| Paquete | Advisory | Alcance real | Decisión |
|---|---|---|---|
| vite 8.0.3 → 8.0.16 | [GHSA-4w7w-66w2-5vf9](https://github.com/advisories/GHSA-4w7w-66w2-5vf9) (path traversal en `.map` de deps optimizadas), [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r) (`server.fs.deny` con queries) | Sólo servidor de desarrollo (`npm run dev`, ligado a 127.0.0.1). El despliegue sirve el build estático con nginx | Actualizado a la versión parcheada mínima de la misma rama 8.0.x (publicada 2026-06-01); build, unitarias y E2E repetidos |
| esbuild 0.27.7 | [GHSA-g7r4-m6w7-qqqr](https://github.com/advisories/GHSA-g7r4-m6w7-qqqr) (lectura de archivos del dev server en Windows) | Dev, Linux | Riesgo aceptado; revisar al subir `tsx`/`vite` |

Herramientas instaladas en esta campaña: k6 v1.0.0 (binario oficial con checksum verificado, `~/.local/bin/k6`) para carga. No se usó `npm audit fix --force` ni se subieron dependencias de versión mayor.
