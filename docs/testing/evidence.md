# Evidencia de ejecución

Sólo resultados reales. Formato: fecha · entorno · comando · resultado · enlace.

| Fecha | Entorno | Comando | Resultado | Tarea |
|---|---|---|---|---|
| 2026-10-10 | Laptop de Aldo, Ubuntu 24.04, kernel 7.0 | `java/mvn/node/npm/docker/psql --version`; `command -v dot drawio` | Ver `docs/architecture/versions.md`; Graphviz y draw.io ausentes | A-001 |
| 2026-10-10 | idem | `pipx list` | `graphifyy 0.9.49` instalado | A-006 |
| 2026-10-10 | idem | `npx @redocly/cli@1.34.5 lint docs/api/openapi.yaml` | "Your API description is valid", 26 warnings (tag-description, operation-4xx-response) | A-007 |
| 2026-10-10 | idem | `python3 tools/verificar_cobertura.py` | AC 9/9, RN 45/45, ENT 41/41, REL 25/25, GOLD 10/10, TEST 35/35, TASK 55/55, ADR 12/12, F 49/49, RNF 10/10; 36/36 archivos de §14.2 presentes. Verifica presencia de IDs, no calidad del contenido | A-006 |
| 2026-10-10 | idem, Docker | `python3 tools/diagramas/gen_mer.py && python3 tools/diagramas/gen_relacional.py`; export con `rlespinasse/drawio-export:v4.5.0` (png/svg/pdf) | 7 fuentes `.drawio`, 11 páginas exportadas en SVG y PDF; revisión visual de PNG con correcciones de superposición; `pdftotext` confirma capa de texto vectorial | A-003 |

Pruebas de dominio, SQL, replicación, FDW, restauración y rendimiento: **ninguna ejecutada aún**.
