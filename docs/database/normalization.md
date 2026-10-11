# Dependencias funcionales y normalización

Referencia: F15. Estado: análisis de las 42 tablas lógicas, contrastadas en catálogo A/B; restricciones no expresadas como DF se prueban por separado. Las tablas técnicas adicionales JDBC/Flyway/captura no son entidades comerciales.

## 1. Dependencias funcionales y claves candidatas por tabla
Notación: X → Y. "CK" = claves candidatas. Las claves técnicas conservan el scope E/S de su UNIQUE o PK: una UUID aislada no se presume única. Se listan además las claves comerciales.

| Tabla | CK | DF no triviales relevantes | Forma |
|---|---|---|---|
| empresa | {id} | id → razon_social, rfc, estado | BCNF |
| sucursal | {E,id}, {E,codigo} | E,id → codigo, nombre, nodo_dueno; E,codigo → id | BCNF (todo determinante es CK) |
| parte | {E,id}, {E,rfc} (si rfc no nulo) | E,id → nombre, rfc, … | BCNF |
| predio | {E,id} | E,id → nombre, parte_responsable_id | BCNF |
| usuario | {E,id}, {E,login_normalizado} | — | BCNF |
| membresia_usuario | {E,S,usuario_id,rol_codigo} | → vigente | BCNF |
| animal | {E,id} (UK(E,sede,id) es superclave usada para FK) | E,id → sede_operadora_id, sexo, situacion | BCNF |
| animal_identificacion | {E,id}, {E,sistema,codigo_normalizado} | codigo_declarado → codigo_normalizado (función determinista, ver §4) | Desnormalización derivada declarada; no afirmar 3FN/BCNF sin tratar codigo_declarado → codigo_normalizado |
| operacion | {E,S,id}, {E,S,tipo,folio} | E,S,id → tipo, parte_id, estado, …; E,S,tipo,folio → id | BCNF |
| lote_operacion | {E,S,operacion_id,numero_lote} | → descripcion | BCNF |
| contrato_version | {E,S,operacion_id,numero_version} | → estado, politica_redondeo | BCNF |
| condicion_lote | {E,S,operacion_id,numero_version,numero_lote} | → precio_unitario, unidad_precio, … | BCNF |
| seleccion_compra | {E,S,op,animal}; PK física {E,S,op,lote,animal} no mínima | E,S,op,animal → lote | BCNF respecto a la DF declarada: el determinante mínimo es {E,S,op,animal} |
| posicion_inventario | {E,S,id}, {E,S,animal_id,numero_ciclo}, {E,S,compra_op,compra_lote,animal_id} | id → estado, …; animal_id,numero_ciclo → id | BCNF |
| reserva_venta | {E,S,id} | id → posicion_id, estado, vence_en | BCNF |
| pesaje | {E,S,id} | id → modo, bruto, tara, neto; (bruto,tara) → neto **cuando modo = BRUTO_TARA** | Dependencia condicional por modo; neto conservado con CHECK, no prueba automática de 3FN |
| pesaje_animal | {E,S,pesaje_id,animal_id} | → peso_individual_kg | BCNF |
| liquidacion | {E,S,id}, {E,S,operacion_id} | id → total, snapshots | BCNF (snapshots dependen de la liquidación, ver §5) |
| concepto_liquidacion | {E,S,liquidacion_id,numero_concepto} | → tipo, cantidad, precio, importe; (cantidad, precio) → importe salvo redondeo | Importe derivado materializado: excepción a normalización estricta, hecho redondeado inmutable |
| pago | {E,S,id} | id → parte_id, importe, tipo | BCNF |
| aplicacion_pago | {E,S,id}, {E,S,reverso_de_id} (si no nulo) | id → pago_id, liquidacion_id, importe | BCNF |
| asignacion_costo | {E,S,id} | id → posicion, fuente, importe | BCNF |
| asiento_valoracion | {E,S,id} | (clase, sentido, importe) → delta_* | deltas generados (no redundancia editable) |
| documento | {E,S,id}, {clave_almacenamiento} | id → sha256, tamano, … | BCNF |
| periodo_cierre | {E,S,id}; además (E,S,fecha) determina el periodo por la exclusión | — | BCNF |

## 2. Ejemplo A — operación / contraparte
**No normalizado** (planilla típica de un comercializador):

| folio | fecha | contraparte | rfc | teléfono | lote | arete | precio_kg |
|---|---|---|---|---|---|---|---|
| C-01 | 2026-10-02 | Productor Demo 01 | DEMO010101AAA | 555-0101 | 1 | DEMO-1, DEMO-2 | 48 |

