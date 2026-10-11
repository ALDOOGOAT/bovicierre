# Evidencia de ejecución

Sólo resultados reales. Formato: fecha · entorno · comando · resultado · enlace.

| Fecha | Entorno | Comando | Resultado | Tarea |
|---|---|---|---|---|
| 2026-10-10 | Laptop de Aldo, Ubuntu 24.04, kernel 7.0 | `java/mvn/node/npm/docker/psql --version`; `command -v dot drawio` | Ver `docs/architecture/versions.md`; Graphviz y draw.io ausentes | A-001 |
| 2026-10-10 | idem | `pipx list` | `graphifyy 0.9.49` instalado | A-006 |
| 2026-10-10 | idem | `npx @redocly/cli@1.34.5 lint docs/api/openapi.yaml` | "Your API description is valid", 26 warnings (tag-description, operation-4xx-response) | A-007 |
| 2026-10-10 | idem | `python3 tools/verificar_cobertura.py` | AC 9/9, RN 45/45, ENT 41/41, REL 25/25, GOLD 10/10, TEST 35/35, TASK 55/55, ADR 12/12, F 49/49, RNF 10/10; 36/36 archivos de §14.2 presentes. Verifica presencia de IDs, no calidad del contenido | A-006 |
| 2026-10-10 | idem, Docker | `python3 tools/diagramas/gen_mer.py && python3 tools/diagramas/gen_relacional.py`; export con `rlespinasse/drawio-export:v4.5.0` (png/svg/pdf) | 7 fuentes `.drawio`, 11 páginas exportadas en SVG y PDF; revisión visual de PNG con correcciones de superposición; `pdftotext` confirma capa de texto vectorial | A-003 |
| 2026-10-11 | idem | `/graphify .` (graphifyy 0.9.49; Gemini rechazó la key, extracción con subagentes Claude) + `graphify path` para §15.4 | 830 nodos, 3,272 aristas, 45 comunidades; 6 de 7 cadenas de trazabilidad en 1–2 saltos; hueco Pantalla 8 → endpoint de liquidación | A-006 |
| 2026-10-11 | idem, Docker | `python3 tools/esquema/esquema.py`; `gen_mer_completo.py`; `gen_relacional_completo.py`; export draw.io | Esquema 42 tablas/80 FK verificado; MER completo y relacional completo exportados (PDF vectorial ≈A0); revisión visual en 4 iteraciones sin líneas sobre cajas ni atributos | A-003, A-004 |

Pruebas de dominio, SQL, replicación, FDW, restauración y rendimiento: **ninguna ejecutada aún**.

## Revisión de diagramas v0.2 · 2026-10-11

- `python3 -m unittest discover -s tools/diagramas -p 'test_*.py'`: 4 pruebas pasan (obstáculos, ausencia de ruta, simplificación y cardinalidades de claves completas).
- `python3 tools/esquema/esquema.py`: 42 tablas y 80 FK verificadas; el esquema no fue modificado.
- `python3 tools/verificar_cobertura.py`: cobertura de IDs y archivos requerida completa; comprueba presencia, no semántica.
- `python3 tools/diagramas/exportar.py`: Docker draw.io v4.5.0 + PyMuPDF; 13 PDF individuales de una página, 13 SVG y un PDF de 11 páginas con marcadores. Auto-comprobación de conservación de texto. Completos A0 ISO 1189 × 841 mm; numeradas A2/A3.
- Revisión visual de renders PNG de las 13 láminas, con ajustes de recorridos, roles recursivos, etiquetas y distribución de tablas. La lámina 7 ya no contiene tablas fuera del marco ni páginas posteriores duplicadas en los PDF individuales.
- Correcciones semánticas puntuales: cardinalidad `animal → sucursal` usa la UK compuesta completa; la vista general enlaza Pesaje con LoteOperacion y dirige los verbos de condición, selección y fuente de costo correctamente. Enlaces y rangos del resto de láminas conservados.
- Alcance TASK-A-003/A-004: artefactos gráficos revisados; no se marcan las tareas como hechas sin la revisión semántica humana. No se ejecutaron pruebas de BD, de dominio ni impresión física.
- Grafo: actualización AST de 8 generadores/herramientas; 853 nodos, 3,319 aristas, 22 comunidades; 790 nodos documentales conservados. Sin extracción semántica nueva ni consumo LLM.
