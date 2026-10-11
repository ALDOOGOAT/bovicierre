# ADR-006: Replicación bidireccional, bootstrap y recuperación
- Estado: propuesto · 2026-10-10 · Requisito: AC-06
## Contexto
Se requiere M–M con dos nodos escritores; PostgreSQL 18 ofrece replicación lógica con `origin = none`.
## Alternativas
1. Streaming físico (un solo escritor) — no cumple M–M.
2. Extensiones de terceros (pglogical, BDR/PGD) — licencia/soporte, más complejidad.
3. **Replicación lógica nativa bidireccional con publicaciones explícitas y `origin = none`.**
## Decisión
Opción 3 con el bootstrap de `docs/database/replication-and-fdw.md` §3 (`copy_data = false` sólo en bases vacías). Recuperación: slots monitoreados, `max_slot_wal_keep_size`, runbook de resincronización.
## Consecuencias
+ Nativo y demostrable. − DDL coordinado; triggers/FK no se verifican en apply → conciliación obligatoria.
