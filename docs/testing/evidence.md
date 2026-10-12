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

Al cierre de esa revisión histórica no había pruebas de producto; las ejecuciones de implementación se registran abajo.

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

## Inicio de implementación · 2026-10-11

Baseline af223fbbe6520dd123b37f9984e806ae10afcf9e, rama feature/mvp-local, working tree modificado. Entorno en tooling-inventory.md.

- `python3 scripts/doctor.py --self-check` y `python3 scripts/doctor.py`: exit0; versiones y daemonDocker accesible. Puertos15432/3/4 ya ocupados por bovicierre-academic, verificados con dockerps, no por servicios ajenos.
- `python3 -m unittest discover -s tools/diagramas -p 'test_*.py'`: 5pruebas, exit0; nueva regresión conserva autorrelaciones Documento/Ajuste. Un primer intento falló por usar APIXMLincorrecta sobre Pagina; corregido y repetido.
- `python3 tools/esquema/esquema.py`: exit0,42tablas80FK de representación lógica; no equivale a catálogoPG ni RNprobadas.
- `python3 tools/verificar_cobertura.py`: exit0; sólo presencia documental/IDs.
- `npx -y @redocly/cli@1.34.5 lint docs/api/openapi.yaml`: exit0, contrato0.2.0 válido con1warning GETpúblicoCSRFsin4xx; no se añade respuesta inexistente por silenciarla.
- Download INEGI mgem/07 por curl, JSON/numReg/claves únicas/scope07 validados mediante asserts:124registros; manifestchecksum.

BuildJava/UI, permisosSQL, flujoeconómico, replicación/FDW/restauración: en construcción, todavía sin aceptación técnica de incremento. Fuente drawioMERregenerada; exportación/revisiónvisual nuevas pendientes.

## Incremento ejecutable — 2026-10-11

Checkout dirty en `feature/mvp-local`, base `af223fb`. Ejecución por agentes de BD/backend; revisión de integración por coordinador.

- `BOVI_API_IT=true ./backend/mvnw -q -f backend/pom.xml verify`: exit 0, 11 pruebas (8 unitarias, 3 HTTP reales contra API 18080 y Pgpool 19999/19998). CSRF/login/scope/logout, idempotencia y recorrido compra 1000.00 → venta 1600.00 → cobro 1200.00 → saldo 400.00; PDF conserva el saldo.
- Suite `db/tests/gold.py`: 50 comandos en PostgreSQL real, con rollback del escenario; oráculos fijos GOLD-02/03/06, aplicaciones, reversos/reembolso, conflictos y periodos. Aún no equivale a todos TEST-01..35 ni a aceptación del ajuste guiado GOLD-07.
- `python3 tools/esquema/comparar_catalogo.py`: exit 0, 42 tablas/83 FK; sin diferencias en columnas/nullabilidad/PK/FK (antes de corrección de pago registrado nullable, debe repetirse tras esa corrección).
- Redocly 1.34.5: contrato 0.2.0 válido; una advertencia en GET CSRF público. No demuestra que todas las respuestas runtime concuerden.
- Capturas `evidence/ui/login-*.png`: Chrome real, renderer Intel RPL-P, 390/768/1440 sin overflow. La primera captura coincidió con reinicio API y mostró 502: evidencia de estado de error, no consola limpia ni flujo final.

Restauración aislada, rendimiento, fallos completos y revisión humana siguen pendientes.

### Corrección responsive comprobada

Chrome real con renderer Intel RPL-P: `responsive-fixed-observations.json` y `ui/operaciones-{390,768,1440}.png`. A 390: html/body 375 px, viewport 390 px, sin desbordamiento global; tabla local 299 px con contenido 570 px y overflow auto. A 768 y 1440: html/body 753 y 1425 px respectivamente, sin overflow global. El defecto provenía de texto accesible `.sr-only` posicionado fuera del contenedor; corregido anclándolo al botón, sin ocultar overflow del body. Navegación móvil usa selector nativo agrupado; el foco al Tab inicial permanece visible. No acredita todavía el recorrido de formularios completo.

### Ampliación comprobada del incremento

