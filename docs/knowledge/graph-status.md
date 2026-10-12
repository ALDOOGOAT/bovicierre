# Estado del grafo

| Fecha | Versión | Commit / alcance | Comando | Archivos | Conteos | Errores / limitaciones |
|---|---|---|---|---|---|---|
| 2026-10-11 | graphifyy 0.9.49 | f7e6db6 (main) · raíz del repo, 62 archivos (58 docs, 4 .py), ~65 mil palabras | `/graphify .` en Claude Code | `graphify-out/graph.json`, `graph.html`, `GRAPH_REPORT.md` (no versionados) | 830 nodos · 3,272 aristas · 45 comunidades · 9 hiperaristas | Ver abajo |

## Actualización estructural de diagramas · 2026-10-11

- Extracción AST de los 8 archivos Python de `tools/diagramas/`, fusionada con el grafo existente mediante `build_merge(root=...)`; conserva los 790 identificadores documentales.
- Resultado local: **853 nodos, 3,319 aristas, 22 comunidades**. `graph.json`, `graph.html` y `GRAPH_REPORT.md` regenerados; coste LLM de esta actualización: 0 tokens.
- Nombres de comunidades recuperados por mayoría de sus nombres anteriores. Las comunidades cambian al reagrupar el grafo.
- Sólo se actualizó código de herramientas; no se reextrajeron semánticamente los documentos ni se marcó su manifiesto como actualizado. Las notas visuales nuevas se incluirán en el siguiente `/graphify . --update` documental.

## Cómo se ejecutó
- AST local para los 4 scripts Python (40 nodos, 100 aristas).
- Extracción semántica: `GEMINI_API_KEY` está definida pero Google la rechazó ("Please pass a valid API key"); se usó el agente anfitrión (3 subagentes de Claude Code, uno por bloque de ~20 documentos), como indica la skill. Consumo reportado por los subagentes: 476,048 tokens (entrada+salida sin desglose).
- Cache semántica guardada para los 58 documentos (`graphify-out/cache`): `/graphify . --update` sólo reextrae lo que cambie.

## Limitaciones encontradas
- 38 aristas colgantes (1.1 %): apuntan a nodos "documento" (`<archivo>_document`, `docs_api_openapi`) que ningún bloque creó; se descartan al construir.
- Duplicados conceptuales: algunos comandos existen como nodo de `administration.md` y como nodo de `traceability.md` (p. ej. `cmd_confirmar_venta`); `graphify path` avisa "source match was ambiguous".
- `graphify query` en BFS con preguntas en lenguaje natural arranca en nodos generales (megaprompt, backlog) y trunca: para trazabilidad conviene `graphify path` o `explain` con IDs concretos.
- Las aristas INFERRED (p. ej. `semantically_similar_to` entre ADR y CLAUDE.md) deben verificarse contra el archivo fuente.
- La extracción histórica descrita arriba cubría diseño. La actualización de implementación figura al final.

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

Documentación UI/UX y herramientas añadida el 2026-10-11: `docs/development/web-tools.md`, `docs/ui/references.md` y detalle de pantallas8/9 aún no están reextraídos semánticamente en el grafo. Usar estos archivos como fuente; los conteos anteriores no acreditan cobertura de esta mejora.

## Implementación local · 11-oct-2026

Revisión `af223fb`, rama `feature/mvp-local`, working tree dirty. `graphify update .` ejecutó AST local de112archivos:1695nodos/4991aristas. Después el coordinador interpretó nueve documentos modificados (ADR013–017, trazabilidad, sistema visual, recuperación y POO); añadió15conceptos y32relaciones mediante `build_merge`, con reemplazo de nodos de esas fuentes. `graphify cluster-only . --no-label` produjo **1652nodos,4313aristas,119comunidades**. La reducción corresponde al reemplazo y deduplicación; no se conserva artificialmente el conteo anterior.

Fragmento reproducible: `python3 tools/dev/update_implementation_graph.py` con graphifyy0.9.49 instalado. El script comprueba IDs, guarda fragmento y manifiesto SHA-256 en `graphify-out/` ignorado. Consumo del modelo anfitrión no medido; no se invocó API externa ni facturación adicional. Los cero del formato de fragmento no representan el consumo de Codex.

