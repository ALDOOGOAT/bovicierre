# Glosario

Nombre canónico en código entre `backticks`. Datos de ejemplo **sintéticos**.

| Término | Definición | Ejemplo | No confundir con |
|---|---|---|---|
| Empresa cliente (`empresa`) | Organización que contrata BoviCierre; todo dato pertenece a una | "Acopio Demo SA" (sintética) | La contraparte con la que compra/vende |
| Sede (`sucursal`) | Centro operativo de la empresa; cada operación pertenece a una | Sede A "Centro", Sede B "Norte" | Predio/establecimiento; nodo de BD |
| Nodo escritor | Instancia PostgreSQL que acepta escrituras de un agregado: A (maestros + sede A) o B (sede B) | Una venta de la sede B se escribe sólo en B | Sede (una sede *tiene* un nodo dueño); Pgpool |
| Contraparte (`parte`) | Persona u organización con la que se compra o vende; puede ser ambas cosas en momentos distintos | "Productor Sintético 01" | Empresa cliente; usuario |
| Establecimiento (`predio`) | Lugar físico declarado de origen, destino o custodia | "Rancho Demo El Llano" | Sede; UPP |
| UPP | Unidad de Producción Pecuaria: clave de registro oficial de un establecimiento productivo; se guarda como texto declarado con evidencia | `UPP-DEMO-0001` (ficticia) | Validación de autenticidad (BoviCierre no la certifica) |
| PSG | Prestador de Servicios Ganaderos: registro oficial para quien compra/acopia/comercializa; se guarda como texto declarado | `PSG-DEMO-01` | Permiso de movilización |
| Animal (`animal`) | Identidad permanente de un bovino dentro de la empresa; UUID técnico | `animal 7b1…` | Posición de inventario |
| Identificación oficial (`animal_identificacion`) | Código de arete/registro (SINIIGA/SINIDA [F04]) asociado a un animal, con sistema, vigencia y evidencia | `SINIIGA DEMO-000123` | UUID; QR interno (no sustituye arete) |
| Lote (`lote_operacion`) | Grupo comercial de animales/posiciones dentro de una operación, numerado | Lote 1 de la compra C-0001 | Pesaje; corral físico |
| Membresía de lote | Pertenencia de un animal (compra) o posición (venta) a un lote: `seleccion_compra` / `seleccion_venta` | Animal X en lote 2 | Composición de un pesaje |
| Posición / ciclo de inventario (`posicion_inventario`) | Tenencia de un animal entre una adquisición y su salida; tiene costo propio | Ciclo 2 del animal X tras recompra | Animal |
| Custodia | Quién tiene físicamente al animal; se registra en movimientos | Transportista durante el viaje | Propiedad comercial; nodo dueño |
| Operación (`operacion`) | Compra o venta por cuenta propia con una contraparte; tipo inmutable | Compra C-0001 | Liquidación; pago |
| Acuerdo / versión (`contrato_version`) | Conjunto numerado de condiciones aceptadas para una operación | v2 aceptada | Condición por lote |
| Condición por lote (`condicion_lote`) | Precio, unidad (kg/cabeza), pesaje base y deducciones pactadas para un lote en una versión | 48.0000 MXN/kg, base pesaje de origen | Tarifa de catálogo |
| Pesaje (`pesaje`) | Medición de báscula de un conjunto exacto de animales | Ticket 4471, 5,000.000 kg | Peso estimado |
| Bruto / tara / neto | Neto = bruto − tara; si el ticket sólo trae neto: modo NETO_REPORTADO | 12,000 − 7,000 = 5,000 kg | — |
| Variación física | Diferencia observada entre dos pesajes compatibles del mismo conjunto | 100 kg (2%) | Deducción contractual |
| Ajuste contractual | Deducción o cargo pactado expresamente en la condición | 1% de deducción pactada | Merma "habitual" supuesta |
| Liquidación comercial (`liquidacion`) | Snapshot inmutable del cálculo de una operación confirmada; es la obligación con la contraparte (DEC-05) | 240,000.00 por pagar | CFDI; PDF |
| Obligación | Saldo por cobrar (venta) o pagar (compra) de una liquidación + ajustes − aplicaciones | 244,000 por cobrar | Pago |
| Pago (`pago`) | Movimiento de dinero registrado (COBRO o PAGO); existe aunque no esté aplicado | Transferencia de 50,000 | Aplicación |
| Aplicación (`aplicacion_pago`) | Asignación de un importe de un pago a una liquidación | 50,000 a la venta V-0001 | Pago |
| Reverso | Contramovimiento que anula un registro conservando el original (aplicación, ajuste, asiento) | Reverso de aplicación 400 | Corrección (nueva versión) / reembolso (dinero real) |
| Corrección | Nuevo registro que sustituye a otro por error de captura, enlazado al original | Pesaje corregido | Reverso |
| Reembolso / reintegro | Devolución real de dinero que consume disponibilidad del pago origen | Devolver 100 al comprador | Reverso de aplicación |
| Costo de adquisición | Precio de compra + gastos capitalizables asignados a cada posición | 1,100 por posición (GOLD-02) | Costo de venta |
| Costo de venta | Costo de las posiciones cuya venta se reconoció | 4,400 | Gasto directo de venta |
| Gasto directo de venta | Gasto atribuible a una venta que no se capitaliza en inventario | Flete de entrega 200 | Costo de adquisición |
| Margen provisional | Margen con costos o revisiones faltantes; siempre etiquetado | "Provisional: falta flete" | Margen cerrado |
| Margen cerrado | Margen incluido en un cierre de periodo publicado (versión inmutable) | Cierre oct v1 | Margen acumulado actualizado |

## Sinónimos aceptados
sede = sucursal · contraparte = tercero = parte · establecimiento = predio · acuerdo = contrato_version · ciclo = posición.

## Denominaciones oficiales
La NOM-001-SAG/GAN-2015 usa **SINIDA**; en la operación del sistema aparece **SINIIGA** [F04–F05]. Se guarda el sistema declarado en `animal_identificacion.sistema`. Un establecimiento registrado, el propietario comercial y la sede que escribe en PostgreSQL son conceptos distintos.

## Unidades y precisión
kg NUMERIC(14,3) · tarifas NUMERIC(14,4) · importes NUMERIC(18,2) · tasas NUMERIC(9,6) · moneda MXN · cantidades enteras positivas · redondeo HALF_UP a 2 decimales en importes.