- `db/tests/gold.py`:127 llamadas, exit0, oráculos fijos incluyendo GOLD01/06/07/08, ANUL/recompra, reparto por cabeza/peso individual/importe explícito y acuerdos históricos. `db/tests/gold.log`.
- `db/tests/academic.py`:20 llamadas, exit0; carreras de reserva/aplicación, réplica y muerteB→A/acuse repetido, FDWSELECT y rechazoDML, roles. Resultado/log y EXPLAIN en `db/tests/`; dataset pequeño (6animales,10operaciones,4posiciones), no prueba de capacidad comercial ni p95.
- `BOVI_TC_IT=true ./backend/mvnw -q -f backend/pom.xml -Dtest=PostgresContainerTest test`: exit0, PostgreSQL18.6 efímero recién creado, migraciones reales, replay/conflicto/rollback, runtimeDDL/DELETE/hash denegados y CHECK23514. Contenedor desechable terminado.
- Navegador real desde formularios: compra1000/recepción/reserva/venta1000/cobro/aplicación1000/bonificación100atómica/reembolso100/PNGprivado/QR y refresh persistente. Auditor por UI con rechazo403 en mutación. Respuesta perdida y recarga resuelta vía lookup sin repetirPOST. Evidencia saneada en `evidence/ui/` al finalizar agentefrontend; no confundir con capturas iniciales de error502.

Ese checkpoint fue anterior a la restauración. Consultar actualización final abajo.

## Cierre incremental · 11-oct-2026

- UI:9unitarias,6E2E reales PASS17.7s; capturas390/768/1440 Intel OpenGL y escenarios en [evidenciaUI](evidence/ui/frontend-ui-tests.md).
- Recuperación: V6 restaurada fuera del origen con5contenedores aislados, sesiones0, conciliación negocio/estado técnico y hashes de documentos. Pausa de fuente7.822s; restauración29.175s. GETprivado y compra1000/replay/lookup en API18180 PASS. [backup](evidence/recovery/backup-v6.json), [restore](evidence/recovery/restore-v6.json). Contenedores de ensayo detenidos; volúmenes privados conservados.
- Diagrama:5módulos relacionales PDF/SVG actualizados a A3 y combinado11p; aserción de texto conservado. No impresión ni revisión del profesor.
- Graphify AST y extracción selectiva real: [alcance y limitaciones](../knowledge/graph-status.md). La CLI path tuvo coincidencias ambiguas; se comprobaron IDs exactos en JSON/NetworkX.
- CI preparado con activación manual, acciones oficiales fijadas por SHA; no publicación de imágenes/despliegue. **NO EJECUTADO en GitHub**.

## Verificación final V11 · 11-oct-2026

Estos resultados sustituyen el estado pendiente de checkpoints anteriores, sin borrar su historia.

- Backend:21PASS,13unit+7HTTP+1TC18.6V1–V11, exit0; [resultado](../../backend/verification-result.json). `make verify-api` repetido por Caddy15180: exit0,13unit+7HTTP (TC no solicitado en esa repetición).
- Frontend:13unit/buildPASS,9E2E23,8s Intel Chromevisible, [resultado](evidence/ui/bovicierre-ui-final-run.json). Pantallas390/768/1440 y foco; nueve flujos descritos en [evidencia UI](evidence/ui/frontend-ui-tests.md).
- SQL157GOLD/22guardas, carreras con barreras, permisos/triggers independientes, fallosA/B/proveedor y persistencia real: [matriz](evidence/sql-test-matrix.md); registros acotados `db/tests/`. No equivale a cobertura universal.
- `make academic`:exit0, imágenes locales nonroot, API/frontend/Caddy activos15180; login/bandeja reales y consola0, [registro](evidence/integrated-compose.json), [captura](evidence/ui/integrated-caddy-1440.png). MCP de la conversación no pudo abrir X server; se reutilizó Playwright instalado con DISPLAY/XAUTHORITY de la sesión y GPU Intel, sin cambiar controles.
- `check_api_contract.py --base http://localhost:15180/api/v1`:17intercambios sesión/lecturas,0errores de schema/format/media/status; [registro](evidence/contract-read.json). No todo OpenAPI.
- `make backup` y `make restore-check` V11: pausa7,77s/restore26,801s, conciliación filas/archivos/hash y dedup/inbox,0sesiones. APIrestaurada18180: compra1000, replayETagoriginal/lookup, inventario y descargahashPASS. [Backup](evidence/recovery/backup-v11.json), [restore](evidence/recovery/restore-v11.json). Restauración detenida conserva volúmenes; fuente activa.
- `make verify-docs`:exit0; presencia IDs,42tablas83FK lógico,5unittestdiagramas, Redocly1.34.5 válido2advertencias GETpúblicos sin4xx. CatálogoA/B:0diferencias en alcance declarado.
- CI remoto, TLS público, datos de clientes, entrevistas y revisión humana: NO EJECUTADOS. Rendimiento sólo microconsultas warmcache, sin capacidad/SLO acreditados; noPITR ni backup externo.

