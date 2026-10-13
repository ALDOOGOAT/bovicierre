# Carga sostenida — 13-oct-2026

Perfil `BOVI_PROFILE=sustained` de `tests/performance/load.js` (k6 v1.0.0): 2 min de subida a 20 sesiones propias, **15 min sostenidos con 20**, 30 s de bajada. Mezcla 70 % lectura / 20 % borradores / 10 % comandos, reflexión 0.3–0.8 s. Instancia local (Caddy 15180), datos DEMO, misma laptop que ejecuta Docker.

| Métrica | Valor |
|---|---|
| Peticiones | 39,674 (37.8/s), 0 fallidas |
| Checks | 39,594 / 39,594 |
| Lectura p50 / p95 / p99 / máx | 7.7 / 14.7 / 45.5 / 1,092.9 ms |
| Escritura p50 / p95 / p99 / máx | 8.3 / 17.0 / 48.8 / 1,337.4 ms |
| Conexiones máx. a PostgreSQL A | 12; esperas de lock 0; deadlocks 0 → 0 |
| CPU máx. por contenedor | backend 46.4 %, pg-a 26.5 %, pg-b 6.0 %, caddy 3.5 % |
| Memoria libre mínima del host | 9,641 MB |
| Conciliación | efectos k6 5,201 = filas nuevas de `auditoria_evento` 5,201; operaciones +3,403 (borradores) |

Límites: no satura el sistema (no es prueba de capacidad máxima); no incluye el dataset de 10,000 posiciones ni red real; los máximos de ~1.3 s son picos aislados (p99 50 ms). Archivos: `summary.json`, `k6.log`, `pg-a.csv`, `docker-stats.csv`, `host-mem.csv`, conteos antes/después.