- **1FN**: "DEMO-1, DEMO-2" es no atómico → una fila por arete: (folio, lote, arete, …). La clave pasa a {folio, arete}.
- **2FN**: con clave {folio, arete}, `fecha`, `contraparte`, `rfc`, `teléfono` dependen sólo de `folio` (dependencia parcial) → se separa `operacion(folio, fecha, parte)` de `seleccion(folio, lote, arete)`.
- **3FN**: en `operacion`, `rfc` y `teléfono` dependen de `contraparte`, no del folio (transitiva folio → contraparte → rfc) → `parte(id, nombre, rfc, telefono)` y `operacion.parte_id`.
- `precio_kg` depende de (folio, lote, **versión** aceptada), no del arete → `condicion_lote` (ejemplo B).
- Resultado: `parte`, `operacion`, `lote_operacion`, `seleccion_compra`, `animal_identificacion` (el arete identifica al animal, no a la selección).

## 3. Ejemplo B — versión / condición por lote
Planteamiento ingenuo: `operacion(id, precio_kg, deduccion, version)` con UPDATE al renegociar.
- Viola el hecho histórico: la versión 1 deja de existir (no es un problema de forma normal, es de modelado temporal).
- Al versionar: `condicion(operacion, version, lote, precio, unidad, deduccion, politica_redondeo)`. DF: (op, version) → politica_redondeo; (op, version, lote) → precio, unidad, deduccion. `politica_redondeo` depende de parte de la clave → **viola 2FN** → se mueve a `contrato_version(op, version, politica_redondeo, estado)`.
- `condicion_lote(op, version, lote, precio, unidad, base_pesaje, deduccion)`: toda DF tiene como determinante la clave completa → 3FN y BCNF.
- Preservación de dependencias: las dos DF quedan cada una en una tabla; la unión `contrato_version ⋈ condicion_lote` sobre (op, version) es sin pérdida porque (op, version) es clave de `contrato_version`.

## 4. Ejemplo C — liquidación / aplicaciones
Planteamiento ingenuo: `liquidacion(id, total, pagado, saldo, pago1_ref, pago1_importe, pago2_ref, …)`.
- **1FN**: grupo repetido pago1/pago2 → tabla aparte.
- `saldo` = total + ajustes − aplicaciones: atributo derivado editable en paralelo → riesgo de inconsistencia; se elimina y se calcula en vista (`v_saldo_liquidacion`).
- Un pago cubre varias liquidaciones y una liquidación recibe varios pagos (N:M) → `pago(id, parte, importe, …)` + `aplicacion_pago(id, pago_id, liquidacion_id, importe, naturaleza, reverso_de_id)`.
- DF en `aplicacion_pago`: id → (pago_id, liquidacion_id, importe). No hay DF (pago_id, liquidacion_id) → importe porque puede haber varias aplicaciones y reversos entre el mismo par: por eso la aplicación tiene identidad propia.
- Restricción entre filas Σ aplicaciones ≤ importe del pago: no es una DF ni puede ser CHECK (F20); se garantiza en el comando AplicarPago con locks.
- Resultado: BCNF; ninguna sumatoria almacenada.

## 5. Excepciones deliberadas
| Caso | Por qué no es redundancia a eliminar |
|---|---|
| `liquidacion.snapshot_*` | Hecho temporal "así se aceptó"; depende de la liquidación, no de la parte actual (RN-024) |
| `concepto_liquidacion.importe` | Valor redondeado HALF_UP que se acordó; recalcular podría diferir por política futura |
| `seleccion_compra.tipo_operacion` | Constante para FK compuesta que garantiza "sólo COMPRA" declarativamente |
| `pesaje.neto_kg` con bruto/tara | En NETO_REPORTADO es dato primario; en BRUTO_TARA se fuerza igualdad con CHECK |
| `animal_identificacion.codigo_normalizado` | Necesario para la UNIQUE; determinado por función inmutable sobre `codigo_declarado` (se podría generar; se mantiene CHECK de igualdad) |
| `asiento_valoracion.delta_*` | Columnas generadas: no editables |

## 6. BCNF y preservación de dependencias
La selección de compra tiene la clave candidata mínima {E,S,op,animal}; añadir lote produce una superclave no mínima. Su DF determina lote y no viola BCNF. La tabla anterior analiza las dependencias declaradas de las tablas enumeradas; no demuestra BCNF del modelo completo. El inventario completo siguiente explicita determinantes mínimos conocidos y excepciones; las restricciones físicas se contrastaron con el catálogo ejecutado, sin confundir una comparación con una demostración exhaustiva de reglas (TEST-30). Los totales materializados y snapshots conservan autoridad e inmutabilidad explícitas; no son campos editables paralelos.

## 7. Inventario completo de determinantes conocidos

Para cada fila, K → todos los atributos propios del registro. Las claves de abajo provienen de PK/UK completas declaradas, eliminando superclaves que contienen otra clave más pequeña. UK con NULL y unicidad parcial por estado no son claves candidatas del conjunto completo. Todas las DF abreviadas id → … de la tabla inicial significan la clave E[,S],id correspondiente, nunca UUID global.

