# Sustento teórico conectado a decisiones

Cada fila liga un concepto a una decisión concreta de BoviCierre, su fuente y la evidencia del proyecto que lo demostrará. "Pendiente" = evidencia aún no producida.

| Fundamento | Decisión en BoviCierre | Fuente | Evidencia en el proyecto | Estado |
|---|---|---|---|---|
| Modelo E-R de Chen | Separar Animal (identidad) de PosicionInventario (ciclo); entidades débiles LoteOperacion, ContratoVersion, ConceptoLiquidacion, CondicionLote | F12, F14 | `docs/database/conceptual-model.md`, láminas MER | diseñado (texto); diagramas pendientes |
| Modelo relacional de Codd | Relaciones con PK/FK compuestas por empresa/sede; restricciones declarativas | F13 | `relational-model.md`, migraciones | diseñado |
| Dependencias funcionales y normalización | Contraparte fuera de operación; condiciones por versión y lote; aplicaciones como relación propia | F15 | `normalization.md` (3 ejemplos + BCNF) | diseñado |
| Integridad y transacciones | Confirmar = todo o nada; locks en orden estable | F20, F21 | Comandos PL/pgSQL + pruebas de dos conexiones | pendiente |
| Replicación y propiedad de escritura | Escritor exclusivo por agregado; maestros en A | F22–F26 | ADR-005/006, prueba de partición | pendiente |
| Trazabilidad comercial | Expediente navegable animal→lote→pesaje→condición→liquidación→pago | — | UC-17, pantalla 10 | pendiente |
| Costeo identificado (gestión) | Costo por posición; inventario separado de costo vendido | F48 | GOLD-02, GOLD-06, asientos | diseñado |
| Devengo gerencial vs. flujo monetario | Obligación ≠ pago ≠ aplicación ≠ entrega | F48 | GOLD-01, GOLD-04, GOLD-07 | diseñado |
| Canvas y validación | Hipótesis versionadas; guion de entrevistas | F03 | `docs/business/*` | diseñado; sin datos |
| Economía de contribución | Equilibrio = ⌈fijos / contribución⌉ | F49 | `unit-economics.md` | ilustrativo |
| Kanban | WIP 1 por persona, columnas Backlog→Hecho | F16 | `docs/project/roadmap.md` | diseñado |
| ADR | Decisiones con alternativas y consecuencias | F17 | `docs/architecture/adr/` | diseñado |

## ACID local ≠ consistencia inmediata entre réplicas
Una transacción en A es atómica, consistente, aislada y durable **en A**. B recibe el cambio después (replicación lógica asíncrona). Caso de doble venta: si una venta de la sede B pudiera reservar una posición consultando su copia local mientras A —con una réplica atrasada— reservara la misma, ambas transacciones serían ACID localmente y aun así el negocio vendería dos veces. BoviCierre lo evita **por propiedad**, no por replicación: la posición pertenece a un solo nodo (el de su sede), y sólo ese nodo reserva y confirma, con `FOR UPDATE` y un índice único parcial. La réplica sirve para lectura y consolidado, nunca para autorizar (RN-040).

## Normalizar no elimina snapshots
`liquidacion.snapshot_contraparte_nombre` o la fórmula aceptada en `condicion_lote` no son redundancia del catálogo: representan el hecho "así se aceptó el día X", que depende funcionalmente de la liquidación, no de la contraparte actual. Renombrar la contraparte no debe propagarse (FK sin `ON UPDATE CASCADE` sobre datos descriptivos; los snapshots no tienen FK).

## Límites declarados
El costeo identificado y la fecha de reconocimiento son **políticas de información gerencial** del producto. No se afirma cumplimiento de US GAAP, IFRS/IAS 2/IAS 41 ni reglas fiscales mexicanas. El software no es contabilidad financiera ni fiscal completa.
