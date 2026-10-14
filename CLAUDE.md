# BoviCierre — instrucciones para Claude

Especificación maestra: `docs/spec/megaprompt.md` (no resumirla; las reglas canónicas viven en los documentos de `docs/`). Estado actual y siguiente tarea: `docs/status.md`.

## Reglas no negociables
- Importes con NUMERIC/BigDecimal, nunca float/double. Redondeo HALF_UP a 2 decimales.
- El cálculo que confirma importes vive en funciones SQL canónicas; Java no recalcula con otra fórmula; el navegador nunca envía totales.
- Un único evento económico por operación: CONFIRMADA. Entrega, pago o PDF no generan venta, deuda ni costo.
- Hechos confirmados son inmutables: correcciones con reverso/ajuste/nueva versión, nunca UPDATE/DELETE.
- Escritor exclusivo por agregado: maestros en nodo A; locales en el nodo de su sede. Sin failover automático de dueño.
- `origin = none` no resuelve conflictos; validar en origen y conciliar.
- Pruebas de BD con PostgreSQL real (Testcontainers), nunca H2. Las pruebas comparan contra cifras GOLD fijas.
- No inventar entrevistas, clientes, resultados, firmas ni URLs. No atribuir trabajo a Aldo/Jared que no hicieron.
- Datos de ejemplo sintéticos (prefijo DEMO); sin secretos en repo, logs ni grafo.
- Casillas `[x]`: verificación técnica local con evidencia, por instrucción del usuario del 12-oct-2026. La revisión humana se registra por separado; no declarar Kanban Hecho ni aprobación humana por agentes. README y backlog deben coincidir.

## Mapa de lectura por tarea
| Si la tarea toca… | Lee primero |
|---|---|
| Reglas, estados, cálculos | `docs/domain/business-rules.md`, `docs/domain/states-and-calculations.md` |
| Tablas, migraciones | `docs/database/relational-model.md`, `docs/database/data-dictionary.md`, `docs/database/administration.md` |
| Replicación, FDW, Pgpool | `docs/database/replication-and-fdw.md`, ADR-005/006/007 |
| API | `docs/api/openapi.yaml` |
| Frontend | `docs/ui/flows-and-screens.md` |
| Decisiones | `docs/architecture/adr/`, `docs/research/evidence-register.md` (DEC-xx) |
| Plan | `docs/project/backlog.md`, `docs/project/roadmap.md` |

## Comandos verificados
```bash
npx -y @redocly/cli@1.34.5 lint docs/api/openapi.yaml   # válido al 2026-10-10
```
Implementación disponible: `make academic` (o `BOVI_INSTALL=vacia BOVI_EMPRESA=… make academic` en volúmenes nuevos), `make demo`, `make demo-profesor`, `make verify-academic`, `make evidence`, `make release-academic`, `make verify-docs`, `make verify-api` (Caddy15180), `make backup` y `make restore-check` con BACKUP_DIR privado. `make verify-release-local`: puerta local en serie (docs, frontend, backend con HTTP/Testcontainers, SQL, inmutabilidad, E2E, seguridad); falla si algo obligatorio falla o se omite. Evidencia/alcance actual en `docs/status.md`; no confundir estas comprobaciones con aceptación humana.

## Skills de proyecto (`.claude/skills/`)
`bovicierre-run` (arranque/diagnóstico), `bovicierre-db-verify` (SQL, réplica, Pgpool, FDW), `bovicierre-ux` (pantallas y validación visual), `bovicierre-release-academic` (puerta, evidencia, paquete). Siguiente migración: V26.

## Al terminar cada tarea
1. Actualizar `docs/status.md`, la documentación afectada y `docs/traceability.md`.
2. Registrar evidencia real en `docs/testing/evidence.md`.
3. Si cambió contexto relevante: `/graphify . --update` (documentos) o `graphify update .` (sólo código) y registrar en `docs/knowledge/graph-status.md`.
4. Nuevos IDs (RN, ENT, REL, TEST, TASK, DEC) sin reutilizar retirados.

# graphify
Este proyecto usa graphify (`graphifyy` 0.9.49). Si existe `graphify-out/`, úsalo para preguntas de arquitectura antes de buscar a ciegas; verifica las aristas contra los archivos fuente.
