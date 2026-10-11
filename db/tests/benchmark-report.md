# Benchmark canónico QA V13

Ejecutado 2026-10-11T21:39:35.635326+00:00 en `bovicierre_release_replay`, namespace histórico `DEMO-BENCH-V11`. Las funciones actuales se validaron como V13 y se conserva SHA del comando, revisión y estado dirty en JSON. API pausada por el coordinador durante preparación/medida y reanudación a su cargo; este script no administra servicios.

Dataset propio:200 animales,200 compras,100 ventas,300 gastos,100 pagos y100 entregas. Se crearon sólo por comandos SQL canónicos. La QA completa también conserva fixtures previas:216 animales,328 operaciones,211 posiciones,316 liquidaciones,303 gastos y103 pagos; no se borraron. Cada compra1000+costo100; venta1600+gasto20; cobro1200/aplicado1000.

Resultados fijos:inventario110000.00,costo vendido110000.00,margen48000.00,saldo ventas60000.00,disponible pagos20000.00;100 posiciones disponibles y100 entregadas.

Preparación1901 comandos en 4.981s; reintento1901 en 1.830s con mismos IDs/resultados/conteos. Ver [idempotencia](benchmark-idempotency-result.json) y [dataset](benchmark-dataset-result.json).

Medición: `bovi.consultar` real con los parámetros de CoreController, rol bovi_app_a por Pgpool19999, autocommit de sólo lectura.100 muestras/query con5 calentamientos en conexión única; después cuatro conexiones persistentes×25 muestras/query y5 calentamientos por conexión. Total800 llamadas medidas,100 calentamientos y4 EXPLAIN(ANALYZE,BUFFERS). Se excluye apertura de conexión; tiempos incluyen consulta/transferencia/decodificación psycopg. No incluyen Java/HTTP/UI.

| Consulta | p50 una conexión ms | p95 una conexión ms | p50 cuatro conexiones ms | p95 cuatro conexiones ms |
|---|---:|---:|---:|---:|
| inventario_posiciones | 9.580 | 14.088 | 9.478 | 13.322 |
| reportes_cartera | 6.866 | 10.825 | 10.025 | 12.372 |
| liquidacion | 1.534 | 3.718 | 1.616 | 2.813 |
| operacion_expediente | 0.244 | 0.970 | 0.444 | 1.075 |

Medida total2.929s. CPU 13th Gen Intel(R) Core(TM) i7-13620H,16 lógicos; RAM total15724.6MiB, disponible5659.8→5630.1MiB. Información complementaria en doctor-final.json. No se afirma uso CPU pico ni RAM dedicada a PG: host incluye otros procesos.

Los cuatro planes canónicos están en [benchmark-result.json](benchmark-result.json), con muestras crudas. EXPLAIN sobre el wrapper PLpgSQL registra tiempo y buffers pero no desglosa sus planes internos; no se presenta como una revisión exhaustiva de índices. Dataset moderado, cache caliente, sin escritores durante medida; no prueba SLO comercial, volumen de producción, carga mixta ni escalabilidad.

Reproducción en una ventana explícita: `python db/tests/benchmark.py --prepare` dos veces y `--measure`, con dependencias de db/requirements.txt y servicios propios ya preparados. `--self-check` no contacta BD. Fuera de run.sh/verify-sql porque conserva datos y necesita aislar la medición. El programa rechaza una base distinta y perfiles production; no elimina QA ni modifica main.
