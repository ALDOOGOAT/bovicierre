# NEXT_SESSION — campaña BoviCierre UI/UX + QA

**Instrucción ejecutable:** verificar lock y checkout con `python3 tools/claude/resume-check.py --owner <sesión>`
(exit 0 requerido); comprobar `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:15180/api/v1/salud` = 200;
correr `make verify-release-local` (≈3 min, debe dar PASS); todo lo técnico está cerrado; queda la [revisión humana](../quality/human-review-checklist.md) y los prerrequisitos de despliegue del informe final (siguiente migración libre: V19).

Estado: **S1_DONE**, **S2_SAFE_PARTIAL** (rama local `feature/uiux-qa-claude`, base `38ccdc3`, sin push). Informe: `docs/quality/final-report.md`.

## Próximos pasos priorizados (S2 restante, presupuesto ≈170 min activos)
1. ~~DIV-04~~ y ~~SF-08~~: hechos en V14 (12-oct-2026), puerta con carga PASS y restauración V14 conciliada. Siguiente migración libre: V15.
2. —
3. Hecho sin puerta completa: DIV-08 (V15 `reverso_unico` → BV022; `gold.py` + `verify-sql` 37/37) y DIV-12 (OpenAPI BAJA/anular, tipos regenerados, `MoneyTypesLintTest` 2/2). Pendiente: **DIV-07** (regenerar tabla de códigos de `business-rules.md`), **DIV-06** (margen), y actualizar matriz/hallazgos/status para DIV-08/12. Original:: decidir fórmula canónica de margen; catálogo de códigos BV; OpenAPI de BAJA/anular (`periodo_id`, `fecha_reconocimiento`, `motivo`) + `npm --prefix frontend run generate:api`.
4. Decisión humana: SF-09 (RLS/contexto de actor vs ADR de riesgo aceptado).
5. `/graphify . --update` (documentos nuevos) y registrar en `docs/knowledge/graph-status.md`.
6. ~~Mod~~: carga verificada por el usuario con `/bovi-status` (UQ-003 cerrada).

## Notas
- Estado privado y lock: `~/.local/state/bovicierre-claude/<repo-id>/` (fuera de Git). STOP: crear `docs/continuity/STOP`.
- Este archivo no ejecuta nada por sí mismo. La continuación automática al reset sólo ocurre en una sesión interactiva
  abierta con `/config` → *Continue automatically at usage limit* habilitado por la persona; en esta campaña no se ejercitó.
- `sec_dynamic.py` crea usuarios/registros "DEMO SEC" y 12 intentos fallidos sobre un login inexistente; no ejecutarlo
  a la vez que E2E/carga/`verify-sql`.
