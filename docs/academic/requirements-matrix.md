# Matriz de requisitos académicos

Clasificación de origen:
- **IMG**: visible en la imagen de la rúbrica que el usuario proporcionó (transcrita en `docs/spec/megaprompt.md` §1; la imagen original no está en el repo — pendiente de agregarla en `docs/academic/rubrica.png`).
- **INS**: instrucción expresa del megaprompt.
- **PROP**: decisión propuesta por el equipo/Claude.
- **PEND**: pendiente de confirmar con el profesor.

Estado: `diseñado` = existe documentación; `implementado` = código/SQL en repo; `demostrado` = prueba ejecutada con evidencia en `docs/testing/evidence.md`. Al 2026-10-10 ningún requisito está implementado ni demostrado.

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
