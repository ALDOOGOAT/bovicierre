# Backlog de campaña UI/UX + QA (UQ-001..015)

Complementa, sin sustituir, las 55 tareas de `docs/project/backlog.md`. `[x]` = verificación técnica local con evidencia (instrucción del usuario del 12-oct-2026); la revisión humana se registra aparte y sigue **pendiente** en todas. Agente ejecutor: Claude Opus 5.5.

| Estado | ID | Entregable | Dueño humano | Evidencia / nota |
|---|---|---|---|---|
| [x] | UQ-001 | Baseline, main/checkout, inventario Claude | Aldo | HEAD = origin/main = `38ccdc3`; árbol limpio salvo carpeta del encargo; rama `feature/uiux-qa-claude`. [claude-tooling](../development/claude-tooling.md) |
| [x] | UQ-002 | Herramientas globales verificadas y puente Codex→Claude | Aldo | MCP `api-anything` user-scope *Connected*; skills `ui-ux-pro-max`, `api-anything` cargadas; ECC 2.2.2, Ponytail 4.9.0, chrome-devtools-mcp 1.9.0 ya presentes |
| [ ] | UQ-003 | Mods probados, scopes y checkpoints | Aldo | Fuente validada `--strict`, 6/6 tests, instalado user-scope; checkpoints 11/11 tests. **Falta:** comprobar carga en una sesión (`/reload-plugins`) — no se marca hasta verlo cargado |
| [x] | UQ-004 | Auditoría visual y decisiones/assets con procedencia | Jared | [brief](../ui/redesign-brief.md), [assets](../ui/asset-register.md) |
| [x] | UQ-005 | Sistema visual/layout/navegación/login/sede | Jared | [design-system](../ui/design-system.md), UXD-01..11 |
| [x] | UQ-006 | Flujos operativos y financieros rediseñados | Jared | Alcance: estilos/insignias/jerarquía en todas las pantallas; sin cambios de flujo. Partición de `screens.tsx` no realizada |
| [x] | UQ-007 | E2E/a11y/capturas antes-después y cierre S1 | Jared | 15/15 E2E, 14 unitarias, capturas 3 anchos; axe y lector de pantalla no ejecutados |
| [x] | UQ-008 | Matriz completa de coherencia y divergencias | Aldo | [coherence-matrix](coherence-matrix.md): 45 RN, 17 DIV; RN-003 y RN-023 con evidencia ejecutada |
| [ ] | UQ-009 | Revisión MER/relacional/DDL y migraciones | Aldo | Catálogo revisado para UNIQUE e inmutabilidad; sin V14 ni revisión de diagramas → pendiente |
| [x] | UQ-010 | Modelo de amenazas y seguridad dirigida | Aldo | [threat-model](../security/threat-model.md), [test-plan](../security/test-plan.md), dinámico 63/63 |
| [x] | UQ-011 | Correcciones de backend/BD con regresión | Aldo | SF-01/02/03/20, Caddy SF-04/05; backend 28/28, SQL 37/37 |
| [x] | UQ-012 | Regresión frontend/contrato/errores | Jared | E2E 16/16 tras CSP y backend; vite 8.0.16; contrato: Redocly OK, divergencias DIV-11/12 abiertas |
| [x] | UQ-013 | Concurrencia, carga HTTP y conciliación | Aldo | Carreras SQL con barreras en `verify-sql`; k6 1→20, conciliación 1,185=1,185. Dataset grande y sostenido no ejecutados |
| [ ] | UQ-014 | Recuperación final y runbooks | Aldo | No repetida: sin cambios de esquema en la campaña; obligatoria antes/después de V14 |
| [ ] | UQ-015 | Dossier, evidencia, grafo y cierre S2 | Ambos | [final-report](final-report.md), grafo AST actualizado; falta `/graphify --update` semántico y revisión humana |
