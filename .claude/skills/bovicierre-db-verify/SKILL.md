---
name: bovicierre-db-verify
description: Verificar integridad de PostgreSQL en BoviCierre — reglas SQL canónicas, roles y permisos, transacciones y concurrencia, réplica lógica A↔B, Pgpool y FDW al proveedor. Úsala al tocar migraciones, funciones bovi.*, triggers, grants, replicación o cuando se necesite evidencia de base de datos.
---
# Verificación de base de datos

Reglas: importes NUMERIC con HALF_UP a 2; el cálculo vive en `bovi.cmd_ejecutar`/`bovi.consultar` (SECURITY DEFINER); hechos confirmados inmutables; escritor exclusivo por agregado (maestros en A, locales en el nodo de su sede); pruebas sólo con PostgreSQL real. Migración nueva = siguiente versión; para cambiar una función grande, parte de `pg_get_functiondef` en A y B (deben coincidir) y cambia sólo lo necesario.

| Qué | Cómo |
|---|---|
| Suite SQL completa | `make verify-sql` (`db/tests/run.sh`) |
| Cifras GOLD del mandato | `db/tests/gold_acad.py` (GOLD-ACAD-01/02); carrera de reservas TEST-10 = GOLD-ACAD-03 (BV402) |
| Pgpool, réplica con IDs, corte de enlace, FDW caída/recuperación | `db/tests/infra_evidence.py` → `db/tests/infra-evidence-result.json` |
| Instalación vacía | `db/tests/empty_install.py` (base `bovicierre_vacia_check`, nunca DROP) |
| Restablecer contraseña (V21) | `db/tests/password_reset.py` |
| Respaldo y restauración | `make backup BACKUP_DIR=<dir nuevo, inexistente>` y `make restore-check BACKUP_DIR=<mismo>` |

Si una verificación debe leer tablas que el rol de app no ve (p. ej. `bovi.usuario`), conecta como `postgres` y usa `SET ROLE bovi_app_a` para el comando dentro de la misma transacción. Hash de idempotencia = SHA-256 hex del cuerpo.

Excepción documentada: el backend autentica directo a `pg-a:5432` (`BOVI_AUTH_URL`, rol `bovi_auth`); el tráfico de negocio va por Pgpool. No la ocultes.
No habilites triggers ALWAYS en bloque ni dos escritores para la misma fila; `origin=none` no resuelve conflictos.