## Revisión adicional de integración · 11-oct-2026

Las nueve E2E anteriores pasaron contra API directa; su repetición por Caddy obtuvo5PASS/4FAIL porque `encode gzip` convertía el ETag `"0"` en `"0-gzip"`, rechazado correctamente por If-Match. Se corrigió el proxy para comprimir únicamente el frontend, sin aceptar versiones alteradas en API. La repetición completa queda pendiente de la siguiente ejecución. También se incorporan predios y corrección de pesajes; la revisión detectó composición ausente en GET y reportes sin el wrapper contractual. Estos controles deben pasar por SQL/API/UI reales antes de aceptar el incremento.

## Cierre SQL/API V13 · 11-oct-2026

- MigracionesV12/V13 aplicadas mediante Flyway en A/B; catálogo42tablas/83FK sin diferencias declaradas. SQLQA66comandosPASS0,202s y rollbackcompleto: tickets/motivo/DTO/replay, cambio de conjunto rechazado, cartera paginada, GOLD06 filtrado y cierre inmutable90 frente margen vivo70. [Resultado](../../db/tests/weighing-reports-result.json). GOLD157 y guardas22 repetidos sobreV13 pasan.
- Backend24PASS15unit+8HTTP porCaddy+1Testcontainers18.6 limpioV1–V13, sin omitidas. [Resultado](../../backend/verification-result-v13.json). Reportes requeridos/filtrosUUID/CSRF/composición original verificados.
- Contrato17intercambios reales porCaddyV13PASS, incluyendo las propiedades ahoraobligatorias de reportes; [registro](evidence/contract-read-v13.json).
- Cierres anteriores sin snapshot de margen permanecenPROVISIONALES; se revisó la rama de compatibilidad, sin caso físico legado en la base principal. La repetición E2E integrada y medición ampliada siguen en ejecución.

### Medición canónica QA V13

Dataset DEMO-BENCH-V11 (nombre estable, migraciones V13): 200 animales, 300 operaciones, 300 gastos, 100 pagos y 100 entregas creados mediante 1,901 comandos; repetición de 1,901 comandos conserva IDs/resultados/conteos. Preparación4,981s; replay1,830s. 800 consultas y100warmups mediante Pgpool, con uno y cuatro clientes, más cuatro EXPLAIN ANALYZE BUFFERS; medición2,929s en Intel i7-13620H/16lógicos/15,724MiB. p95ms con1/4clientes: inventario14,088/13,322; cartera10,825/12,372; liquidación3,718/2,813; expediente0,970/1,075. [Resultado](../../db/tests/benchmark-result.json), [deduplicación](../../db/tests/benchmark-idempotency-result.json). API pausada durante la medición y reanudada; QA separada de main. Caché caliente, sin HTTP ni carga escritora: no SLO ni certificación de capacidad comercial. Los planes del wrapper PL/pgSQL no desglosan sus consultas internas.

### CSV integrado tras V13

Backend reconstruido (`cf49daa30e29…`):24/24 pruebasPASS,15unitarias+8HTTP reales por Caddy+1Testcontainers PostgreSQL18.6 frescoV1–V13. La prueba HTTP comprueba cartera.filas (liquidación/saldo400), fila de margen igual al resultadoSQL y posición del inventario en CSV. [Resultado](../../backend/verification-result-v13.json). Se corrigió el exportador compartido para reconocer los DTO canónicos de cartera y margen, manteniendo autorización y escape de fórmulas.

### Restauración final V13

