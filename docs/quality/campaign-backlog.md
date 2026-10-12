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
| [ ] | UQ-008 | Matriz completa de coherencia y divergencias | Aldo | S2 |
| [ ] | UQ-009 | Revisión MER/relacional/DDL y migraciones | Aldo | S2 |
| [ ] | UQ-010 | Modelo de amenazas y seguridad dirigida | Aldo | S2 |
| [ ] | UQ-011 | Correcciones de backend/BD con regresión | Aldo | S2 |
| [ ] | UQ-012 | Regresión frontend/contrato/errores | Jared | S2 |
| [ ] | UQ-013 | Concurrencia, carga HTTP y conciliación | Aldo | S2 |
| [ ] | UQ-014 | Recuperación final y runbooks | Aldo | S2 |
| [ ] | UQ-015 | Dossier, evidencia, grafo y cierre S2 | Ambos | S2 |
