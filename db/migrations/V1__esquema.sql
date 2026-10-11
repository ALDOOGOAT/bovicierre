-- 42 tablas / 83 FK; PostgreSQL 18. Los defaults no sustituyen validaciones de comandos.

CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA public;

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;

CREATE SCHEMA IF NOT EXISTS bovi AUTHORIZATION bovi_owner;

CREATE SCHEMA IF NOT EXISTS infra AUTHORIZATION bovi_owner;

ALTER SCHEMA infra OWNER TO bovi_owner;

GRANT USAGE ON SCHEMA public TO bovi_owner;

SET search_path = bovi, infra, public;

SET ROLE bovi_owner;

CREATE TABLE bovi.empresa (
    id uuid DEFAULT uuidv7() NOT NULL,
    razon_social varchar(200) NOT NULL,
    rfc varchar(13),
    estado varchar(12) NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    creado_en timestamptz DEFAULT now() NOT NULL,
    PRIMARY KEY (id),
    CHECK (estado IN ('ACTIVA','SUSPENDIDA'))
);

CREATE TABLE bovi.sucursal (
    empresa_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    codigo varchar(10) NOT NULL,
    nombre varchar(120) NOT NULL,
    nodo_dueno char(1) NOT NULL,
    zona_horaria varchar(40) NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, id),
    UNIQUE (empresa_id, codigo),
    CHECK (nodo_dueno IN ('A','B')),
    CHECK (codigo ~ '^[A-Z0-9-]+$')
);

CREATE TABLE bovi.rol_aplicacion (
    codigo varchar(12) NOT NULL,
    descripcion varchar(80) NOT NULL,
    PRIMARY KEY (codigo),
    CHECK (codigo IN ('ADMIN','OPERADOR','CAJA','AUDITOR'))
);

CREATE TABLE bovi.usuario (
    empresa_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    login_normalizado varchar(80) NOT NULL,
    nombre varchar(120) NOT NULL,
    hash_contrasena varchar(255) NOT NULL,
    estado varchar(10) NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    creado_en timestamptz DEFAULT now() NOT NULL,
    PRIMARY KEY (empresa_id, id),
    UNIQUE (empresa_id, login_normalizado),
    CHECK (estado IN ('ACTIVO','BLOQUEADO')),
    CHECK (login_normalizado = lower(btrim(login_normalizado)))
);

CREATE TABLE bovi.membresia_usuario (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    rol_codigo varchar(12) NOT NULL,
    vigente boolean DEFAULT true NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, usuario_id, rol_codigo)
);

CREATE TABLE bovi.parte (
    empresa_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    tipo_persona varchar(6) NOT NULL,
    nombre varchar(200) NOT NULL,
    rfc varchar(13),
    telefono varchar(20),
    es_sintetico boolean DEFAULT true NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, id),
    CHECK (tipo_persona IN ('FISICA','MORAL'))
);

CREATE TABLE bovi.predio (
    empresa_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    nombre varchar(160) NOT NULL,
    clave_upp_declarada varchar(40),
    municipio varchar(80),
    entidad_federativa varchar(40),
    parte_responsable_id uuid,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, id)
);

CREATE TABLE bovi.animal (
    empresa_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    sede_operadora_id uuid NOT NULL,
    sexo char(1) NOT NULL,
    fecha_nacimiento_declarada date,
    raza_declarada varchar(60),
    situacion varchar(24) NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    creado_en timestamptz DEFAULT now() NOT NULL,
    PRIMARY KEY (empresa_id, id),
    UNIQUE (empresa_id, sede_operadora_id, id),
    CHECK (sexo IN ('M','H')),
    CHECK (situacion IN ('VIGENTE','IDENTIDAD_EN_REVISION','MUERTO'))
);

CREATE TABLE bovi.animal_identificacion (
    empresa_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    animal_id uuid NOT NULL,
    sistema varchar(10) NOT NULL,
    codigo_declarado varchar(40) NOT NULL,
    codigo_normalizado varchar(40) NOT NULL,
    estado varchar(12) NOT NULL,
    vigente_desde date NOT NULL,
    vigente_hasta date,
    evidencia_sucursal_id uuid,
    evidencia_documento_id uuid,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, id),
    UNIQUE (empresa_id, sistema, codigo_normalizado),
    CHECK (sistema IN ('SINIIGA','SINIDA','INTERNO','OTRO')),
    CHECK (estado IN ('VIGENTE','INACTIVA','EN_REVISION')),
    CHECK (vigente_hasta IS NULL OR vigente_hasta >= vigente_desde),
    CHECK ((evidencia_sucursal_id IS NULL) = (evidencia_documento_id IS NULL))
);

CREATE TABLE bovi.operacion (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    tipo varchar(6) NOT NULL,
    folio varchar(20) NOT NULL,
    parte_id uuid NOT NULL,
    predio_origen_id uuid,
    predio_destino_id uuid,
    moneda char(3) DEFAULT 'MXN' NOT NULL,
    estado varchar(12) NOT NULL,
    estado_entrega varchar(10) NOT NULL,
    numero_version_aceptada smallint,
    fecha_operacion date NOT NULL,
    version_lock integer DEFAULT 0 NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    creado_por uuid NOT NULL,
    creado_en timestamptz DEFAULT now() NOT NULL,
    confirmada_en timestamptz,
    PRIMARY KEY (empresa_id, sucursal_id, id),
    UNIQUE (empresa_id, sucursal_id, tipo, folio),
    UNIQUE (empresa_id, sucursal_id, id, tipo),
    CHECK (tipo IN ('COMPRA','VENTA')),
    CHECK (moneda = 'MXN'),
    CHECK (estado IN ('BORRADOR','ACORDADA','CONFIRMADA','CANCELADA','ANULADA')),
    CHECK (estado_entrega IN ('PENDIENTE','PARCIAL','COMPLETA')),
    CHECK (estado NOT IN ('CONFIRMADA','ANULADA') OR numero_version_aceptada IS NOT NULL),
    CHECK (version_lock >= 0)
);

