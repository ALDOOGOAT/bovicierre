# Matriz de relaciones

Lectura de "Rango A→B": para **una** instancia de A, cuántas de B. "Mín. otro extremo" = para una instancia de B, cuántas de A. Participación: **T** total (línea doble) / **P** parcial, en el orden A / B. Condiciones por estado indican cuándo cambia el mínimo. Estado: diseñado.

| ID | A — verbo — B | Rango A→B | Mín./máx. otro extremo | Partic. A/B | Condición por estado | Identificante | Ejemplo válido | Contraejemplo (rechazado) |
|---|---|---|---|---|---|---|---|---|
| REL-01 | Empresa *administra* Sucursal | (0,N) | (1,1) | P/T | — | No | Empresa demo con sedes A y B | Sucursal sin empresa |
| REL-02 | Sucursal *tramita* Operacion | (0,N) | (1,1) | P/T | Sede inmutable en la operación | No | Venta V-0001 en sede B | Mover V-0001 a sede A con UPDATE |
| REL-03 | Parte *interviene en* Operacion | (0,N) | (1,1) | P/T | Rol = vendedor si COMPRA, comprador si VENTA | No | Productor 01 vende en C-0001 y compra en V-0007 | Operación sin contraparte |
| REL-04 | Animal *posee* Identificacion | (0,N) | (1,1) | P/T | Máx. 1 VIGENTE por sistema | No | Arete anterior INACTIVA + nuevo VIGENTE | Mismo código normalizado en dos animales de la empresa |
| REL-05 | Operacion *contiene* LoteOperacion | (0,N) en BORRADOR; (1,N) en CONFIRMADA | (1,1) | P→T al confirmar / T | Confirmar exige ≥1 lote | **Sí** (numero_lote) | C-0001 lote 1 y 2 | Confirmar sin lotes |
| REL-06 | Operacion *conserva* ContratoVersion | (0,N) en BORRADOR; CONFIRMADA referencia exactamente 1 ACEPTADA | (1,1) | P/T | Versión aceptada inmutable | **Sí** (numero_version) | v1 SUPERADA, v2 ACEPTADA | Editar precio de v2 tras aceptarla |
| REL-07 | ContratoVersion *establece* CondicionLote | (0,N); ACEPTADA cubre todos los lotes vigentes | (1,1) | P/T | Confirmar exige condición para cada lote | **Sí** (con LoteOperacion) | v2 × lote 1 a 48/kg | Lote 2 sin condición en v2 confirmada |
| REL-08 | LoteOperacion(COMPRA) *selecciona* Animal | (0,N) | Animal (0,N) histórico; máx. 1 por operación | P/P | Sólo operaciones COMPRA | Asociativa SeleccionCompra | Animal X en C-0001 lote 1 y en C-0009 (recompra) | Animal X en lote 1 y lote 2 de C-0001 |
| REL-09 | SeleccionCompra *origina* PosicionInventario | (0,1); tras confirmar (1,1) | (1,1) | P→T / T | ConfirmarCompra crea la posición | No (posición fuerte) | Selección → posición ciclo 1 | Dos posiciones desde la misma selección |
| REL-10 | Animal *participa en* PosicionInventario | (0,N) | (1,1) | P/T | Máx. 1 activa (regla temporal, índice parcial) | No | Ciclo 1 CERRADA_VENTA + ciclo 2 DISPONIBLE | Dos posiciones activas del mismo animal |
| REL-11 | LoteOperacion(VENTA) *selecciona* PosicionInventario | (0,N) | Posición (0,N) histórico | P/P | Compromiso vigente único vía reserva ACTIVA / estado vendido | Asociativa SeleccionVenta | Posición en V-0002 tras liberar reserva de V-0001 | Posición vendida en V-0001 seleccionada y confirmada en V-0002 |
| REL-12 | SeleccionVenta *mantiene* ReservaVenta | (0,N) | (1,1) | P/T | Máx. 1 ACTIVA por posición | No | Reserva EXPIRADA y nueva ACTIVA | Dos ACTIVAS de la misma posición |
| REL-13 | PosicionInventario *registra* MovimientoInventario | (0,N) | (1,1) | P/T | Inmutable; corrección por reverso | No | RECEPCION y luego ENTREGA | Borrar la recepción |
| REL-14 | LoteOperacion *recibe* Pesaje | (0,N) | (1,1) | P/T | Confirmar por kg exige pesaje APROBADO del lote | No | Ticket de origen y de destino del lote 1 | Pesaje sin lote |
| REL-15 | Pesaje *comprende* Animal | (1,N) al aprobar | Animal (0,N) | T/P | Composición congelada al aprobar; peso individual sólo si se midió | Atributo `peso_individual` (nullable) | 10 animales, sin pesos individuales | Inventar 500 kg c/u dividiendo 5,000 |
| REL-16 | Operacion *origina* Liquidacion | (0,1) en BORRADOR; (1,1) en CONFIRMADA | (1,1) | P→T / T | Una principal por operación | No (UK operación) | C-0001 → L-0001 | Segunda liquidación principal por entrega/pago |
| REL-17 | Liquidacion *desglosa* ConceptoLiquidacion | (1,N) al confirmar | (1,1) | T/T | Inmutable | **Sí** (numero_concepto) | Concepto 1 BASE 240,000 | Liquidación confirmada sin conceptos |
| REL-18 | Operacion *incurre en* GastoOperacion | (0,N) | (1,1) | P/T | Original inmutable al aprobar | No | Flete 12,000 en C-0001 | Gasto sin operación |
| REL-19 | Fuente de costo (Concepto / Gasto / Ajuste de compra) *se distribuye en* PosicionInventario mediante AsignacionCosto | Fuente (1,N) al aprobar | Posición (0,N) | T/P | Σ asignaciones = importe de la fuente; exactamente 1 fuente por asignación (XOR) | Asociativa | Flete 500 → 10 asignaciones de 50 | Asignación con gasto y concepto a la vez |
| REL-20 | Pago *se aplica a* Liquidacion mediante AplicacionPago | (0,N) | (0,N) | P/P | Σ ≤ disponible y ≤ saldo; mismo E/S/parte/moneda/dirección | Asociativa con id | Pago 600 → 400 + 200 a L-1 | Aplicar 0.01 de más |
| REL-21 | Liquidacion *recibe* AjusteLiquidacion | (0,N) | (1,1) | P/T | Periodo destino abierto | No | ABONO 100 (GOLD-07) | Modificar el total de la liquidación |
| REL-22 | Operacion *incorpora* Documento | (0,N) | (0,N) | P/P | Archivo privado | Asociativa OperacionDocumento | Ticket PDF en C-0001 | Ruta arbitraria del navegador |
| REL-23 | RevisionAdministrativa *examina* Documento | (1,N) | (0,N) | T/P | Revisión apunta a la versión exacta | Asociativa RevisionDocumento | Revisión R1 de documento v1 | Que subir v2 cambie R1 |
| REL-24 | PeriodoCierre *conserva* CierrePeriodoVersion | (0,N) | (1,1) | P/T | Versiones inmutables | **Sí** (numero_version) | v1 CIERRE, v2 REAPERTURA, v3 CIERRE | Editar v1 |
| REL-25 | PosicionInventario *acumula* AsientoValoracion | (1,N) tras confirmar compra | (1,1) | T/T | Cada asiento con periodo de registro | No | ADQUISICION 1,100; VENTA 1,100 | Asiento con signo libre |
| REL-26 | Usuario *es autorizado en* Sucursal *con* RolAplicacion (ternaria → `membresia_usuario`) | Usuario (0,N) | Sucursal (0,N), Rol (0,N) | P/P/P | — | No | Usuario U1 OPERADOR en sede B | Acceso a sede sin membresía |
| REL-27 | Animal *opera en* Sucursal (sede operadora) | (1,1) | Sucursal (0,N) | T/P | Inmutable (RN-004) | No | Animal X opera en B | Cambiar a A con UPDATE |
| REL-28 | Parte *es responsable de* Predio | (0,N) | (0,1) | P/P | — | No | — | — |
| REL-29 | Documento *reemplaza* Documento (recursiva) | (0,1) | (0,1) | P/P | Bytes aceptados nunca se sobrescriben | No | v2 reemplaza v1 | Sobrescribir v1 |
| REL-30 | AplicacionPago *revierte* AplicacionPago (recursiva) | (0,1) | (0,1) | P/P | Reverso completo, único | No | Reverso de 1,000 (GOLD-07) | Dos reversos de la misma aplicación |
| REL-31 | Pesaje *corrige* Pesaje (recursiva) | (0,1) | (0,1) | P/P | Original pasa a CORREGIDO | No | — | Editar ticket aprobado |
| REL-32 | Pago *reembolsa* Pago (recursiva) | (0,N) | (0,1) | P/P | Σ reembolsos ≤ disponible del origen | No | Reembolso 100 (GOLD-07) | Reembolsar más que el disponible |
| REL-33 | GastoOperacion *bonifica* GastoOperacion (recursiva) | (0,N) | (0,1) | P/P | Σ bonificaciones ≤ gasto original | No | Bonificación 200 sobre flete 500 | Bonificación de 600 |
| REL-34 | AjusteLiquidacion *revierte* AjusteLiquidacion | (0,1) | (0,1) | P/P | — | No | — | — |
| REL-35 | RevisionAdministrativa *revisa* Operacion **xor** Identificacion | (1,1) | (0,N) | T/P | Exactamente una referencia | No | Revisión de expediente de C-0001 | Revisión sin objeto |
| REL-36 | AsientoValoracion / AjusteLiquidacion *se imputa a* PeriodoCierre | (1,1) | (0,N) | T/P | Periodo ABIERTO al registrar | No | Ajuste de nov. con referencia a venta de oct. | Asiento en periodo CERRADO |
| REL-37 | Usuario *origina* AuditoriaEvento | (0,N) | (0,1) (SIS sin usuario) | P/P | Sólo en el nodo origen | No | — | Duplicado en apply |

## Contraste con casos difíciles
- **Borrador**: REL-05/06/16 con mínimo 0 → un borrador incompleto es válido (RN-017).
- **Error de captura**: REL-29/31 (corrige) en lugar de UPDATE.
- **Devolución física posterior**: aplazada; bloqueada explícitamente (no existe relación que la registre en el MVP).
- **Recompra**: REL-08 histórica + REL-10 (0,N) con máx. 1 activa → GOLD-05/09.
- **Muerte**: Animal.situacion = MUERTO impide REL-08 nueva (DEC-04, TEST-33).
