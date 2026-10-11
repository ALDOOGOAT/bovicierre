# Guion de demostración (12–15 min)

Datos 100 % sintéticos (prefijo DEMO). Ensayar con cronómetro; si no hay red, mostrar evidencia guardada (`evidence.md`) indicando que es grabación de una ejecución real.

| Min | Bloque | Qué se muestra | Evidencia/comando |
|---|---|---|---|
| 0–2 | Problema y propuesta | Comprador, propuesta de valor, alcance y límites | `docs/business/business-model.md` |
| 2–5 | Datos | MER Chen (entidad débil LoteOperacion, cardinalidad Animal–Posición), relacional, índice único parcial de posición activa | láminas, `relational-model.md` |
| 5–9 | Flujo | Compra GOLD-01 → pesaje → venta → liquidación → anticipo 50,000 → saldo 244,000 | UI o API |
| 9–12 | Garantías | Doble venta concurrente rechazada (TEST-10); permiso denegado; escritura en A y B converge; consulta FDW y DML rechazado | scripts de prueba |
| 12–14 | Operación | Restauración medida, arquitectura, grafo | runbook, `graph-status.md` |
| 14–15 | Comercial | Modelo de ingresos, resultados reales obtenidos, límite del piloto | `unit-economics.md` |
