# Inventario de ejecución

Comprobado 2026-10-11 desde el checkout; sin secretos.

| Capacidad | Resultado real |
|---|---|
| Sistema/shell | Ubuntu24.04.4 x86_64, zsh; RAM15Gi, disponibleaprox8.4Gi |
| Codex | 0.162.1; `codex debug models` lista gpt-6.1-sol, gpt-6-astra, gpt-6-sol, gpt-6-luna y modelos de respaldo |
| Esfuerzos | Sol/Astra low/medium/high/xhigh/max/ultra; Luna low/medium/high/xhigh/max |
| Agentes | Herramienta collaboration.spawn_agent; 4slots incluyendo coordinador; checkout compartido |
| Java/Maven | Java21.0.12.1; Mavenhost3.8.7; wrapper3.9.12 probado |
| Node/npm | 20.20.2/10.8.2; Node24.21.0 ya instalado para ChromeMCP |
| Docker/Compose | 29.4.1/v5.1.3; daemon accesible. Contenedores ajenos tendi/dagon preservados |
| PostgreSQL | cliente18.3; servidoresA/B/proveedor18.6 reales |
| Graphify | graphifyy0.9.49, ejecutable ~/.local/bin/graphify; grafo previo existe; AST local y extracción semántica por agentes de los53documentos canónicos cambiados. Integración y métricas verificables en graph-status; no proveedor externo ni reextracción de documentos históricos sin cambios |
| ChromeDevTools | MCP1.10.1, launcherNode24/perfilpropio, comprobado por cliente independiente; no se presume servidor recién cargado en catálogo de sesión |
| APIAnything | 0.1.0 commitfe5cca7, runtime22.23.3 separado, operación públicaHNsqlite comprobada; sin necesidad de integración económica externa |
| UIUX | .agents/skills/ui-ux-pro-max, revision-ui-referencias; CLI2.15.0, buscadorPython disponible |
| ECC/Ponytail | skills instaladas y Ponytail activo; no `/ecc` universal ni cambiohooks |
| Memoriaautomática | allowance observer agotado; se conservan checkpointsMarkdown, no se reinicia worker |

Versiones de fuentes verificadas: [SpringBoot4.1.1](https://docs.spring.io/spring-boot/system-requirements.html) admiteJava17..26 yMaven≥3.6.3; [Vite](https://vite.dev/guide/) exigeNode20.19+/22.12+. Elecciones finales y pruebas en versions.md/lockfiles.

RTK.md enlazado por instrucciones no existe en la raíz; no se inventa su contenido. ConfiguraciónMCP propia y resultados detallados en [web-tools](web-tools.md).

Validación de contrato auxiliar: jsonschema4.10.3 disponible y PyYAML6.0.1 (`tools/dev/requirements-contract.txt`);17 intercambios de sesión/consultas comparados con OpenAPI, formatos y mediatype. Sin payloads/cookies en evidencia. WorkflowGitHubmanual fijado por SHA preparado y comprobado estructuralmente; no se ejecutó remoto.
