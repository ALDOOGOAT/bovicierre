# Estados, reconocimiento y cálculos

## 1. Máquinas de estado (campos independientes; ningún campo mezcla venta, pago, entrega y revisión)

### Operación (`operacion.estado`)
| De | A | Comando | Precondición |
|---|---|---|---|
| BORRADOR | ACORDADA | AcordarOperacion | Contraparte, ≥1 lote, versión de condiciones registrada |
| ACORDADA | BORRADOR | ReabrirBorrador | Sin reservas activas; versión nueva |
| BORRADOR/ACORDADA | CONFIRMADA | ConfirmarCompra / ConfirmarVenta | RN-017; venta: reservas ACTIVAS vigentes |
| BORRADOR/ACORDADA | CANCELADA | CancelarOperacion | Libera reservas; sin liquidación |
| CONFIRMADA | ANULADA | AnularVentaAntesDeEntrega | Ninguna posición entregada; periodo abierto; produce contramovimientos (§5) |

### Reserva (`reserva_venta.estado`)
ACTIVA → CONSUMIDA (ConfirmarVenta) · ACTIVA → LIBERADA (LiberarReserva/Cancelar) · ACTIVA → EXPIRADA (ExpirarReserva cuando `vence_en ≤ now()`, ejecutado por comando, no por índice).

### Posición (`posicion_inventario.estado`) — DEC-01/02/03
| Estado | Inventario gerencial | Vendible | Llega desde |
|---|---|---|---|
| PENDIENTE_RECEPCION | valuado (+C) | No | ConfirmarCompra cuando la política exige recepción |
| DISPONIBLE | valuado | Sí | ConfirmarCompra / RegistrarRecepcion / anulación de venta |
| VENDIDA_PENDIENTE_ENTREGA | 0 (costo ya reconocido en venta) | No | ConfirmarVenta |
| CERRADA_VENTA | 0 | No (terminal) | RegistrarEntrega completa |
| BAJA | 0 (pérdida reconocida) | No (terminal) | RegistrarBajaInventario con motivo |

"Reservada" es **derivada**: posición DISPONIBLE con reserva ACTIVA. Posición activa (índice único) = estados PENDIENTE_RECEPCION, DISPONIBLE, VENDIDA_PENDIENTE_ENTREGA.

### Animal (`animal.situacion`) — DEC-04
VIGENTE · IDENTIDAD_EN_REVISION (no admite nuevos compromisos) · MUERTO (no admite recompra; corrección sólo por procedimiento autorizado con reverso).

### Liquidación
BORRADOR (previsualización, no persistida como hecho) → CONFIRMADA (inmutable). Ajustes y reversos son registros nuevos.

### Entrega (`operacion.estado_entrega`, derivado de movimientos)
PENDIENTE → PARCIAL → COMPLETA.

### Pago
REGISTRADO → VALIDADO → (REVERTIDO por contramovimiento con evidencia). La aplicación es una relación separada con su propio reverso.

### Periodo
ABIERTO → CERRADO (crea `cierre_periodo_version` n) → ABIERTO por ReabrirPeriodo (crea versión n+1 de tipo REAPERTURA).

## 2. Política de reconocimiento gerencial (§6.1)
**CONFIRMADA es el único evento económico** de una operación. ConfirmarCompra/Venta crea en una transacción: liquidación principal confirmada (= obligación), efectos de inventario/valoración, auditoría y outbox. Entrega, pago y PDF no reconocen nada. Es una política operativa del producto, no un dictamen contable [F48].

## 3. Política de valoración (asientos)
| Hecho | Δ inventario | Δ costo de venta | Δ pérdida |
|---|---:|---:|---:|
| Adquisición a costo C | +C | 0 | 0 |
| Venta reconocida de la posición | −C | +C | 0 |
| Costo tardío δ, posición capitalizada | +δ | 0 | 0 |
| Costo tardío δ, venta reconocida | 0 | +δ | 0 |
| Baja por pérdida | −C | 0 | +C |
| Costo tardío δ, posición dada de baja | 0 | 0 | +δ |
| Anulación de venta antes de entrega | +C_neto | −C_neto | 0 |

