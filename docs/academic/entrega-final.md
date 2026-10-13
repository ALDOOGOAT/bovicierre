# Entrega final académica — BoviCierre

Estado al 13-oct-2026, rama `feature/cierre-academico-v1` (sin push ni merge). Tres planos separados:

| Plano | Estado |
|---|---|
| Verificación técnica local | Puerta `make verify-release-local` en PASS (ver `docs/testing/evidence.md` y `docs/testing/evidence/academic-release/`) |
| Despliegue externo | **Bloqueado**: no hay destino, credenciales ni presupuesto autorizados por el equipo. No se publicó nada. |
| Aceptación humana / profesor | **Pendiente**: ver [aceptacion-final.md](aceptacion-final.md). Ningún agente la declara. |

## Cómo usarlo
- Demo académica: `make demo-profesor` → http://localhost:15180, usuarios `demo.admin|operador|caja|auditor`; contraseñas sólo por canal privado (`~/.local/share/bovicierre-academic/secrets/`).
- Instalación vacía para operaciones nuevas: volúmenes nuevos y `BOVI_INSTALL=vacia BOVI_EMPRESA="…" BOVI_ADMIN_LOGIN=… make academic`; contraseña inicial en `secrets/install_admin_password`; cambiarla desde Usuarios y permisos.
- Recorrido: Bandeja (pendientes + guía) → Nueva operación → lote/ganado → revisar y confirmar → Recibir ganado → Liquidación → Cobrar/Pagar.

## Requisitos de la rúbrica
Matriz AC-01..09: [requirements-matrix.md](requirements-matrix.md). **La imagen `RUBRICA_ORIGINAL_PIZARRON.png` no está en este entorno**; los temas se toman de la transcripción del mandato y no se afirma haber visto la foto. Al recibirla: copiarla sin alterar a `docs/academic/rubrica.png` y registrar su SHA-256 y procedencia.

## Entregables
- Modelo y BD: `docs/database/*`, `docs/diagrams/`, `db/migrations/V1..V21`.
- Pruebas y evidencia: `docs/testing/evidence.md`, `db/tests/*`, `frontend/tests_e2e/*`, `db/tests/infra-evidence-result.json`.
- Java/SOLID: [oop-solid-patterns.md](oop-solid-patterns.md).
- Defensa: [guion-defensa.md](guion-defensa.md), [preguntas-profesor.md](preguntas-profesor.md).
- UX y referencias públicas: `docs/ui/competitive-review.md`.
- Paquete: `make release-academic` → `dist/bovicierre-academico-<commit>.tar.gz` + `.sha256` (desde `git archive`, con escaneo de secretos).

## Límites conocidos
Un solo host (no alta disponibilidad); proveedor FDW simulado; sin PITR; PDF interno no es CFDI; QR no es certificación; sin envío de correo (recuperación administrativa de contraseña); restablecer contraseña no cierra sesiones abiertas del usuario (usar “Bloqueado” para cortar acceso).