Respaldo con pausa8,038s; API fuente reanudada y salud comprobada antes del ensayo. Restauración aislada28,616s en `bovicierre-restore-20261011214723`, puertos y volúmenes propios: firmasA/B y técnicas coinciden, archivosSHA-256 iguales,0sesiones, inbox/deduplicación conservados y suscripciones/FDW recreados contra la red restaurada. API18180 descargó archivo anterior y confirmó compraDEMO1000, replayETagoriginal y lookup persistido. Se corrigió el harness que consultaba sólo los primeros100UUIDs de inventario usando filtro real por animal; no se eliminó la compra inicial del ensayo. [Respaldo](evidence/recovery/backup-v13.json), [restauración](evidence/recovery/restore-v13.json). API restaurada y cinco contenedores del ensayo detenidos gradualmente; fuente15180saludable. Dumps/roles/documentos/secretos fueraGit privados. No PITR, copia externa ni pérdida física del host.

### Cierre UI integrado V13

16/16 casosPASS,0skips/0retries: tanda15 por Caddy15180 (CLI1,3min redondeado; suma de duraciones individuales73520ms, no duración global) y una caída física de proveedor (tanda47,432s). Chrome visible con IntelRPL-P/Mesa25.2.8 y perfil temporal. Compra→venta→pago, recompra/ciclos, pesajes/corrección/incompatibilidad, conflictos409/reserva vencida real, predios, CSV reales, recuperación de respuesta perdida y flujo completo sólo teclado390px. Responsive390/768/1440. Proveedor detenido503→reanudado200, captura preservada y sin escritura comercial durante la caída. [Resumen](evidence/ui/bovicierre-ui-final-run.json), [alcance y antecedentes](evidence/ui/frontend-ui-tests.md), [manifiesto de capturas](evidence/ui/bovicierre-ui-artifacts-manifest.json). Sin erroresJavaScript; HTTP negativos esperados se identifican por caso. No teléfono físico, lector de pantalla ni certificaciónWCAG. Artefactos de9casos anteriores son históricos y quedaron sustituidos por el resumen16actual.

## Manual integral y acceso · 12-oct-2026

- PDF único de239páginas/23capítulos,308marcadores/309enlaces: [manual](../pdf/BoviCierre_Manual_Integral.pdf), [proveniencia y compilación](../manual/README.md), [QA y SHA](../manual/verification.json). Revisión de código92d3d41; no prueba nueva del comportamiento económico. 239páginas renderizadas, revisión de contactos/páginas detalladas, cero spans fuera de página y cero coincidencias con once credenciales privadas. LaTeX sin Overfull ni Missing character; PDF legible por extracción y Poppler.
- [Acceso real](evidence/local-access-2026-10-12.json): ocho contenedores activos, saludA/B/auth disponible, CSRF/loginADMIN204, sesión de dos sedes y periodosOctABIERTO consultados, logout204. Apertura mediante xdg-openexit0; pestaña no comprobada visualmente, ChromeMCP sin Xserver/Cua sinbrowser. Sin reinicio, reseed ni escritura financiera.
- Casillas: instrucción del usuario cambia su significado a verificación técnica local.52marcadas;A028externa,A031/J020diferidas.55revisiones humanas pendientes; no se declara aprobación del profesor ni PR revisada. README y backlog se generan desde el mismo estado.

## Campaña UI/UX + QA (Claude) · S1 rediseño · 12-oct-2026

Ejecutor: agente Claude Opus 5.5 (Claude Code 2.1.296), rama local `feature/uiux-qa-claude` desde `38ccdc3`. Revisión humana pendiente.

