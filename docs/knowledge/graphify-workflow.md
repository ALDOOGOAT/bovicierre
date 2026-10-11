# Flujo de trabajo con Graphify

Implementación: **Graphify-Labs/graphify**, paquete PyPI `graphifyy` (doble y), ejecutable `graphify`, slash command `/graphify` dentro de Claude Code [F36–F37]. Instalado en la máquina de Aldo: 0.9.49 vía pipx (Python 3.12.3). Skill en `~/.claude/skills/graphify/`.

## Instalación en otra máquina (Jared)
```bash
pipx install graphifyy==0.9.49     # o: uv tool install graphifyy==0.9.49
graphify install --platform claude # copia la skill; revisar qué archivos toca antes de aceptar
```
No instalar paquetes de nombre parecido. No cambiar el Python del sistema.

## Alcance y exclusiones
Se indexa la raíz del repo. `.graphifyignore` (sintaxis gitignore; se suma a `.gitignore`, verificado en `graphify/detect.py`) excluye: `graphify-out/`, `.env*`, claves/certificados, `secrets/`, `backups/`, dumps, `data/`, `storage/`, `node_modules/`, `target/`, `dist/`, exportes de diagramas. Ningún dato real de clientes entra al corpus. El análisis de código es local; la extracción semántica de esta implementación usa agentes disponibles de la sesión y conserva fuentes/huellas locales; no activa otro proveedor ni facturación API.

## Comandos
| Cuándo | Comando |
|---|---|
| Primera vez / reconstrucción | `/graphify .` (en Claude) |
| Tras cambios en .md, reglas, ADR, contrato | `/graphify . --update` (en Claude) |
| Tras cambios sólo de código | `graphify update .` (shell) — no sustituye la actualización semántica |
| Consultas | `graphify query "…"`, `graphify path "A" "B"`, `graphify explain "X"` |

Salidas: `graphify-out/graph.json`, `graph.html`, `GRAPH_REPORT.md`. **No se versionan** (cada integrante genera el suyo por checkout/worktree). Sin Graphify Cloud ni servidor público.

## Hitos de actualización
Paquete de diseño · 18-oct · 24-oct · 28-oct · 31-oct. Cada ejecución se registra en `graph-status.md`.

## Preguntas de verificación (§15.4)
1. ¿Qué RN y qué comando evitan la doble venta?
2. ¿Qué entidad, FK, función y prueba sostienen la aplicación de un pago?
3. ¿Qué pantalla consume el contrato de liquidación?
4. ¿Qué ADR explica el maestro A y la propiedad de escritura?
5. ¿Dónde se documenta el costo tardío de animales vendidos?
6. ¿Qué requisito del profesor demuestra cada script de replicación y FDW?
Las aristas inferidas se verifican contra los archivos fuente; el grafo no sustituye la evidencia de pruebas.

## Codex en esta implementación

La skill disponible es `~/.codex/skills/graphify/SKILL.md`; se leyó su esquema de extracción. Se reutiliza graphifyy0.9.49, sin actualizar ni activar proveedores externos. AST: `graphify update .`. Semántica: los agentes leen los documentos canónicos cambiados y generan fragmentos locales `graphify-out/backend-final-semantic.json`, `frontend-final-semantic.json` y `operations-final-semantic.json`, con manifiestos de fuentes y SHA-256. Antes de integrarlos, comprobar las huellas contra los archivos actuales y la unión de fuentes contra `graphify-out/final-doc-files.json`. Ejecutar `python3 tools/dev/update_implementation_graph.py --self-check`, luego el mismo script con los tres fragmentos como argumentos y finalmente `graphify cluster-only . --no-label`. El integrador conserva nodos AST existentes, identifica los nuevos como semánticos, valida referencias y guarda caché con el esquema de la skill. Registrar métricas y corte reales en graph-status. Este proceso reinterpreta los documentos cambiados; los documentos sin cambios conservan su extracción histórica. No afirmar que todo el corpus histórico se reextrajo.
