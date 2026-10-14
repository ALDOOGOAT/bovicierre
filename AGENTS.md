# Repository Guidelines

## Project Structure & Module Organization
BoviCierre is a cattle trading and settlement application with canonical design and local implementation verified within the documented scope. Read `README.md`, `CLAUDE.md`, and `docs/status.md` before contributing.

- `docs/domain/` contains business rules, states, calculations, and use cases.
- `docs/database/`, `docs/architecture/adr/`, and `docs/api/openapi.yaml` define the data model, decisions, and API contract.
- `docs/project/` tracks scope, tasks, and completion criteria; `docs/testing/` contains planned scenarios and evidence.
- `tools/esquema/esquema.py` defines the logical schema; `tools/diagramas/` generates diagrams.
- `docs/diagrams/sources/` holds editable `.drawio` assets; `exports/` holds SVG/PDF outputs.

Check `docs/status.md` and `docs/testing/evidence.md` for what is implemented and actually verified. The active local mandate and ownership are in `docs/implementation/execution-plan.md` and `docs/development/agent-assignments.md`. Physical schema authority is `db/migrations/` (ADR-016).

## Build, Test, and Development Commands
Run available checks from the repository root:

```bash
python3 tools/verificar_cobertura.py
python3 tools/esquema/esquema.py
npx -y @redocly/cli@1.34.5 lint docs/api/openapi.yaml
```

These check specification ID/document coverage, foreign-key references, and OpenAPI validity, respectively. Diagram generation example: `python3 tools/diagramas/gen_relacional_completo.py`. Preserve manual diagram edits before regenerating.

Do not assume a README command was executed: use the evidence register. `make doctor` diagnoses the local environment; `make verify-docs` checks documentation only; `make verify-academic` runs the full local gate. Claude project skills live in `.claude/skills/bovicierre-*` (run, db-verify, ux, release-academic); next migration is V27. Preserve other projects' Docker containers and volumes.

## Coding Style & Naming Conventions
Follow existing Python style: four-space indentation and `snake_case` functions and variables. Keep documentation in Spanish, using concise Markdown headings, relative links, and UTF-8 text. Preserve identifiers such as `RN-001`, `TEST-01`, and `TASK-A-001`; never reuse retired IDs. No repository-wide formatter configuration currently exists.

## Testing Guidelines
Use the scenarios in `docs/testing/test-plan.md`. Implemented tooling is JUnit 5, Testcontainers with real PostgreSQL, and Playwright. Compare financial results with fixed GOLD expectations; never substitute H2. No numeric coverage threshold is currently defined. Document actual commands, outcomes, and limitations in `docs/testing/evidence.md`.

## Commit & Pull Request Guidelines
History uses descriptive Spanish Conventional Commits, including `docs(diagramas): ...` and `docs(grafo): ...`. Keep commits focused. PRs should explain the change, reference TASK/RN/TEST identifiers, include validation evidence, and attach reviewed diagram exports when relevant. Update affected documentation and traceability; mark backlog tasks complete only with evidence.

## Agent Instructions
Use the installed graphify skill when `/graphify` is invoked. Consult `~/.codex/skills/seguridad-bd.md` for database access, permissions, or auditing work. Preserve confirmed economic facts; use exact decimal arithmetic and canonical SQL calculations as required by `CLAUDE.md`.

## UI/UX e integraciones web
- Nueva pantalla, rediseño o mejora importante: leer `docs/ui/flows-and-screens.md`, consultar `.agents/skills/ui-ux-pro-max/SKILL.md` y usar `revision-ui-referencias` cuando observar referencias ayude a decidir. Reutilizar decisiones vigentes de `docs/ui/references.md` para cambios pequeños.
- Error visual/responsive: Chrome DevTools MCP para DOM, CSS aplicado y capturas en los tamaños afectados. Cambios de flujo: recorrer interacciones y estados de principio a fin en la aplicación local; comprobar teclado, foco y consola.
- Datos/funciones externas: buscar primero API oficial o integración mantenida. Evaluar `.agents/skills/api-anything/SKILL.md` sólo si falta una opción suficiente y la operación es accesible y autorizada. Sin importar sesiones personales ni habilitar escrituras por iniciativa propia; el registro MCP no autoriza efectos externos.
- Backend sin UI ni integración web: usar herramientas de backend; no abrir navegador ni investigar referencias sin necesidad.
- Configuración, versiones, pruebas y reanudación: `docs/development/web-tools.md`. Herramientas y perfiles separados del producto; no versionar cookies, HAR, credenciales ni capturas privadas. Mientras no exista frontend, mejorar especificaciones y declarar que no hubo prueba de aplicación.