CREATE TABLE bovi.folio_contador (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    tipo varchar(6) NOT NULL,
    anio smallint NOT NULL,
    ultimo integer NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, tipo, anio),
    CHECK (tipo IN ('COMPRA','VENTA')),
    CHECK (ultimo > 0)
);

CREATE TABLE bovi.lote_operacion (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    operacion_id uuid NOT NULL,
    numero_lote smallint NOT NULL,
    descripcion varchar(120),
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, operacion_id, numero_lote),
    CHECK (numero_lote > 0)
);

CREATE TABLE bovi.contrato_version (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    operacion_id uuid NOT NULL,
    numero_version smallint NOT NULL,
    estado varchar(10) NOT NULL,
    politica_redondeo varchar(12) NOT NULL,
    requiere_recepcion boolean NOT NULL,
    documento_id uuid,
    aceptada_por uuid,
    aceptada_en timestamptz,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, operacion_id, numero_version),
    CHECK (estado IN ('PROPUESTA','ACEPTADA','SUPERADA')),
    CHECK (politica_redondeo = 'HALF_UP_2'),
    CHECK (numero_version > 0)
);

CREATE TABLE bovi.condicion_lote (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    operacion_id uuid NOT NULL,
    numero_version smallint NOT NULL,
    numero_lote smallint NOT NULL,
    unidad_precio varchar(6) NOT NULL,
    precio_unitario numeric(14,4) NOT NULL CHECK (precio_unitario NOT IN ('NaN','Infinity','-Infinity')),
    base_pesaje varchar(10) NOT NULL,
    pesaje_base_id uuid,
    deduccion_pct numeric(9,6) DEFAULT 0 NOT NULL CHECK (deduccion_pct NOT IN ('NaN','Infinity','-Infinity')),
    cargos_pactados numeric(18,2) DEFAULT 0 NOT NULL CHECK (cargos_pactados NOT IN ('NaN','Infinity','-Infinity')),
    bonificaciones_pactadas numeric(18,2) DEFAULT 0 NOT NULL CHECK (bonificaciones_pactadas NOT IN ('NaN','Infinity','-Infinity')),
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, operacion_id, numero_version, numero_lote),
    CHECK (unidad_precio IN ('KG','CABEZA')),
    CHECK (precio_unitario > 0),
    CHECK (deduccion_pct >= 0 AND deduccion_pct < 100),
    CHECK (cargos_pactados >= 0 AND bonificaciones_pactadas >= 0),
    CHECK ((unidad_precio = 'KG' AND base_pesaje = 'PESAJE' AND pesaje_base_id IS NOT NULL) OR (unidad_precio = 'CABEZA' AND base_pesaje = 'NINGUNA' AND pesaje_base_id IS NULL))
);

CREATE TABLE bovi.pesaje (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    operacion_id uuid NOT NULL,
    numero_lote smallint NOT NULL,
    modo varchar(14) NOT NULL,
    bruto_kg numeric(14,3) CHECK (bruto_kg NOT IN ('NaN','Infinity','-Infinity')),
    tara_kg numeric(14,3) CHECK (tara_kg NOT IN ('NaN','Infinity','-Infinity')),
    neto_kg numeric(14,3) NOT NULL CHECK (neto_kg NOT IN ('NaN','Infinity','-Infinity')),
    ticket_folio varchar(40),
    bascula varchar(80),
    pesado_en timestamptz DEFAULT now() NOT NULL,
    documento_id uuid,
    estado varchar(10) NOT NULL,
    fuente varchar(8) NOT NULL,
    corrige_a_id uuid,
    aprobado_por uuid,
    aprobado_en timestamptz,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, id),
    CHECK (modo IN ('BRUTO_TARA','NETO_REPORTADO')),
    CHECK (neto_kg > 0),
    CHECK ((modo = 'BRUTO_TARA' AND bruto_kg IS NOT NULL AND tara_kg IS NOT NULL AND tara_kg >= 0 AND tara_kg <= bruto_kg AND neto_kg = bruto_kg - tara_kg) OR (modo = 'NETO_REPORTADO' AND bruto_kg IS NULL AND tara_kg IS NULL)),
    CHECK (estado IN ('PROPUESTA','APROBADO','CORREGIDO')),
    CHECK (fuente IN ('MANUAL','CSV','OCR','FDW'))
);

CREATE TABLE bovi.pesaje_animal (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    pesaje_id uuid NOT NULL,
    animal_id uuid NOT NULL,
    peso_individual_kg numeric(14,3) CHECK (peso_individual_kg NOT IN ('NaN','Infinity','-Infinity')),
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, pesaje_id, animal_id),
    CHECK (peso_individual_kg IS NULL OR peso_individual_kg > 0)
);

CREATE TABLE bovi.seleccion_compra (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    operacion_id uuid NOT NULL,
    numero_lote smallint NOT NULL,
    animal_id uuid NOT NULL,
    tipo_operacion varchar(6) NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, operacion_id, numero_lote, animal_id),
    UNIQUE (empresa_id, sucursal_id, operacion_id, animal_id),
    CHECK (tipo_operacion = 'COMPRA')
);

CREATE TABLE bovi.posicion_inventario (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    animal_id uuid NOT NULL,
    numero_ciclo smallint NOT NULL,
    compra_operacion_id uuid NOT NULL,
    compra_numero_lote smallint NOT NULL,
    estado varchar(26) NOT NULL,
    motivo_baja varchar(10),
    abierta_en timestamptz DEFAULT now() NOT NULL,
    cerrada_en timestamptz,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, id),
    UNIQUE (empresa_id, sucursal_id, animal_id, numero_ciclo),
    UNIQUE (empresa_id, sucursal_id, compra_operacion_id, compra_numero_lote, animal_id),
    CHECK (estado IN ('PENDIENTE_RECEPCION','DISPONIBLE','VENDIDA_PENDIENTE_ENTREGA','CERRADA_VENTA','BAJA')),
    CHECK (numero_ciclo > 0),
    CHECK ((estado = 'BAJA') = (motivo_baja IS NOT NULL)),
    CHECK (motivo_baja IS NULL OR motivo_baja IN ('PERDIDA','MUERTE')),
    CHECK ((estado IN ('BAJA','CERRADA_VENTA')) = (cerrada_en IS NOT NULL))
);

