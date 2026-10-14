# Administración de BD: roles, constraints, PL/pgSQL, triggers, consultas

Estado: implementado y probado parcialmente en PostgreSQL18.6. Scripts ejecutables: `db/bootstrap/01_roles.sql`, `db/migrations/V*__*.sql`; resultados reales en `docs/testing/evidence.md`. Las funciones cmd_* de la tabla son nombres conceptuales: el despachador real es `bovi.cmd_ejecutar` con tipo de comando explícito.

## 1. Distribución de controles
| Control | Mecanismo |
|---|---|
| Obligatorios, rangos, combinaciones de una fila | NOT NULL, tipos, CHECK (sin consultar otras filas) |
| Identidad, no duplicación, mismo scope | PK, UNIQUE, FK compuestas (E[,S]) |
| Una posición/reserva activa | Índices UNIQUE parciales con estado explícito (nunca con `now()`) |
| Sumatorias (aplicaciones, asignaciones, ajustes) | Comando PL/pgSQL + `FOR UPDATE` de filas cabecera |
| Inmutabilidad y propiedad de escritura | Privilegios + triggers `hecho_inmutable`, `aprobado_inmutable`, `estado_terminal_inmutable`, `guarda_propietario` |
| Autorización de usuario y caso de uso | Spring Security + capa application |
| Cálculo confirmado y snapshot | `fn_calcular_liquidacion` (canónica) dentro del comando |
| Auditoría | Insert explícito en el comando (no trigger en apply) |
| Concurrencia de cierre | Lock de la fila `periodo_cierre` común a todo comando que imputa |

## 2. Roles PostgreSQL (distintos de los roles del producto)
| Rol | LOGIN | Privilegios | Notas |
|---|---|---|---|
| bovi_owner | NOLOGIN | Dueño de esquemas/tablas/funciones | Nadie se conecta como él |
| bovi_migrator | LOGIN | Miembro de bovi_owner sólo durante migración | Usado por Flyway en tarea controlada |
| bovi_command | NOLOGIN | Dueño de funciones `SECURITY DEFINER` de comandos | `SET search_path = pg_catalog`; todos los objetos bovi/infra/public calificados |
| bovi_app_a / bovi_app_b | LOGIN | SELECT acotado (sin hashes), EXECUTE explícito en consultar/cmd_ejecutar; sin DML directo, DDL ni comandos internos worker | No superusuario, no BYPASSRLS, no dueño, no puede cambiar `session_replication_role` |
| bovi_auditor | LOGIN | SELECT en tablas y vistas de reporte | Sin mutaciones |
| bovi_repl | LOGIN REPLICATION | SELECT en tablas publicadas; usado por la suscripción | `pg_hba` restringido a la IP del otro nodo |
| bovi_fdw_read (en el servidor proveedor) | LOGIN | SELECT sobre `proveedor.tarifa_transporte`, `proveedor.ticket_bascula` | User mapping en A y B (DEC-26) |
| bovi_consulta (V22/V23) | NOLOGIN (grupo) | Hereda `bovi_auditor`: lectura de `bovi` sin `hash_contrasena`; sin `pg_monitor` (V23) | Grupo de las cuentas personales `profesor_bd`, `aldo_bd`, `jared_bd` (LOGIN, `CONNECTION LIMIT 5`), creadas por `scripts/academic_users.py` con contraseñas fuera del repo |
| bovi_monitor | LOGIN | `pg_monitor` | — |
| bovi_backup | LOGIN | `pg_read_all_data` (respaldo lógico) | Sólo desde host de respaldo |

Se revocan privilegios de PUBLIC sobre el esquema `public` y EXECUTE de PUBLIC sobre funciones del esquema `bovi`. Contraseñas: sólo en secretos de Compose (`/run/secrets/*`), nunca en el repo. Rotación: `ALTER ROLE … PASSWORD` + actualización del secreto + reinicio controlado del servicio que lo usa (`docs/runbooks/incident.md`).

