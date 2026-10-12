# bovicierre-workbench

Plugin propio (mods + skills) de la campaña UI/UX+QA. Se instala en scope usuario, pero sólo se activa si el
checkout tiene remote `ALDOOGOAT/bovicierre`, `docs/continuity/campaign.marker`, sin `docs/continuity/STOP` y con
estado no terminal en `SESSION_STATE.md`.

- **Mod 1 — sesión/continuidad:** línea de estado con bloque y cuota real (`$.session.usage()`; "cuota desconocida"
  si no hay lectura), avisos a 80/90 % y recordatorio de checkpoint cada 25 min. No envía prompts ni aprueba nada.
- **Mod 2 — evidencia:** marca como pendientes las verificaciones afectadas por cada Edit/Write y sólo las limpia un
  comando de verificación terminado sin error. `/bovi-status` las lista.

```bash
claude plugin validate tools/claude/bovicierre-workbench --strict
claude plugin test tools/claude/bovicierre-workbench
```
Instalación: copia versionada en `~/.local/share/bovicierre-claude/marketplace/` (marketplace `bovicierre-local`).
