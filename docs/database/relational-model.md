# Modelo relacional (lógico)

Estado: diseñado · 2026-10-10. Detalle de columnas por tabla en `data-dictionary.md`. Abreviaturas sólo en este documento: **E** = `empresa_id`, **S** = `sucursal_id`. Claves subrayadas = PK; `UK` = clave candidata alterna; `→` = FK.

## 1. Reglas de transformación MER → relacional
| Construcción MER | Transformación aplicada | Ejemplo |
|---|---|---|
| Entidad fuerte maestra | Tabla con PK (E, id) | `parte(E, id, …)` |
| Entidad fuerte local de sede | Tabla con PK (E, S, id); FK incluyen E y S | `operacion(E, S, id, …)` |
| Entidad débil | PK = PK del propietario + clave parcial; FK identificante `ON DELETE CASCADE` sólo mientras el propietario es borrador (trigger lo impide después) | `lote_operacion(E, S, operacion_id, numero_lote)` |
| Débil con dos propietarios | PK con la parte común + ambas parciales; dos FK | `condicion_lote(E,S,operacion_id,numero_version,numero_lote)` → contrato_version, → lote_operacion |
| Relación 1:N | FK en el lado N | `operacion.parte_id → parte` |
| Relación N:M sin identidad | Tabla asociativa con PK compuesta | `pesaje_animal`, `operacion_documento`, `revision_documento` |
| Asociativa con identidad propia | Tabla con id + FKs | `aplicacion_pago`, `asignacion_costo` |
| Ternaria | Tabla con las tres claves | `membresia_usuario(E,S,usuario_id,rol_codigo)` |
| Recursiva | FK a la misma tabla con UNIQUE si es 1:1 | `aplicacion_pago.reverso_de_id UNIQUE` |
| Restricción de tipo (COMPRA/VENTA) | Columna redundante constante + FK compuesta a UK(E,S,id,tipo) | `seleccion_compra.tipo_operacion = 'COMPRA'` |
| XOR de fuente | Columnas mutuamente excluyentes + `CHECK (num_nonnulls(...) = 1)` | `asignacion_costo` |
| Derivados | No se almacenan; vistas | `v_saldo_liquidacion` |

Identificadores técnicos: `uuid` generados con `uuidv7()` (PostgreSQL 18), ordenables por tiempo; no sustituyen claves comerciales (folio, código normalizado).

## 2. Esquema
### Acceso y organización (maestros, nodo A)
- empresa(<u>id</u>, razon_social, rfc, estado, nodo_origen, creado_en)
- sucursal(<u>E, id</u>, codigo, nombre, nodo_dueno, zona_horaria, nodo_origen) · UK(E, codigo) · E → empresa
- rol_aplicacion(<u>codigo</u>, descripcion)
- usuario(<u>E, id</u>, login_normalizado, nombre, hash_contrasena, estado, nodo_origen, creado_en) · UK(E, login_normalizado)
- membresia_usuario(<u>E, S, usuario_id, rol_codigo</u>, vigente, nodo_origen) · (E,S) → sucursal · (E,usuario_id) → usuario · rol_codigo → rol_aplicacion

### Contrapartes e identidad (maestros, nodo A)
- parte(<u>E, id</u>, tipo_persona, nombre, rfc, telefono, es_sintetico, nodo_origen) · UK parcial(E, rfc) WHERE rfc IS NOT NULL
- predio(<u>E, id</u>, nombre, clave_upp_declarada, municipio, entidad_federativa, parte_responsable_id, nodo_origen) · (E, parte_responsable_id) → parte
- animal(<u>E, id</u>, sede_operadora_id, sexo, fecha_nacimiento_declarada, raza_declarada, situacion, nodo_origen, creado_en) · UK(E, sede_operadora_id, id) · (E, sede_operadora_id) → sucursal
- animal_identificacion(<u>E, id</u>, animal_id, sistema, codigo_declarado, codigo_normalizado, estado, vigente_desde, vigente_hasta, evidencia_sucursal_id, evidencia_documento_id, nodo_origen) · UK(E, sistema, codigo_normalizado) · (E, animal_id) → animal · (E, evidencia_sucursal_id, evidencia_documento_id) → documento

