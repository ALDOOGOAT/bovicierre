# Repository Guidelines

## Project Structure & Module Organization
BoviCierre is currently a design repository for a cattle trading and settlement application. Read `README.md`, `CLAUDE.md`, and `docs/status.md` before contributing.

- `docs/domain/` contains business rules, states, calculations, and use cases.
- `docs/database/`, `docs/architecture/adr/`, and `docs/api/openapi.yaml` define the data model, decisions, and API contract.
- `docs/project/` tracks scope, tasks, and completion criteria; `docs/testing/` contains planned scenarios and evidence.
- `tools/esquema/esquema.py` defines the logical schema; `tools/diagramas/` generates diagrams.
- `docs/diagrams/sources/` holds editable `.drawio` assets; `exports/` holds SVG/PDF outputs.

Backend, frontend, migrations, and application test suites are not implemented yet.

## Build, Test, and Development Commands
Run available checks from the repository root:

```bash
python3 tools/verificar_cobertura.py
python3 tools/esquema/esquema.py
npx -y @redocly/cli@1.34.5 lint docs/api/openapi.yaml
```

These check specification ID/document coverage, foreign-key references, and OpenAPI validity, respectively. Diagram generation example: `python3 tools/diagramas/gen_relacional_completo.py`. Preserve manual diagram edits before regenerating.

The README's Maven, npm development, and Docker Compose commands are planned; their target directories do not exist yet.

## Coding Style & Naming Conventions
Follow existing Python style: four-space indentation and `snake_case` functions and variables. Keep documentation in Spanish, using concise Markdown headings, relative links, and UTF-8 text. Preserve identifiers such as `RN-001`, `TEST-01`, and `TASK-A-001`; never reuse retired IDs. No repository-wide formatter configuration currently exists.

## Testing Guidelines
Use the scenarios in `docs/testing/test-plan.md`. Planned tooling is JUnit 5, Testcontainers with real PostgreSQL, and Playwright. Compare financial results with fixed GOLD expectations; never substitute H2. No numeric coverage threshold is currently defined. Document actual commands, outcomes, and limitations in `docs/testing/evidence.md`.

## Commit & Pull Request Guidelines
History uses descriptive Spanish Conventional Commits, including `docs(diagramas): ...` and `docs(grafo): ...`. Keep commits focused. PRs should explain the change, reference TASK/RN/TEST identifiers, include validation evidence, and attach reviewed diagram exports when relevant. Update affected documentation and traceability; mark backlog tasks complete only with evidence.

## Agent Instructions
Use the installed graphify skill when `/graphify` is invoked. Consult `~/.codex/skills/seguridad-bd.md` for database access, permissions, or auditing work. Preserve confirmed economic facts; use exact decimal arithmetic and canonical SQL calculations as required by `CLAUDE.md`.