CREATE TABLE bovi.seleccion_venta (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    operacion_id uuid NOT NULL,
    numero_lote smallint NOT NULL,
    posicion_id uuid NOT NULL,
    tipo_operacion varchar(6) NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, operacion_id, numero_lote, posicion_id),
    UNIQUE (empresa_id, sucursal_id, operacion_id, posicion_id),
    CHECK (tipo_operacion = 'VENTA')
);

CREATE TABLE bovi.reserva_venta (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    operacion_id uuid NOT NULL,
    numero_lote smallint NOT NULL,
    posicion_id uuid NOT NULL,
    estado varchar(10) NOT NULL,
    creada_en timestamptz DEFAULT now() NOT NULL,
    vence_en timestamptz NOT NULL,
    cerrada_en timestamptz,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, id),
    CHECK (estado IN ('ACTIVA','CONSUMIDA','LIBERADA','EXPIRADA')),
    CHECK (vence_en > creada_en)
);

CREATE TABLE bovi.movimiento_inventario (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    posicion_id uuid NOT NULL,
    operacion_id uuid,
    tipo varchar(12) NOT NULL,
    ocurrido_en timestamptz DEFAULT now() NOT NULL,
    predio_id uuid,
    custodio_parte_id uuid,
    documento_id uuid,
    reverso_de_id uuid,
    registrado_por uuid NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, id),
    CHECK (tipo IN ('RECEPCION','ENTREGA','BAJA','REVERSO'))
);

CREATE TABLE bovi.periodo_cierre (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    desde date NOT NULL,
    hasta date NOT NULL,
    estado varchar(8) NOT NULL,
    version_lock integer DEFAULT 0 NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, id),
    CHECK (estado IN ('ABIERTO','CERRADO')),
    CHECK (desde = date_trunc('month',desde)::date AND hasta = (desde + interval '1 month' - interval '1 day')::date)
);

CREATE TABLE bovi.cierre_periodo_version (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    periodo_id uuid NOT NULL,
    numero_version smallint NOT NULL,
    tipo varchar(10) NOT NULL,
    actor_id uuid NOT NULL,
    motivo varchar(200) NOT NULL,
    corte_en timestamptz NOT NULL,
    hash_conciliacion char(64) NOT NULL,
    totales jsonb NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, periodo_id, numero_version),
    CHECK (tipo IN ('CIERRE','REAPERTURA')),
    CHECK (numero_version > 0),
    CHECK (length(btrim(motivo)) > 0)
);

CREATE TABLE bovi.liquidacion (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    operacion_id uuid NOT NULL,
    numero_version smallint NOT NULL,
    direccion varchar(10) NOT NULL,
    total numeric(18,2) NOT NULL CHECK (total NOT IN ('NaN','Infinity','-Infinity')),
    snapshot_contraparte_nombre varchar(200) NOT NULL,
    snapshot_contraparte_rfc varchar(13),
    snapshot_condiciones jsonb NOT NULL,
    vence_el date,
    periodo_id uuid NOT NULL,
    confirmada_por uuid NOT NULL,
    confirmada_en timestamptz NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, id),
    UNIQUE (empresa_id, sucursal_id, operacion_id),
    CHECK (direccion IN ('POR_PAGAR','POR_COBRAR')),
    CHECK (total >= 0)
);

CREATE TABLE bovi.concepto_liquidacion (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    liquidacion_id uuid NOT NULL,
    numero_concepto smallint NOT NULL,
    tipo varchar(12) NOT NULL,
    descripcion varchar(160) NOT NULL,
    numero_lote smallint,
    cantidad numeric(14,3) NOT NULL CHECK (cantidad NOT IN ('NaN','Infinity','-Infinity')),
    unidad varchar(6) NOT NULL,
    precio_unitario numeric(14,4) CHECK (precio_unitario NOT IN ('NaN','Infinity','-Infinity')),
    importe numeric(18,2) NOT NULL CHECK (importe NOT IN ('NaN','Infinity','-Infinity')),
    pesaje_id uuid,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, liquidacion_id, numero_concepto),
    CHECK (tipo IN ('BASE','CARGO','BONIFICACION','DEDUCCION')),
    CHECK (unidad IN ('KG','CABEZA','MXN')),
    CHECK ((tipo IN ('BASE','CARGO') AND importe >= 0) OR (tipo IN ('BONIFICACION','DEDUCCION') AND importe <= 0))
);

CREATE TABLE bovi.ajuste_liquidacion (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    liquidacion_id uuid NOT NULL,
    naturaleza varchar(6) NOT NULL,
    monto numeric(18,2) NOT NULL CHECK (monto NOT IN ('NaN','Infinity','-Infinity')),
    motivo varchar(200) NOT NULL,
    fuente varchar(24) NOT NULL,
    documento_id uuid,
    revierte_ajuste_id uuid,
    periodo_id uuid NOT NULL,
    fecha_reconocimiento date NOT NULL,
    registrado_por uuid NOT NULL,
    registrado_en timestamptz DEFAULT now() NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, id),
    CHECK (naturaleza IN ('CARGO','ABONO')),
    CHECK (monto > 0),
    CHECK (length(btrim(motivo)) > 0),
    CHECK (fuente IN ('PRECIO_GANADO','BONIFICACION_COMERCIAL','ANULACION','OTRO'))
);

CREATE TABLE bovi.gasto_operacion (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    operacion_id uuid NOT NULL,
    naturaleza varchar(12) NOT NULL,
    clasificacion varchar(14) NOT NULL,
    importe numeric(18,2) NOT NULL CHECK (importe NOT IN ('NaN','Infinity','-Infinity')),
    concepto varchar(160) NOT NULL,
    proveedor_parte_id uuid,
    referencia_origen varchar(60),
    documento_id uuid,
    bonifica_gasto_id uuid,
    estado varchar(10) NOT NULL,
    fecha_economica date NOT NULL,
    aprobado_por uuid,
    aprobado_en timestamptz,
    snapshot_fuente_externa jsonb,
    periodo_id uuid NOT NULL,
    fecha_reconocimiento date NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, id),
    CHECK (naturaleza IN ('COSTO','BONIFICACION')),
    CHECK (clasificacion IN ('CAPITALIZABLE','DIRECTO_VENTA','OTRO')),
    CHECK (importe > 0),
    CHECK (estado IN ('BORRADOR','APROBADO')),
    CHECK ((naturaleza = 'BONIFICACION') = (bonifica_gasto_id IS NOT NULL))
);

