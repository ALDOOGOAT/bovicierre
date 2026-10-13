# Revisión competitiva enfocada (13-oct-2026)

Alcance: dos páginas públicas de presentación, consultadas el 13-oct-2026 sin cuenta, sin formularios, sin cookies ni endpoints privados. Son **afirmaciones comerciales públicas**, no una auditoría de sus aplicaciones; no se atribuyen pantallas internas que no se vieron. Las decisiones son diseño propio de BoviCierre, implementado contra su API real y probado.

| Fuente | Nivel de acceso | Observación pública (resumen) |
|---|---|---|
| C1 EngordaMax `https://engordamax.mx/` | Landing pública | Módulo “Compras de ganado”: lotes con fecha, origen, raza, cabezas, precio, flete y gastos de compra; peso de embarque y de llegada en kg, merma %; “costo real por kg incluyendo gastos (flete)”. Comercialización en pie/canal/cortes, “utilidad real por lote”. No menciona tablero de pendientes ni pagos. |
| C2 Agryxo · Agroapp `https://www.agryxo.com/` | Landing pública | Módulos: compras y ventas por lotes con márgenes; lotes y animales con estados; cuentas por cobrar y pagar con fechas e historial; cobros y abonos con conciliación de cartera; “Carteras y dashboard” con visión consolidada de saldos; usuarios y roles. Muestra pestañas Compras/Ventas/Cartera en “Agroapp en acción”. |

## Matriz problema → decisión

| Problema en BoviCierre (antes) | Fuente | Observación usada | Decisión propia | Archivos | Prueba y resultado |
|---|---|---|---|---|---|
| La Bandeja sólo listaba operaciones; no decía qué atender primero | C2 (cartera + dashboard) | Agrupar el trabajo comercial con saldos visibles | Tablero “Pendientes de la sede” con **conteos del servidor**: ganado por recibir, entregas pendientes, por cobrar, por pagar e incidencias de sincronización; cada tarjeta lleva a su pantalla. Sin sumas de dinero en el navegador (el dinero lo calcula SQL); error o 403 se muestran como “—”, nunca 0 | `frontend/src/screens.tsx` (`TaskBoard`, `TaskCount`), `App.tsx` | `academic.spec.ts` “bandeja”: conteos iguales a la API; PASS |
| Primer ingreso sin explicación del orden de trabajo | C2 (estructura por módulos) | Separación compra/venta/cartera | Guía de 4 pasos (contraparte → borrador → recibir/entregar → cobrar/pagar) que se cierra y se recuerda por navegador | `screens.tsx` (`FirstSteps`) | `academic.spec.ts`: abierta primera vez, cerrada al volver; PASS |
| Recepción/entrega exigían pegar posiciones | C1/C2 (lotes y estados) | El usuario piensa en lotes/animales, no en claves | Abrir la operación y marcar animales por arete (`PhysicalMovement`, `AnimalChecklist`); V19 filtra posiciones por operación | `screens.tsx`, `V19__consultar_operacion_identificacion.sql` | `closure.spec.ts`, `keyboard.spec.ts`; PASS |
| Selección de ganado limitada a 100 sin paginar | C2 (inventario de lotes) | Inventario grande por lote | Páginas de 50, selección que sobrevive a páginas y búsquedas, sin duplicados, aviso de seleccionados fuera de vista | `screens.tsx` (`LotEditor`) | `academic.spec.ts` “lote”: 51+1 animales, 3 seleccionados persistidos; PASS |
| Costo de compra con flete | C1 (costo real con flete) | Flete y gastos forman parte del costo | Ya existía: gasto capitalizable repartido por cabeza/kg/valor con vista previa del servidor; GOLD-ACAD-01 lo comprueba (11000 por cabeza) | `gold_acad.py` | PASS |
| Merma/deducción | C1 (merma %) | Peso y merma son conceptos distintos | Se mantiene “Deducción pactada en %” separada del peso del ticket; no se añade cálculo de merma automática (fuera del alcance) | — | — |

No adoptado: nutrición, corral, medicamentos, canal/cortes (C1) y multi-producto/SaaS (C2) quedan fuera del cierre académico (§8.6).
