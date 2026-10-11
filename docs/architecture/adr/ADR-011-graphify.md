# ADR-011: Graphify y mantenimiento del contexto
- Estado: propuesto · 2026-10-10
## Contexto
El equipo quiere contexto navegable para Claude y personas. Instalado: paquete `graphifyy` 0.9.49.
## Decisión
Grafo de desarrollo (no dependencia del runtime) con `/graphify .` y `/graphify . --update` tras cambios de documentos; `graphify update .` sólo para cambios de código. `.graphifyignore` excluye secretos, datos, dumps, dependencias y `graphify-out/`. Salidas por checkout; `graphify-out/` no se versiona; sin Graphify Cloud ni servidor público. Estado en `docs/knowledge/graph-status.md`.
## Consecuencias
+ Navegación de reglas↔tablas↔pruebas. − Aristas inferidas deben verificarse contra fuentes; el procesamiento semántico puede usar el modelo configurado (no es offline garantizado).
