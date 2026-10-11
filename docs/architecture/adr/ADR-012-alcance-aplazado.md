# ADR-012: Alcance aplazado y condiciones para comercializar
- Estado: propuesto · 2026-10-10
## Fuera del MVP
Exportación, subastas, sacrificio/cortes, leche, reproducción, nutrición, diagnósticos, prescripciones, crédito, custodia de dinero, timbrado CFDI, Carta Porte, básculas en tiempo real, cambio de sede escritora, transacciones entre sedes, edición concurrente de la misma entidad en ambos nodos, devoluciones físicas posteriores a la entrega, migración de inventario histórico, cuentas por pagar a transportistas.
## Condiciones para comercializar
1. Problema y precio validados (validation-plan). 2. Contrato con cancelación, exportación, retención y aviso de privacidad. 3. Respaldo con WAL y restauración ensayada. 4. Facturación del servicio vía PAC. 5. Soporte dimensionado.
## Consecuencias
Las funciones aplazadas se bloquean explícitamente en API/UI (no botones genéricos como "restaurar inventario").
