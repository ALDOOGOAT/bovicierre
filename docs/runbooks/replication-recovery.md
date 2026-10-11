# Runbook: recuperación de replicación

## Diagnóstico
```sql
SELECT subname, pid, received_lsn, latest_end_lsn, last_msg_receipt_time FROM pg_stat_subscription;
SELECT subname, apply_error_count, sync_error_count FROM pg_stat_subscription_stats;
SELECT slot_name, active, wal_status, safe_wal_size FROM pg_replication_slots;
```
## Casos
| Síntoma | Acción |
|---|---|
| Enlace caído, slot `reserved/extended` | Restablecer red; el apply se reanuda solo. Verificar barrera y conciliación |
| `apply_error_count` creciente (UNIQUE/CHECK) | Leer log del suscriptor; identificar fila; corregir en el **dueño** con contramovimiento; si es un error de diseño, `ALTER SUBSCRIPTION … SKIP (lsn = …)` sólo con acta y reconciliación posterior |
| `wal_status = lost` | El slot no sirve: detener escrituras del nodo origen afectado, corte, resincronizar el lado receptor (dump/restore de tablas del dueño o rebootstrap), recrear suscripción |
| Cae A | No promover B; maestros quedan pendientes; comunicar a usuarios |
Nunca cambiar `nodo_dueno` para "mover" una sede a otro nodo.
