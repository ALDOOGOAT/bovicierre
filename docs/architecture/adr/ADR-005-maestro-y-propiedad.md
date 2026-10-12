# ADR-005: Maestro de identidad en A y propiedad de escritura inmutable
- Estado: propuesto · 2026-10-10 · Requisito: AC-06 · Reglas: RN-003, RN-004, RN-040, RN-041
## Contexto
Dos escritores independientes podrían dar dos UUID al mismo arete; la replicación lógica no garantiza unicidad global.
## Alternativas
1. Unicidad por nodo — permite duplicados entre nodos.
2. Escritura libre en ambos + resolución de conflictos — no existe resolución de negocio segura para inventario/dinero.
3. **Maestros sólo en A; agregados locales sólo en el nodo de su sede; sede del animal inmutable.**
## Decisión
Opción 3, con `nodo_origen` en cada fila y el trigger de propiedad (implementado como `guarda_propietario` → `trg_propietario`; nombre corregido el 12-oct-2026, DIV-15). Sin failover automático de dueño. Transferir un animal de sede queda fuera (requiere fencing y otro ADR).
## Consecuencias
+ Sin conflictos de negocio por diseño. − Si A cae no hay maestros nuevos ni login nuevo.
