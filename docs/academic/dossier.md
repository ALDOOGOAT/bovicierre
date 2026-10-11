# Dossier local de BoviCierre

Datos sintéticos, empresaDEMO. La imagen original de rúbrica y aceptación del profesor siguen pendientes; [matriz](requirements-matrix.md) identifica su procedencia. No se afirma piloto contratado ni certificación sanitaria.

1. [Problema/oferta](../business/business-model.md), [propuesta piloto](../business/pilot-proposal.md) e [investigación](../research/evidence-register.md): tarifa3000/sede es hipótesis, no ingreso validado.
2. [Modelo conceptual](../database/conceptual-model.md), [matriz relaciones](../database/relationship-matrix.md), [diagramas editables/exportados](../diagrams/README.md), [relacional](../database/relational-model.md), [diccionario](../database/data-dictionary.md), [normalización](../database/normalization.md).
3. [AdministraciónSQL](../database/administration.md): roles, constraints, comandos/locks, triggers y privilegios; autoridad física `db/migrations/`.
4. [POO real](oop-solid-patterns.md), [arquitectura](../architecture/overview.md) y [ADR](../architecture/adr/): JavaHTTP y SQL confirmado; no clases ficticias para la exposición.
5. [Replicación/FDW](../database/replication-and-fdw.md): A/B escritores de conjuntos disjuntos, Pgpoolraw y proveedorDEMO; mismohost no alta disponibilidad.
6. [Pruebas](../testing/evidence.md), [guion](../testing/demo-script.md), [manual usuario](../ui/user-manual.md): recorrido real y cifrasGOLD. Identificar privilegio/constraint/trigger/transacción como comprobaciones distintas.
7. [Recuperación](../runbooks/backup-restore.md), [rendimiento](../testing/evidence.md) y [handoff](../implementation/handoff.md): usar resultados registrados, no promesas de RPO/RTO/PITR.
8. [BacklogA/J](../project/backlog.md) y [Graphify](../knowledge/graph-status.md): responsabilidad humana y ejecución asistida separadas, sin casillasHecho por revisión de agentes.

Para exponer: mostrar un registro real, abrir su liquidación/expediente, explicar costo/saldo/margen; ejecutar una negativa de constraint, otra de trigger como rol controlado, rollback y carreraun ganador; cerrar con topología y ensayo recuperado. El manual de comandos y resultados se actualiza con cada incremento.