| Comprobación | Comando | Resultado |
|---|---|---|
| Build + typecheck | `npm --prefix frontend run build` | PASS (Vite 8.0.3; CSS 23 KB, fuente 48 KB) |
| Unitarias frontend | `npm --prefix frontend test` | 14 pass / 0 fail / 0 skip (13 previas + `tone.test.ts`) |
| Regresión E2E con API real (Caddy 15180) | `BOVI_UI_TEST_URL=http://127.0.0.1:15180 npm --prefix frontend run test:e2e -- closure.spec.ts additional.spec.ts keyboard.spec.ts` | 15 pass / 0 fail / 0 skip, 1.3 min ([log](evidence/ui-redesign/20261012T0214/e2e-regression-final.log)) |
| Recorrido visual 3 anchos, sin mutaciones | `… test:e2e -- visual.spec.ts` | PASS; 0 vistas con desbordamiento horizontal ([report](evidence/ui-redesign/20261012T0214/after/report.json)) |
| Errores en tiempo de ejecución | `/tmp/bovicierre-ui-runtime-*.json` → [resumen](evidence/ui-redesign/20261012T0214/runtime-summary.json) | 0 page errors; HTTP ≥400 sólo deliberados: 401 `/sesion/actual` inicial ×22, 502 simulado ×1, 409/422/400 de validación negativa, 403 de rol auditor |
| Contraste de tokens | `python3 tools/ui/contrast.py` | 20/20 pares OK tras corregir borde de controles (2.07→3.69:1) |
| No ejecutado | `provider.spec.ts` (detiene el proveedor; requiere ventana aislada), lector de pantalla, teléfono físico, axe | Pendiente |

Hallazgo de prueba corregido: `keyboard.spec.ts` dependía del idioma del sistema (es_ES invierte día/mes en `datetime-local`) y fijaba la fecha esperada a octubre de 2026. Se fijó `--lang=en-US` en ese spec y se calcula el valor esperado desde la fecha tecleada. La primera ejecución de la regresión dio 14/15 por esa causa ([log](evidence/ui-redesign/20261012T0214/e2e-regression.log)).

## Campaña UI/UX + QA (Claude) · S2 coherencia, seguridad y carga · 12-oct-2026

| Comprobación | Comando | Resultado |
|---|---|---|
| Puerta local completa | `make verify-release-local` | **PASS** — docs exit 0; frontend 14; backend 28 (8 HTTP + 1 Testcontainers); SQL 37; inmutabilidad 26; E2E 16; seguridad 63; 0 fallos/0 omitidos ([release-gate](evidence/release-local/20261012T0302/release-gate.json)). Primera corrida rechazada por la puerta (etapa sin conteo) conservada en `20261012T0259-rechazada/` |
| Seguridad dinámica | `python3 tests/security/sec_dynamic.py` | 48/56 inicial (4 defectos del test + 4 hallazgos reales) → 63/63 tras correcciones y casos nuevos ([security/](evidence/security/20261012T0234/)) |
| Inmutabilidad RN-023 | `python3 db/tests/immutability.py` | 13 tablas × UPDATE/DELETE → 26/26 BV016, conteos intactos ([coherence/](evidence/coherence/)) |
| Carga HTTP | `k6 run tests/performance/load.js` (k6 v1.0.0) | 1→20 sesiones, 8,105 peticiones, p95 19.5/20.0 ms, 1 error (DIV-01, corregido), conciliación 1,185=1,185 ([report](evidence/performance/20261012T0242-ramp/report.md)) |
| Dependencias | `npm audit` | 1 alto dev (vite 8.0.3) corregido con 8.0.16; queda 1 bajo dev. Maven/Python/imágenes: INCOMPLETO ([informe](../security/dependency-report.md)) |
| No ejecutado | recuperación (sin cambios de esquema), `provider.spec.ts`, DAST/ZAP, Semgrep/Gitleaks/Trivy, dataset 10k/100k, carga sostenida | Pendiente |

## Campaña UI/UX + QA (Claude) · S2 · V14 inmutabilidad terminal y search_path · 12-oct-2026

