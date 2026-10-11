# Despliegue

Estado: diseñado. Nada desplegado aún; no existe URL pública.

## Entornos
| Entorno | Topología | Uso | Prueba que admite |
|---|---|---|---|
| dev | 1 PostgreSQL + backend + Vite dev server | Iterar reglas y pantallas | Dominio, SQL, API (no M–M) |
| academic | pg-a, pg-b, pg-prov, pgpool-a, pgpool-b, backend, frontend, volumen de documentos (Compose local) | Demostración AC-01..09 | M–M, FDW, Pgpool, restauración |
| staging | Igual que academic en VPS, datos sintéticos, secretos externos | Ensayo de despliegue | Smoke test, TLS |
| pilot | Sólo tras verificar reglas, permisos, respaldo y acuerdo con cliente | Cliente real | — |

## Compose (`infra/compose/compose.academic.yml`)
- Imágenes fijadas por digest (postgres:18, pgpool 4.7.x, caddy 2.x, backend/frontend con tag de versión).
- Redes: `edge` (caddy), `app` (backend ↔ pgpool), `db` (pg-a, pg-b, pg-prov, pgpool); `db` interna, sin puertos al host salvo en dev.
- Volúmenes: `pga_data:/var/lib/postgresql`, `pgb_data`, `prov_data`, `documentos`. PG18 usa `PGDATA=/var/lib/postgresql/18/docker` [F29]; persistencia se prueba recreando el contenedor (TEST-27).
- Healthchecks: `pg_isready`; readiness de suscripción con script que consulta `pg_stat_subscription`; backend `/actuator/health` (readiness exige ambos nodos alcanzables o reporta degradado).
- Secretos: `secrets:` de Compose (archivos fuera del repo); `.env.example` con nombres ficticios.
- Límites: `mem_limit` por servicio (pg 1.5 GB, backend 768 MB) — a calibrar.

## Infraestructura objetivo (hipótesis de capacidad)
VPS Linux 4 vCPU / 8 GB; disco para BD, WAL temporal y documentos; respaldo fuera del host. Referencia USD 48/mes [F33] sin convertir. No se contratan recursos sin autorización del dueño de la cuenta. Caddy expone 80/443 con HTTPS automático [F32] (requiere DNS); PostgreSQL, Pgpool y FDW sólo en red privada. Dos PostgreSQL en un host comparten su fallo: no se anuncia alta disponibilidad.

## Pipeline (GitHub Actions, `.github/workflows/ci.yml`)
1. Lint/format + build backend (`./mvnw -B verify`) y frontend (`npm ci && npm run build`).
2. Pruebas de dominio y SQL con Testcontainers (PostgreSQL real).
3. Lint de OpenAPI (Redocly) y migraciones sobre base limpia.
4. Construir imágenes con tag `git describe`.
5. Publicar en GHCR (registro autorizado del repo).
6. Desplegar staging (manual, con secretos del entorno).
7. Migración una vez por nodo mediante job `migrate` (no al arrancar el backend: `spring.flyway.enabled=false` en runtime).
8. Smoke test de compra/venta/pago.
9. Registrar versión, responsable y evidencia.
Rollback: sólo a una versión de app compatible con el esquema vigente; sin migraciones "down" destructivas; si no es compatible → corrección hacia adelante o restauración con corte (`docs/runbooks/rollback.md`).

## Respaldo y recuperación
Ver `docs/runbooks/backup-restore.md`. Objetivos de piloto propuestos (no alcanzados): RPO ≤ 15 min, RTO ≤ 2 h, que requieren backup base + archivo WAL por nodo fuera del host [F35]. Una réplica no es respaldo.
