# Diccionario de datos

Convenciones comunes (no se repiten por tabla):
- `empresa_id uuid NOT NULL`, `sucursal_id uuid NOT NULL` en tablas locales; `id uuid NOT NULL DEFAULT uuidv7()`.
- `nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B'))`, lo deriva el comando; trigger `trg_guarda_propietario` rechaza INSERT/UPDATE cuando `nodo_origen` ≠ `infra.nodo_config.nodo` (no corre en apply porque `session_replication_role = replica`).
- Importes `numeric(18,2)`, kg `numeric(14,3)`, tarifas `numeric(14,4)`, tasas `numeric(9,6)`; todos con `CHECK (x NOT IN ('NaN','Infinity','-Infinity'))` como defensa explícita (comportamiento de NaN/∞ con typmod a verificar en TASK-A-009 con prueba negativa).
- Instantes `timestamptz`; fechas civiles `date`; presentación en America/Mexico_City.
- Hechos comprometidos: `ON UPDATE RESTRICT ON DELETE RESTRICT`; la app no tiene privilegio DELETE en tablas de hechos.
- Sensibilidad: **P** personal (LFPDPPP [F10]), **C** comercial confidencial, **T** técnica, **S** secreta.
- Replicación: **A→B** maestros originados en A; **L↔** local del dueño (A→B y B→A según nodo_origen); **local** no se publica.

---
## ENT-01 empresa
Propósito: cliente del SaaS; raíz del aislamiento (RN-001). Dueño: A · Replicación A→B · Sensibilidad C.
| Columna | Tipo | Nulo | Default | Dominio / nota |
|---|---|---|---|---|
| id | uuid | no | uuidv7() | PK |
| razon_social | varchar(200) | no | | |
| rfc | varchar(13) | sí | | P/C |
| estado | varchar(12) | no | 'ACTIVA' | ACTIVA, SUSPENDIDA |
| creado_en | timestamptz | no | now() | |
Válido: `('Acopio Demo SA', NULL)`. Rechazado: estado 'BORRADA'.

## ENT-02 sucursal
Propósito: sede y su nodo dueño (RN-004, RN-040). PK(E,id); UK(E,codigo). Dueño A · A→B · C.
| Columna | Tipo | Nulo | Default | Nota |
|---|---|---|---|---|
| codigo | varchar(10) | no | | `^[A-Z0-9-]+$` |
| nombre | varchar(120) | no | | |
| nodo_dueno | char(1) | no | | A, B; inmutable (trigger) |
| zona_horaria | varchar(40) | no | 'America/Mexico_City' | |
Índices: PK, UK. Válido: (E,'CEN','A'). Rechazado: dos sedes con código 'CEN' en la misma empresa.

## ENT-03 parte
Propósito: contraparte que compra y/o vende (RN-010). PK(E,id); UK parcial(E,rfc). A · A→B · **P**.
| Columna | Tipo | Nulo | Default | Nota |
|---|---|---|---|---|
| tipo_persona | varchar(6) | no | | FISICA, MORAL |
| nombre | varchar(200) | no | | |
| rfc | varchar(13) | sí | | normalizado mayúsculas |
| telefono | varchar(20) | sí | | P |
| es_sintetico | boolean | no | false | RN-045 |
Índices: `(E, lower(nombre))` búsqueda. Rechazado: mismo RFC dos veces en la empresa.

## ENT-04 predio
Propósito: origen/destino/custodia declarados. PK(E,id); FK(E,parte_responsable_id). A · A→B · C/P.
Columnas: nombre varchar(160) NOT NULL; clave_upp_declarada varchar(40) NULL (texto declarado, no certificado); municipio varchar(80); entidad_federativa varchar(40); parte_responsable_id uuid NULL.
Rechazado: parte_responsable_id de otra empresa (FK compuesta falla, TEST-14).

## ENT-05 usuario
Propósito: usuario del producto (no rol PostgreSQL). PK(E,id); UK(E,login_normalizado). A · A→B · **S** (hash).
Columnas: login_normalizado varchar(80) NOT NULL (`lower(trim())`); nombre varchar(120); hash_contrasena varchar(255) NOT NULL (formato `{bcrypt}`/`{argon2}` de Spring Security DelegatingPasswordEncoder); estado varchar(10) DEFAULT 'ACTIVO' (ACTIVO, BLOQUEADO); creado_en.
Nunca se loguea ni se indexa en el grafo el hash.

