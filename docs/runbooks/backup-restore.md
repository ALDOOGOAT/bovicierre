# Runbook: respaldo y restauración (demo académica)

Estado: diseñado; ensayo en TASK-A-029. La réplica **no** es respaldo.

## Respaldo con corte
1. Cerrar nuevas escrituras (modo mantenimiento en backend) y detener workers de outbox.
2. Esperar fin de transacciones y convergencia (barrera A→B y B→A).
3. Registrar corte: `fn_validar_conciliacion_propietario()` en A y B + conteos por `nodo_origen`.
4. `pg_dump -Fc --no-publications --no-subscriptions` de A y de B (las publicaciones/suscripciones se reconstruyen por bootstrap) [F34]; `pg_dumpall --roles-only` (sin contraseñas en el repo).
5. Copiar volumen de documentos y generar manifiesto `sha256sum`.
6. Guardar todo fuera del host.

## Restauración aislada
1. Red Docker nueva sin acceso a producción; cronometrar desde aquí.
2. Crear clusters vacíos, restaurar roles y dumps de A y B.
3. Restaurar documentos y verificar manifiesto.
4. Validar: usuarios, relaciones (huérfanos = 0), cifras GOLD de la semilla, conciliación igual al corte.
5. Reconstruir replicación con bootstrap (sin reactivar slots antiguos).
6. Registrar tiempo real (RTO medido) en evidencia.

## Piloto (no implementado)
RPO ≤ 15 min / RTO ≤ 2 h exigen backup base + archivo WAL continuo por nodo fuera del host [F35] y ensayo medido. Dos dumps en instantes arbitrarios no son un snapshot global consistente.
