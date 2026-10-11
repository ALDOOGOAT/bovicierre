# Plan de ejecución (aprobado 2026-10-10)

Documento histórico del 10-10-2026. El encargo activo y cola actual están en [execution-plan](../implementation/execution-plan.md). El estado inicial vacío y la antigua propuesta de exención de hooks no describen el entorno actual ni autorizan bypass.

Copia del plan aprobado en la sesión de Claude Code. El estado vivo está en `docs/status.md` y `docs/project/backlog.md`.


## Contexto
El repo `/home/aldo/Descargas/PROYECTO_ZACA_TOPICOS_AVANZADOS` está **vacío** (rama `master` sin commits; la rama principal declarada es `main`). El megaprompt pide construir BoviCierre por incrementos: primero el paquete de negocio + MER Chen + relacional + arquitectura + contexto + grafo, y después la implementación por backlog (TASK-A/J) hasta la entrega del 31-oct-2026. Hoy es 10-oct; el plan arranca el 11.

Inventario verificado (read-only):

| Herramienta | Estado |
|---|---|
| Java | OpenJDK 21.0.12 ✔ |
| Maven | 3.8.7 (se usará Maven Wrapper con 3.9.x) |
| Node / npm | 20.20.2 / 10.8.2 ✔ (Vite requiere ≥20.19) — pnpm no instalado, se usa npm |
| Docker / Compose | 29.4.1 / v5.1.3 ✔ |
| PostgreSQL cliente | psql 18.3 ✔ (servidores irán en contenedores `postgres:18`) |
| Graphviz `dot` / draw.io CLI | **no instalados** |
| Graphify | `graphify 0.9.49` + skill en `~/.claude/skills/graphify` ✔ |
| uv / pipx | ✔ |

Decisiones derivadas del inventario:
- **Diagramas**: fuentes `.drawio` escritas como XML mxGraph nativo (objetos y conectores reales, editables). Exportación SVG/PDF con contenedor `rlespinasse/drawio-export` (versión fijada); fallback: instalar Graphviz y generar alternativa `.dot`. Revisión visual de cada export con lectura de imagen.
- **Graphify**: usar la instalación existente; verificar `graphify --help` y que el paquete sea `graphifyy` antes de ejecutar `/graphify .`.
- Guardar el megaprompt como `docs/spec/megaprompt.md` (fuente canónica, no se resume).
- Crear rama `main` con commit inicial; trabajo posterior en ramas cortas por tarea.

## Avance real (2026-10-10)
Hecho: rama `main` (sin commit aún), `.gitignore`, `.graphifyignore` (sintaxis gitignore verificada en `graphify/detect.py`), `docs/spec/megaprompt.md` (copiado de `~/Descargas/BoviCierre_Megaprompt_Claude.md`, 21 272 palabras), `docs/architecture/versions.md` (Spring Boot 4.1.1, Vite 8/Node ≥20.19, Pgpool 4.7.3 verificados en web), `docs/academic/requirements-matrix.md`, `docs/research/sources.md` (F01–F50; F18, F46, F50 verificadas).
Pendiente de Fase 0: `evidence-register.md`, `docs/project/risks.md`, primer commit.
Bloqueo operativo: el hook GateGuard (ECC) exige un intento fallido + hechos por cada archivo nuevo. El usuario aprobó eximir el repo, pero el clasificador impidió que Claude editara la configuración → el usuario debe crear `.claude/settings.local.json` con `{"env":{"GATEGUARD_EXEMPT_GLOBS":"**"}}` y reiniciar la sesión. Sin eso se continúa cumpliendo el hook (más lento).

## Fase 0 — Arranque (TASK-A-001) · 11 oct
1. `git checkout -b main`; `.gitignore`, `.graphifyignore` (secretos, `.env`, dumps, `node_modules`, `target`, `dist`, `graphify-out/`).
2. `docs/spec/megaprompt.md` (copia íntegra).
3. `docs/architecture/versions.md` con el inventario anterior + versiones objetivo a verificar en fuentes oficiales (Spring Boot 4.1.x, PG 18, Pgpool-II 4.6.x, React 19, Vite 7, Flyway, Testcontainers).
4. `docs/academic/requirements-matrix.md` (AC-01..09; cada ítem clasificado: imagen / instrucción / propuesta / pendiente).
5. `docs/research/evidence-register.md` y `docs/research/sources.md` (F01–F49 con fecha de consulta; verificar enlaces con WebFetch y registrar caídos).
6. `docs/project/risks.md` con los 7 riesgos de §20.3 (dueño, mitigación, acción en backlog).