## ENT-06 rol_aplicacion
PK(codigo varchar(12)); descripcion. Valores: ADMIN, OPERADOR, CAJA, AUDITOR. A→B · T.

## ENT-07 membresia_usuario
PK(E,S,usuario_id,rol_codigo); vigente boolean DEFAULT true. Autoriza por sede (RN-001). A · A→B · T.
Índice: `(E, usuario_id) WHERE vigente`. Rechazado: rol inexistente.

## ENT-08 animal
Propósito: identidad permanente (RN-002, RN-004). PK(E,id); UK(E,sede_operadora_id,id). A · A→B · C.
| Columna | Tipo | Nulo | Default | Nota |
|---|---|---|---|---|
| sede_operadora_id | uuid | no | | FK (E,·) → sucursal; inmutable (trigger) |
| sexo | char(1) | no | | M, H |
| fecha_nacimiento_declarada | date | sí | | declarada |
| raza_declarada | varchar(60) | sí | | |
| situacion | varchar(24) | no | 'VIGENTE' | VIGENTE, IDENTIDAD_EN_REVISION, MUERTO (DEC-04) |
| creado_en | timestamptz | no | now() | |
Rechazado: `UPDATE animal SET sede_operadora_id = …` (BV010).

## ENT-36 animal_identificacion
Propósito: códigos oficiales/internos con historia (RN-003). PK(E,id); UK(E,sistema,codigo_normalizado). A · A→B · C.
| Columna | Tipo | Nulo | Nota |
|---|---|---|---|
| animal_id | uuid | no | FK (E,·) → animal |
| sistema | varchar(10) | no | SINIIGA, SINIDA, INTERNO, OTRO |
| codigo_declarado | varchar(40) | no | tal como se capturó |
| codigo_normalizado | varchar(40) | no | `regexp_replace(upper(codigo),'[ -]','','g'); INTERNO admite ASCII alfanumérico, espacio/guion; rechaza vacío o caracteres fuera de política` |
| estado | varchar(12) | no | VIGENTE, INACTIVA, EN_REVISION |
| vigente_desde / vigente_hasta | date | no / sí | CHECK hasta ≥ desde |
| evidencia_sucursal_id, evidencia_documento_id | uuid | sí | FK documento (ambas o ninguna) |
Índice parcial: UNIQUE(E, animal_id, sistema) WHERE estado='VIGENTE'. Rechazado: mismo código normalizado en otro animal (TEST-13).

## ENT-09 operacion
Propósito: compra o venta por cuenta propia (RN-009, RN-010). PK(E,S,id); UK(E,S,tipo,folio); UK(E,S,id,tipo). Dueño: nodo de la sede · L↔ · C.
| Columna | Tipo | Nulo | Default | Nota |
|---|---|---|---|---|
| tipo | varchar(6) | no | | COMPRA, VENTA; inmutable |
| folio | varchar(20) | no | | `C-2026-000123`; de folio_contador; no fiscal |
| parte_id | uuid | no | | → parte |
| predio_origen_id / predio_destino_id | uuid | sí | | → predio |
| moneda | char(3) | no | 'MXN' | CHECK = 'MXN' en MVP |
| estado | varchar(12) | no | 'BORRADOR' | BORRADOR, ACORDADA, CONFIRMADA, CANCELADA, ANULADA |
| estado_entrega | varchar(10) | no | 'PENDIENTE' | PENDIENTE, PARCIAL, COMPLETA (mantenido por comando de movimientos) |
| numero_version_aceptada | smallint | sí | | NOT NULL si CONFIRMADA (CHECK) |
| fecha_operacion | date | no | | |
| version_lock | integer | no | 0 | concurrencia optimista de borrador |
| creado_por / creado_en / confirmada_en | uuid / timestamptz / timestamptz | no/no/sí | | |
Índices: `(E,S,estado,fecha_operacion)` bandeja; `(E,parte_id)` historial de contraparte. Rechazado: tipo 'CONSIGNA'.

