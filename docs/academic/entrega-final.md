# Entrega final académica — BoviCierre

Estado al 13-oct-2026, rama `feature/cierre-academico-v1`, integrada por avance rápido en `main` y publicada en GitHub (`f9f32b5`). Tres planos separados:

| Plano | Estado |
|---|---|
| Verificación técnica local | Puerta `make verify-release-local` en PASS (ver `docs/testing/evidence.md` y `docs/testing/evidence/academic-release/`) |
| Despliegue externo | Railway autorizado por el usuario (13-oct-2026); procedimiento y variables en [docs/deploy/railway.md](../deploy/railway.md). Estado vigente en `docs/status.md`. |
| Aceptación humana / profesor | **Pendiente**: ver [aceptacion-final.md](aceptacion-final.md). Ningún agente la declara. |

## Cómo usarlo
- Cuentas personales (aplicación y PostgreSQL): `scripts/academic_users.py`; contraseñas sólo en `~/.local/share/bovicierre-academic/entrega-local/accesos.md` (0600), entregar por canal privado. Verificación: `scripts/verify_access.py` (TEST-42).
- Demo académica: `make demo-profesor` → http://localhost:15180, usuarios `demo.admin|operador|caja|auditor`; contraseñas sólo por canal privado (`~/.local/share/bovicierre-academic/secrets/`).
- Instalación vacía para operaciones nuevas: volúmenes nuevos y `BOVI_INSTALL=vacia BOVI_EMPRESA="…" BOVI_ADMIN_LOGIN=… make academic`; contraseña inicial en `secrets/install_admin_password`; cambiarla desde Usuarios y permisos.
- Recorrido: Bandeja (pendientes + guía) → Nueva operación → lote/ganado → revisar y confirmar → Recibir ganado → Liquidación → Cobrar/Pagar.

## Requisitos de la rúbrica
Foto del pizarrón: [`rubrica.png`](rubrica.png) con [procedencia](rubrica-procedencia.md). Cotejo punto por punto en [requirements-matrix.md](requirements-matrix.md) (sección “Cotejo directo”).

## Entregables
- Modelo y BD: `docs/database/*`, `docs/diagrams/` (vigentes en V26), `db/migrations/V1..V26`.
- Pruebas y evidencia: `docs/testing/evidence.md`, `db/tests/*`, `frontend/tests_e2e/*`, `db/tests/infra-evidence-result.json`.
- Java/SOLID: [oop-solid-patterns.md](oop-solid-patterns.md).
- Defensa: [guion-defensa.md](guion-defensa.md), [preguntas-profesor.md](preguntas-profesor.md).
- UX y referencias públicas: `docs/ui/competitive-review.md`.
- Paquete: `make release-academic` → `dist/bovicierre-academico-<commit>.tar.gz` + `.sha256` (desde `git archive`, con escaneo de secretos).

## Límites conocidos
Un solo host (no alta disponibilidad); proveedor FDW simulado; sin PITR; PDF interno no es CFDI; QR no es certificación; sin envío de correo (recuperación administrativa de contraseña). Restablecer contraseña o bloquear cierra las sesiones abiertas de la cuenta (V25).
