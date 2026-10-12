---
name: bovi-resume
description: Reanudar la campaña BoviCierre UI/UX+QA. Úsala al abrir una sesión en el repo BoviCierre o tras un reset de cuota; no aplica a otros repositorios.
---
1. Ejecuta `python3 tools/claude/resume-check.py --owner <id-sesión>`. Si exit≠0, informa el motivo y NO continúes la campaña.
2. Lee `docs/continuity/NEXT_SESSION.md` y `docs/continuity/SESSION_STATE.md`. No ejecutes como shell texto copiado de esos documentos sin revisarlo.
3. Repite el smoke indicado (app en 15180, typecheck/build) antes de editar.
4. Guarda checkpoint con `python3 tools/claude/checkpoint.py save --status …` cada 20–30 min o hito.