Piloto: una empresa por despliegue; no se vende aislamiento multiempresa compartido. Sin RLS en el MVP: el scope de la conexión se fija por despliegue (`infra.nodo_config`), no por un GUC editable por la app.

## 3. Comandos PL/pgSQL
Todos: `LANGUAGE plpgsql SECURITY DEFINER`, sin COMMIT interno (la transacción la controla Spring), sin llamadas externas. Contexto común: `(p_empresa uuid, p_sucursal uuid, p_actor uuid, p_idem_clave text, p_idem_hash char(64), p_correlation uuid, …)`. Primer paso de cada comando con efecto: `fn_reclamar_idempotencia` (INSERT … ON CONFLICT; si existe COMPLETADA con mismo hash → devuelve resultado; hash distinto → BV405).

Orden global de locks: **idempotencia → periodo → operaciones ordenadas → posiciones ordenadas → reservas ordenadas → pagos ordenados → liquidaciones ordenadas**. Las pruebas con dos conexiones y barreras comprueban los conflictos cubiertos; no se presume ausencia de deadlocks sólo por documentar un orden.

| # | Comando | Entradas clave | Permiso | Locks | Efectos | Errores | RN | Prueba |
|---|---|---|---|---|---|---|---|---|
| 1 | `cmd_registrar_identidad_animal` | sede_operadora, sistema, código, sexo | OPERADOR (en A) | — (UNIQUE) | animal + identificación + auditoría + outbox | 23505→BV401; nodo≠A → BV501 | RN-002..004 | TEST-13 |
| 2a | `cmd_reservar_posiciones` | operación VENTA, posiciones, vence_en | OPERADOR | operación; posiciones FOR UPDATE ORDER BY id | reserva ACTIVA por posición | BV402; 23505 | RN-018 | TEST-10 |
| 2b | `cmd_liberar_reserva` / `cmd_expirar_reservas` | reserva / instante | OPERADOR / SIS | reservas FOR UPDATE SKIP LOCKED (expirador) | LIBERADA / EXPIRADA | — | RN-019 | TEST-20 |
| 3 | `cmd_ejecutar(…,'confirmar_operacion')` COMPRA (antes llamado `cmd_confirmar_compra` en el diseño) | operación, version_lock | OPERADOR | periodo; operación; selecciones | posiciones, liquidación, conceptos, asignaciones, asientos ADQUISICION, auditoría, outbox | BV015, BV404, BV025 | RN-021 | TEST-01..03 |
| 4 | `cmd_ejecutar(…,'confirmar_operacion')` VENTA (antes llamado `cmd_confirmar_venta` en el diseño) | operación, version_lock | OPERADOR | periodo; operación; posiciones; reservas | consume reservas; posiciones → VENDIDA_PENDIENTE_ENTREGA; asientos VENTA; liquidación; auditoría; outbox | BV403 (revalida); BV402 | RN-022 | TEST-10, TEST-20 |
| 5 | `cmd_aprobar_pesaje` / `cmd_corregir_pesaje` | pesaje, composición | OPERADOR | pesaje | congela composición / nuevo pesaje + original CORREGIDO | BV013 | RN-012..014 | TEST-18 |
| 6 | `cmd_distribuir_costo` / `cmd_registrar_costo_tardio` | gasto, método | OPERADOR | periodo; posiciones | asignaciones (Σ exacta) + asientos por destino | BV018, BV019 | RN-026, RN-027 | TEST-03, 06, 08 |
| 7 | `cmd_registrar_pago` / `cmd_validar_pago` | parte, tipo, importe | CAJA | — | pago | 23514 | RN-028 | TEST-04 |
| 8 | `cmd_aplicar_pago` | pago, [(liquidación, importe)] | CAJA | pago; liquidaciones | aplicaciones | BV020; BV021 | RN-029..031 | TEST-04, TEST-11 |
| 9 | `cmd_revertir_aplicacion` / `cmd_registrar_reembolso` | aplicación / pago origen | CAJA + ADMIN | pago; liquidación | reverso / pago REEMBOLSO | BV022 | RN-033 | TEST-07 |
| 10 | `cmd_ajustar_liquidacion` | liquidación, naturaleza, monto, motivo | ADMIN | periodo; pagos; liquidación | ajuste (+ reverso/reaplicación guiada GOLD-07) | BV020, BV025 | RN-023, RN-027 | TEST-07 |
| 11 | `cmd_registrar_recepcion` / `cmd_registrar_entrega` | posiciones | OPERADOR | posiciones | movimientos; estado posición; estado_entrega | BV026 | RN-020 | TEST-32 |
| 12 | `cmd_registrar_baja` | posición, motivo, evidencia | ADMIN | periodo; posición | BAJA; asiento BAJA; animal MUERTO si aplica | BV024 | RN-038 | TEST-08, 33 |
| 13 | `cmd_cerrar_periodo` / `cmd_reabrir_periodo` | periodo, motivo | ADMIN | periodo FOR UPDATE | versión de cierre con totales + hash | BV025 | RN-039 | TEST-09 |
| 14 | `fn_validar_conciliacion_propietario` | — | AUDITOR/SIS | lectura | conteos, huérfanos, Σ | — | RN-040 | TEST-23 |

