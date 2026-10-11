# Respaldo y restauración local

La réplica no es respaldo. Ensayo final V13 el2026-10-11: pausa8,038s, restauración28,616s, [evidencia saneada](../testing/evidence/recovery/restore-v13.json). Incluye compra nueva1000, reintento con ETagoriginal, lookup, inventario y descarga restaurada con mismoSHA256. API fuente Docker reanudada antes del ensayo y salud comprobada; restauración y API18180 detenidas después, conservando volúmenes.

## Corte del origen

1. Coordinar pausa de pruebas SQL/clientes externos. `scripts/recovery.py backup` identifica API Docker propia o PIDJava/cwd/runtime18080 de este checkout y la termina gradualmente; así cesan requests/uploads/finalizaciones/limpieza y worker.
2. Esperar fin de transacciones, mensajes propios pendientes0 y huellas A/B iguales de todas las tablas replicables. Cero actividad en una sola observación no protege frente a otro escritor externo: la pausa coordinada es una precondición del procedimiento.
3. Dumps A/B/proveedor con `--no-publications --no-subscriptions`, roles privados, sesiones excluidas. Rechazar enlaces simbólicos antes de copiar; comparar hashes fuente/copia y comprobar fuente estable al final. Copiar archivos, calcularSHA256 y guardar también huellas locales de deduplicación/inbox/leases/capturas/Flyway.
4. Fuente vuelve a arrancar antes del ensayo. Dumps/roles/secretos/archivos permanecen fuera deGit con permisos privados. No hay copia fuera del host todavía.

```bash
make backup BACKUP_DIR="$HOME/.local/share/bovicierre-academic/backups/ensayo-nuevo"
make restore-check BACKUP_DIR="$HOME/.local/share/bovicierre-academic/backups/ensayo-nuevo"
```

El destino debe ser nuevo y externo al checkout. La restauración crea proyecto `bovicierre-restore-<UTC>`, red/volúmenes independientes y puertos18432/18433/18434/18999/18998 libres. Nunca ejecuta down-v ni conecta al origen. Se restauran roles y proveedor, se reconstruye FDW/suscripciones contra aliases de esa red y se prueba convergencia antes de copy_data=false. Sesiones se invalidan; inbox/idempotencia se conservan.

## Prueba HTTP restaurada

Iniciar una segunda API **sólo en18180**, `BOVI_RUNTIME_DIR` y `BOVI_DOCUMENTS_DIR` del ensayo, secretos del respaldo y JDBC contra18999/18998/auth18432; no sobrescribir PID/runtime del origen. Después:

```bash
python3 scripts/recovery.py verify-http --directory "$HOME/.local/share/bovicierre-academic/backups/ensayo-nuevo"
```

Esta prueba exclusivamente18180 descarga un archivo previo, compruebahash y crea compraDEMO1000 por comandosAPI; repite la confirmación/ETagoriginal y comprueba resultado persistido. Guarda resultado privado, sin cookies/credenciales. Detener esa API gradualmente antes de detener su Compose. El comando stop impreso incluye el directorio de secretos necesario; conserva volúmenes.

## Límites para un piloto

Es recuperación medida en mismohost, sin PITR, resistencia a pérdida de laptop ni RPO/RTO comercial garantizado. Copia fuera del host, archivadoWAL y ensayos ante pérdida real requieren procedimiento y autorización posteriores. Los snapshots son consistentes porbase; la pausa y convergencia hacen compatible el parA/B, no existe snapshot distribuido automático.