### Operaciones y contratos (local del dueño)
- operacion(<u>E, S, id</u>, tipo, folio, parte_id, predio_origen_id, predio_destino_id, moneda, estado, estado_entrega, numero_version_aceptada, fecha_operacion, version_lock, nodo_origen, creado_por, creado_en, confirmada_en) · UK(E,S,tipo,folio) · UK(E,S,id,tipo) · (E,S) → sucursal · (E,parte_id) → parte · (E,predio_*) → predio · (E,S,id,numero_version_aceptada) → contrato_version (DEFERRABLE)
- folio_contador(<u>E, S, tipo, anio</u>, ultimo) — soporte técnico
- lote_operacion(<u>E, S, operacion_id, numero_lote</u>, descripcion, nodo_origen) · (E,S,operacion_id) → operacion
- contrato_version(<u>E, S, operacion_id, numero_version</u>, estado, politica_redondeo, requiere_recepcion, documento_id, aceptada_por, aceptada_en, nodo_origen) · (E,S,operacion_id) → operacion · (E,S,documento_id) → documento
- condicion_lote(<u>E, S, operacion_id, numero_version, numero_lote</u>, unidad_precio, precio_unitario, base_pesaje, pesaje_base_id, deduccion_pct, cargos_pactados, bonificaciones_pactadas, nodo_origen) · (E,S,operacion_id,numero_version) → contrato_version · (E,S,operacion_id,numero_lote) → lote_operacion · (E,S,pesaje_base_id) → pesaje

### Inventario (local del dueño)
- seleccion_compra(<u>E, S, operacion_id, numero_lote, animal_id</u>, tipo_operacion='COMPRA', nodo_origen) · UK(E,S,operacion_id,animal_id) · (E,S,operacion_id,numero_lote) → lote_operacion · (E,S,operacion_id,tipo_operacion) → operacion(E,S,id,tipo) · (E,S,animal_id) → animal(E,sede_operadora_id,id)
- posicion_inventario(<u>E, S, id</u>, animal_id, numero_ciclo, compra_operacion_id, compra_numero_lote, estado, motivo_baja, abierta_en, cerrada_en, nodo_origen) · UK(E,S,animal_id,numero_ciclo) · UK(E,S,compra_operacion_id,compra_numero_lote,animal_id) · (E,S,compra_operacion_id,compra_numero_lote,animal_id) → seleccion_compra · (E,S,animal_id) → animal(E,sede_operadora_id,id) · UNIQUE parcial(E, animal_id) WHERE estado IN ('PENDIENTE_RECEPCION','DISPONIBLE','VENDIDA_PENDIENTE_ENTREGA')
- seleccion_venta(<u>E, S, operacion_id, numero_lote, posicion_id</u>, tipo_operacion='VENTA', nodo_origen) · UK(E,S,operacion_id,posicion_id) · → lote_operacion · → operacion(E,S,id,tipo) · (E,S,posicion_id) → posicion_inventario
- reserva_venta(<u>E, S, id</u>, operacion_id, numero_lote, posicion_id, estado, creada_en, vence_en, cerrada_en, nodo_origen) · (E,S,operacion_id,numero_lote,posicion_id) → seleccion_venta · UNIQUE parcial(E,S,posicion_id) WHERE estado='ACTIVA'
- movimiento_inventario(<u>E, S, id</u>, posicion_id, operacion_id, tipo, ocurrido_en, predio_id, custodio_parte_id, documento_id, reverso_de_id, registrado_por, nodo_origen) · → posicion_inventario · → operacion · → predio · → parte · → documento · reverso_de_id UNIQUE → movimiento_inventario

### Pesajes y evidencia (local del dueño; evidencia de identidad en A)
- pesaje(<u>E, S, id</u>, operacion_id, numero_lote, modo, bruto_kg, tara_kg, neto_kg, ticket_folio, bascula, pesado_en, documento_id, estado, fuente, corrige_a_id, aprobado_por, aprobado_en, nodo_origen) · → lote_operacion · → documento · corrige_a_id UNIQUE → pesaje
- pesaje_animal(<u>E, S, pesaje_id, animal_id</u>, peso_individual_kg, nodo_origen) · → pesaje · (E,S,animal_id) → animal(E,sede_operadora_id,id)
- documento(<u>E, S, id</u>, tipo_documental, clave_almacenamiento, sha256, tamano_bytes, mime, version, documento_previo_id, emisor, folio, fecha_emision, vigente_hasta, origen_texto, destino_texto, finalidad, es_sintetico, nodo_origen, subido_por, subido_en) · UK(clave_almacenamiento) · documento_previo_id UNIQUE → documento
- operacion_documento(<u>E, S, operacion_id, documento_id</u>, rol, nodo_origen) · → operacion · → documento
- revision_administrativa(<u>E, S, id</u>, operacion_id, identificacion_id, criterio, resultado, revision_anterior_id, responsable_id, revisado_en, nodo_origen) · CHECK num_nonnulls(operacion_id, identificacion_id)=1 · (E,S,operacion_id) → operacion · (E,identificacion_id) → animal_identificacion
- revision_documento(<u>E, S, revision_id, documento_id</u>, resultado, observacion, nodo_origen) · → revision_administrativa · → documento

