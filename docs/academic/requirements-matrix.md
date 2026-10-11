# Matriz de requisitos académicos

Clasificación de origen:
- **IMG**: atribuido a una transcripción histórica de la rúbrica; no comprobado contra la imagen original (transcrita en `docs/spec/megaprompt.md` §1; la imagen original no está en el repo — pendiente de agregarla en `docs/academic/rubrica.png`).
- **INS**: instrucción expresa del megaprompt.
- **PROP**: decisión propuesta por el equipo/Claude.
- **PEND**: pendiente de confirmar con el profesor.

Estado: `diseñado` = existe documentación; `implementado` = código/SQL en repo; `demostrado` = prueba ejecutada con evidencia en `docs/testing/evidence.md`. La línea base de diseño era2026-10-10; al2026-10-11 hay implementación y demostraciones locales por incremento. No se atribuye aceptación del profesor ni cobertura completa por marcar una fila parcial.

| ID | Requisito | Origen | Interpretación adoptada | Artefactos de evidencia | Pruebas | Tareas | Estado |
|---|---|---|---|---|---|---|---|
| AC-01 | MER | IMG | MER conceptual en notación Chen/EER con entidades fuertes/débiles, atributos, relaciones con verbo, cardinalidad (mín,máx) y participación | `docs/database/conceptual-model.md`, `relationship-matrix.md`, `docs/diagrams/sources/mer-*.drawio` + exportes | TEST-30 | A-003 | pendiente |
| AC-02 | Modelo relacional | IMG | Esquema lógico con PK/UK/FK, transformación verificable desde el MER, normalización y diccionario | `relational-model.md`, `data-dictionary.md`, `normalization.md`, `relacional-*.drawio` | TEST-30 | A-004 | pendiente |
| AC-03 | Administración de BDD: usuarios, constraints y reglas | IMG | Roles PostgreSQL de mínimo privilegio, constraints declarativas, reglas en PL/pgSQL, pruebas positivas y negativas | `docs/database/administration.md`, `db/bootstrap/roles*.sql`, `db/migrations/` | TEST-14, 16, 17 | A-009, A-010 | pendiente |
| AC-04 | PL y triggers | IMG | Funciones PL/pgSQL de comandos (ConfirmarCompra/Venta, AplicarPago…) y triggers de inmutabilidad, protección de dueño y auditoría | `db/migrations/`, `administration.md` §comandos | TEST-01..09, 17 | A-017..A-022 | pendiente |
| AC-05 | Transacciones | IMG | Comandos atómicos, rollback, locks en orden estable, idempotencia persistida, reintento 40001/40P01 | `administration.md` §10.3, pruebas Testcontainers | TEST-10, 11, 12, 20, 9 | A-019, A-020, A-027 | pendiente |
| AC-06 | Replicación M–M | IMG | Dos nodos escritores (A, B) con replicación lógica bidireccional, `origin = none`, escritor exclusivo por agregado; maestros sólo en A | `replication-and-fdw.md`, ADR-005, ADR-006, `db/bootstrap/replication*.sql` | TEST-21..24 | A-011, A-026 | pendiente; **PEND**: confirmar con el profesor que no exige dos escritores sobre la misma fila |
| AC-07 | FDW | IMG | `postgres_fdw` desde A hacia un tercer PostgreSQL (proveedor simulado), sólo lectura | `replication-and-fdw.md` §FDW, `db/bootstrap/fdw*.sql` | TEST-25 | A-012, A-025 | pendiente |
| AC-08 | Programa en Java | IMG | Backend Spring Boot 4 / Java 21, monolito modular, POO/SOLID/patrones documentados con referencia a código | `backend/`, `docs/academic/oop-solid-patterns.md` | TEST-01..12 vía API | A-008, A-013..A-024 | pendiente |
| AC-09 | PostgreSQL y Pgpool-II en el dibujo | IMG | Pgpool-II modo raw, una instancia por nodo; la app conecta por Pgpool; aparece en diagramas de contenedores/despliegue | `docs/architecture/overview.md`, `deployment.md`, `infra/compose/` | demo de conexión vía Pgpool | A-011, A-028 | pendiente |

## Requisitos de contexto (no rúbrica)

| ID | Requisito | Origen | Nota |
|---|---|---|---|
| CTX-01 | Integrar POO, programación avanzada, diseño y administración de BD | INS | No se afirma cubrir "todo el temario": no se dispone del programa completo (**PEND**) |
| CTX-02 | Entregar MER Chen, diagrama lógico y esquema físico como tres niveles del mismo diseño | INS | "DER/ER/MER" se tratan como el mismo modelo conceptual |
| CTX-03 | Formato de documento, páginas, citación | PEND | No proporcionado; se usa estilo consistente con IDs F01..F49 |

## Preguntas abiertas para el profesor

1. ¿M–M exige que ambos nodos editen la **misma fila**, o basta con dos escritores sobre recursos distintos? (ver riesgo R-01)
2. ¿Hay formato o rúbrica detallada de entrega (documento, video, exposición)?
3. ¿El FDW debe apuntar a otro motor o basta otra instancia PostgreSQL?

## Evidencia técnica actual por requisito

| ID | Avance comprobado | Pendiente concreto |
|---|---|---|
| AC01 | MER Chen completo/autorreferencias y módulos PDF/SVG editables revisados | revisión humana y rúbrica original |
| AC02 | 42tablas83FK comparadas A/B; PK/UK/NN/tipos, determinantes/normalización y exportaciónrelacionalA0/A3 | revisión humana de DF/legibilidad; comparación no cubre todas las RN |
| AC03/04 | roles/runtime42501, constraints23514/FK23503, triggers negativos como rolcontrolado, funciones financieras positivas/negativas | evaluación humana de rúbrica |
| AC05 | comandos atómicos/rollback/idem/ETag, carreras dosconexiones con barreras, respuesta perdida UI; TC18.6 | evaluación humana; no prueba formal de todos los interleavings |
| AC06 | A/B origin-none disjuntos/convergencia, muerteinbox/ACKperdido y caídasA/B reales | confirmar interpretación profesor M–M; mismohost noHA |
| AC07 | SELECTFDW/DMLdenegado, proveedorcaído503, snapshotBseparado y hashpersistido; UIaceptafuente | fuente es simulada, no organismo integrado |
| AC08 | backend Java21/JDBC/Spring,24pruebas; POO/puertos/patrones sobre código real | evaluación humana del temario |
| AC09 | dosPgpoolraw reales, API por dueño, Dockerapp/Caddy15180 real y restoreV13conciliado | staging/TLS público externo pendiente |

[Estado](../status.md), [matriz TEST](../testing/evidence/sql-test-matrix.md), [evidencia](../testing/evidence.md) y [dossier](dossier.md) distinguen diseño/implementación/verificación local/revisión humana. La imagen de rúbrica no se recuperó; los requisitos IMG son transcripción histórica provisional, no aprobación del profesor.
