# Modelo conceptual (MER Chen / EER)

> **Vigencia (14-oct-2026):** válido hasta la migración **V26**. V19–V26 no agregan ni cambian tablas o columnas (sólo funciones, triggers y roles); `tools/esquema/comparar_catalogo.py` contra A y B: 42 tablas, 0 diferencias.

Versión 0.1 · 2026-10-10 · Diagrama completo en una hoja: `docs/diagrams/exports/mer-completo.pdf`; láminas por dominio: `docs/diagrams/exports/mer-0*.pdf`.

## 1. Notación y lectura
| Símbolo | Significado |
|---|---|
| Rectángulo simple | Entidad fuerte (identidad propia) |
| Rectángulo doble | Entidad débil (identificada por propietario + clave parcial) |
| Rombo | Relación nombrada con verbo |
| Rombo doble | Relación identificante de una débil |
| Óvalo | Atributo simple; **subrayado** = clave elegida; subrayado discontinuo = clave parcial |
| Óvalo doble | Multivaluado (no se usa en este modelo: los multivaluados se modelaron como entidades con historia, p. ej. Identificacion) |
| Óvalo discontinuo | Derivado (con fórmula) |
| Óvalos anidados | Compuesto |
| Línea doble / simple | Participación total / parcial |
| (mín,máx) | Se coloca **junto a la entidad** y dice en cuántas instancias de la relación participa *una* instancia de esa entidad |
| ISA | Especialización: no se usa (ver §5) |

Ejemplo de lectura: "(0,N) junto a Animal en *participa*" = un animal participa en cero o muchas posiciones de inventario. Esta es la convención "look-here" (mín,máx) de Chen/Elmasri; **no** es la convención "look-across" de UML/crow's foot.

## 2. Subordinación: tres conceptos distintos
- **Dependencia de existencia**: la instancia no puede existir sin otra (p. ej. un Pesaje sin su Lote). Se expresa con participación total.
- **Dependencia de identificación**: la clave de la instancia incluye la de su propietario (LoteOperacion = Operacion + numero_lote). Sólo esto hace a una entidad **débil**.
- **Participación total**: toda instancia participa al menos una vez en la relación; no implica debilidad.

Una FK NOT NULL implementa existencia, no identificación. Pesaje tiene FK obligatoria a Lote pero es **fuerte**: tiene identidad propia (un ticket existe como hecho propio y puede corregirse con otro).