## ENT-10 lote_operacion
PK(E,S,operacion_id,numero_lote smallint CHECK > 0); descripcion varchar(120). Débil. L↔. Editable sólo si la operación está en BORRADOR (trigger).

## ENT-11 seleccion_compra
PK(E,S,operacion_id,numero_lote,animal_id); UK(E,S,operacion_id,animal_id); `tipo_operacion varchar(6) NOT NULL DEFAULT 'COMPRA' CHECK (= 'COMPRA')`. FKs a lote, a operacion(E,S,id,tipo) y a animal(E,sede_operadora_id,id). L↔.
Rechazado: animal de la sede A en compra de sede B (FK falla, RN-009); mismo animal en dos lotes de la misma compra (UK).

## ENT-12 seleccion_venta
Igual que ENT-11 con `posicion_id` y `tipo_operacion='VENTA'`; UK(E,S,operacion_id,posicion_id). L↔.

## ENT-13 posicion_inventario
Propósito: ciclo de inventario (RN-005, RN-006). PK(E,S,id). L↔ · C.
| Columna | Tipo | Nulo | Nota |
|---|---|---|---|
| animal_id | uuid | no | → animal(E,sede_operadora_id,id) |
| numero_ciclo | smallint | no | > 0; max+1 por animal |
| compra_operacion_id, compra_numero_lote | uuid, smallint | no | → seleccion_compra (con animal_id) |
| estado | varchar(26) | no | PENDIENTE_RECEPCION, DISPONIBLE, VENDIDA_PENDIENTE_ENTREGA, CERRADA_VENTA, BAJA |
| motivo_baja | varchar(10) | sí | PERDIDA, MUERTE; NOT NULL ⇔ estado = BAJA |
| abierta_en / cerrada_en | timestamptz | no / sí | cerrada_en NOT NULL ⇔ estado terminal |
Índices: UNIQUE parcial `(E, animal_id) WHERE estado IN (activos)`; `(E,S,estado)` inventario disponible. Sin INSERT/UPDATE directos de la app (sólo comandos). Rechazado: segunda posición activa del mismo animal (TEST-05).

## ENT-14 movimiento_inventario
Hecho físico inmutable (RN-020). Columnas: posicion_id NOT NULL; operacion_id NULL; tipo varchar(12) (RECEPCION, ENTREGA, BAJA, REVERSO); ocurrido_en timestamptz; predio_id, custodio_parte_id, documento_id NULL; reverso_de_id UNIQUE NULL; registrado_por. Índice `(E,S,posicion_id, ocurrido_en)`. L↔.

## ENT-15 reserva_venta
Columnas: operacion_id, numero_lote, posicion_id (→ seleccion_venta); estado varchar(10) (ACTIVA, CONSUMIDA, LIBERADA, EXPIRADA); creada_en; vence_en timestamptz NOT NULL CHECK > creada_en; cerrada_en NULL. Índice UNIQUE parcial `(E,S,posicion_id) WHERE estado='ACTIVA'` (RN-018); `(E,S,vence_en) WHERE estado='ACTIVA'` para el expirador. L↔.

## ENT-16 contrato_version
PK(E,S,operacion_id,numero_version smallint > 0). estado (PROPUESTA, ACEPTADA, SUPERADA); politica_redondeo varchar(12) DEFAULT 'HALF_UP_2'; requiere_recepcion boolean DEFAULT false; documento_id NULL; aceptada_por/aceptada_en NULL. Inmutable una vez ACEPTADA (RN-011). Pueden conservarse varias versiones ACEPTADAS históricas: `operacion.numero_version_aceptada` identifica la que referencia la operación. La restricción parcial propuesta inicialmente para permitir sólo una ACEPTADA no existe en el DDL vigente de `V1__esquema.sql`; la PK distingue cada versión sin modificar las aceptadas anteriores.

