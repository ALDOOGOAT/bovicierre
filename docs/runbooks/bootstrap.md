# Runbook: bootstrap del entorno academic

Estado: procedimiento diseñado; scripts pendientes (TASK-A-011/A-012). Detalle conceptual: `docs/database/replication-and-fdw.md` §3.

Prerrequisitos: Docker 29+, Compose v5, secretos en `infra/compose/secrets/` (no versionados) creados a partir de `.env.example`.

1. `docker compose -f infra/compose/compose.academic.yml up -d pg-a pg-b pg-prov` y esperar `healthy`.
2. `db/bootstrap/01_roles.sql` en A y B (como superusuario de bootstrap, sólo esta vez).
3. Migraciones: `docker compose run --rm migrate-a` y `migrate-b` (Flyway con `bovi_migrator`).
4. `db/bootstrap/02_nodo_config.sql` con `NODO=A` / `NODO=B`.
5. `db/bootstrap/03_publicaciones.sql` en ambos.
6. `db/bootstrap/04_suscripciones.sql` (fuera de transacción) en B y luego en A.
7. `tools/verificar_suscripciones.sh` → todas las tablas en estado `r`.
8. `db/seed/10_maestros.sql` sólo en A; `tools/esperar_barrera.sh A B`.
9. `db/seed/20_operaciones_a.sql` en A; `db/seed/21_operaciones_b.sql` en B.
10. `db/bootstrap/05_fdw.sql` en A + `db/seed/30_proveedor.sql` en pg-prov.
11. `SELECT * FROM bovi.fn_validar_conciliacion_propietario();` en ambos; guardar salida en `docs/testing/evidence.md`.
12. `docker compose up -d pgpool-a pgpool-b backend frontend caddy`.
Si algún paso falla: no continuar; `docker compose down -v` sólo en entorno academic desechable y repetir desde 1.