Reintento en Java: hasta 3 veces el comando completo ante 40001/40P01 con la misma clave; nunca ante BVxxx ni 42501. Nivel: READ COMMITTED + locks explícitos.

## 4. Triggers
| Trigger | Tablas | Propósito |
|---|---|---|
| `guarda_propietario` → `trg_propietario` BEFORE INSERT/UPDATE | todas salvo `clave_idempotencia`, `mensaje_inbox` | `nodo_origen` = nodo local y, en tablas locales, = `sucursal.nodo_dueno`; maestros sólo en A |
| `hecho_inmutable` → `trg_inmutable` BEFORE UPDATE/borrado (13 tablas: liquidacion, concepto_liquidacion, ajuste_liquidacion, asignacion_costo, asiento_valoracion, aplicacion_pago, cierre_periodo_version, movimiento_inventario, documento, auditoria_evento, evento_outbox, revision_administrativa, revision_documento); `aprobado_inmutable` → `trg_aprobado` en contrato_version (ACEPTADA) y pesaje (APROBADO/CORREGIDO); `composicion_inmutable` → `trg_pesaje_composicion` en pesaje_animal | RN-023, RN-011, RN-013 |
| dentro de `trg_propietario` (BV010) | animal.sede_operadora_id, operacion.tipo, sucursal.nodo_dueno | RN-004, RN-010 |
| `solo_borrador` → `trg_borrador` | lote_operacion, seleccion_*, condicion_lote | sólo con operación BORRADOR/ACORDADA |
| `estado_terminal_inmutable` → `trg_estado_terminal` (V14) BEFORE UPDATE/borrado | operacion (CONFIRMADA, ANULADA, CANCELADA), gasto_operacion (APROBADO), pago (VALIDADO, REVERTIDO), posicion_inventario (CERRADA_VENTA, BAJA) | RN-023 (DIV-04). Permite sólo CONFIRMADA→ANULADA, `estado_entrega` en CONFIRMADA y `version_lock`; BV016 |

| `liquidacion_cuadrada` → `trg_liquidacion_cuadrada` (V16/V17) CONSTRAINT AFTER INSERT DEFERRABLE INITIALLY DEFERRED | liquidacion, concepto_liquidacion | total = Σ conceptos al confirmar la transacción (DIV-05); BV015 |
| `reserva_venta_vence_max_check` (V18) CHECK | reserva_venta | vencimiento ≤ 30 días desde la creación (DIV-14) |
| `reserva_activa_unica` → `trg_reserva_activa_unica` (V20) BEFORE INSERT | reserva_venta | una sola reserva ACTIVA por posición; la carrera perdedora recibe BV402/RN-018 en lugar de 23505 (GOLD-ACAD-03) |

