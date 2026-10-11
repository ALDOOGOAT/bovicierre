# Runbook: incidentes

1. Registrar: hora, síntoma, `correlation_id` de los errores, sedes afectadas.
2. Clasificar: datos (conciliación), disponibilidad (nodo/servicio), seguridad (credencial expuesta).
3. Seguridad — credencial expuesta: rotar de inmediato (`ALTER ROLE … PASSWORD`, actualizar secreto de Compose, reiniciar el servicio que la usa), revisar logs de acceso, documentar.
4. Datos — diferencia en conciliación: congelar el periodo afectado, identificar origen, corregir con contramovimientos, nunca con UPDATE directo.
5. Cierre: causa, acciones, prevención; enlazar en `docs/testing/evidence.md` si afecta la entrega.
