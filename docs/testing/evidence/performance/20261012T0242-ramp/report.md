# Carga HTTP mixta autenticada — rampa 1→5→10→20 sesiones

**Fecha:** 2026-10-12 08:42–08:50 UTC · **Instancia:** local `127.0.0.1:15180` (Caddy → Spring Boot → Pgpool → PostgreSQL 18.6 A/B/proveedor, todo en la misma laptop: 16 núcleos, 15.7 GiB, compartida con otros proyectos Docker) · **Herramienta:** k6 v1.0.0 (binario oficial, SHA256 verificado contra `k6-v1.0.0-checksums.txt`) · **Script:** `tests/performance/load.js` · **Muestreo:** `tests/performance/sample.sh` cada ~12 s.

## Escenario
- 70 % lecturas (operaciones, inventario, cartera, liquidaciones, margen, búsqueda+expediente), 20 % borradores de compra válidos, 10 % altas de contraparte/animal. Comandos económicos (confirmar, pagar) **no** incluidos; las carreras sobre un mismo recurso están en `db/tests` (TEST-xx), no aquí.
- Cada VU tiene su propia sesión (cookie + CSRF) con uno de 4 usuarios DEMO; sólo admin/operador escriben. Tiempo de reflexión 0.3–0.8 s por iteración.
- Etapas: 1 min @1, 1 min @5, 2 min @10, 3 min @20, 30 s bajada. Datos de partida de la sede A: 310 contrapartes, 331 animales, 676 operaciones (no es el objetivo de 10,000 posiciones / 100,000 hechos: **no se alcanzó**).

## Resultado
| Métrica | Valor |
|---|---|
| Peticiones | 8,105 (18.0/s), 7,058 iteraciones, máx. 20 VUs |
| Latencia lecturas | mediana 9.7 ms · p95 19.5 ms · p99 26.1 ms · máx 388 ms |
| Latencia escrituras | mediana 11.9 ms · p95 20.0 ms · p99 30.1 ms · máx 200 ms |
| Umbrales heredados (p95 lectura <500 ms, escritura <1 s) | cumplidos en este entorno; **no son SLA** |
| Errores | 1 de 8,105 (0.01 %): `alta_animal` → 500 BV500 |
| Conciliación | k6 contó 1,185 efectos 201; la BD creció 213 contrapartes + 209 animales + 763 operaciones = **1,185** (sin duplicados ni pérdidas) |
| PostgreSQL A | máx. 12 conexiones (4 activas), 0 esperas de lock, 0 deadlocks, 14.1 MB de WAL, 66,344 commits |
| CPU (% de un núcleo) | pg-a máx 34.7 % (media 14.8), backend máx 14.9 %, Caddy 4.8 % |
| Memoria | backend 287 MiB, pg-a 176 MiB; memoria disponible del host mínima 3,171 MiB |

**El error 500** se analizó: dos códigos de identificación generados por el script (`…13-61` y `…136-1`) se normalizan igual con `bovi.fn_codigo`, violan `animal_identificacion_empresa_id_sistema_codigo_normalizado_key` (log de PostgreSQL 08:48:32 UTC) y el backend no traducía ese nombre de constraint → 500. Es la divergencia **DIV-01**, corregida después (ahora 409 BV401, ver `docs/quality/coherence-matrix.md`). El script usa ahora letras como separador.

## Límites e interpretación
- La carga no saturó el sistema: no se identificó cuello de botella a 20 sesiones con tiempo de reflexión. No demuestra capacidad para 20 usuarios sostenidos de negocio, ni volumen empresarial, ni HA.
- Entre 08:43 y 08:45 UTC corrió en paralelo una compilación Maven/pruebas unitarias del coordinador (misma máquina), lo que pudo elevar algunas latencias; no se repitió la rampa por presupuesto.
- No se ejecutó la observación sostenida de 15–20 min ni el pico sin tiempo de reflexión. Smoke previo (2 VUs sin reflexión, 20 s): 2,309 peticiones, p95 14.7 ms, 0 errores (`../20261012T0241-smoke/summary.json`).