## ENT-17 condicion_lote
| Columna | Tipo | Nulo | Default | Nota |
|---|---|---|---|---|
| unidad_precio | varchar(6) | no | | KG, CABEZA |
| precio_unitario | numeric(14,4) | no | | > 0 |
| base_pesaje | varchar(10) | no | 'NINGUNA' | NINGUNA (por cabeza), PESAJE |
| pesaje_base_id | uuid | sí | | NOT NULL ⇔ base_pesaje = 'PESAJE' |
| deduccion_pct | numeric(9,6) | no | 0 | 0 ≤ x < 100; sólo pactada (RN-015) |
| cargos_pactados / bonificaciones_pactadas | numeric(18,2) | no | 0 | ≥ 0 |
Rechazado: unidad KG sin pesaje base.

## ENT-18 pesaje
| Columna | Tipo | Nulo | Nota |
|---|---|---|---|
| operacion_id, numero_lote | uuid, smallint | no | → lote_operacion |
| modo | varchar(14) | no | BRUTO_TARA, NETO_REPORTADO |
| bruto_kg, tara_kg | numeric(14,3) | sí | NOT NULL ⇔ BRUTO_TARA; tara ≤ bruto |
| neto_kg | numeric(14,3) | no | > 0; = bruto − tara si BRUTO_TARA |
| ticket_folio | varchar(40) | sí | |
| bascula | varchar(80) | sí | descripción declarada |
| pesado_en | timestamptz | no | |
| estado | varchar(10) | no | PROPUESTA, APROBADO, CORREGIDO |
| fuente | varchar(8) | no | MANUAL, CSV, OCR, FDW (RN-016) |
| corrige_a_id | uuid | sí | UNIQUE → pesaje |
Rechazado: bruto 5,000, tara 6,000 (TEST); NETO_REPORTADO con bruto informado.

## ENT-19 pesaje_animal
PK(E,S,pesaje_id,animal_id); peso_individual_kg numeric(14,3) NULL (> 0 si existe; sólo medido, RN-013). Inmutable tras APROBADO.

## ENT-20 gasto_operacion
| Columna | Tipo | Nulo | Nota |
|---|---|---|---|
| operacion_id | uuid | no | |
| naturaleza | varchar(12) | no | COSTO, BONIFICACION |
| clasificacion | varchar(14) | no | CAPITALIZABLE, DIRECTO_VENTA, OTRO (RN-025) |
| importe | numeric(18,2) | no | > 0 (signo derivado de naturaleza) |
| concepto | varchar(160) | no | |
| proveedor_parte_id | uuid | sí | |
| referencia_origen | varchar(60) | sí | UK parcial con proveedor: detecta duplicados |
| bonifica_gasto_id | uuid | sí | NOT NULL ⇔ BONIFICACION |
| estado | varchar(10) | no | BORRADOR, APROBADO |
| fecha_economica | date | no | |
| snapshot_fuente_externa | jsonb | sí | tarifa FDW aceptada: fuente, ref, fecha, unidad, hash (RN-042) |

## ENT-21 asignacion_costo
Columnas: posicion_id; **exactamente una** de (fuente_liquidacion_id + fuente_numero_concepto) / fuente_gasto_id / fuente_ajuste_id (`CHECK (num_nonnulls(fuente_liquidacion_id, fuente_gasto_id, fuente_ajuste_id) = 1)`); metodo (IMPORTE_INDIVIDUAL, POR_CABEZA, POR_PESO_MEDIDO); base_valor numeric(14,3); importe numeric(18,2) firmado (≠ 0); lote_reparto_id uuid (agrupa un reparto); periodo_id. Índice `(E,S,lote_reparto_id)` para verificar Σ = fuente.

## ENT-22 liquidacion
| Columna | Tipo | Nulo | Nota |
|---|---|---|---|
| operacion_id | uuid | no | UK(E,S,operacion_id) principal |
| numero_version | smallint | no | versión aceptada |
| direccion | varchar(10) | no | POR_PAGAR (compra), POR_COBRAR (venta) |
| total | numeric(18,2) | no | ≥ 0; = Σ conceptos (validado en comando) |
| snapshot_contraparte_nombre / _rfc | varchar | no / sí | RN-024 |
| snapshot_condiciones | jsonb | no | condiciones aceptadas tal cual |
| vence_el | date | sí | cartera vencida |
| periodo_id | uuid | no | periodo de reconocimiento |
| confirmada_por / confirmada_en | | no | |
Inmutable (trigger BV016). Índice `(E,S,direccion,vence_el)` cartera.

