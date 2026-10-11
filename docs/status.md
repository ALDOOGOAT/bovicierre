# Estado del proyecto

Actualizado: 2026-10-11.

## Existe (verificable)
- Paquete documental completo de §14.2 del megaprompt (ver índice en README).
- Contrato OpenAPI validado con Redocly (válido, 26 warnings de estilo).
- Decisiones DEC-01..11 que resuelven contradicciones del megaprompt (`docs/research/evidence-register.md`).
- Backlog de 55 tareas con estado Kanban.
- Grafo Graphify local: 853 nodos, 22 comunidades (`docs/knowledge/graph-status.md`; `graphify-out/` no se versiona).
- Diagramas v0.2: MER completo y relacional completo en PDF A0 ISO; líneas ortogonales, direcciones y cardinalidades revisadas, 42 tablas/80 FK. Las 11 páginas numeradas están reunidas en `docs/diagrams/exports/laminas-numeradas.pdf`. Esquema lógico: `tools/esquema/esquema.py`.
- 7 láminas `.drawio` (MER Chen 1–6 y relacional por módulo) con exportes SVG/PDF revisados (`docs/diagrams/README.md`).

## No existe todavía
- Código backend/frontend, migraciones, scripts de bootstrap, Compose, pruebas.
- Ninguna prueba TEST-01..35 ejecutada.

## Bloqueos / dependencias externas
- PEND-01 interpretación de M–M por el profesor (riesgo R-01).
- PEND-02 imagen de la rúbrica para el repo.
- PEND-03 servidor/credenciales de staging.
- Revisión humana de los documentos en estado "Revisión" (Aldo y Jared).

## Siguiente tarea ejecutable
1. Revisión humana de las láminas (TASK-A-003) y del resto de documentos en "Revisión".
2. TASK-A-011: Compose A/B + Pgpool + experimento M–M mínimo.
Para Jared: TASK-J-001/J-002 a partir de `docs/ui/flows-and-screens.md` y `docs/domain/glossary.md`.
