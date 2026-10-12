# Herramientas de Claude Code para BoviCierre

Inventario del 12-oct-2026 (Claude Code **2.1.296**, autenticación por suscripción claude.ai, modelo de la sesión coordinadora `claude-opus-5-5`, esfuerzo `medium` elegido por el usuario). Estados: **instalado** (archivos presentes) · **registrado** (configurado en Claude) · **cargado** (visible en la sesión) · **usado** (invocado en esta campaña). Sin secretos; rutas privadas sólo como referencia.

| Capacidad | Versión / origen | Alcance | Estado | Prueba y resultado |
|---|---|---|---|---|
| ECC (`ecc@ecc`) | 2.2.2, marketplace `ecc` @ `e482e57` | user | instalado, registrado, cargado (skills `ecc:*` visibles) | Ya existía; no se reinstaló. No se copiaron hooks crudos |
| Ponytail (`ponytail@ponytail`) | 4.9.0, marketplace @ `2ed6c52` | user | instalado, registrado, cargado (`ponytail:ponytail-review`, `-audit`) | Ya existía |
| Chrome DevTools MCP | plugin `chrome-devtools-mcp@claude-plugins-official` 1.9.0 (`npx chrome-devtools-mcp@1.9.0`) | user | registrado, *Connected* (`claude mcp list`) | Se reutiliza; **no** se registró `bovi-chrome-devtools` porque ya hay un servidor equivalente válido. ECC también expone uno (`@latest`) — duplicado preexistente, no se tocó |
| API Anything MCP | wrapper `~/.local/bin/api-anything` → upstream `goodnight000/api-anything` 0.1.0 (commit documentado `fe5cca70…`), runtime Node separado | user | **registrado en esta campaña**, *Connected* | `claude mcp add --scope user api-anything -- ~/.local/bin/api-anything mcp`; `claude mcp get api-anything` → ✔ Connected. Backup previo de `~/.claude.json` en `~/.local/state/bovicierre-claude/backups/` |
| Skill `api-anything` | copia de `.agents/skills/api-anything/` (SKILL.md + LICENSE MIT) | user (`~/.claude/skills/`) | instalada, cargada (aparece en el catálogo de skills) | Sólo lectura autorizada; sin login/cookies/`--allow-writes` |
| Skill `ui-ux-pro-max` | copia de `.agents/skills/ui-ux-pro-max/` (scripts, data, LICENSE) | user | instalada, cargada, **usada** | `python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py 'financial table readability' --domain ux -n 2` → 2 resultados. Se eligió la vía skill copiada, no el plugin (no ambas) |
| Graphify | `~/.local/bin/graphify` (`graphifyy` 0.9.49) + skill `~/.claude/skills/graphify` | user | instalado, cargado | Pendiente de actualización al cierre de bloque |
| `bovicierre-workbench` (mods propios) | 0.1.0, fuente `tools/claude/bovicierre-workbench/`, marketplace local `bovicierre-local` en `~/.local/share/bovicierre-claude/marketplace` | user | validado (`--strict`), probado (6/6), instalado y habilitado (`claude plugin list`) | **Carga en sesión no verificada todavía**: requiere `/reload-plugins` o nueva sesión. Hash del árbol instalado: `fb3ef9d7…aa16c` |
| Continuidad | `tools/claude/checkpoint.py`, `resume-check.py` | repo | probado 11/11 (`python3 -m unittest tools/claude/test_continuity.py`) | Estado privado en `~/.local/state/bovicierre-claude/<repo-id>/` |
| Playwright runner | `@playwright/test` 1.58.2 del producto, Chrome visible `/usr/bin/google-chrome` | repo | usado | Regresión 15/15 |
| Otros plugins presentes | claude-mem, superpowers, security-guidance, claude-security, frontend-design, github (falla auth), supabase/railway (requieren auth), codex | user | preexistentes | No se usaron servicios remotos con coste; no se cambió de proveedor |

## Modelos
La sesión coordinadora corre en `claude-opus-5-5`. El encargo propone `sonnet`/`haiku` para trabajadores; en S1 no se lanzaron subagentes (el trabajo fue secuencial sobre los mismos archivos de estilo y un solo navegador). Si se lanzan en S2 se registrará el modelo que la herramienta muestre.

## Continuación al límite de uso
No se encontró en la configuración de usuario la opción *Continue automatically at usage limit* activada (sólo una bandera de caché de funciones, que no es preferencia del usuario). Activación humana, una sola vez, si se desea: `/config` → **Continue automatically at usage limit** (o `/rate-limit-options`). No se activó por atajo. Sin ella, la reanudación es manual con `docs/continuity/NEXT_SESSION.md`.