| Comprobación | Comando | Resultado |
|---|---|---|
| Fase roja DIV-04 (antes de migrar) | `python3 db/tests/immutability.py` | 13 fallos esperados: los 13 intentos sobre estados terminales pasaban o sólo los frenaba una FK; borrar un `pago` VALIDADO se permitía ([antes](evidence/coherence/20261012-v14/immutability-antes-v14.json)) |
| Migración | `sh db/bootstrap/migrate.sh` (Flyway, A y B) | V14 aplicada; validadas 15 migraciones; `prepare.sh` la aplicó a las bases aisladas (6 bases en V14) |
| Inmutabilidad RN-023 + DIV-04 | `python3 db/tests/immutability.py` | 44/44: 26 previos + 13 bloqueos BV016 + 5 transiciones legítimas permitidas; conteos intactos ([después](evidence/coherence/20261012-v14/immutability.json)) |
| SF-08 | `psql < db/tests/security.sql` en A y B | PASS: todas las funciones `pg_catalog, pg_temp`; PUBLIC/runtime sin TEMP; `CREATE TEMP TABLE pg_tables` como `bovi_auditor` → 42501 |
| Catálogo A/B | `python3 tools/esquema/comparar_catalogo.py` (A y B) | 0 errores (alcance: columnas/tipos/PK/UK/FK) |
| Puerta local con carga | `python3 scripts/verify_release_local.py --with-load` | **PASS** — docs; frontend 14; backend 28 (Testcontainers limpio V1–V14); SQL 37; inmutabilidad 44; E2E 16; seguridad 63; k6 8,194 peticiones, 0 fallidas, 8,114/8,114 checks, p95 21.2 ms ([release-gate](evidence/release-local/20261012T0544/release-gate.json)) |
| Recuperación tras V14 | `make backup` / `make restore-check` (BACKUP_DIR privado) | Primer ensayo: firma y hashes OK, pero la base restaurada **recuperaba TEMP para PUBLIC** (ACL de base fuera de `pg_dump`). Corregido en `scripts/recovery.py`; segundo ensayo conciliado en 29.7 s con 4 triggers V14, TEMP revocado y `security.sql` PASS en la base restaurada ([restore-v14](evidence/recovery/restore-v14.json)) |
| No ejecutado | dataset 10k/100k, carga sostenida 15–20 min, `provider.spec.ts`, PITR | Pendiente |

### V15 y contrato (parcial, 12-oct-2026)
- DIV-08: fase roja `gold.py` (23505 en el segundo reverso) → V15 `reverso_unico` → `make verify-sql` 37/37 PASS con negativo BV022. V15 aplicada en A/B.
- DIV-12: OpenAPI con `periodo_id`/`fecha_reconocimiento`/`operacion_id` en movimientos (`if tipo=BAJA`) y `motivo` en anular; Redocly válido; `generate:api` regenerado; build frontend OK. DIV-12b: `MoneyTypesLintTest` 2/2 (sin float/double en backend, sin parseFloat/toFixed en frontend).
- Puerta completa tras V15: **PASS** — frontend 14, backend 30 (incluye `MoneyTypesLintTest`), SQL 37, inmutabilidad 44, E2E 16, seguridad 63, 0 omitidos ([release-gate](evidence/release-local/20261012T0702/release-gate.json)). Restauración V15 conciliada en 31.6 s, 5 triggers y TEMP revocado ([restore-v15](evidence/recovery/restore-v15.json)).
- DIV-06: `gold.py same_margin` vista = `consultar('reportes_margen')` en GOLD-02/07 y GOLD-01; `gold.py` PASS (158 llamadas, rollback). DIV-07: catálogo regenerado en business-rules.
- DIV-10 (RN-012): `db/tests/weighing_reports.py` BRUTO_TARA neto calculado en servidor (300.250, ignora neto enviado) y tara>bruto → 23514; `make verify-sql` 37 PASS / 0 FAIL.

### V16/V17 DIV-05 (12-oct-2026)
- Fase roja `immutability.py`: concepto que descuadra una liquidación y segundo periodo ABIERTO aceptados (2 fallos) ([antes](evidence/coherence/20261012-v16/immutability-antes-v16.json)).
- V16 aplicada en A/B; la fase verde falló con `record "new" has no field "id"` en `concepto_liquidacion` (defecto de V16). V17 `CREATE OR REPLACE` corrige; `immutability.py` 46/46 ([después](evidence/coherence/20261012-v16/immutability.json)); `security.sql` PASS en A/B.
- Puerta con carga: **PASS** — backend 30, SQL 37, inmutabilidad 46, E2E 16, seguridad 63; k6 8,214 peticiones, 0 fallidas, 8,134/8,134 checks, p95 22.9 ms; 125 operaciones confirmadas tras V17, 0 liquidaciones descuadradas ([release-gate](evidence/release-local/20261012T0732/release-gate.json)).
- Restauración V17: 30.8 s, firma OK, 7 triggers + `uk_periodo_un_abierto` + TEMP revocado en la base restaurada ([restore-v17](evidence/recovery/restore-v17.json)).