Comprobación con IDs exactos sobre JSON/NetworkX (el CLI dio coincidencias ambiguas): Pantalla8→detalleliquidacion tiene arista directa; RN029→flujoDinero→CommandService tiene dos saltos. Son enlaces contrastados con `docs/traceability.md`, no pruebas de comportamiento. AST y extracción selectiva no acreditan relectura semántica de todo el corpus; quedan documentos fuera de estas nueve fuentes por reextraer. FK y reglas se verifican en SQL/catálogo, no por aristas inferidas.

### Repetición final V11

AST107archivos sincache en `graphify update .`, fragmento selectivo15conceptos/32relaciones repetido con hashes actuales y `cluster-only --no-label`:1871nodos/4633aristas/146comunidades. IDs exactos Pantalla8↔detalleliquidacion y RN029→flujoDinero→CommandService comprobados con NetworkX. No se invocó etiquetadoLLM externo; nueve fuentes semánticas no equivalen al corpus completo. Registro asociado a `af223fb` dirty, antes del commit local de implementación.

## Cierre V13: método de extracción final

Los registros anteriores son históricos. La actualización final parte de los53documentos canónicos modificados: relectura completa repartida entre agentes backend, frontend y operaciones, con fuentes/huellas y fragmentos locales ignorados. También se leen código/contrato como apoyo. Graphify0.9.49 integra AST local, fragmentos con `_origin=semantic`, caché con el esquema real y clustering `--no-label`. No se invoca otro proveedor ni facturaciónAPI. Consumo del modelo anfitrión no medido; tokens0 del formato no representa uso deCodex. Los documentos históricos sin cambios conservan su extracción anterior. El integrador genérico requiere los tres fragmentos como argumentos; el comando sin argumentos descrito en el registro selectivo anterior quedó sustituido.

Las métricas y comprobaciones del cierre se agregan después de la ejecución; no inferir finalización de este apartado metodológico.

### Corte comprobado de integración final

AST final114archivos y fragmentos backend/frontend/operaciones integrados con anclas de documento reutilizadas, validación de referencias antes de escribir y caché semántica:53documentos canónicos reinterpretados,102fuentes leídas entre primarias/apoyo,80fuentes cacheadas. `cluster-only --no-label`:2,507nodos/4,877aristas/248comunidades. [Registro y rutas exactas](../testing/evidence/graph-final.json). Pantalla8→detalleLiquidacion directo; RN029→comandoaplicar_pagoV13→TEST11 directo; tablaAplicacionPago→FK→tablaLiquidacion→relacional→ENT22→REL20delMER. Se contrastaron fuentes y catálogo; una arista no prueba comportamiento. Los documentos históricos sin cambios conservan extracción anterior.

Las cifras corresponden al corte registrado antes de añadir este estado operacional y cerrar las tareas. Tras actualizar estado, se releen las fuentes afectadas y se renueva caché; las métricas finales del registro prevalecen sobre las cifras de cortes anteriores. Los artefactos Graphify permanecen ignorados. No etiquetadoLLM externo ni consumo anfitrión medido; revisión humana pendiente.

## Publicación del manual · 12-oct-2026

Incremento AST real (`graphify update .`) y extracción semántica local de las dos guías nuevas: manual/README y runbooks/local-use. Se integraron13conceptos y16relaciones explícitas; las rutas críticas previas se conservan. Resultado: **2537 nodos, 4911 aristas y 262 comunidades**. [Registro reproducible](../testing/evidence/graph-publication-2026-10-12.json). Sin API LLM externa, consumo anfitrión no medido.

El PDF y su fuente LaTeX, que duplican el corpus explicado, quedan excluidos en .graphifyignore; su guía los enlaza. Esta actualización no reinterpreta todo el PDF ni todo el corpus histórico, y no renueva a ciegas los manifiestos antiguos de README/backlog/DoD modificados por la convención de casillas. Sus textos actuales son la autoridad para la convención técnica52casillas/55revisiones humanas pendientes. Los conteos y lecturas previos siguen siendo cortes históricos.
