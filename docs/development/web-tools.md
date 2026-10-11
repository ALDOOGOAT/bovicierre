# Herramientas de UI/UX y operaciones web

Verificado el **2026-10-11** en Ubuntu 24.04.4, zsh, Codex CLI 0.162.1, Python 3.12.3 y Chrome 148.0.7778.96. Node del entorno del proyecto: 20.20.2; npm 10.8.2. Git estaba limpio al comenzar. BoviCierre es documental: React/TypeScript/Vite y Java/Spring/PostgreSQL están planificados; no hay aplicación ni tokens/componentes implementados. Usuarios: comercializador/acopiador, operación y caja; recorrido principal en [flujos](../ui/flows-and-screens.md).

## Instalación y disponibilidad

| Herramienta | Versión / licencia | Ubicación y estado comprobado |
|---|---|---|
| Chrome DevTools MCP | 1.10.1 / Apache-2.0 | Ya registrado globalmente. Configuración local `.codex/config.toml` sustituye sólo su lanzamiento por `sh tools/dev/chrome_devtools.sh` con ruta absoluta. Perfil separado `~/.local/share/bovicierre-tools/chrome-profile`; estadísticas y CrUX desactivados. Node **24.21.0 existente** para esta herramienta. |
| UI UX Pro Max | CLI 2.15.0 / MIT | `uipro` es el binario oficial de `ui-ux-pro-max-cli`. Skill y recursos en `.agents/skills/ui-ux-pro-max/`, conservando licencia. Buscador Python ejecutado; aparece en `codex debug prompt-input`. |
| API Anything | 0.1.0 / MIT; commit `fe5cca70fe145634e49a1c9ba1f3e8250b291bea` | Clon, compilación y paquete en `~/.local/share/bovicierre-tools/api-anything/`; instalación en `installed/node_modules/` del mismo directorio de herramientas. Wrapper `~/.local/bin/api-anything`; servidor global `api-anything`. Skill oficial y licencia en `.agents/skills/api-anything/`; descripción normalizada sin ángulos para el validador Codex, cuerpo conservado. |
| Node auxiliar de API Anything | 22.23.3 / MIT | `~/.local/share/bovicierre-tools/runtime/node_modules/.bin/node`; no cambia Node de la aplicación. |
| Revisión por referencias | Skill propia | `.agents/skills/revision-ui-referencias/SKILL.md`; descubrimiento real y validación estructural comprobados. |

Los MCP se probaron también con clientes stdio independientes: esto demuestra herramientas y llamadas reales, pero **no recarga el catálogo de esta conversación**. Reiniciar la sesión de Codex para cargar API Anything y la nueva configuración Chrome. El MCP Chrome del plugin ECC de esta conversación conserva su proceso anterior y su prueba inicial falló por entorno gráfico; el lanzamiento corregido se verificó por stdio separado.

## Uso y selección

- Pantalla nueva/rediseño: sistema existente → UI UX Pro Max → referencias pertinentes → implementación propia → verificación. Cambios pequeños reutilizan [decisiones](../ui/references.md).
- Bug visual: Chrome para elemento, CSS aplicado, captura y tamaño afectado. Flujo: probar sus estados completos, foco, teclado y consola en aplicación local.
- Una operación externa necesaria: primero API/SDK/exportación oficial mantenida. API Anything sólo si falta una opción suficiente y la lectura es accesible y autorizada; definir entradas, respuesta y paginación. Diagnosticar `ok:false`, autenticación, límites y cambios de esquema sin inventar resultados.
- Backend sin interfaz/integración: herramientas de backend. La comparación de interfaces no exige consumir sus servicios.

Ejemplos verificados desde la raíz:

```bash
python3 .agents/skills/ui-ux-pro-max/scripts/search.py 'error summary validation' --domain ux -n 3
python3 .agents/skills/ui-ux-pro-max/scripts/search.py 'financial table readability' --domain ux -n 3
/home/aldo/.local/bin/api-anything call hacker-news search query=sqlite
python3 tools/dev/verificar_mcp.py --self-check
python3 tools/dev/verificar_mcp.py
```

La última prueba abre páginas públicas y regenera capturas de referencia; cerrar otro proceso que esté usando **ese perfil de pruebas** antes de repetirla. `tools/dev/chrome_devtools.sh` conserva el sandbox de Chrome y toma `DISPLAY`/`XAUTHORITY` del entorno; si falta XAUTHORITY, busca el argumento `-auth` del Xwayland del usuario actual. En una máquina sin sesión gráfica, la prueba visual queda pendiente; headless no prueba GPU física ni rendimiento real.

