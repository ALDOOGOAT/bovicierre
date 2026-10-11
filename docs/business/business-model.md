# Modelo de negocio (hipótesis versionadas)

Versión 0.1 · 2026-10-10 · Estado: **hipótesis**, sin validación con clientes. Marco: Business Model Canvas [F03].

## Qué es y qué no es
BoviCierre es un SaaS B2B para comercializadores recurrentes de bovinos en pie y centros de acopio que compran y venden **por cuenta propia**. Reconstruye cada negocio: animales, pesos, condiciones pactadas, gastos asignados, cálculo de la liquidación y saldos por cobrar/pagar.

- El dinero del ganado es del cliente; **no** es ingreso de BoviCierre.
- No custodia dinero, no origina crédito, no timbra CFDI, no autoriza movilizaciones.
- Propuesta de valor a validar: *"Explicar cada liquidación y conciliar inventario, saldos y margen con la evidencia que respalda el trato."*

## Canvas
| Bloque | Hipótesis | Qué falta validar | Evidencia esperada |
|---|---|---|---|
| Segmentos | Comercializadores/acopiadores con 1–2 sedes, operaciones recurrentes, precio por kg o cabeza, pagos parciales | Frecuencia, complejidad y capacidad de contratación | Entrevistas E1–E5 |
| Propuesta de valor | Liquidación explicable, saldos conciliados, margen por operación | Cuál problema es prioritario | Ranking en entrevistas |
| Canales | Demostración directa, referencias y contactos del sector | Costo y conversión por canal | Registro de contactos |
| Relación | Implantación acompañada, capacitación, soporte con horario | Horas de soporte por cliente | Bitácora del piloto |
| Ingresos | Configuración inicial + suscripción por sede | Disposición a pagar y permanencia | Propuesta firmada (no existe) |
| Recursos clave | Software, reglas validadas, infraestructura, equipo de 2 | Capacidad operativa | Registro de horas |
| Actividades | Desarrollo, operación, respaldos, soporte, ventas | Esfuerzo recurrente real | Bitácora |
| Socios | Cliente piloto, asesor contable/pecuario, proveedores **cuando exista acuerdo** | Acuerdos efectivos | Ninguno firmado |
| Costos | Trabajo, alojamiento, almacenamiento, respaldos, soporte, ventas, administración | Presupuesto medido | `unit-economics.md` |

"Socios" son posibles, no alianzas firmadas.

## Competencia
EngordaMax [F01] anuncia compras, pesajes, merma, costos y utilidad; Agryxo/Agroapp [F02] anuncia compraventa, inventario, cartera, margen y control contra doble venta. Son referencias competitivas, no pruebas de demanda. Diferenciación propuesta (a validar): mesa de cierre comercial con evidencia original, condiciones versionadas, costo por ciclo de inventario y expediente navegable. No se afirmará ser "el primero", "el único" ni "eliminar el fraude".

## Oferta comercial a probar
| Concepto | Propuesta | Nota |
|---|---|---|
| Suscripción | MXN 2,000–4,000/sede/mes (referencia de ejemplos: 2,000) | Rango de investigación |
| Configuración y migración inicial | Cotización por horas, complejidad y calidad de datos | Inventario histórico requiere módulo de apertura (aún no existe) |
| Integraciones especiales | Alcance y presupuesto aparte | — |
| Comisión sobre ganado | No | — |
| Custodia de dinero | No; sólo registro y conciliación | — |

La suscripción debe declarar: sedes, usuarios, almacenamiento, exportación, horario y límites de soporte. Antes de un piloto real se definen por escrito: cancelación, entrega/exportación de datos, retención, aviso de privacidad [F10] y responsabilidades.

## Hitos comerciales separados
1. **Entrega académica (31-oct)**: requisitos y evidencia reproducible. No demuestra product–market fit.
2. **Piloto controlado**: cliente, alcance, datos autorizados, respaldo/recuperación y soporte definidos.
3. **Venta recurrente**: problema y precio validados, contrato, facturación del servicio (CFDI vía PAC [F09]), operación medida.

## Contribución social (hipótesis de impacto)
Transparencia de pagos a productores, conservación de evidencia comercial y trazabilidad administrativa. Se medirá en el piloto; el software no sustituye a la autoridad sanitaria, la acreditación de propiedad ni la revisión profesional.
