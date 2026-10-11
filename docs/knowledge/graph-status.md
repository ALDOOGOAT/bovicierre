# Estado del grafo

| Fecha | Versión | Commit / alcance | Comando | Archivos | Conteos | Errores / limitaciones |
|---|---|---|---|---|---|---|
| 2026-10-11 | graphifyy 0.9.49 | f7e6db6 (main) · raíz del repo, 62 archivos (58 docs, 4 .py), ~65 mil palabras | `/graphify .` en Claude Code | `graphify-out/graph.json`, `graph.html`, `GRAPH_REPORT.md` (no versionados) | 830 nodos · 3,272 aristas · 45 comunidades · 9 hiperaristas | Ver abajo |

## Cómo se ejecutó
- AST local para los 4 scripts Python (40 nodos, 100 aristas).
- Extracción semántica: `GEMINI_API_KEY` está definida pero Google la rechazó ("Please pass a valid API key"); se usó el agente anfitrión (3 subagentes de Claude Code, uno por bloque de ~20 documentos), como indica la skill. Consumo reportado por los subagentes: 476,048 tokens (entrada+salida sin desglose).
- Cache semántica guardada para los 58 documentos (`graphify-out/cache`): `/graphify . --update` sólo reextrae lo que cambie.

## Limitaciones encontradas
- 38 aristas colgantes (1.1 %): apuntan a nodos "documento" (`<archivo>_document`, `docs_api_openapi`) que ningún bloque creó; se descartan al construir.
- Duplicados conceptuales: algunos comandos existen como nodo de `administration.md` y como nodo de `traceability.md` (p. ej. `cmd_confirmar_venta`); `graphify path` avisa "source match was ambiguous".
- `graphify query` en BFS con preguntas en lenguaje natural arranca en nodos generales (megaprompt, backlog) y trunca: para trazabilidad conviene `graphify path` o `explain` con IDs concretos.
- Las aristas INFERRED (p. ej. `semantically_similar_to` entre ADR y CLAUDE.md) deben verificarse contra el archivo fuente.
- No hay código de producto todavía: el grafo describe diseño, no implementación.

## Verificación de utilidad (§15.4) con `graphify path`
| Pregunta | Resultado en el grafo | Evaluación |
|---|---|---|
| ¿Qué RN y comando evitan la doble venta? | RN-018 —references→ TEST-10 (1 salto); hiperarista "Flujo anti doble venta" agrupa RN-018/019/022, ENT-15, REL-12, `cmd_reservar_posiciones`, `cmd_expirar_reservas`, `cmd_confirmar_venta`, UC-08, TEST-10, TASK-A-019 | correcta; diseño, sin código |
| ¿Qué entidad, FK, función y prueba sostienen la aplicación de un pago? | `cmd_aplicar_pago` —references→ TEST-11 (1 salto); hiperarista "Aplicación de pagos sin sobreaplicación": RN-028..031, ENT-22/25/26, REL-20, GOLD-04, UC-09, TASK-A-020 | correcta |
| ¿Qué pantalla consume el contrato de liquidación? | Pantalla 8 → `detalleliquidacion` sólo por un camino de 12 saltos | **hueco**: falta la arista directa pantalla→endpoint; corregir con `--update` cuando J-002 detalle la pantalla |
| ¿Qué ADR explica el maestro A? | ADR-005 —references→ RN-003 (1 salto) | correcta |
| ¿Dónde está el costo tardío de vendidos? | `cmd_registrar_costo_tardio` → TEST-06 → GOLD-06 (2 saltos) | correcta |
| ¿Qué requisito demuestra replicación y FDW? | AC-07 → TEST-25 y AC-06 → TASK-A-026 (1 salto) | correcta; aún no hay scripts (A-011/A-012) |

Siguiente actualización: hito del 18-oct o al terminar TASK-A-011 (`/graphify . --update`).