## ENT-23 concepto_liquidacion
PK(E,S,liquidacion_id,numero_concepto smallint). tipo (BASE, CARGO, BONIFICACION, DEDUCCION); descripcion; numero_lote NULL; cantidad numeric(14,3); unidad (KG, CABEZA, MXN); precio_unitario numeric(14,4) NULL; importe numeric(18,2) firmado (negativo para BONIFICACION/DEDUCCION, CHECK por tipo); pesaje_id NULL. Inmutable.

## ENT-24 ajuste_liquidacion
naturaleza (CARGO, ABONO); monto numeric(18,2) > 0; motivo varchar(200) NOT NULL; fuente (PRECIO_GANADO, BONIFICACION_COMERCIAL, ANULACION, OTRO); documento_id NULL; revierte_ajuste_id UNIQUE NULL; periodo_id NOT NULL; fecha_reconocimiento date NOT NULL dentro del periodo abierto; registrado_por/en.

## ENT-25 pago
| Columna | Tipo | Nulo | Nota |
|---|---|---|---|
| parte_id | uuid | no | |
| tipo | varchar(10) | no | COBRO (entra), PAGO (sale); naturaleza separada NORMAL/REEMBOLSO |
| moneda | char(3) | no | MXN |
| importe | numeric(18,2) | no | > 0 |
| metodo | varchar(14) | no | TRANSFERENCIA, EFECTIVO, CHEQUE, OTRO |
| referencia | varchar(60) | sí | |
| recibido_el | date | no | |
| estado | varchar(10) | no | REGISTRADO, VALIDADO, REVERTIDO |
| naturaleza | varchar(10) | no | NORMAL / REEMBOLSO; no sustituye dirección COBRO/PAGO |
| periodo_id | uuid | sí | NULL en registro; obligatorio al validar y para reembolso |
| fecha_reconocimiento | date | sí | NULL en registro; dentro del periodo al validar |
| pago_origen_id | uuid | sí | NOT NULL ⇔ naturaleza REEMBOLSO |
Rechazado: importe 0; REEMBOLSO sin origen.

## ENT-26 aplicacion_pago
pago_id, liquidacion_id NOT NULL; importe numeric(18,2) > 0; naturaleza (APLICACION, REVERSO); reverso_de_id UNIQUE NULL; aplicada_en; registrado_por; periodo_id uuid y fecha_reconocimiento date NOT NULL. El registro de pago no cambia cartera; validación/aplicación/reverso/reembolso identifican reconocimiento explícito. Índices `(E,S,liquidacion_id)`, `(E,S,pago_id)`.

## ENT-27 documento
| Columna | Tipo | Nulo | Nota |
|---|---|---|---|
| tipo_documental | varchar(24) | no | TICKET_BASCULA, CONTRATO, GUIA_MOVILIZACION, COMPROBANTE_PAGO, IDENTIFICACION, OTRO |
| clave_almacenamiento | varchar(80) | no | aleatoria; UK; nunca ruta del cliente |
| sha256 | char(64) | no | `^[0-9a-f]{64}$` |
| tamano_bytes | bigint | no | 1..20 MiB |
| mime | varchar(60) | no | application/pdf, image/jpeg, image/png |
| version | smallint | no | 1 + versión previa |
| documento_previo_id | uuid | sí | UNIQUE |
| emisor, folio, fecha_emision, vigente_hasta, origen_texto, destino_texto, finalidad | varios | sí | según tipo (§4.2) |
| es_sintetico | boolean | no | RN-045 |
Sensibilidad C/P. Bytes fuera de la BD (DocumentStorage).

## ENT-28 operacion_documento
PK(E,S,operacion_id,documento_id); rol varchar(16).

## ENT-29 auditoria_evento
ocurrido_en; actor_id NULL; comando varchar(60); correlation_id uuid; entidad varchar(40); entidad_id uuid; cambio jsonb (sólo campos pertinentes, sin secretos). Insertado por el comando en el nodo origen; replicado como dato; nunca generado por apply. Índice `(E,S,entidad,entidad_id)`.