Índice `uk_periodo_un_abierto` (V16): un solo periodo ABIERTO por sede, respaldo del advisory lock de `crear_periodo`.

Desde V14 toda función de `bovi`/`infra` fija `search_path = pg_catalog, pg_temp` y PUBLIC no tiene TEMP sobre la base (SF-08). El ACL de base no viaja en `pg_dump`: `restore-check` lo reaplica y lo comprueba.
Los triggers ordinarios no se disparan en el apply (F24–F25): validación en origen + conciliación (TEST-23).

### Administración de usuarios de la aplicación (V21, V24–V26)

`cmd_ejecutar(…,'actualizar_usuario')` (sólo ADMIN): cambia nombre, estado o contraseña. La contraseña llega como hash bcrypt generado por la API (nunca texto plano; la huella de idempotencia no deriva de ella) y la auditoría registra sólo `contrasena_restablecida`. Desde V24/V26 el actor debe ser ADMIN en **todas** las sedes donde la cuenta tiene membresías (vigentes o no, con las filas bloqueadas), para impedir tomar una cuenta ADMIN de otra sede (SF-28). Desde V25, restablecer o bloquear borra las sesiones abiertas de la cuenta (`infra.spring_session`). Pruebas: TEST-38.

### “Reglas” (rúbrica) y `CREATE RULE`

Las reglas de negocio RN-001..045 viven en CHECK, triggers y funciones, que fallan con un error explícito (BVxxx). El sistema de reescritura de PostgreSQL (`CREATE RULE … DO INSTEAD / DO ALSO`) se demuestra en un laboratorio revertido (TEST-41, `db/tests/rules_lab.py`) y no se usa en el esquema `bovi`, porque una regla `DO INSTEAD NOTHING` haría desaparecer escrituras sin error (DEC-27).

## 5. Consultas e índices
| Consulta | Índice |
|---|---|
| Inventario disponible por sede | `posicion_inventario (E,S,estado)` + anti-join a reserva ACTIVA |
| Ficha por identificador | UK `animal_identificacion (E,sistema,codigo_normalizado)` |
| Cartera vencida | `liquidacion (E,S,direccion,vence_el)` + vista de saldo |
| Detalle de liquidación | PK de concepto + `aplicacion_pago (E,S,liquidacion_id)` |
| Margen por operación | `asiento_valoracion (E,S,operacion_id)` |
Medición: `EXPLAIN (ANALYZE, BUFFERS)` sobre dataset sintético RNF-05 en entorno declarado; resultados en `docs/testing/evidence.md`.

## 6. Mantenimiento
Autovacuum con `autovacuum_vacuum_scale_factor = 0.05` en `auditoria_evento` y `evento_outbox`; `ANALYZE` tras seed; vigilar `pg_stat_user_tables`, `pg_replication_slots.wal_status`, `max_slot_wal_keep_size` (2GB inicial, a calibrar), `pg_stat_statements`. Alertas iniciales a calibrar: retraso de réplica > 60 s, disco > 80 %.

## Ejecución local actual

`bovi_auth` se limita a autorización central y tablas JDBC de sesión en A; `bovi_worker` ejecuta únicamente entrega/inbox y estado técnico. `bovi_command` NOLOGIN tiene grants efectivos a las tablas que usan sus funciones SECURITYDEFINER. La propiedad de funciones no sustituye esos grants. Runtime no pertenece a migrador/owner ni dispone de SUPERUSER/BYPASSRLS.

Testcontainers prueba CREATE/DELETE/hash denegados como runtime y CHECK23514 como rol controlado separado. Academic prueba réplica, carreras y muerte/inbox, con evidencia propia. No se declara que un rechazo por privilegios ejerció un trigger; las pruebas negativas del trigger usan el rol controlado autorizado en BD desechable.

La aplicación autentica al actor antes de llamar SQL; un actor_id enviado por navegador no modifica el scope. current_user dentro de SECURITYDEFINER es el dueño técnico, no el humano. No hay acceso directo DB por usuario final ni promesa de RLS multiempresa.