Los datos escalares/composición separados sostienen 1FN; los atributos comerciales de contraparte/animal se separan de selecciones y hechos (2FN/3FN). Las constantes para FK de tipo, valores calculados, JSON snapshots y efectos históricos son excepciones explícitas. Una comprobación de claves no descubre automáticamente todas las DF semánticas; este inventario analiza las reconocidas por el dominio, sin una proclamación global falsa de BCNF.

| Tabla | Determinantes mínimos NOT NULL | UK condicional conocida | Análisis / excepción |
|---|---|---|---|
| empresa | {id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| sucursal | {empresa_id,id}, {empresa_id,codigo} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| rol_aplicacion | {codigo} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| usuario | {empresa_id,id}, {empresa_id,login_normalizado} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| membresia_usuario | {empresa_id,sucursal_id,usuario_id,rol_codigo} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| parte | {empresa_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| predio | {empresa_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| animal | {empresa_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| animal_identificacion | {empresa_id,id}, {empresa_id,sistema,codigo_normalizado} | — | normalización derivada del código; véase §5, no BCNF estricta |
| operacion | {empresa_id,sucursal_id,id}, {empresa_id,sucursal_id,tipo,folio} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| folio_contador | {empresa_id,sucursal_id,tipo,anio} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| lote_operacion | {empresa_id,sucursal_id,operacion_id,numero_lote} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| contrato_version | {empresa_id,sucursal_id,operacion_id,numero_version} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| condicion_lote | {empresa_id,sucursal_id,operacion_id,numero_version,numero_lote} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| pesaje | {empresa_id,sucursal_id,id} | — | neto derivado sólo en BRUTO_TARA; dependencia condicional con CHECK |
| pesaje_animal | {empresa_id,sucursal_id,pesaje_id,animal_id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| seleccion_compra | {empresa_id,sucursal_id,operacion_id,animal_id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| posicion_inventario | {empresa_id,sucursal_id,id}, {empresa_id,sucursal_id,animal_id,numero_ciclo}, {empresa_id,sucursal_id,compra_operacion_id,compra_numero_lote,animal_id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| seleccion_venta | {empresa_id,sucursal_id,operacion_id,posicion_id} | — | selección de posición por operación mínima; estado derivado de reserva/posición, no atributo repetido |
| reserva_venta | {empresa_id,sucursal_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| movimiento_inventario | {empresa_id,sucursal_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| periodo_cierre | {empresa_id,sucursal_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| cierre_periodo_version | {empresa_id,sucursal_id,periodo_id,numero_version} | — | totales/versiones y hash de corte materializados e inmutables |
| liquidacion | {empresa_id,sucursal_id,id}, {empresa_id,sucursal_id,operacion_id} | — | snapshots temporales inmutables, no copia del maestro actual |
| concepto_liquidacion | {empresa_id,sucursal_id,liquidacion_id,numero_concepto} | — | importe redondeado materializado; no 3FN estricta respecto a fórmula |
| ajuste_liquidacion | {empresa_id,sucursal_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| gasto_operacion | {empresa_id,sucursal_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| asignacion_costo | {empresa_id,sucursal_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| asiento_valoracion | {empresa_id,sucursal_id,id} | — | deltas generados, fórmulas no editables |
| pago | {empresa_id,sucursal_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| aplicacion_pago | {empresa_id,sucursal_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| documento | {empresa_id,sucursal_id,id} | — | sha256 no determina nombre original/versión/scope; múltiples metadatos de mismos bytes son válidos |
| operacion_documento | {empresa_id,sucursal_id,operacion_id,documento_id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| revision_administrativa | {empresa_id,sucursal_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| revision_documento | {empresa_id,sucursal_id,revision_id,documento_id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| auditoria_evento | {empresa_id,sucursal_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| evento_outbox | {empresa_id,sucursal_id,id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| clave_idempotencia | {empresa_id,sucursal_id,principal_id,comando,clave} | — | resultado inmutable de intención; contenido/hash/resultado forman hecho temporal |
| mensaje_inbox | {consumidor,fuente_id,event_id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| infra.nodo_config | {nodo} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| infra.entrega_outbox | {evento_id,destino} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |
| infra.importacion_fuente | {id} | — | 1FN/2FN/3FN y BCNF respecto a DF declaradas: determinantes son claves; no se presume otra unicidad comercial |

### Tablas técnicas del catálogo

SpringSession (clave PRIMARY_ID; SESSION_ID única) y attributes (PRIMARY_ID,ATTRIBUTE_NAME) separan el grupo repetido; bytes de atributo son serialización técnica, no una nueva entidad comercial. Flyway conserva historia de versión/checksum. `infra.tarifa_snapshot.id` determina captura/actor/scope/contenido; sólo aceptada_en puede transitar de NULL a timestamp una vez. Precio y hash son derivados materializados deliberados; el snapshot aceptado del gasto conserva hechos aunque cambie la fuente FDW. Ninguna se publica como maestro comercial ni implica normalización de contenido binario/JSON.
