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

## Herramientas UI/UX y web · 2026-10-11

Entorno: Ubuntu 24.04.4, zsh, Codex 0.162.1, Python 3.12.3, Chrome 148.0.7778.96. Inventario inicial Git limpio; Node20.20.2/npm10.8.2 del entorno conservados. Configuración y ubicaciones: [web-tools](../development/web-tools.md).

| Comando / comprobación real | Resultado |
|---|---|
| `npm view chrome-devtools-mcp version engines license`; `npm view ui-ux-pro-max-cli version bin license`; ayudas de Codex/uipro/Chrome | Chrome1.10.1 Apache-2.0; uipro2.15.0 MIT, binario `uipro`. uipro no acepta `--dry-run`; inspección previa en carpeta temporal y posterior instalación con la misma versión. |
| `npm ci --no-audit --no-fund`, `npm pack --silent`, instalación del `.tgz` de API Anything fijado por commit | Compilación correcta, paquete 0.1.0; runtime auxiliar Node22.23.3. MCP registrado después de copia privada de config global. |
| `api-anything call hacker-news search query=sqlite` mediante wrapper instalado | `ok:true`, `class:ok`, tier1, 30 registros, 557 ms. Prueba pública sin login. |
| Cliente MCP SDK independiente: `initialize`, `tools/list`, `call_operation` con `site=hacker-news`, `op=search`, `args.query=sqlite` | 4 herramientas; `ok:true`, tier1, 30 filas, 364 ms. No se invocó login ni operación con efectos. |
| `env -u XAUTHORITY -u DISPLAY python3 tools/dev/verificar_mcp.py` | Lanzador persistente autodetecta sesión gráfica. MCP1.10.1/Node24.21.0: 30 herramientas; navegación, DOM/CSS, snapshot, `get_css_styles`, consola y capturas pasan. [Informe sanitizado](../ui/evidence/mcp-smoke.json). |
| `python3 tools/dev/verificar_mcp.py --self-check`; `sh -n tools/dev/chrome_devtools.sh` | Pasan notificación previa/respuesta JSON-RPC y error; sintaxis del lanzador correcta. Assertions de dimensiones verifican PNG1440/768/390 ×1000. |
| Buscador UI UX: `error summary validation` y `financial table readability`, dominio ux | 3 resultados pertinentes en cada consulta; adoptados resumen enfocable, errores inline, tablas localizadas y legibilidad, conservando importes completos. |
| `codex debug prompt-input` | Descubrimiento real de `ui-ux-pro-max`, `api-anything` y `revision-ui-referencias`. No demuestra recarga MCP en la conversación ya iniciada. |
| `quick_validate.py .agents/skills/revision-ui-referencias`; `git diff --check` | Skill válida y diff sin errores de whitespace. |
| `python3 tools/verificar_cobertura.py`; `python3 tools/esquema/esquema.py`; Redocly1.34.5 lint | Cobertura documental completa; 42 tablas/80FK; OpenAPI válido con 26 warnings existentes. No demuestra calidad semántica ni comportamiento backend. |

Chrome visible con renderer `ANGLE (Intel, Mesa Intel(R) Graphics (RPL-P), OpenGL ES 3.2)`, sin headless/SwiftShader ni desactivar sandbox. Capturas públicas de documentación CattleMax y AgriWebb a 390/768/1440; revisión visual realizada y límites en [referencias](../ui/references.md). No son capturas del producto BoviCierre. CattleMax presenta warning de meta obsoleto; AgriWebb presenta advertencia iframe y avisos de CSP/IDs duplicados: son de las páginas externas, no fallos introducidos al repo.

Fallos resueltos: MCP de esta conversación sin X server; lanzamiento stdio separado con sesión gráfica. Node20 navegaba pero `get_css_styles` falló (`longhandValues.intersection is not a function`): launcher usa Node24 existente. npx de otro runtime combinado con Node npm auxiliar causó ENOENT: se usa instalación Node24/npx completa para Chrome.

Primera mejora aplicada **al diseño** de pantallas8/9 y referencias; TASK-J-002/J-012/J-013 siguen pendientes. Sin aplicación ejecutable: no hay build, lint/tipos frontend, flujo de producto, API real de BoviCierre, teclado/foco del producto ni FPS medidos. No se ejecutaron TEST de dominio. Playwright MCP y alternativas alojadas no se activaron por falta de necesidad. MCP nuevos pendientes de cargar al reiniciar Codex.
