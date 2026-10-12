# Manifiesto de cambios en la configuración de usuario de Claude

Campaña UI/UX + QA, 12-oct-2026. Todos reversibles.

| Cambio | Archivo/ruta | Cómo revertir |
|---|---|---|
| MCP `api-anything` (user) | `~/.claude.json` (backup previo en `~/.local/state/bovicierre-claude/backups/claude.json.<epoch>`, 0600) | `claude mcp remove --scope user api-anything` |
| Skill `ui-ux-pro-max` | `~/.claude/skills/ui-ux-pro-max/` (copia del repo) | borrar la carpeta |
| Skill `api-anything` | `~/.claude/skills/api-anything/` (copia del repo) | borrar la carpeta |
| Marketplace `bovicierre-local` | `~/.local/share/bovicierre-claude/marketplace/` | `claude plugin marketplace remove bovicierre-local` |
| Plugin `bovicierre-workbench@bovicierre-local` 0.1.0 | caché de plugins de Claude | `claude plugin uninstall bovicierre-workbench@bovicierre-local` |
| Estado de campaña | `~/.local/state/bovicierre-claude/<repo-id>/` (state.json, lock.json) | borrar la carpeta al cerrar la campaña |

No se modificaron permisos, modo de aprobación, sandbox, hooks globales ni la preferencia de auto-continuación.
