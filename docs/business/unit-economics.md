# Economía unitaria del SaaS

Estado: **ilustrativo**. Ninguna cifra es medida. Moneda MXN, periodo mensual salvo indicación.

## Fórmulas
```text
MRR = Σ mensualidades recurrentes activas            (no incluye cobros únicos, IVA trasladado ni volumen de ganado)
Ingreso de implementación = Σ cobros únicos de configuración  (se reporta aparte del MRR)
Contribución por cliente = mensualidad − costo variable mensual de atenderlo
Equilibrio operativo = ⌈costos fijos mensuales / contribución por cliente⌉   (sólo si contribución > 0)
CAC = gasto atribuible a adquirir clientes / clientes nuevos adquiridos       (por periodo)
```
Si la contribución es ≤ 0 el equilibrio no existe: subir precio o bajar costo variable antes de vender.

## Ejemplo ilustrativo (empresas de una sede)
| Variable | Valor | Qué incluye |
|---|---:|---|
| Mensualidad | 2,000 | Suscripción 1 sede |
| Costo variable por cliente | 550 | Parte de servidor/almacenamiento/respaldo + horas de soporte asignadas (supuesto) |
| Contribución | 1,450 | 2,000 − 550 |
| Costos fijos mensuales | 6,000 | Infraestructura base, dominio, herramientas (supuesto) |
| Equilibrio operativo | 5 clientes | ⌈6,000 / 1,450⌉ = ⌈4.14⌉ |
| Resultado con 5 clientes | 1,250 | 10,000 − 2,750 − 6,000 |

**Los 1,250 no son utilidad neta.** No incluyen: sueldo/valor del tiempo de Aldo y Jared, adquisición de clientes (CAC), impuestos, amortización del desarrollo ni contingencias.

Rango de validez supuesto: 1–10 clientes de una sede sobre un VPS de 4 vCPU/8 GB (referencia USD 48/mes [F33], sin convertir a MXN hasta documentar tipo de cambio). Por encima, servidores y soporte crecen en escalón.

## Presupuesto editable (plantilla)
| Concepto | Tipo | Cantidad | Costo unitario | Total mensual | Fuente |
|---|---|---:|---:|---:|---|
| VPS 4 vCPU / 8 GB | Fijo | 1 | USD 48 | por cotizar en MXN | F33 (verificar) |
| Respaldo fuera del host | Fijo | — | por cotizar | — | pendiente |
| Almacenamiento de documentos | Variable | GB | por cotizar | — | pendiente |
| Dominio + DNS | Fijo | 1 | por cotizar | — | pendiente |
| Tiempo de Aldo (valor de mercado supuesto) | Fijo | h/mes | por definir | — | supuesto del equipo |
| Tiempo de Jared (valor de mercado supuesto) | Fijo | h/mes | por definir | — | supuesto del equipo |
| Soporte por cliente | Variable | h/cliente | valor hora | — | medir en piloto |
| Adquisición (viajes, demos) | CAC | — | — | — | medir |

Regla: actualizar con cotizaciones reales antes de enviar una propuesta comercial.

## Escenarios a recalcular cuando haya datos
| Escenario | Mensualidad | Costo variable | Fijos (incl. tiempo del equipo) | Equilibrio |
|---|---:|---:|---:|---|
| Conservador | 2,000 | por medir | por medir | por calcular |
| Medio | 3,000 | por medir | por medir | por calcular |
| Alto | 4,000 | por medir | por medir | por calcular |