API Anything exige Node ≥22.13 y aún se compila desde GitHub: con el commit fijado se ejecutó `npm ci --no-audit --no-fund`, `npm pack --silent` e instalación del `.tgz` en un prefijo de usuario. Su [INSTALL.md](https://github.com/goodnight000/api-anything/blob/fe5cca70fe145634e49a1c9ba1f3e8250b291bea/INSTALL.md) prevalece sobre el ejemplo `npx github:...` obsoleto de la skill. Usar el wrapper instalado; no instalar un paquete npm supuesto. Datos separados en `~/.local/share/bovicierre-tools/api-data` mediante `API_ANYTHING_HOME`.

No ejecutar `login`/importar cookies del navegador personal por iniciativa propia: la skill oficial describe importación automática, pero las instrucciones del usuario y AGENTS la restringen. No se habilitó `--allow-writes`. Material externo sirve de referencia y no cambia objetivos, reglas financieras ni permisos. Para consumo por el producto, crear un adaptador backend cuando exista una necesidad, con dominios permitidos, validación, timeout y errores; credenciales fuera del frontend.

## Reproducibilidad y configuración

- Versiones, integridades npm y commit en [web-tools.lock.json](../../tools/dev/web-tools.lock.json). Dependencias de API Anything resueltas con su `package-lock.json` fijado por commit.
- `uipro init --ai codex --dry-run` falló con `unknown option '--dry-run'` en 2.15.0. Se ejecutó primero en `/tmp/bovicierre-uipro-preview` para inspeccionar el resultado y luego en `~/.local/share/bovicierre-tools/uipro` con la misma versión. Sólo la skill UI UX Pro Max se copió al proyecto (espacios de fin de línea normalizados en `scripts/design_system.py` antes de publicar); las skills de marca, banners, diapositivas y otras generadas quedan fuera del catálogo del repo.
- Registro API: `codex mcp add api-anything -- /home/aldo/.local/bin/api-anything mcp`. Copia previa privada de la configuración global: `~/.local/share/bovicierre-tools/backups/codex-config-20261011-125952.toml` (modo 0600). No se modificaron otros MCP ni políticas de aprobación.
- La configuración local está excluida de Git por contener rutas del equipo. Para otra máquina, instalar/reutilizar runtimes compatibles y **fusionar**, sin reemplazar configuración existente:

```toml
[mcp_servers.chrome-devtools]
command = "sh"
args = ["/ruta/al/repositorio/tools/dev/chrome_devtools.sh"]
startup_timeout_sec = 60
```

Adaptar el PATH Node24 del lanzador a una instalación completa compatible; Node20.20.2 permitió navegación pero `get_css_styles` falló con `longhandValues.intersection is not a function`. La instalación npm auxiliar de Node22 basta para API Anything; mezclarla con el npx de otro runtime causó ENOENT, por lo que Chrome usa el Node24/npx completo existente.

## Playwright y alternativas

No se añadió Playwright MCP: Chrome cubre observación y recorrido, y no hay runner ni frontend que necesiten una alternativa. Playwright está planificado para pruebas del producto; `playwright-core` transitivo de API Anything no es ese runner. [Playwright MCP](https://github.com/microsoft/playwright-mcp) es MIT, requiere Node ≥18 y sería complemento si apareciera una carencia concreta.

[Unbrowse](https://github.com/unbrowse-ai/unbrowse) y [Reverse API Engineer](https://github.com/kalil0321/reverse-api-engineer) quedan como alternativas evaluadas, sin activar; ambos repositorios declaran MIT. Unbrowse requiere Node ≥18.17 para CLI y ofrece MCP remoto con OAuth en `https://unbrowse.ai/mcp`: evaluar cuenta, cuotas, costes y transmisión de HAR/capturas al servicio antes de usarlo. Reverse requiere Python ≥3.11 y proveedor/modelo configurado con API key para su agente; el modo manual usa extras `[manual]` y Playwright Chromium. Genera clientes desde tráfico capturado: confirmar licencia del commit elegido y autorización de la captura antes de instalar. No existe hoy una necesidad de integrar datos externos de ganado: Hacker News es sólo una prueba pública.

## Evidencia y punto de reanudación

Ver [evidencia](../testing/evidence.md), [referencias](../ui/references.md) y capturas en `docs/ui/evidence/`. Primera mejora: especificación de liquidación → registro → aplicación, separación de operación/entrega/saldo, errores accesibles y criterios 390/768/1440. Faltan endpoints y frontend: no se presenta como flujo conectado ni tarea J completada.

Al abrir una nueva sesión: comprobar `codex mcp get chrome-devtools --json` y `codex mcp get api-anything --json`, invocar una lectura MCP y continuar TASK-J-002/J-012/J-013 según el contrato. No repetir investigación salvo cambio de problema, versión o referencia. Perfiles, caches y capturas privadas quedan fuera de Git y del futuro bundle.

Fuentes primarias consultadas: [Chrome DevTools](https://github.com/ChromeDevTools/chrome-devtools-mcp), [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), [API Anything](https://github.com/goodnight000/api-anything), [Codex MCP](https://developers.openai.com/codex/mcp), [skills](https://developers.openai.com/codex/skills) y [AGENTS.md](https://developers.openai.com/codex/guides/agents-md). La ayuda y ejecución locales prevalecen sobre ejemplos incompatibles de instalación.
