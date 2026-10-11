# Dependencias funcionales y normalización

Referencia: F15. Estado: análisis diseñado; se comprobará contra el DDL (TEST-30).

## 1. Dependencias funcionales y claves candidatas por tabla
Notación: X → Y. "CK" = claves candidatas. `id` técnico es CK en todas las tablas que lo tienen; se listan además las claves comerciales.

| Tabla | CK | DF no triviales relevantes | Forma |
|---|---|---|---|
| empresa | {id} | id → razon_social, rfc, estado | BCNF |
| sucursal | {E,id}, {E,codigo} | E,id → codigo, nombre, nodo_dueno; E,codigo → id | BCNF (todo determinante es CK) |
| parte | {E,id}, {E,rfc} (si rfc no nulo) | E,id → nombre, rfc, … | BCNF |
| predio | {E,id} | E,id → nombre, parte_responsable_id | BCNF |
| usuario | {E,id}, {E,login_normalizado} | — | BCNF |
| membresia_usuario | {E,S,usuario_id,rol_codigo} | → vigente | BCNF |
| animal | {E,id} (UK(E,sede,id) es superclave usada para FK) | E,id → sede_operadora_id, sexo, situacion | BCNF |
| animal_identificacion | {E,id}, {E,sistema,codigo_normalizado} | codigo_declarado → codigo_normalizado (función determinista, ver §4) | 3FN; BCNF salvo la DF funcional derivable |
| operacion | {E,S,id}, {E,S,tipo,folio} | E,S,id → tipo, parte_id, estado, …; E,S,tipo,folio → id | BCNF |
| lote_operacion | {E,S,operacion_id,numero_lote} | → descripcion | BCNF |
| contrato_version | {E,S,operacion_id,numero_version} | → estado, politica_redondeo | BCNF |
| condicion_lote | {E,S,operacion_id,numero_version,numero_lote} | → precio_unitario, unidad_precio, … | BCNF |
| seleccion_compra | {E,S,op,lote,animal}, {E,S,op,animal} | E,S,op,animal → lote | BCNF (ambos determinantes son CK) |
| posicion_inventario | {E,S,id}, {E,S,animal_id,numero_ciclo}, {E,S,compra_op,compra_lote,animal_id} | id → estado, …; animal_id,numero_ciclo → id | BCNF |
| reserva_venta | {E,S,id} | id → posicion_id, estado, vence_en | BCNF |
| pesaje | {E,S,id} | id → modo, bruto, tara, neto; (bruto,tara) → neto **cuando modo = BRUTO_TARA** | 3FN con CHECK (ver §4) |
| pesaje_animal | {E,S,pesaje_id,animal_id} | → peso_individual_kg | BCNF |
| liquidacion | {E,S,id}, {E,S,operacion_id} | id → total, snapshots | BCNF (snapshots dependen de la liquidación, ver §5) |
| concepto_liquidacion | {E,S,liquidacion_id,numero_concepto} | → tipo, cantidad, precio, importe; (cantidad, precio) → importe salvo redondeo | 3FN; importe se conserva como hecho redondeado |
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
Todas las tablas de negocio cumplen BCNF salvo las DF "funcionales" de §5, que se controlan con CHECK o columnas generadas, no con descomposición. No se encontró ninguna descomposición BCNF que pierda dependencias: el caso típico (3FN pero no BCNF por solapamiento de claves candidatas) aparece en `seleccion_compra` con CK {op, lote, animal} y {op, animal}; la DF (op, animal) → lote tiene determinante que **es** CK, por lo que sigue en BCNF.