CREATE TABLE bovi.asignacion_costo (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    posicion_id uuid NOT NULL,
    fuente_liquidacion_id uuid,
    fuente_numero_concepto smallint,
    fuente_gasto_id uuid,
    fuente_ajuste_id uuid,
    metodo varchar(18) NOT NULL,
    base_valor numeric(14,3) NOT NULL CHECK (base_valor NOT IN ('NaN','Infinity','-Infinity')),
    importe numeric(18,2) NOT NULL CHECK (importe NOT IN ('NaN','Infinity','-Infinity')),
    lote_reparto_id uuid NOT NULL,
    periodo_id uuid NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, id),
    CHECK (num_nonnulls(fuente_liquidacion_id,fuente_gasto_id,fuente_ajuste_id) = 1),
    CHECK ((fuente_liquidacion_id IS NULL) = (fuente_numero_concepto IS NULL)),
    CHECK (metodo IN ('IMPORTE_INDIVIDUAL','POR_CABEZA','POR_PESO_MEDIDO')),
    CHECK (base_valor > 0),
    CHECK (importe <> 0)
);

CREATE TABLE bovi.asiento_valoracion (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    posicion_id uuid NOT NULL,
    periodo_id uuid NOT NULL,
    clase varchar(26) NOT NULL,
    sentido varchar(12) NOT NULL,
    importe numeric(18,2) NOT NULL CHECK (importe NOT IN ('NaN','Infinity','-Infinity')),
    delta_inventario numeric(18,2) GENERATED ALWAYS AS (CASE clase WHEN 'ADQUISICION' THEN importe WHEN 'VENTA' THEN -importe WHEN 'BAJA' THEN -importe WHEN 'ANULACION_VENTA' THEN importe WHEN 'COSTO_TARDIO_INVENTARIO' THEN CASE sentido WHEN 'AUMENTO' THEN importe ELSE -importe END ELSE 0 END) STORED NOT NULL CHECK (delta_inventario NOT IN ('NaN','Infinity','-Infinity')),
    delta_costo_venta numeric(18,2) GENERATED ALWAYS AS (CASE clase WHEN 'VENTA' THEN importe WHEN 'ANULACION_VENTA' THEN -importe WHEN 'COSTO_TARDIO_VENTA' THEN CASE sentido WHEN 'AUMENTO' THEN importe ELSE -importe END ELSE 0 END) STORED NOT NULL CHECK (delta_costo_venta NOT IN ('NaN','Infinity','-Infinity')),
    delta_perdida numeric(18,2) GENERATED ALWAYS AS (CASE clase WHEN 'BAJA' THEN importe WHEN 'COSTO_TARDIO_PERDIDA' THEN CASE sentido WHEN 'AUMENTO' THEN importe ELSE -importe END ELSE 0 END) STORED NOT NULL CHECK (delta_perdida NOT IN ('NaN','Infinity','-Infinity')),
    asignacion_id uuid,
    operacion_id uuid,
    fecha_economica date NOT NULL,
    registrado_en timestamptz DEFAULT now() NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, id),
    CHECK (clase IN ('ADQUISICION','VENTA','COSTO_TARDIO_INVENTARIO','COSTO_TARDIO_VENTA','COSTO_TARDIO_PERDIDA','BAJA','ANULACION_VENTA')),
    CHECK (sentido IN ('AUMENTO','DISMINUCION')),
    CHECK (sentido = 'AUMENTO' OR clase LIKE 'COSTO_TARDIO_%'),
    CHECK (importe > 0)
);

CREATE TABLE bovi.pago (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    parte_id uuid NOT NULL,
    tipo varchar(10) NOT NULL,
    moneda char(3) DEFAULT 'MXN' NOT NULL,
    importe numeric(18,2) NOT NULL CHECK (importe NOT IN ('NaN','Infinity','-Infinity')),
    metodo varchar(14) NOT NULL,
    referencia varchar(60),
    recibido_el date NOT NULL,
    estado varchar(10) NOT NULL,
    pago_origen_id uuid,
    documento_id uuid,
    registrado_por uuid NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    naturaleza varchar(10) NOT NULL,
    periodo_id uuid,
    fecha_reconocimiento date,
    PRIMARY KEY (empresa_id, sucursal_id, id),
    CHECK (tipo IN ('COBRO','PAGO')),
    CHECK (naturaleza IN ('NORMAL','REEMBOLSO')),
    CHECK (moneda = 'MXN'),
    CHECK (importe > 0),
    CHECK (metodo IN ('TRANSFERENCIA','EFECTIVO','CHEQUE','OTRO')),
    CHECK (estado IN ('REGISTRADO','VALIDADO','REVERTIDO')),
    CHECK (estado = 'REGISTRADO' OR (periodo_id IS NOT NULL AND fecha_reconocimiento IS NOT NULL)),
    CHECK ((naturaleza = 'REEMBOLSO') = (pago_origen_id IS NOT NULL))
);

CREATE TABLE bovi.aplicacion_pago (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    pago_id uuid NOT NULL,
    liquidacion_id uuid NOT NULL,
    importe numeric(18,2) NOT NULL CHECK (importe NOT IN ('NaN','Infinity','-Infinity')),
    naturaleza varchar(10) NOT NULL,
    reverso_de_id uuid,
    aplicada_en timestamptz DEFAULT now() NOT NULL,
    registrado_por uuid NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    periodo_id uuid NOT NULL,
    fecha_reconocimiento date NOT NULL,
    PRIMARY KEY (empresa_id, sucursal_id, id),
    CHECK (importe > 0),
    CHECK (naturaleza IN ('APLICACION','REVERSO')),
    CHECK ((naturaleza = 'REVERSO') = (reverso_de_id IS NOT NULL))
);