### Liquidaciones, costos y periodos (local del dueño)
- periodo_cierre(<u>E, S, id</u>, desde, hasta, estado, version_lock, nodo_origen) · EXCLUDE gist (E =, S =, daterange(desde,hasta,'[]') &&)
- cierre_periodo_version(<u>E, S, periodo_id, numero_version</u>, tipo, actor_id, motivo, corte_en, hash_conciliacion, totales, nodo_origen) · → periodo_cierre
- liquidacion(<u>E, S, id</u>, operacion_id, numero_version, direccion, total, snapshot_contraparte_nombre, snapshot_contraparte_rfc, snapshot_condiciones, vence_el, periodo_id, confirmada_por, confirmada_en, nodo_origen) · UK(E,S,operacion_id) · (E,S,operacion_id,numero_version) → contrato_version · → periodo_cierre
- concepto_liquidacion(<u>E, S, liquidacion_id, numero_concepto</u>, tipo, descripcion, numero_lote, cantidad, unidad, precio_unitario, importe, pesaje_id, nodo_origen) · → liquidacion · → pesaje
- ajuste_liquidacion(<u>E, S, id</u>, liquidacion_id, naturaleza, monto, motivo, fuente, documento_id, revierte_ajuste_id, periodo_id, registrado_por, registrado_en, nodo_origen) · revierte_ajuste_id UNIQUE → ajuste_liquidacion
- gasto_operacion(<u>E, S, id</u>, operacion_id, naturaleza, clasificacion, importe, concepto, proveedor_parte_id, referencia_origen, documento_id, bonifica_gasto_id, estado, fecha_economica, aprobado_por, aprobado_en, snapshot_fuente_externa, nodo_origen) · UK parcial(E,S,proveedor_parte_id,referencia_origen) · → operacion · → parte · bonifica_gasto_id → gasto_operacion
- asignacion_costo(<u>E, S, id</u>, posicion_id, fuente_liquidacion_id, fuente_numero_concepto, fuente_gasto_id, fuente_ajuste_id, metodo, base_valor, importe, lote_reparto_id, periodo_id, nodo_origen) · CHECK XOR · → posicion · (E,S,fuente_liquidacion_id,fuente_numero_concepto) → concepto_liquidacion · → gasto_operacion · → ajuste_liquidacion
- asiento_valoracion(<u>E, S, id</u>, posicion_id, periodo_id, clase, sentido, importe, delta_inventario*, delta_costo_venta*, delta_perdida*, asignacion_id, operacion_id, fecha_economica, registrado_en, nodo_origen) · (* columnas generadas a partir de clase/sentido/importe)

### Pagos (local del dueño)
- pago(<u>E, S, id</u>, parte_id, tipo, moneda, importe, metodo, referencia, recibido_el, estado, pago_origen_id, documento_id, registrado_por, nodo_origen) · → parte · pago_origen_id → pago
- aplicacion_pago(<u>E, S, id</u>, pago_id, liquidacion_id, importe, naturaleza, reverso_de_id, aplicada_en, registrado_por, nodo_origen) · reverso_de_id UNIQUE → aplicacion_pago · CHECK (naturaleza='REVERSO') = (reverso_de_id IS NOT NULL)

### Auditoría, integración y soporte técnico
- auditoria_evento(<u>E, S, id</u>, ocurrido_en, actor_id, comando, correlation_id, nodo_origen, entidad, entidad_id, cambio)
- evento_outbox(<u>E, S, id</u>, tipo_evento, version_payload, payload, nodo_origen, propietario_despacho, creado_en)
- mensaje_inbox(<u>consumidor, fuente_id, event_id</u>, empresa_id, sucursal_id, recibido_en, resultado) — local
- clave_idempotencia(<u>E, S, principal_id, comando, clave</u>, hash_peticion, estado, resultado, creada_en, expira_en) — local
- infra.nodo_config(<u>nodo</u>, empresa_id, descripcion) — local, no replicada, sin privilegios de escritura para la app
- infra.entrega_outbox(<u>evento_id, destino</u>, intentos, proximo_intento, confirmado_en, ultimo_error) — local
- infra.importacion_fuente(<u>id</u>, empresa_id, sucursal_id, fuente, corte_en, sha256, filas_leidas, filas_error, actor_id, creado_en) · UK(empresa_id, fuente, sha256) — local

## 3. Cambios respecto al catálogo candidato (ENT-01..41)
| Cambio | Motivo |
|---|---|
| `nodo_origen` en todas las tablas replicadas | Guardas de propietario y despacho (DEC-07) |
| `folio_contador` añadida (soporte) | Folio interno por E/S/tipo/año bajo lock; puede tener huecos, no es fiscal |
| `posicion_inventario.estado` sin RESERVADA; con PENDIENTE_RECEPCION, CERRADA_VENTA, BAJA | DEC-01..03 |
| `animal.situacion` | DEC-04 |
| `pago.tipo` incluye REEMBOLSO con `pago_origen_id` | Reembolso como dinero real (§8.3) |
| `asiento_valoracion` con deltas generados | Signo derivado de la clase |
| `gasto_operacion.snapshot_fuente_externa` (jsonb) | RN-042: tarifa FDW aceptada |