Signos derivados de `asiento_valoracion.clase`; el usuario nunca introduce un signo libre. Bonificación = efecto contrario, sin dejar costo acumulado negativo.

## 4. Fórmulas
```text
neto_kg = bruto_kg − tara_kg                          (tara ≤ bruto)
variacion_kg = peso_inicial − peso_final               (negativa = incremento, se conserva)
variacion_pct = 100 × variacion_kg / peso_inicial      (peso_inicial > 0)
base_kg = kg_liquidables × precio_kg
base_cabeza = n_animales × precio_cabeza
total_comercial = base + cargos_pactados − bonificaciones_pactadas
saldo_obligacion = total + Σ ajustes CARGO − Σ ajustes ABONO − Σ aplicaciones netas
disponible_pago = importe − Σ aplicaciones netas − Σ reembolsos vinculados
margen = venta_neta_reconocida − costo_posiciones_vendidas − gastos_directos_venta
```
Redondeo HALF_UP a 2 decimales al materializar cada importe persistido (concepto, asignación, ajuste). Reparto: valor exacto → redondeo → residuo en centavos a las primeras filas por `posicion_id` ascendente.

## 5. Casos GOLD (datos ficticios; esperados fijos para las pruebas)

| Caso | Datos | Resultado esperado |
|---|---|---|
| GOLD-01 | Compra 5,000 kg × 48 = 240,000; gastos adquisición 12,000; venta 4,900 kg × 60 = 294,000; gastos directos venta 8,000; anticipo 50,000 | Costo vendido 252,000; margen 34,000; saldo por cobrar 244,000; variación 100 kg / 2% **sin descuento automático** |
| GOLD-02 | 10 animales × 1,000; gasto 1,000 por cabeza; vende 4 × 1,600; gasto directo 200 | Costo/posición 1,100; venta 6,400; costo vendido 4,400; margen 1,800; inventario 6,600 |
| GOLD-03 | Asignar 1.00 entre 3 posiciones iguales | 0.34, 0.33, 0.33 por orden de id; suma 1.00 |
| GOLD-04A | Obligación 1,000; pago 600; aplicaciones 400 y 200 | Saldo 400; disponible 0; reintento no descuenta; aplicar 0.01 más falla |
| GOLD-04B | Obligación 1,000; pago 1,200; aplicación 1,000 | Saldo 0; disponible 200; no es venta adicional |
| GOLD-05 | Animal vendido y entregado, luego recomprado | Nueva posición ciclo 2; nunca 2 posiciones activas |
| GOLD-06 | Sobre GOLD-02: flete tardío 500 (50 × 10); luego bonificación 200 del mismo gasto | Tras flete: costo vendido 4,600, inventario 6,900, margen 1,600. Tras bonificación (−20 × 10): costo vendido 4,520, inventario 6,780, margen 1,680. Deuda con vendedor/comprador sin cambio |
| GOLD-07 | Liquidación 1,000; pago 1,000 aplicado; bonificación 100 | Reverso aplicación 1,000 + aplicación 900 + ajuste ABONO 100: obligación 900, aplicaciones netas 900, saldo 0, disponible 100; reembolso 100 → disponible 0 |
| GOLD-08 | Posición sin venta, costo 1,100, baja por pérdida; luego costo 50 | Inventario −1,100 → 0; pérdida 1,100 → 1,150; sin venta ni cuenta por cobrar |
| GOLD-09 | Recompra del mismo animal | Ciclo anterior conserva costo; ciclo nuevo con su propio costo |
| GOLD-10 | Costo concurrente con cierre de periodo | Ambos bloquean la fila del periodo; el costo entra antes del corte o falla BV025 sin efecto; nueva intención reconoce explícitamente en periodo abierto; nunca retroactivo |
| ANUL-01 (TEST-35) | Costo de venta 1,100 + ajuste tardío 100; anulación antes de entrega | Restituye 1,200 a inventario; costo neto de la venta anulada 0 |

Nota GOLD-06: el megaprompt da "80 de costo vendido y 120 de inventario" para la bonificación de 200; el margen 1,680 = 1,600 + 80 es consistente con eso.