CREATE TABLE bovi.documento (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    tipo_documental varchar(24) NOT NULL,
    clave_almacenamiento varchar(80) NOT NULL,
    sha256 char(64) NOT NULL,
    tamano_bytes bigint NOT NULL,
    mime varchar(60) NOT NULL,
    version smallint NOT NULL,
    documento_previo_id uuid,
    emisor varchar(160),
    folio varchar(60),
    fecha_emision date,
    vigente_hasta date,
    origen_texto varchar(200),
    destino_texto varchar(200),
    finalidad varchar(120),
    es_sintetico boolean DEFAULT true NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    subido_por uuid NOT NULL,
    subido_en timestamptz DEFAULT now() NOT NULL,
    PRIMARY KEY (empresa_id, sucursal_id, id),
    CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (tamano_bytes BETWEEN 1 AND 20971520),
    CHECK (mime IN ('application/pdf','image/jpeg','image/png')),
    CHECK (version > 0)
);

CREATE TABLE bovi.operacion_documento (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    operacion_id uuid NOT NULL,
    documento_id uuid NOT NULL,
    rol varchar(16) NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, operacion_id, documento_id)
);

CREATE TABLE bovi.revision_administrativa (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    operacion_id uuid,
    identificacion_id uuid,
    criterio varchar(200) NOT NULL,
    resultado varchar(18) NOT NULL,
    revision_anterior_id uuid,
    responsable_id uuid NOT NULL,
    revisado_en timestamptz NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, id),
    CHECK (num_nonnulls(operacion_id,identificacion_id) = 1),
    CHECK (resultado IN ('SIN_OBSERVACIONES','CON_OBSERVACIONES','RECHAZADA'))
);

CREATE TABLE bovi.revision_documento (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    revision_id uuid NOT NULL,
    documento_id uuid NOT NULL,
    resultado varchar(18) NOT NULL,
    observacion varchar(500),
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    PRIMARY KEY (empresa_id, sucursal_id, revision_id, documento_id)
);

CREATE TABLE bovi.auditoria_evento (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    ocurrido_en timestamptz DEFAULT now() NOT NULL,
    actor_id uuid,
    comando varchar(60) NOT NULL,
    correlation_id uuid NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    entidad varchar(40) NOT NULL,
    entidad_id uuid NOT NULL,
    cambio jsonb NOT NULL,
    PRIMARY KEY (empresa_id, sucursal_id, id)
);

CREATE TABLE bovi.evento_outbox (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    id uuid DEFAULT uuidv7() NOT NULL,
    tipo_evento varchar(60) NOT NULL,
    version_payload smallint NOT NULL,
    payload jsonb NOT NULL,
    nodo_origen char(1) NOT NULL CHECK (nodo_origen IN ('A','B')),
    propietario_despacho char(1) NOT NULL,
    creado_en timestamptz DEFAULT now() NOT NULL,
    PRIMARY KEY (empresa_id, sucursal_id, id)
);

CREATE TABLE bovi.clave_idempotencia (
    empresa_id uuid NOT NULL,
    sucursal_id uuid NOT NULL,
    principal_id uuid NOT NULL,
    comando varchar(60) NOT NULL,
    clave varchar(80) NOT NULL,
    hash_peticion char(64) NOT NULL,
    estado varchar(12) NOT NULL,
    resultado jsonb,
    creada_en timestamptz DEFAULT now() NOT NULL,
    expira_en timestamptz NOT NULL,
    PRIMARY KEY (empresa_id, sucursal_id, principal_id, comando, clave),
    CHECK (estado IN ('EN_CURSO','COMPLETADA')),
    CHECK (hash_peticion ~ '^[0-9a-f]{64}$'),
    CHECK (expira_en >= creada_en + interval '30 days')
);

CREATE TABLE bovi.mensaje_inbox (
    consumidor varchar(40) NOT NULL,
    fuente_id varchar(40) NOT NULL,
    event_id uuid NOT NULL,
    empresa_id uuid,
    sucursal_id uuid,
    recibido_en timestamptz DEFAULT now() NOT NULL,
    resultado varchar(10) NOT NULL,
    PRIMARY KEY (consumidor, fuente_id, event_id)
);

CREATE TABLE infra.nodo_config (
    nodo char(1) NOT NULL,
    empresa_id uuid NOT NULL,
    descripcion varchar(80),
    PRIMARY KEY (nodo),
    CHECK (nodo IN ('A','B'))
);

CREATE TABLE infra.entrega_outbox (
    evento_id uuid NOT NULL,
    destino varchar(40) NOT NULL,
    intentos integer DEFAULT 0 NOT NULL,
    proximo_intento timestamptz,
    confirmado_en timestamptz,
    ultimo_error text,
    lease_token uuid,
    lease_vence_en timestamptz,
    PRIMARY KEY (evento_id, destino),
    CHECK (intentos >= 0)
);

CREATE TABLE infra.importacion_fuente (
    id uuid DEFAULT uuidv7() NOT NULL,
    empresa_id uuid NOT NULL,
    sucursal_id uuid,
    fuente varchar(20) NOT NULL,
    corte_en timestamptz NOT NULL,
    sha256 char(64) NOT NULL,
    filas_leidas integer NOT NULL,
    filas_error integer NOT NULL,
    actor_id uuid NOT NULL,
    creado_en timestamptz DEFAULT now() NOT NULL,
    PRIMARY KEY (id),
    CHECK (filas_leidas >= 0 AND filas_error >= 0),
    CHECK (fuente IN ('CSV','OCR','FDW'))
);

