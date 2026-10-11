# Runbook: rollback

- **Rollback de aplicación**: sólo a una versión compatible con el esquema actual (verificar en notas de la migración "compatible con app ≥ X"). `docker compose up -d backend` con el tag anterior.
- **Nunca** ejecutar migraciones "down" destructivas para simular reversibilidad.
- Si el esquema no es compatible: corrección hacia adelante (nueva migración) o restauración con corte y reconciliación (`backup-restore.md`).
- Registrar decisión, motivo y efecto en evidencia.