## ENT-30 evento_outbox
tipo_evento varchar(60); version_payload smallint; payload jsonb; propietario_despacho char(1); creado_en. Sólo `propietario_despacho = nodo local` se despacha.

## ENT-31 mensaje_inbox (local)
PK(consumidor varchar(40), fuente_id varchar(40), event_id uuid); empresa_id, sucursal_id NULL; recibido_en; resultado varchar(10).

## ENT-32 clave_idempotencia (local)
PK(E,S,principal_id,comando,clave varchar(80)); hash_peticion char(64); estado (EN_CURSO, COMPLETADA); resultado jsonb; creada_en; deduplicación conservada mientras existan los hechos financieros; no expira a los 30 días.

## ENT-33 infra.nodo_config (local)
nodo char(1) PK CHECK IN ('A','B'); empresa_id; descripcion. Una fila. App sólo SELECT.

## ENT-34 infra.entrega_outbox (local)
PK(evento_id, destino); intentos int DEFAULT 0; proximo_intento timestamptz; confirmado_en NULL; ultimo_error text NULL.

## ENT-35 infra.importacion_fuente (local)
fuente varchar(20) (CSV, OCR, FDW); corte_en; sha256; filas_leidas, filas_error int; actor_id. UK(empresa_id, fuente, sha256) evita reimportar el mismo archivo.

## ENT-37 periodo_cierre
desde, hasta date (hasta ≥ desde); estado (ABIERTO, CERRADO); version_lock. `EXCLUDE USING gist (empresa_id WITH =, sucursal_id WITH =, daterange(desde, hasta, '[]') WITH &&)` (extensión btree_gist, justificada: no solapamiento declarativo).

## ENT-38 cierre_periodo_version
PK(E,S,periodo_id,numero_version); tipo (CIERRE, REAPERTURA); actor_id; motivo; corte_en; hash_conciliacion char(64); totales jsonb (inventario, costo de venta, pérdida, cartera). Inmutable.

## ENT-39 asiento_valoracion
clase (ADQUISICION, VENTA, COSTO_TARDIO_INVENTARIO, COSTO_TARDIO_VENTA, COSTO_TARDIO_PERDIDA, BAJA, ANULACION_VENTA); sentido (AUMENTO, DISMINUCION) — DISMINUCION sólo para bonificaciones de costo tardío; importe numeric(18,2) > 0; columnas `GENERATED ALWAYS AS (...) STORED`: delta_inventario, delta_costo_venta, delta_perdida según la tabla de `states-and-calculations.md` §3; asignacion_id, operacion_id NULL; fecha_economica; periodo_id. Índice `(E,S,posicion_id)`.

## ENT-40 revision_administrativa
operacion_id XOR identificacion_id; criterio varchar(200); resultado (SIN_OBSERVACIONES, CON_OBSERVACIONES, RECHAZADA); revision_anterior_id NULL; responsable_id; revisado_en. La UI rotula "Revisión administrativa registrada", nunca "autorizado".

## ENT-41 revision_documento
PK(E,S,revision_id,documento_id); resultado; observacion varchar(500).

## Soporte: folio_contador (local del dueño, L↔)
PK(E,S,tipo,anio); ultimo integer. Bloqueado FOR UPDATE al asignar folio.

## Concordancia física durante implementación

Autoridad ejecutable: `db/migrations/`. Se incorporaron `periodo_id`/`fecha_reconocimiento` en gasto, pago y aplicación, y fecha de reconocimiento en ajuste (ADR-015). Pago admite ambos nulos mientras está REGISTRADO; validación exige ambos y comprueba periodo abierto. Gasto y aplicación los conservan no nulos. Son tres FK de periodo adicionales: metadata 42 tablas/83 FK. Sesiones JDBC son dos tablas técnicas locales, fuera del MER de negocio y de réplica.

`python3 tools/esquema/comparar_catalogo.py` contrasta tipos, columnas, nullabilidad, PK, UK declaradas y FK contra PostgreSQL. No sustituye pruebas de CHECK, índices parciales, triggers, permisos ni revisión conceptual.
