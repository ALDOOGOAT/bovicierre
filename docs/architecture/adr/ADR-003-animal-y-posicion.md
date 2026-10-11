# ADR-003: Animal permanente y posición de inventario por ciclo
- Estado: propuesto · 2026-10-10 · Reglas: RN-002, RN-005, RN-006
## Contexto
Un animal puede comprarse, venderse y recomprarse; cada tenencia tiene su propio costo.
## Alternativas
1. Estado y costo en `animal` — pierde historia en recompra.
2. **`animal` (identidad) + `posicion_inventario` (ciclo)** con índice único parcial de ciclo activo.
## Decisión
Opción 2. Estados de posición: PENDIENTE_RECEPCION, DISPONIBLE, VENDIDA_PENDIENTE_ENTREGA, CERRADA_VENTA, BAJA; "reservada" derivada de reserva ACTIVA (DEC-01..03). `animal.situacion` bloquea recompra de MUERTO (DEC-04).
## Consecuencias
+ GOLD-05/09 naturales. − Consultas de ficha requieren join animal–posiciones.
