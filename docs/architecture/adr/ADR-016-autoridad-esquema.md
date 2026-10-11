# ADR-016: Autoridad del esquema físico

- Estado: aceptado para implementación local por encargo del usuario · 2026-10-11

## Decisión

db/migrations es autoridad física ejecutable. tools/esquema/esquema.py es representación lógica documental que debe contrastarse con catálogo PostgreSQL; no se genera DDL ciegamente. Migrador separado, runtime noDDL. Tablas técnicas locales y excepciones de publicación explícitas. P0001 DETAIL JSON validado transporta códigos BV, no SQLSTATE inventado.

## Validación

Implementación y pruebas pendientes al registrar esta decisión; ver [evidencia](../../testing/evidence.md). La revisión humana permanece pendiente.
