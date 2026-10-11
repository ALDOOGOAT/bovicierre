# Estado del proyecto

Actualizado: 2026-10-10.

## Existe (verificable)
- Paquete documental completo de §14.2 del megaprompt (ver índice en README).
- Contrato OpenAPI validado con Redocly (válido, 26 warnings de estilo).
- Decisiones DEC-01..11 que resuelven contradicciones del megaprompt (`docs/research/evidence-register.md`).
- Backlog de 55 tareas con estado Kanban.

## No existe todavía
- Láminas MER Chen `.drawio` + exportes SVG/PDF (TASK-A-003, en curso).
- Diagrama lógico relacional por módulos.
- Grafo de Graphify (TASK-A-006).
- Código backend/frontend, migraciones, scripts de bootstrap, Compose, pruebas.
- Ninguna prueba TEST-01..35 ejecutada.

## Bloqueos / dependencias externas
- PEND-01 interpretación de M–M por el profesor (riesgo R-01).
- PEND-02 imagen de la rúbrica para el repo.
- PEND-03 servidor/credenciales de staging.
- Revisión humana de los documentos en estado "Revisión" (Aldo y Jared).

## Siguiente tarea ejecutable
1. TASK-A-003: generar láminas MER Chen `.drawio` y exportarlas.
2. TASK-A-006: ejecutar `/graphify .` y registrar en `graph-status.md`.
3. TASK-A-011: Compose A/B + Pgpool + experimento M–M mínimo.
Para Jared: TASK-J-001/J-002 a partir de `docs/ui/flows-and-screens.md` y `docs/domain/glossary.md`.
