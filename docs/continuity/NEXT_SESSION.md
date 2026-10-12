# NEXT_SESSION — campaña BoviCierre UI/UX + QA

**Instrucción ejecutable:** verificar lock y checkout con `python3 tools/claude/resume-check.py --owner <sesión>`
(exit 0 requerido); comprobar `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:15180/api/v1/salud` = 200;
correr `make verify-release-local` (≈3 min, debe dar PASS); después continuar con DIV-04 en una migración nueva V14.

Estado: **S1_DONE**, **S2_SAFE_PARTIAL** (rama local `feature/uiux-qa-claude`, base `38ccdc3`, sin push). Informe: `docs/quality/final-report.md`.

## Próximos pasos priorizados (S2 restante, presupuesto ≈170 min activos)
1. **DIV-04** (media): triggers de inmutabilidad para `operacion` CONFIRMADA, `gasto_operacion` APROBADO y `pago` VALIDADO en `db/migrations/V14__…sql` (no tocar V1–V13); ampliar `db/tests/immutability.py`; aplicar en A y B con el procedimiento existente; `make verify-sql` + puerta; **repetir recuperación** (`make backup` / `make restore-check` con BACKUP_DIR privado) porque cambia el esquema.
2. **SF-08** en la misma V14: `SET search_path = pg_catalog, pg_temp` en las SECURITY DEFINER, calificar catálogos, `REVOKE TEMP ON DATABASE … FROM PUBLIC`; prueba de sombreado como `bovi_auditor`.
3. **DIV-06/07/08/12**: decidir fórmula canónica de margen; catálogo de códigos BV; OpenAPI de BAJA/anular (`periodo_id`, `fecha_reconocimiento`, `motivo`) + `npm --prefix frontend run generate:api`.
4. Decisión humana: SF-09 (RLS/contexto de actor vs ADR de riesgo aceptado).
5. `/graphify . --update` (documentos nuevos) y registrar en `docs/knowledge/graph-status.md`.
6. Activar el mod: `/reload-plugins` y comprobar `/bovi-status` (UQ-003 sigue abierta hasta verlo cargado).

## Notas
- Estado privado y lock: `~/.local/state/bovicierre-claude/<repo-id>/` (fuera de Git). STOP: crear `docs/continuity/STOP`.
- Este archivo no ejecuta nada por sí mismo. La continuación automática al reset sólo ocurre en una sesión interactiva
  abierta con `/config` → *Continue automatically at usage limit* habilitado por la persona; en esta campaña no se ejercitó.
- `sec_dynamic.py` crea usuarios/registros "DEMO SEC" y 12 intentos fallidos sobre un login inexistente; no ejecutarlo
  a la vez que E2E/carga/`verify-sql`.