## Fase 1 — Paquete de negocio y dominio (TASK-A-002, J-001) · 11–12 oct
- `docs/business/business-model.md`, `validation-plan.md`, `unit-economics.md` (fórmulas §3.3, ejemplo 2,000/550/6,000 marcado ilustrativo, costo de tiempo de Aldo/Jared).
- `docs/domain/glossary.md`, `business-rules.md` (RN-001..045 con ID, razón, actor, precondición, transición, datos, error/SQLSTATE, implementación prevista, prueba, fuente), `use-cases.md`, `states-and-calculations.md` (máquinas de estado §5.3, política de reconocimiento único §6.1, GOLD-01..10 con tabla de valoración §12.1).
- `docs/research/theoretical-foundation.md` (tabla §6 ligada a decisiones concretas).
- **Revisión de contradicciones** registrada en `docs/research/evidence-register.md` (p. ej. ENT-13 "Posición FK selección de compra" vs. recompra; REL-19 XOR de fuente; reverso completo vs. parcial; nodo_origen de maestros con S=B).

## Fase 2 — MER Chen (TASK-A-003) · 11–12 oct
- `docs/database/conceptual-model.md` (fuertes/débiles con justificación: LoteOperacion, ContratoVersion, ConceptoLiquidacion, CondicionLote; dependencia de existencia vs. identificación vs. participación total).
- `docs/database/relationship-matrix.md` REL-01..25 + mínimos del otro extremo, condición por estado y ejemplo/contraejemplo.
- `docs/diagrams/sources/mer-0X-*.drawio` — 6 láminas (general, identidad/sedes, operaciones/lotes/condiciones/pesajes, inventario/reserva, liquidación/costos/pagos, evidencia/periodos/auditoría) + leyenda Chen, versión y fecha; A3 horizontal (general A2).
- Exportes `docs/diagrams/exports/*.svg|pdf`; checklist de revisión (acentos, cortes, cardinalidades, B/N).

## Fase 3 — Modelo relacional (TASK-A-004) · 12–13 oct
- `docs/database/relational-model.md` (41 ENT con PK/UK/FK compuestas E/S, mapeo desde MER), `data-dictionary.md` (cada columna: tipo, precisión, nulabilidad, default, unidad, dueño de escritura, publicación, sensibilidad, ejemplo válido/rechazado), `normalization.md` (DF y claves candidatas globales; 3 ejemplos completos 1FN→3FN + evaluación BCNF; justificación de snapshots).
- `docs/diagrams/sources/relacional-0X.drawio` por módulo + exportes.
- TEST-30 manual: checklist MER ↔ relacional ↔ reglas.

## Fase 4 — Arquitectura, ADR, API (TASK-A-005, A-007) · 12–13 oct
- `docs/architecture/overview.md` (monolito modular 10 módulos, capas domain/application/adapters, OwnerDatabaseRouter + BranchTransactionRunner, secuencias ConfirmarVenta y AplicarPago en Mermaid), `deployment.md`.
- `docs/architecture/adr/ADR-001..012.md` (formato Nygard; estado "propuesto").
- `docs/database/administration.md` (roles §10.4, distribución de controles §10.1, comandos §10.2 con firma/locks/SQLSTATE), `replication-and-fdw.md` (matriz tabla→dueño→dirección, bootstrap §11.2, restricciones §11.3).
- `docs/api/openapi.yaml` (familias §12.2, decimales como string, errores con `regla_id`/`correlation_id`, `Idempotency-Key`, `If-Match`); validar con `npx @redocly/cli lint`.
- `docs/ui/flows-and-screens.md` base (Jared completa en J-002).