## 3. Entidades
| Entidad | Tipo | Clave conceptual | Atributos conceptuales principales | Justificación |
|---|---|---|---|---|
| Empresa | Fuerte | id | razón social, RFC, estado | Raíz del aislamiento |
| Sucursal (sede) | Fuerte | id; candidata (empresa, código) | código, nombre, nodo dueño, zona horaria | Tiene código propio; no débil aunque dependa existencialmente de Empresa |
| Parte | Fuerte | id | tipo de persona, nombre, RFC | Puede comprar y vender: sin ISA disjunta |
| Predio | Fuerte | id | nombre, clave UPP declarada, ubicación | — |
| Usuario | Fuerte | id; candidata (empresa, login) | login, nombre, estado, hash | — |
| RolAplicacion | Fuerte (catálogo) | código | descripción | ADMIN/OPERADOR/CAJA/AUDITOR |
| Animal | Fuerte | id | sexo, nacimiento declarado, raza declarada, situación, sede operadora | Identidad permanente |
| Identificacion | Fuerte | id; candidata (empresa, sistema, código normalizado) | sistema, código declarado, estado, vigencia | Historia de aretes; multivaluado modelado como entidad |
| Operacion | Fuerte | id; candidata (empresa, sede, tipo, folio) | tipo (COMPRA/VENTA), folio, fecha, moneda, estado, estado de entrega | Tipo inmutable en lugar de ISA |
| **LoteOperacion** | **Débil** | Operacion + <u>numero_lote</u> (parcial) | descripción | Su identidad no tiene sentido fuera de la operación |
| **ContratoVersion** | **Débil** | Operacion + numero_version | estado, política de redondeo, requiere recepción, aceptación | Versionado del acuerdo |
| **CondicionLote** | **Débil (dos propietarios)** | ContratoVersion + LoteOperacion (misma operación) | unidad, precio, base de pesaje, deducción, cargos, bonificaciones | Una condición es "la del lote L en la versión V" |
| SeleccionCompra | Entidad asociativa (débil) | LoteOperacion + Animal | — | Agregación: origina una Posicion |
| SeleccionVenta | Entidad asociativa (débil) | LoteOperacion + PosicionInventario | — | Agregación: mantiene Reservas |
| PosicionInventario | Fuerte | id; candidata (animal, numero_ciclo) | número de ciclo, estado, motivo de baja, apertura, cierre | Ciclo de costo con identidad propia |
| MovimientoInventario | Fuerte | id | tipo, instante, custodio, predio | Hecho físico inmutable |
| ReservaVenta | Fuerte | id | estado, creada, vence | Historia de reservas por selección |
| Pesaje | Fuerte | id | modo, bruto, tara, neto, folio de ticket, instante, estado, fuente | Hecho de báscula |
| Liquidacion | Fuerte | id; candidata (operación) | dirección, total, snapshots, vencimiento | Obligación principal (DEC-05) |
| **ConceptoLiquidacion** | **Débil** | Liquidacion + numero_concepto | tipo, cantidad, precio, importe | Desglose |
| GastoOperacion | Fuerte | id | naturaleza, clasificación, importe, concepto, fecha económica | Fuente de costo |
| AsignacionCosto | Entidad asociativa fuerte | id | método, base, importe, lote de reparto | Fuente XOR tipada → posición |
| AjusteLiquidacion | Fuerte | id | naturaleza, monto, motivo | Corrección sin sobrescritura |
| Pago | Fuerte | id | tipo, importe, método, referencia, fecha, estado | Dinero registrado |
| AplicacionPago | Entidad asociativa fuerte | id | importe, naturaleza, instante | Identidad propia por reverso |
| Documento | Fuerte | id | tipo documental, hash, tamaño, MIME, versión, emisor, folio, vigencia | Evidencia privada |
| RevisionAdministrativa | Fuerte | id | criterio, resultado, responsable, instante | Nunca "autorización sanitaria" |
| PeriodoCierre | Fuerte | id | desde, hasta, estado | — |
| **CierrePeriodoVersion** | **Débil** | PeriodoCierre + numero_version | tipo, motivo, corte, hash | Actas inmutables |
| AsientoValoracion | Fuerte | id | clase, sentido, importe, fecha económica | Efecto temporal en inventario/costo/pérdida |
| AuditoriaEvento | Fuerte | id | comando, actor, correlación, nodo origen, cambio | Lámina 6 |

Atributos derivados (óvalo discontinuo): `Liquidacion.saldo` (fórmula en `docs/domain/states-and-calculations.md` §4), `Pago.disponible`, `PosicionInventario.costo_vigente` (Σ asientos), `Pesaje.neto` cuando modo BRUTO_TARA, `Operacion.estado_entrega`. Compuesto: `Predio.ubicacion` (municipio, estado).

## 4. Láminas previstas
1. Vista general por dominios (sin atributos técnicos).
2. Identidad, contrapartes y sedes: Empresa, Sucursal, Parte, Predio, Usuario, Rol, Animal, Identificacion.
3. Operaciones, lotes, condiciones y pesajes.
4. Inventario, selección de venta, reserva y movimientos.
5. Liquidaciones, costos, pagos y aplicaciones.
6. Evidencia, revisiones, periodos y auditoría.
7. Lógico relacional por módulos (aparte, no Chen).

Tablas técnicas (outbox, inbox, idempotencia, infra.*, sesiones, flyway) **no** entran al MER de negocio; van en una vista técnica separada.

## 5. Por qué no hay ISA
- Parte comprador/vendedor: una especialización disjunta impediría que el mismo tercero compre y venda. El rol lo da el tipo de la operación.
- Compra/Venta: atributo `tipo` inmutable basta en el MVP; reglas que dependen del tipo se garantizan con FK compuesta (`seleccion_compra` sólo referencia operaciones COMPRA). Si se agregara ISA, sería total y disjunta.

## 6. Relaciones recursivas (corrige ≠ revierte ≠ reembolsa)
| Relación | Significado |
|---|---|
| Documento *reemplaza* Documento | Nueva versión de un archivo; la anterior se conserva y las revisiones previas siguen apuntando a ella |
| Pesaje *corrige* Pesaje | Error de captura; el original queda CORREGIDO |
| AplicacionPago *revierte* AplicacionPago | Contramovimiento completo; libera el importe |
| AjusteLiquidacion *revierte* AjusteLiquidacion | Anula un ajuste |
| Pago *reembolsa* Pago | Dinero real devuelto; consume el disponible del pago origen |
| GastoOperacion *bonifica* GastoOperacion | Bonificación del proveedor sobre un gasto previo |
| RevisionAdministrativa *sustituye* RevisionAdministrativa | Revisión posterior que corrige una anterior |
