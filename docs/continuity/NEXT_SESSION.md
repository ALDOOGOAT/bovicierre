# NEXT_SESSION — campaña BoviCierre UI/UX + QA

**Instrucción ejecutable:** verificar lock y checkout con `python3 tools/claude/resume-check.py --owner <sesión>`
(exit 0 requerido); comprobar `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:15180/` = 200 y
`npm --prefix frontend run typecheck`; continuar con el primer paso de "Próximos pasos" de `SESSION_STATE.md`.

- Rama de trabajo: `feature/uiux-qa-claude` (base `38ccdc3` = origin/main al 2026-10-12). Sin push.
- Encargo: `docs/TAREAS NUEVAS PARA CLAUDE /BoviCierre_Megaprompt_Claude_UIUX_QA.md` (activo) + auditoría `…Auditoria_Main_92d3d41.md`.
- Estado privado y lock: `~/.local/state/bovicierre-claude/<repo-id>/` (fuera de Git). STOP: crear `docs/continuity/STOP`.
- Este archivo no ejecuta nada por sí mismo. La continuación automática al reset sólo ocurre en una sesión
  interactiva abierta con `/config` → *Continue automatically at usage limit* habilitado por la persona.
