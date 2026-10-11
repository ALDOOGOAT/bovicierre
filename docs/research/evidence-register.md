# Registro de evidencia y decisiones

Clasificación: **HECHO** (comprobado por Claude con comando o fuente leída, con fecha) · **HIP** (hipótesis de negocio a validar) · **PROP** (decisión propuesta de diseño) · **PEND** (pendiente de información externa).

## Hechos comprobados

| ID | Hecho | Cómo se comprobó | Fecha |
|---|---|---|---|
| EV-01 | El repositorio estaba vacío (sin commits, sólo `.git`) | `ls -la`, `git log` | 2026-10-10 |
| EV-02 | Herramientas instaladas y versiones (ver `docs/architecture/versions.md`) | `--version` de cada binario | 2026-10-10 |
| EV-03 | graphify instalado es el paquete `graphifyy` 0.9.49 | `pipx list` | 2026-10-10 |
| EV-04 | `.graphifyignore` usa sintaxis gitignore y se suma a `.gitignore` | lectura de `graphify/detect.py` instalado | 2026-10-10 |
| EV-05 | Spring Boot 4.1.1 admite Java 17–26 y Maven ≥3.6.3 | F18 | 2026-10-10 |
| EV-06 | Vite actual (8.x) requiere Node 20.19+ o 22.12+ | F46 | 2026-10-10 |
| EV-07 | Pgpool-II 4.7.3 y 4.6.8 publicadas el 2026-09-29 | F50 | 2026-10-10 |
| EV-08 | Graphviz y draw.io CLI no están instalados | `command -v` | 2026-10-10 |

## Hipótesis de negocio (no validadas)

| ID | Hipótesis | Cómo se validará | Estado |
|---|---|---|---|
| HIP-01 | Comercializadores/acopiadores con 1–2 sedes tienen dolor frecuente al conciliar liquidaciones | 5 entrevistas (`docs/business/validation-plan.md`) | sin datos |
| HIP-02 | Disposición a pagar MXN 2,000–4,000/sede/mes | Discusión de piloto con precio | sin datos |
| HIP-03 | La diferenciación valiosa es la liquidación explicable con evidencia | Ranking de problemas en entrevistas | sin datos |
| HIP-04 | Costo variable ≈ MXN 550/cliente/mes y fijos ≈ 6,000/mes | Cotizaciones reales | ilustrativo |

No existen entrevistas, clientes, pilotos ni resultados de pruebas a la fecha.

## Contradicciones y huecos detectados en el megaprompt, con decisión

| ID | Conflicto / hueco | Decisión (PROP) | Artefactos afectados |
|---|---|---|---|
| DEC-01 | §5.3 lista posición RESERVADA, pero la reserva vive en `reserva_venta` (ENT-15) con UNIQUE parcial ACTIVA: dos fuentes de verdad | El estado "reservada" se **deriva** de una reserva ACTIVA; `posicion_inventario.estado` no incluye RESERVADA. La UI lo muestra como estado calculado | states-and-calculations, data-dictionary, openapi |
| DEC-02 | §8.3 exige posición "pendiente" si falta recepción; §5.3 no tiene ese estado | Agregar estado `PENDIENTE_RECEPCION` (inventario valuado, no vendible) | states, ENT-13 |
| DEC-03 | §5.3 usa CERRADA para todo cierre, pero TEST-33 distingue muerte de venta | Estados terminales separados: `CERRADA_VENTA` (vendida y entregada) y `BAJA` (pérdida/muerte, con `motivo_baja`) | states, ENT-13, RN-038 |
| DEC-04 | Recompra tras muerte (TEST-33): el bloqueo debe vivir en el animal, no sólo en la posición | `animal.situacion` ∈ {VIGENTE, MUERTO, IDENTIDAD_EN_REVISION}; ConfirmarCompra rechaza animal MUERTO | ENT-08, RN-038 |
| DEC-05 | No hay tabla "obligacion"; RN-021/022 hablan de obligación | La obligación **es** la liquidación principal confirmada más sus ajustes; saldo derivado. Dirección: compra→POR_PAGAR, venta→POR_COBRAR | ENT-22, ENT-26, RN-028..031 |
| DEC-06 | Pago con "dirección compatible" (RN-030) sin campo | `pago.tipo` ∈ {COBRO, PAGO}; COBRO sólo aplica a liquidaciones de VENTA, PAGO a COMPRA | ENT-25 |
| DEC-07 | Maestros escritos en A con `sucursal_id` = B (§9.4): S no indica escritor | Columnas `nodo_origen` y `propietario_despacho` derivadas por el comando y verificadas por trigger en auditoría, outbox, documento y revisión | ENT-27, 29, 30, 40 |
| DEC-08 | GOLD-01: gastos directos de venta (8,000) no forman parte de la deuda del comprador | Gasto directo de venta es `gasto_operacion` clasificación DIRECTO_VENTA; afecta margen, no la liquidación con la contraparte | GOLD-01, RN-025 |
| DEC-09 | Reverso parcial de aplicación ambiguo | MVP sólo reverso **completo** de una aplicación; corrección parcial = reverso + nueva aplicación (§8.3) | ENT-26, GOLD-07 |
| DEC-10 | Fecha de inicio del megaprompt (11-oct) vs. trabajo real iniciado 10-oct | Se registra fecha real; calendario no cambia | roadmap |
| DEC-11 | `seleccion_venta` debe garantizar "un compromiso comercial vigente por posición" entre operaciones distintas | Garantía vía reserva ACTIVA única + transición de posición a VENDIDA_PENDIENTE_ENTREGA bajo lock en ConfirmarVenta; la selección en borrador no compromete | ENT-12, ENT-15, RN-018 |

## Pendientes externos

| ID | Pendiente | Quién lo resuelve |
|---|---|---|
| PEND-01 | Interpretación de M–M (¿misma fila?) | Profesor |
| PEND-02 | Imagen original de la rúbrica en el repo | Aldo |
| PEND-03 | Credenciales/servidor para staging | Aldo |
| PEND-04 | Disponibilidad real de horas de Aldo y Jared | Equipo |