ALTER TABLE bovi.sucursal ADD CONSTRAINT fk_sucursal_1 FOREIGN KEY (empresa_id) REFERENCES bovi.empresa (id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.usuario ADD CONSTRAINT fk_usuario_1 FOREIGN KEY (empresa_id) REFERENCES bovi.empresa (id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.membresia_usuario ADD CONSTRAINT fk_membresia_usuario_1 FOREIGN KEY (empresa_id, sucursal_id) REFERENCES bovi.sucursal (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.membresia_usuario ADD CONSTRAINT fk_membresia_usuario_2 FOREIGN KEY (empresa_id, usuario_id) REFERENCES bovi.usuario (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.membresia_usuario ADD CONSTRAINT fk_membresia_usuario_3 FOREIGN KEY (rol_codigo) REFERENCES bovi.rol_aplicacion (codigo) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.parte ADD CONSTRAINT fk_parte_1 FOREIGN KEY (empresa_id) REFERENCES bovi.empresa (id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.predio ADD CONSTRAINT fk_predio_1 FOREIGN KEY (empresa_id, parte_responsable_id) REFERENCES bovi.parte (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.animal ADD CONSTRAINT fk_animal_1 FOREIGN KEY (empresa_id, sede_operadora_id) REFERENCES bovi.sucursal (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.animal_identificacion ADD CONSTRAINT fk_animal_identificacion_1 FOREIGN KEY (empresa_id, animal_id) REFERENCES bovi.animal (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.animal_identificacion ADD CONSTRAINT fk_animal_identificacion_2 FOREIGN KEY (empresa_id, evidencia_sucursal_id, evidencia_documento_id) REFERENCES bovi.documento (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.operacion ADD CONSTRAINT fk_operacion_1 FOREIGN KEY (empresa_id, sucursal_id) REFERENCES bovi.sucursal (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.operacion ADD CONSTRAINT fk_operacion_2 FOREIGN KEY (empresa_id, parte_id) REFERENCES bovi.parte (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.operacion ADD CONSTRAINT fk_operacion_3 FOREIGN KEY (empresa_id, predio_origen_id) REFERENCES bovi.predio (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.operacion ADD CONSTRAINT fk_operacion_4 FOREIGN KEY (empresa_id, predio_destino_id) REFERENCES bovi.predio (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.operacion ADD CONSTRAINT fk_operacion_5 FOREIGN KEY (empresa_id, sucursal_id, id, numero_version_aceptada) REFERENCES bovi.contrato_version (empresa_id, sucursal_id, operacion_id, numero_version) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.folio_contador ADD CONSTRAINT fk_folio_contador_1 FOREIGN KEY (empresa_id, sucursal_id) REFERENCES bovi.sucursal (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.lote_operacion ADD CONSTRAINT fk_lote_operacion_1 FOREIGN KEY (empresa_id, sucursal_id, operacion_id) REFERENCES bovi.operacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.contrato_version ADD CONSTRAINT fk_contrato_version_1 FOREIGN KEY (empresa_id, sucursal_id, operacion_id) REFERENCES bovi.operacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.contrato_version ADD CONSTRAINT fk_contrato_version_2 FOREIGN KEY (empresa_id, sucursal_id, documento_id) REFERENCES bovi.documento (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.condicion_lote ADD CONSTRAINT fk_condicion_lote_1 FOREIGN KEY (empresa_id, sucursal_id, operacion_id, numero_version) REFERENCES bovi.contrato_version (empresa_id, sucursal_id, operacion_id, numero_version) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.condicion_lote ADD CONSTRAINT fk_condicion_lote_2 FOREIGN KEY (empresa_id, sucursal_id, operacion_id, numero_lote) REFERENCES bovi.lote_operacion (empresa_id, sucursal_id, operacion_id, numero_lote) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.condicion_lote ADD CONSTRAINT fk_condicion_lote_3 FOREIGN KEY (empresa_id, sucursal_id, pesaje_base_id) REFERENCES bovi.pesaje (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.pesaje ADD CONSTRAINT fk_pesaje_1 FOREIGN KEY (empresa_id, sucursal_id, operacion_id, numero_lote) REFERENCES bovi.lote_operacion (empresa_id, sucursal_id, operacion_id, numero_lote) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.pesaje ADD CONSTRAINT fk_pesaje_2 FOREIGN KEY (empresa_id, sucursal_id, documento_id) REFERENCES bovi.documento (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.pesaje ADD CONSTRAINT fk_pesaje_3 FOREIGN KEY (empresa_id, sucursal_id, corrige_a_id) REFERENCES bovi.pesaje (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.pesaje_animal ADD CONSTRAINT fk_pesaje_animal_1 FOREIGN KEY (empresa_id, sucursal_id, pesaje_id) REFERENCES bovi.pesaje (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.pesaje_animal ADD CONSTRAINT fk_pesaje_animal_2 FOREIGN KEY (empresa_id, sucursal_id, animal_id) REFERENCES bovi.animal (empresa_id, sede_operadora_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.seleccion_compra ADD CONSTRAINT fk_seleccion_compra_1 FOREIGN KEY (empresa_id, sucursal_id, operacion_id, numero_lote) REFERENCES bovi.lote_operacion (empresa_id, sucursal_id, operacion_id, numero_lote) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.seleccion_compra ADD CONSTRAINT fk_seleccion_compra_2 FOREIGN KEY (empresa_id, sucursal_id, operacion_id, tipo_operacion) REFERENCES bovi.operacion (empresa_id, sucursal_id, id, tipo) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.seleccion_compra ADD CONSTRAINT fk_seleccion_compra_3 FOREIGN KEY (empresa_id, sucursal_id, animal_id) REFERENCES bovi.animal (empresa_id, sede_operadora_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.posicion_inventario ADD CONSTRAINT fk_posicion_inventario_1 FOREIGN KEY (empresa_id, sucursal_id, compra_operacion_id, compra_numero_lote, animal_id) REFERENCES bovi.seleccion_compra (empresa_id, sucursal_id, operacion_id, numero_lote, animal_id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.posicion_inventario ADD CONSTRAINT fk_posicion_inventario_2 FOREIGN KEY (empresa_id, sucursal_id, animal_id) REFERENCES bovi.animal (empresa_id, sede_operadora_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.seleccion_venta ADD CONSTRAINT fk_seleccion_venta_1 FOREIGN KEY (empresa_id, sucursal_id, operacion_id, numero_lote) REFERENCES bovi.lote_operacion (empresa_id, sucursal_id, operacion_id, numero_lote) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.seleccion_venta ADD CONSTRAINT fk_seleccion_venta_2 FOREIGN KEY (empresa_id, sucursal_id, operacion_id, tipo_operacion) REFERENCES bovi.operacion (empresa_id, sucursal_id, id, tipo) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.seleccion_venta ADD CONSTRAINT fk_seleccion_venta_3 FOREIGN KEY (empresa_id, sucursal_id, posicion_id) REFERENCES bovi.posicion_inventario (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.reserva_venta ADD CONSTRAINT fk_reserva_venta_1 FOREIGN KEY (empresa_id, sucursal_id, operacion_id, numero_lote, posicion_id) REFERENCES bovi.seleccion_venta (empresa_id, sucursal_id, operacion_id, numero_lote, posicion_id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.movimiento_inventario ADD CONSTRAINT fk_movimiento_inventario_1 FOREIGN KEY (empresa_id, sucursal_id, posicion_id) REFERENCES bovi.posicion_inventario (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.movimiento_inventario ADD CONSTRAINT fk_movimiento_inventario_2 FOREIGN KEY (empresa_id, sucursal_id, operacion_id) REFERENCES bovi.operacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.movimiento_inventario ADD CONSTRAINT fk_movimiento_inventario_3 FOREIGN KEY (empresa_id, predio_id) REFERENCES bovi.predio (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.movimiento_inventario ADD CONSTRAINT fk_movimiento_inventario_4 FOREIGN KEY (empresa_id, custodio_parte_id) REFERENCES bovi.parte (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.movimiento_inventario ADD CONSTRAINT fk_movimiento_inventario_5 FOREIGN KEY (empresa_id, sucursal_id, documento_id) REFERENCES bovi.documento (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.movimiento_inventario ADD CONSTRAINT fk_movimiento_inventario_6 FOREIGN KEY (empresa_id, sucursal_id, reverso_de_id) REFERENCES bovi.movimiento_inventario (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.periodo_cierre ADD CONSTRAINT fk_periodo_cierre_1 FOREIGN KEY (empresa_id, sucursal_id) REFERENCES bovi.sucursal (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.cierre_periodo_version ADD CONSTRAINT fk_cierre_periodo_version_1 FOREIGN KEY (empresa_id, sucursal_id, periodo_id) REFERENCES bovi.periodo_cierre (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.liquidacion ADD CONSTRAINT fk_liquidacion_1 FOREIGN KEY (empresa_id, sucursal_id, operacion_id, numero_version) REFERENCES bovi.contrato_version (empresa_id, sucursal_id, operacion_id, numero_version) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.liquidacion ADD CONSTRAINT fk_liquidacion_2 FOREIGN KEY (empresa_id, sucursal_id, periodo_id) REFERENCES bovi.periodo_cierre (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.concepto_liquidacion ADD CONSTRAINT fk_concepto_liquidacion_1 FOREIGN KEY (empresa_id, sucursal_id, liquidacion_id) REFERENCES bovi.liquidacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.concepto_liquidacion ADD CONSTRAINT fk_concepto_liquidacion_2 FOREIGN KEY (empresa_id, sucursal_id, pesaje_id) REFERENCES bovi.pesaje (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.ajuste_liquidacion ADD CONSTRAINT fk_ajuste_liquidacion_1 FOREIGN KEY (empresa_id, sucursal_id, liquidacion_id) REFERENCES bovi.liquidacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.ajuste_liquidacion ADD CONSTRAINT fk_ajuste_liquidacion_2 FOREIGN KEY (empresa_id, sucursal_id, revierte_ajuste_id) REFERENCES bovi.ajuste_liquidacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.ajuste_liquidacion ADD CONSTRAINT fk_ajuste_liquidacion_3 FOREIGN KEY (empresa_id, sucursal_id, periodo_id) REFERENCES bovi.periodo_cierre (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.ajuste_liquidacion ADD CONSTRAINT fk_ajuste_liquidacion_4 FOREIGN KEY (empresa_id, sucursal_id, documento_id) REFERENCES bovi.documento (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.gasto_operacion ADD CONSTRAINT fk_gasto_operacion_1 FOREIGN KEY (empresa_id, sucursal_id, operacion_id) REFERENCES bovi.operacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.gasto_operacion ADD CONSTRAINT fk_gasto_operacion_2 FOREIGN KEY (empresa_id, proveedor_parte_id) REFERENCES bovi.parte (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.gasto_operacion ADD CONSTRAINT fk_gasto_operacion_3 FOREIGN KEY (empresa_id, sucursal_id, bonifica_gasto_id) REFERENCES bovi.gasto_operacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.gasto_operacion ADD CONSTRAINT fk_gasto_operacion_4 FOREIGN KEY (empresa_id, sucursal_id, documento_id) REFERENCES bovi.documento (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.gasto_operacion ADD CONSTRAINT fk_gasto_operacion_5 FOREIGN KEY (empresa_id, sucursal_id, periodo_id) REFERENCES bovi.periodo_cierre (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.asignacion_costo ADD CONSTRAINT fk_asignacion_costo_1 FOREIGN KEY (empresa_id, sucursal_id, posicion_id) REFERENCES bovi.posicion_inventario (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.asignacion_costo ADD CONSTRAINT fk_asignacion_costo_2 FOREIGN KEY (empresa_id, sucursal_id, fuente_liquidacion_id, fuente_numero_concepto) REFERENCES bovi.concepto_liquidacion (empresa_id, sucursal_id, liquidacion_id, numero_concepto) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.asignacion_costo ADD CONSTRAINT fk_asignacion_costo_3 FOREIGN KEY (empresa_id, sucursal_id, fuente_gasto_id) REFERENCES bovi.gasto_operacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.asignacion_costo ADD CONSTRAINT fk_asignacion_costo_4 FOREIGN KEY (empresa_id, sucursal_id, fuente_ajuste_id) REFERENCES bovi.ajuste_liquidacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.asignacion_costo ADD CONSTRAINT fk_asignacion_costo_5 FOREIGN KEY (empresa_id, sucursal_id, periodo_id) REFERENCES bovi.periodo_cierre (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.asiento_valoracion ADD CONSTRAINT fk_asiento_valoracion_1 FOREIGN KEY (empresa_id, sucursal_id, posicion_id) REFERENCES bovi.posicion_inventario (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.asiento_valoracion ADD CONSTRAINT fk_asiento_valoracion_2 FOREIGN KEY (empresa_id, sucursal_id, periodo_id) REFERENCES bovi.periodo_cierre (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.asiento_valoracion ADD CONSTRAINT fk_asiento_valoracion_3 FOREIGN KEY (empresa_id, sucursal_id, asignacion_id) REFERENCES bovi.asignacion_costo (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.asiento_valoracion ADD CONSTRAINT fk_asiento_valoracion_4 FOREIGN KEY (empresa_id, sucursal_id, operacion_id) REFERENCES bovi.operacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.pago ADD CONSTRAINT fk_pago_1 FOREIGN KEY (empresa_id, parte_id) REFERENCES bovi.parte (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.pago ADD CONSTRAINT fk_pago_2 FOREIGN KEY (empresa_id, sucursal_id, pago_origen_id) REFERENCES bovi.pago (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.pago ADD CONSTRAINT fk_pago_3 FOREIGN KEY (empresa_id, sucursal_id, documento_id) REFERENCES bovi.documento (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.pago ADD CONSTRAINT fk_pago_4 FOREIGN KEY (empresa_id, sucursal_id, periodo_id) REFERENCES bovi.periodo_cierre (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.aplicacion_pago ADD CONSTRAINT fk_aplicacion_pago_1 FOREIGN KEY (empresa_id, sucursal_id, pago_id) REFERENCES bovi.pago (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.aplicacion_pago ADD CONSTRAINT fk_aplicacion_pago_2 FOREIGN KEY (empresa_id, sucursal_id, liquidacion_id) REFERENCES bovi.liquidacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.aplicacion_pago ADD CONSTRAINT fk_aplicacion_pago_3 FOREIGN KEY (empresa_id, sucursal_id, reverso_de_id) REFERENCES bovi.aplicacion_pago (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.aplicacion_pago ADD CONSTRAINT fk_aplicacion_pago_4 FOREIGN KEY (empresa_id, sucursal_id, periodo_id) REFERENCES bovi.periodo_cierre (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.documento ADD CONSTRAINT fk_documento_1 FOREIGN KEY (empresa_id, sucursal_id, documento_previo_id) REFERENCES bovi.documento (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.operacion_documento ADD CONSTRAINT fk_operacion_documento_1 FOREIGN KEY (empresa_id, sucursal_id, operacion_id) REFERENCES bovi.operacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.operacion_documento ADD CONSTRAINT fk_operacion_documento_2 FOREIGN KEY (empresa_id, sucursal_id, documento_id) REFERENCES bovi.documento (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.revision_administrativa ADD CONSTRAINT fk_revision_administrativa_1 FOREIGN KEY (empresa_id, sucursal_id, operacion_id) REFERENCES bovi.operacion (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.revision_administrativa ADD CONSTRAINT fk_revision_administrativa_2 FOREIGN KEY (empresa_id, identificacion_id) REFERENCES bovi.animal_identificacion (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.revision_administrativa ADD CONSTRAINT fk_revision_administrativa_3 FOREIGN KEY (empresa_id, sucursal_id, revision_anterior_id) REFERENCES bovi.revision_administrativa (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.revision_documento ADD CONSTRAINT fk_revision_documento_1 FOREIGN KEY (empresa_id, sucursal_id, revision_id) REFERENCES bovi.revision_administrativa (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.revision_documento ADD CONSTRAINT fk_revision_documento_2 FOREIGN KEY (empresa_id, sucursal_id, documento_id) REFERENCES bovi.documento (empresa_id, sucursal_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE bovi.auditoria_evento ADD CONSTRAINT fk_auditoria_evento_1 FOREIGN KEY (empresa_id, actor_id) REFERENCES bovi.usuario (empresa_id, id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY IMMEDIATE;

CREATE UNIQUE INDEX uk_parte_rfc ON bovi.parte (empresa_id,rfc);

CREATE UNIQUE INDEX uk_gasto_operacion_referencia_origen ON bovi.gasto_operacion (empresa_id,sucursal_id,proveedor_parte_id,referencia_origen);

CREATE UNIQUE INDEX uk_documento_clave_almacenamiento ON bovi.documento (clave_almacenamiento);

CREATE UNIQUE INDEX uk_documento_documento_previo_id ON bovi.documento (empresa_id,sucursal_id,documento_previo_id);

CREATE UNIQUE INDEX uk_pesaje_corrige_a_id ON bovi.pesaje (empresa_id,sucursal_id,corrige_a_id);

CREATE UNIQUE INDEX uk_aplicacion_pago_reverso_de_id ON bovi.aplicacion_pago (empresa_id,sucursal_id,reverso_de_id);

CREATE UNIQUE INDEX uk_ajuste_liquidacion_revierte_ajuste_id ON bovi.ajuste_liquidacion (empresa_id,sucursal_id,revierte_ajuste_id);

CREATE UNIQUE INDEX uk_movimiento_inventario_reverso_de_id ON bovi.movimiento_inventario (empresa_id,sucursal_id,reverso_de_id);

CREATE UNIQUE INDEX uk_posicion_inventario_activo ON bovi.posicion_inventario (empresa_id,animal_id) WHERE estado IN ('PENDIENTE_RECEPCION','DISPONIBLE','VENDIDA_PENDIENTE_ENTREGA');

CREATE UNIQUE INDEX uk_reserva_venta_activo ON bovi.reserva_venta (empresa_id,sucursal_id,posicion_id) WHERE estado = 'ACTIVA';


CREATE UNIQUE INDEX uk_animal_identificacion_activo ON bovi.animal_identificacion (empresa_id,animal_id,sistema) WHERE estado = 'VIGENTE';

CREATE UNIQUE INDEX uk_nodo_unico ON infra.nodo_config ((true));

ALTER TABLE bovi.periodo_cierre ADD CONSTRAINT periodo_no_solapado EXCLUDE USING gist (empresa_id WITH =, sucursal_id WITH =, daterange(desde,hasta,'[]') WITH &&);

RESET ROLE;
