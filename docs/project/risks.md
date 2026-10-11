# Registro de riesgos

| ID | Riesgo | Impacto | Evidencia actual | Dueño | Mitigación / acción en backlog | Estado |
|---|---|---|---|---|---|---|
| R-01 | El profesor interpreta M–M como escritura libre sobre la misma fila | Alto: cambia arquitectura de replicación | Ninguna; interpretación propia (AC-06) | Aldo | Preguntar en la siguiente clase (requirements-matrix, pregunta 1). Si se confirma: ADR nuevo con resolución de conflictos (p. ej. `last_update_wins` sólo en tabla de demostración aislada) sin tocar tablas financieras | abierto |
| R-02 | El primer cliente necesita traspasos entre sedes o inventario histórico | Medio: fuera de MVP | HIP | Aldo | Documentado como aplazado (ADR-012); cotizar módulo de apertura por separado | abierto |
| R-03 | Documentos/pesajes reales no permiten costo individual | Medio | HIP | Aldo | Reparto gerencial aprobado por cabezas o pesos medidos (RN-026, §12.1) | abierto |
| R-04 | El problema prioritario del cliente es otro o el precio no se sostiene | Alto comercial | Sin entrevistas | Ambos | Guion de 5 entrevistas antes del piloto (validation-plan) | abierto |
| R-05 | Capacidad real < 168 h-persona | Alto académico | Sin registro de horas | Ambos | Registrar horas en roadmap; recortar OCR/offline/visuales primero (§16.2) | abierto |
| R-06 | Convergencia o restauración no cumplen objetivos | Alto | Sin pruebas | Aldo | Experimento M–M/FDW el 13–14 oct (A-011/A-012); ensayo de restauración A-029 | abierto |
| R-07 | Integración externa con costo, permiso o API distinta | Medio | SINACAM sin API pública verificada | Aldo | FDW contra proveedor simulado; no anunciar integración oficial | abierto |
| R-08 | Hook GateGuard duplica el costo de cada escritura de archivo | Bajo-medio (tiempo) | Observado 2026-10-10 | Aldo | Exención por ruta en `.claude/settings.local.json` | abierto |
