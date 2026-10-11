# Casos de uso

Actores: Administrador (ADM), Operador (OPE), Caja (CAJ), Auditor (AUD), Sistema (SIS). Todos los comandos con efecto exigen `Idempotency-Key` y se ejecutan en el nodo dueño (OwnerDatabaseRouter).

| UC | Nombre | Actor | Flujo normal | Alternativos / errores | Invariantes | RN | Comando |
|---|---|---|---|---|---|---|---|
| UC-01 | Iniciar sesión y elegir sede | Todos | Login → lista de sedes autorizadas → selección | Credenciales inválidas 401; sede no autorizada 403; A caído: no hay login nuevo (503) | Sesión de servidor, cookie HttpOnly | RN-001 | — |
| UC-02 | Registrar contraparte/predio | OPE | Captura en A, replicación a B | Duplicado de RFC/código → 409 | Maestros sólo en A | RN-001, RN-010 | CRUD maestro |
| UC-03 | Registrar identidad animal | OPE | Alta en A con código normalizado; si es para B, esperar visibilidad en B (estado PENDIENTE_CONVERGENCIA) | Colisión → revisión central, no fusión automática | UK(E,sistema,codigo) | RN-002..004 | RegistrarIdentidadAnimal |
| UC-04 | Capturar compra | OPE | Borrador → lotes → selección de animales → versión y condiciones → pesajes → revisión | Edición concurrente → 409 por version_lock | Un animal una vez por operación | RN-007..011, RN-017 | edición de borrador |
| UC-05 | Aprobar pesaje | OPE | Adjuntar ticket → modo BRUTO_TARA/NETO_REPORTADO → composición → aprobar | Composición distinta del lote → advertencia; corrección = nuevo pesaje | Composición congelada | RN-012..016 | AprobarPesaje, RegistrarCorreccionPesaje |
| UC-06 | Confirmar compra | OPE | Valida precondiciones → crea posiciones, liquidación, asignaciones, asientos, auditoría, outbox | Precondición faltante 422; periodo cerrado 422; reintento devuelve mismo resultado | Todo o nada | RN-021, RN-026, RN-043 | ConfirmarCompra |
| UC-07 | Registrar recepción/entrega | OPE | Movimiento por posición; recepción → DISPONIBLE; entrega → CERRADA_VENTA | Posición en otro estado 422 | No genera venta ni costo | RN-020 | RegistrarRecepcion/Entrega |
| UC-08 | Reservar y confirmar venta | OPE | Selección → ReservarPosiciones → condiciones → ConfirmarVenta | Posición reservada por otra venta 409; reserva vencida → revalida | Una reserva activa por posición | RN-018, RN-019, RN-022 | ReservarPosiciones, ConfirmarVenta |
| UC-09 | Registrar y aplicar pago | CAJ | Registrar pago → validar → aplicar a liquidaciones compatibles | Excede saldo/disponible 422; carrera → 409 | Σ aplicaciones ≤ pago y ≤ saldo | RN-028..032 | Registrar/ConfirmarPago, AplicarPago |
| UC-10 | Revertir aplicación / reembolsar | CAJ+ADM | Reverso completo; reembolso consume disponible | Doble reverso 409 | Original conservado | RN-033 | RevertirAplicacion, RegistrarReembolso |
| UC-11 | Ajustar liquidación | ADM | Ajuste CARGO/ABONO con motivo y fuente | Bonificación sobre pagada → guía GOLD-07 | Liquidación inmutable | RN-023, RN-027 | AjustarLiquidacion |
| UC-12 | Registrar costo tardío | OPE | Gasto → previsualizar reparto → aprobar → asientos por destino económico | Periodo cerrado → periodo abierto | Σ asignaciones = gasto | RN-025..027 | DistribuirCosto, RegistrarCostoTardio |
| UC-13 | Dar de baja posición | ADM | Motivo (PERDIDA/MUERTE) + evidencia → BAJA | Posición vendida 422 | No borrar | RN-038 | RegistrarBajaInventario |
| UC-14 | Cerrar/reabrir periodo | ADM | Lock periodo → conciliación → versión de cierre con hash | Hechos concurrentes esperan el lock | Cierre publicado inmutable | RN-039 | CerrarPeriodo, ReabrirPeriodo |
| UC-15 | Consultar reportes | Todos/AUD | Cartera, margen, inventario con corte y antigüedad | Réplica atrasada → marca de antigüedad | Margen provisional etiquetado | RN-035, RN-036 | consultas |
| UC-16 | Consultar proveedor FDW y aceptar tarifa | OPE | Consulta fuera de transacción con locks → aceptar → snapshot local | Fuente caída: mensaje y reintento | No media liquidación | RN-042 | AceptarTarifaExterna |
| UC-17 | Revisión administrativa de documentos | ADM | Revisión de versión exacta con resultado y observación | Nueva versión no altera revisión previa | "Revisión administrativa registrada", nunca "autorizado" | RN-037 | RegistrarRevision |
| UC-18 | Validar conciliación del propietario | ADM/SIS | Conteos por dueño, huérfanos, sumatorias | Diferencias → incidente | — | RN-040, RN-043 | ValidarConciliacionDelPropietario |
| UC-19 | Simular margen | OPE | Usa la función canónica en modo preview sin mutar | — | No persiste | RN-035 | preview |
