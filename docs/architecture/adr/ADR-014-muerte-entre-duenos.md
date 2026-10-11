# ADR-014: Muerte en B e identidad en A

- Estado: aceptado para implementación local por encargo del usuario · 2026-10-11

## Decisión

B reconoce baja/pérdida y MuerteAnimalSolicitada.v1 atómicamente. Worker reclama lease local corto, termina la transacción y entrega a inbox idempotente A. A actualiza identidad sin volver a reconocer pérdida. Acuse perdido recupera resultado inbox; estado aplicado en A y visibilidad en B son distintos. Sustituye la actualización directa del maestro desde el comando B.

## Validación

Implementación y pruebas pendientes al registrar esta decisión; ver [evidencia](../../testing/evidence.md). La revisión humana permanece pendiente.
