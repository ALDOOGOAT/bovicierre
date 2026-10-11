# Despliegue

Estado: aplicación integrada ejecutada en Docker/Caddy HTTP loopback15180. Sin despliegue público ni URL externa.

## Entornos
| Entorno | Topología | Uso | Prueba que admite |
|---|---|---|---|
| dev | A/B/proveedor + backend nativo + Vite dev server (implementado; simplificación a una BD no preparada) | Iterar reglas y pantallas | Dominio, SQL, API (no M–M) |
| academic | pg-a, pg-b, pg-prov, pgpool-a, pgpool-b, backend, frontend, volumen de documentos (Compose local) | Demostración AC-01..09 | M–M, FDW, Pgpool, restauración |
| staging | Igual que academic en VPS, datos sintéticos, secretos externos | Ensayo de despliegue | Smoke test, TLS |
| pilot | Sólo tras verificar reglas, permisos, respaldo y acuerdo con cliente | Cliente real | — |

## Compose (`infra/compose/compose.academic.yml`)
- Imágenes fijadas por digest (postgres:18, pgpool 4.7.x, caddy 2.x, backend/frontend con tag de versión).
- Local comprobable: red bridge propia del proyecto Compose; los puertos publicados son sólo loopback. La segmentación edge/app/db pertenece a la preparación de piloto y no está aplicada aún. Antes de VM pública retirar los mapeos PostgreSQL/Pgpool locales y configurar redes privadas.
- Volúmenes: `pga_data:/var/lib/postgresql`, `pgb_data`, `prov_data`, `documentos`. PG18 usa `PGDATA=/var/lib/postgresql/18/docker` [F29]; persistencia se prueba recreando el contenedor (TEST-27).
- Healthchecks: `pg_isready`; readiness de suscripción con script que consulta `pg_stat_subscription`; backend `/api/v1/salud` (implementación propia; sin Actuator) (disponibilidad A requerida para nuevas peticiones autenticadas; B/proveedor degradados no reinician el backend que sirve A).
- Secretos: `secrets:` de Compose (archivos fuera del repo); `.env.example` con nombres ficticios.
- Límites: `mem_limit` por servicio (A/B1GiB, proveedor512MiB, backend1GiB, frontend/Caddy128MiB) — a calibrar.

## Infraestructura objetivo (hipótesis de capacidad)
VPS Linux 4 vCPU / 8 GB; disco para BD, WAL temporal y documentos; respaldo fuera del host. Referencia USD 48/mes [F33] sin convertir. No se contratan recursos sin autorización del dueño de la cuenta. Caddy expone 80/443 con HTTPS automático [F32] (requiere DNS); PostgreSQL, Pgpool y FDW sólo en red privada. Dos PostgreSQL en un host comparten su fallo: no se anuncia alta disponibilidad.

## Pipeline (GitHub Actions, `.github/workflows/local-verification.yml`)
1. Workflow manual preparado: comprobaciones documentales/OpenAPI, backend+Testcontainers y build/unitariasfrontend. No hay formatter/lint de aplicación configurado; no inventar esa ejecución.
2. Pruebas de dominio y SQL con Testcontainers (PostgreSQL real).
3. Lint de OpenAPI (Redocly) y migraciones sobre base limpia.
4. Build de imágenes local con tags`:local`; pipeline de imágenes remoto no configurado.
5. Publicación GHCR excluida del workflow local; requiere encargo posterior.
6. Staging externo pendiente de autorización, dominio y secretos; no se activa por push.
7. Migración una vez por nodo mediante job `migrate` (no al arrancar el backend: `spring.flyway.enabled=false` en runtime).
8. Smoke test de compra/venta/pago.
9. Registrar versión, responsable y evidencia.
Rollback: sólo a una versión de app compatible con el esquema vigente; sin migraciones "down" destructivas; si no es compatible → corrección hacia adelante o restauración con corte (`docs/runbooks/rollback.md`).

## Respaldo y recuperación
Ver `docs/runbooks/backup-restore.md`. Objetivos de piloto propuestos (no alcanzados): RPO ≤ 15 min, RTO ≤ 2 h, que requieren backup base + archivo WAL por nodo fuera del host [F35]. Una réplica no es respaldo.

## Uso integrado local

`make academic` ejecuta bootstrap/migración independiente y arranca API/frontend/Caddy; rechaza API manual concurrente en18080. Acceso15180 loopback. UID/GID son del usuario, documentos0700 externos. `make stop` conserva volúmenes y detiene sólo servicios del Compose propio. `.env.example` contiene rutas/dominio inválidos de muestra, no contraseñas. Producción requiere revisión explícita del despliegue, perfil `production`, TLS real, datos iniciales conciliados, seed prohibido y respaldos fuera del host. No copiar el Compose local como si ya ofreciera aislamiento de red o recuperación comercial.

## Configuración de VM para revisión

[Overrideproduction](../../infra/compose/production.example.yml) y [condiciones de arranque](../../infra/compose/README.production.md): quita puertos publicados de PostgreSQL/Pgpool, Caddy80/443/TLSpersistente, perfilproduction/cookieSecure y secretos externos. Compose5.1.3 `config` comprobado sinarranque; dominio `.invalid`, sinDNS ni certificado. Los scriptsDEMO rechazanproduction antes de operaciones; bootstrap comercial y migración separada requieren revisión. No se publica ni se aplica esta configuración al host local.

## ETag y proxy

La API conserva ETag fuerte de versión, sin transformación por compresión en Caddy. `encode gzip` se aplica sólo al frontend: comprimir respuestas API añadía `-gzip` al ETag y el If-Match posterior fallaba400. Se comprueba mediante el recorrido integrado, además de las pruebas directas del backend.

## Presupuesto local de conexiones

Hikari limita ownerA/ownerB/auth a4cadauno y workerA/workerB a2cadauno, minimumIdle0. App y worker de un dueño consumen como máximo6clientes dentro de los16children/max_pool1 de su Pgpool; no se suman dos veces a conexiones físicas. Auth añade hasta4conexiones directas aA. PostgreSQL permite50clientes,12WALsenders y12slots por nodo; la topología usa una suscripción entrante y una saliente por nodo, además de administración/migración y conexiones FDW salientes deA al proveedor. El límite de clientes no equivale al límite de backgroundworkers/WALsenders. [Observación real](../testing/evidence/connection-budget.json) agrupa backend_type/rol e incluye el lector administrativo; deja capacidad reservada para diagnóstico. El benchmark4clientes utiliza una ventana exclusiva y no demuestra saturación ni autoriza aumentar pools.
