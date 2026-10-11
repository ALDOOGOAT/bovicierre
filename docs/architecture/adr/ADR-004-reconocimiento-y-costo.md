# ADR-004: Reconocimiento gerencial y costo por posición
- Estado: propuesto · 2026-10-10 · Reglas: RN-021, RN-022, RN-035
## Contexto
Entrega, cobro y PDF no deben generar una segunda venta, deuda o costo.
## Alternativas
1. Reconocer al entregar.
2. Reconocer al cobrar.
3. **Reconocer al CONFIRMAR** la operación (animales, base, versión y costos determinados).
## Decisión
Opción 3 como política operativa versionada (no dictamen contable). Costo identificado por posición mediante `asignacion_costo` (soporte) y `asiento_valoracion` (efecto), con la tabla de destino económico de `states-and-calculations.md` §3.
## Consecuencias
+ Un único evento económico; margen y cartera conciliables. − Cambiar la política exige migración de modelo y reportes.
