# Replicación M–M y FDW

Estado: diseñado; experimento mínimo en TASK-A-011/A-012 (13–14 oct), esquema definitivo en TASK-A-026.

## 1. Política
Replicación **lógica bidireccional asíncrona** A ↔ B con **escritor exclusivo por agregado**. Maestros sólo en A; operaciones y sus hijos en el nodo dueño de su sede. No se editan simultáneamente las mismas filas en ambos nodos. `origin = none` evita reenvío (loops) de cambios replicados; **no** resuelve conflictos de negocio [F22]. Interpretación pendiente de confirmar con el profesor (R-01). Si el profesor exige dos escritores sobre la misma fila, se registrará como cambio arquitectónico con otro ADR.

## 2. Matriz tabla → propietario → dirección
| Grupo | Tablas | Escritor | Publicación | Política UPDATE/DELETE |
|---|---|---|---|---|
| Maestros | empresa, sucursal, rol_aplicacion, usuario, membresia_usuario, parte, predio, animal, animal_identificacion | A | `pub_a` (A→B) | UPDATE sólo en A; sin DELETE (se usa estado) |
| Locales | operacion, folio_contador, lote_operacion, contrato_version, condicion_lote, seleccion_compra, seleccion_venta, posicion_inventario, movimiento_inventario, reserva_venta, pesaje, pesaje_animal, gasto_operacion, asignacion_costo, liquidacion, concepto_liquidacion, ajuste_liquidacion, pago, aplicacion_pago, periodo_cierre, cierre_periodo_version, asiento_valoracion, operacion_documento, revision_documento | dueño de la sede | `pub_a` en A y `pub_b` en B (misma lista) | Sólo el dueño (trigger); hechos inmutables; DELETE sólo en hijos de borrador |
| Mixtas con nodo_origen | documento, revision_administrativa, auditoria_evento, evento_outbox | A para identidad/maestros; dueño para operación | idem | Sólo INSERT |
| No replicadas | infra.nodo_config, infra.entrega_outbox, infra.importacion_fuente, mensaje_inbox, clave_idempotencia, spring_session*, flyway_schema_history | local | — | — |

Cada nodo publica la **lista explícita** (no `FOR ALL TABLES`). Como cada fila sólo se escribe en su dueño (guarda por trigger) y `origin = none` filtra lo ya replicado, cada cambio viaja una sola vez.

## 3. Bootstrap desde bases vacías (`db/bootstrap/`)
1. Levantar `pg-a`, `pg-b`, `pg-prov` con volúmenes independientes (`wal_level = logical`, `max_replication_slots`, `max_wal_senders`).
2. Aplicar roles (`01_roles.sql`) y migraciones Flyway en **ambos** nodos (misma versión).
3. Insertar `infra.nodo_config` ('A' / 'B').
4. Verificar que las tablas publicadas están vacías.
5. `CREATE PUBLICATION pub_a FOR TABLE …` en A; `pub_b` en B.
6. Fuera de transacción, en B: `CREATE SUBSCRIPTION sub_b_desde_a CONNECTION '…pg-a…' PUBLICATION pub_a WITH (slot_name = 'slot_a_para_b', origin = none, copy_data = false);` y simétrico en A (`slot_b_para_a`). Sin precrear slots (si otra receta los precrea: `create_slot = false`).
7. Verificar `pg_stat_subscription` y `pg_subscription_rel` (estado `r`).
8. Sembrar maestros sólo en A.
9. Barrera: insertar fila marcador en A y esperar su visibilidad en B.
10. Sembrar operaciones de A en A y de B en B (nunca la misma semilla en ambos).
11. `fn_validar_conciliacion_propietario` en ambos: conteos por nodo_origen, PK, huérfanos.
12. Habilitar escrituras de la app.

`copy_data = false` sólo vale para este arranque vacío o un snapshot común validado. Con datos existentes se requiere procedimiento de corte/snapshot/slots específico. La app nunca crea ni borra suscripciones.

## 4. Restricciones conocidas (también en README)
- DDL, roles y secuencias no se replican [F23]; migraciones coordinadas en ambos nodos.
- Foreign tables, vistas y large objects no se replican como tablas.
- El apply usa `session_replication_role = replica`: no ejecuta triggers ordinarios ni verifica FK como en el origen [F24–F25] → validar en origen y conciliar.
- UNIQUE/CHECK/NOT NULL pueden detener el apply ante conflicto: se investiga cada error (`pg_stat_subscription_stats`); no se declara "sin conflictos".
- No se usa `ENABLE ALWAYS` en triggers (duplicaría auditoría/outbox o rechazaría la escritura remota).
- Sólo `propietario_despacho = nodo local` despacha outbox; `infra.entrega_outbox` es local.
- Padres maestros deben ser visibles en B antes de crear dependencias en B; no hay orden global entre streams.
- Folios internos pueden tener huecos; no son fiscales. UUID no da unicidad comercial a un arete.
- Pgpool raw conecta a su backend fijo; no sincroniza ni decide propietario.
- Presupuesto de conexiones por nodo: Hikari 8 + Pgpool `num_init_children` 16 × `max_pool` 1 + 2 suscripción/walsender + 5 administración ≤ `max_connections` 50.

## 5. Caídas
| Escenario | Comportamiento |
|---|---|
| Sólo se corta la replicación | Cada sede opera sus recursos ya registrados con sesión válida; consolidados muestran antigüedad; slots retienen WAL hasta `max_slot_wal_keep_size` |
| Cae B | Comandos de sede B → 503 (BV501); A sigue |
| Cae A | Sin login nuevo ni maestros nuevos (identidades pendientes); B opera sus recursos con sesiones existentes; **no** se promueve B |
| Slot invalidado (`wal_status = lost`) | Resincronización controlada (`docs/runbooks/replication-recovery.md`) |
Pruebas: TEST-21, TEST-22, TEST-23, TEST-24.

## 6. FDW (AC-07)
Tercer PostgreSQL `pg-prov` = **"Proveedor Simulado de Transporte y Báscula (datos sintéticos)"**.
- Esquema `proveedor`: `tarifa_transporte(ruta, origen, destino, precio_mxn numeric(14,4), unidad, vigente_desde, version)` y `ticket_bascula(folio, bascula, pesado_en, neto_kg, nota)`.
- Rol remoto `bovi_fdw_read` sólo SELECT.
- En A: `CREATE EXTENSION postgres_fdw`; `CREATE SERVER prov_sim FOREIGN DATA WRAPPER postgres_fdw OPTIONS (host 'pg-prov', dbname 'proveedor', connect_timeout '3')`; `CREATE USER MAPPING FOR bovi_app_a SERVER prov_sim OPTIONS (user 'bovi_fdw_read', password '…secreto…')`; `IMPORT FOREIGN SCHEMA proveedor LIMIT TO (tarifa_transporte, ticket_bascula) FROM SERVER prov_sim INTO ext_proveedor`; `GRANT SELECT` a la app, sin INSERT/UPDATE/DELETE.
- TEST-25: SELECT correcto; INSERT/UPDATE/DELETE fallan (local por privilegio, remoto por rol); con `pg-prov` detenido, error controlado: "Fuente externa no disponible, reintente".
- La consulta FDW se hace **fuera** de transacciones con locks financieros; al aceptar se guarda snapshot local (fuente, referencia, fecha, unidad, hash) en `gasto_operacion.snapshot_fuente_externa`.
- postgres_fdw no tiene 2PC remoto [F27]: nunca se usa para atomicidad monetaria. No se anuncia conexión oficial con SINIIGA, SENASICA ni empresa real.