## Fase 5 — Contexto, backlog y grafo (TASK-A-006) · 13 oct
- `README.md` (problema, negocio, stack, arquitectura, ejecución, diagramas, roles, calendario §16.2, tablas §17 con `[ ]` + listas GFM `- [ ] TASK-…` para A-001..033 y J-001..022).
- `CLAUDE.md` (<200 líneas; reglas no negociables, comandos reales, mapa de lectura; respeta `~/AGENTS.md`/graphify/RTK).
- `docs/project/roadmap.md`, `backlog.md`, `definition-of-done.md`; `docs/traceability.md` (cadena AC→RN→UC→ENT→comando→API→pantalla→TEST→TASK); `docs/status.md`.
- `docs/testing/test-plan.md` (TEST-01..35), `demo-script.md`, `evidence.md` (vacío salvo lo ejecutado).
- `docs/knowledge/graphify-workflow.md`; ejecutar `/graphify .`, parsear `graphify-out/graph.json`, responder las 6 preguntas de §15.4, registrar en `docs/knowledge/graph-status.md`.
- Commit del primer incremento. **Informe** del §19: archivos, decisiones propuestas vs. confirmadas, muestra de relaciones, siguiente tarea.

## Fase 6 — Experimento de topología y esqueleto (A-008, A-011, A-012) · 13–14 oct
- `infra/compose/compose.academic.yml`: `pg-a`, `pg-b`, `pg-fdw` (postgres:18 con digest fijado, volumen en `/var/lib/postgresql`), `pgpool-a`, `pgpool-b` (raw), healthchecks; `.env.example` ficticio.
- `db/bootstrap/` scripts separados: roles, publicaciones explícitas, `CREATE SUBSCRIPTION … origin=none, copy_data=false`, FDW con `bovi_fdw_read` SELECT-only.
- Prueba mínima aislada: escritura A y B en tablas propias → convergencia; DML sobre foreign table falla. Evidencia en `docs/testing/evidence.md`.
- `backend/` Spring Boot 4 + Maven Wrapper + Flyway + JdbcTemplate, perfiles dev/academic, arranque verificado. `frontend/` (Jared: Vite+React+TS, mocks desde OpenAPI).

## Fase 7 — Esquema y núcleo (A-009, A-010, A-013..A-017) · 13–18 oct
- `db/migrations/V1__…` por módulo (DDL real con CHECK finitos, UNIQUE parciales, FK compuestas, RESTRICT), roles/grants, triggers de inmutabilidad/auditoría, seed sintético.
- Testcontainers PG real: pruebas positivas/negativas por constraint (TEST-14, 16, 17).
- Auth sesión+CSRF; maestros en A; operaciones/lotes/versiones; documentos privados + pesajes; ConfirmarCompra PL/pgSQL (GOLD-01/02 compra, GOLD-03).
- Hito 18-oct: actualización de grafo.

## Fase 8 — Venta, dinero y cierre (A-018..A-022) · 18–23 oct
Movimientos/entrega/baja; reservas + ConfirmarVenta con lock ordenado (TEST-10, 20); pagos/aplicaciones (GOLD-04, TEST-11/12); ajustes/reversos/reembolsos (GOLD-07); costo tardío, valoración y periodos (GOLD-06/08/10, TEST-35).

## Fase 9 — Integración, réplica y operación (A-023..A-030) · 22–28 oct
Outbox/inbox; reportes + EXPLAIN; snapshot FDW + QR; M–M del esquema definitivo (TEST-21..24); pipeline CI (GitHub Actions), staging (pendiente de credenciales de VPS — no se inventa URL); backup/restore aislado medido (TEST-26/27); carga RNF (TEST-28). Hito 24 y 28: grafo.

## Fase 10 — Entrega (A-031 opcional, A-032, A-033) · 29–31 oct
Congelar extras; dossier académico §18.2 con cada AC enlazado a evidencia; demo §18.3; README con casillas marcadas sólo con evidencia; grafo final.

## Dependencias externas (se dejan pendientes, no bloquean)
- Rúbrica/interpretación M–M del profesor.
- Credenciales VPS/dominio para staging/pilot.
- Entrevistas reales (sólo guion; nada inventado).
- Trabajo de Jared (J-*): se le dejan contrato, mocks y wireframes base; no se le atribuyen commits.

## Verificación
- Diagramas: export SVG/PDF abierto y revisado visualmente; checklist en `docs/diagrams/README`.
- OpenAPI: `redocly lint` sin errores.
- Migraciones: `./mvnw verify` con Testcontainers sobre base limpia; GOLD-01..10 como pruebas que comparan contra cifras fijas del megaprompt.
- Topología: `docker compose -f infra/compose/compose.academic.yml up` + scripts de prueba de convergencia/FDW con salida guardada.
- Grafo: `graphify-out/graph.json` existe, conteos reales registrados, 6 preguntas respondidas.
- Cada tarea se marca `[x]` sólo con enlace a evidencia en `docs/testing/evidence.md`.
