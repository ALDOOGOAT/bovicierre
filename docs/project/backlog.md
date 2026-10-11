# Backlog

Fuente detallada de tareas. Las tablas del README son copia sin la columna de evidencia; ambas se generan con el mismo estado. **[ ]** = casilla textual (en tablas no es interactiva [F44]); se marca **[x]** sólo con evidencia enlazada y revisión de Aldo/Jared. Columna Kanban: Backlog → Listo → En curso → Revisión → Hecho. "Revisión" = artefacto producido por Claude el 2026-10-10, pendiente de revisión humana; no está Hecho.

Notas de dependencia: la infraestructura de auditoría/idempotencia/periodo que necesitan los primeros comandos se implementa junto con ellos (A-022/A-023 consolidan, no posponen). A-011/A-012 usan un esquema mínimo aislado; A-026 repite con el esquema definitivo. A-027 acumula evidencia desde cada módulo; J-019 empieza cuando el recorrido tenga backend real.

### Aldo — backend, bases de datos e infraestructura

| Estado | ID | Tarea/entregable | Depende de | Ventana (oct) | Criterio de aceptación | Kanban | Evidencia |
|---|---|---|---|---|---|---|---|
| [ ] | TASK-A-001 | Inventario del repo/herramientas y matriz AC | Inicio | 11 | Requisitos de imagen separados de supuestos; archivos existentes respetados | Revisión | docs/architecture/versions.md, docs/academic/requirements-matrix.md |
| [ ] | TASK-A-002 | Negocio, glosario, reglas y GOLD | A-001 | 11–12 | RN completas, reconocimiento único, costos/pagos distinguibles | Revisión | docs/business/, docs/domain/ |
| [ ] | TASK-A-003 | MER Chen y matriz de relaciones | A-002 | 11–12 | Fuertes/débiles, rombos, óvalos, verbos, mínimos/máximos y exportaciones revisadas | En curso | docs/database/conceptual-model.md, relationship-matrix.md (texto); láminas .drawio pendientes |
| [ ] | TASK-A-004 | Modelo relacional, diccionario y normalización | A-003 | 12–13 | Todas las relaciones con claves, FKs, tipos, restricciones y justificación | Revisión | docs/database/relational-model.md, data-dictionary.md, normalization.md |
| [ ] | TASK-A-005 | Arquitectura, ADR y plan de despliegue | A-002/A-004 | 12–13 | Dueños, transacciones, límites M–M y recuperación explícitos | Revisión | docs/architecture/ |
| [ ] | TASK-A-006 | Contexto Markdown, README y grafo inicial | A-003/A-005/A-007 | 12–13 | Archivos sustantivos y grafo real verificado; si Graphify está bloqueado, sólo el avance documental se registra y la subtarea de grafo sigue pendiente | En curso | README.md, CLAUDE.md, docs/knowledge/graph-status.md |
| [ ] | TASK-A-007 | OpenAPI, errores y ejemplos para Jared | A-004/A-005 | 13 | Contrato validado con decimales exactos, scope e idempotencia | Revisión | docs/api/openapi.yaml (Redocly 1.34.5: válido, 26 warnings) |
| [ ] | TASK-A-008 | Backend modular y build reproducible | A-005/A-007 | 13–14 | Maven Wrapper, configuración por entorno y arranque verificable | Listo | — |
| [ ] | TASK-A-009 | DDL/Flyway, claves, índices y seed sintético | A-004 | 13–15 | Base limpia construida; restricciones fallan ante datos inválidos | Listo | — |
| [ ] | TASK-A-010 | Roles PostgreSQL, grants y guardas de dueño | A-009 | 13–15 | App sin privilegios administrativos; DML indebido rechazado | Backlog | — |
| [ ] | TASK-A-011 | Compose A/B + Pgpool y experimento M–M mínimo | A-005 y esquema mínimo aislado | 13–14 | Dos clusters escriben dueños distintos y convergen; prueba inicial no sustituye dominio definitivo | Listo | — |
| [ ] | TASK-A-012 | Tercero simulado y FDW sólo lectura | A-011 | 14 | Consulta real externa; escrituras rechazadas; procedencia visible | Backlog | — |
| [ ] | TASK-A-013 | Autenticación y permisos por sede | A-008/A-010 | 14–15 | Sesión/CSRF; pruebas 401/403 y autorización de recursos | Backlog | — |
| [ ] | TASK-A-014 | Maestros, animal e identificaciones centrales | A-009/A-013 | 15 | Colisión de identificador resuelta en A; B espera visibilidad | Backlog | — |
| [ ] | TASK-A-015 | Operaciones, lotes y versiones contractuales | A-014 | 15–16 | Borradores, selecciones únicas y condiciones versionadas | Backlog | — |
| [ ] | TASK-A-016 | Documentos, revisión y pesajes | A-015 | 16–17 | Archivos privados; neto/grupo reales; revisión de versión exacta | Backlog | — |
| [ ] | TASK-A-017 | ConfirmarCompra y asignar costo inicial | A-015/A-016 | 17–18 | Posiciones, obligación y costo inicial atómicos; componentes de compra de GOLD-01/02 y GOLD-03 completo | Backlog | — |
| [ ] | TASK-A-018 | Movimientos, recepción, entrega y baja | A-017 | 18–20 | Ejes físicos separados; baja conserva historia y costo | Backlog | — |
| [ ] | TASK-A-019 | Reservas, expiración y ConfirmarVenta | A-017/A-018 | 19–20 | Una venta ganadora en carrera; costo parcial correcto | Backlog | — |
| [ ] | TASK-A-020 | Pagos, anticipos y aplicaciones | A-017/A-019 | 20–21 | Sumatorias bajo lock, mismo scope, idempotencia y GOLD-04 | Backlog | — |
| [ ] | TASK-A-021 | Ajustes, reversos y reembolsos | A-020 | 21–22 | GOLD-07; ninguna sobreaplicación o borrado de originales | Backlog | — |
| [ ] | TASK-A-022 | Costo tardío, valoración y periodos | A-019/A-021 | 21–23 | GOLD-06/08/10; cierre conserva versiones y concilia | Backlog | — |
| [ ] | TASK-A-023 | Auditoría, outbox/inbox y reintentos | A-017..A-022 | 22–24 | Hecho y evento atómicos; consumidor no duplica al reintentar | Backlog | — |
| [ ] | TASK-A-024 | Consultas de cartera, margen e inventario | A-020/A-022 | 23–24 | Totales reconciliados, corte visible y EXPLAIN documentado | Backlog | — |
| [ ] | TASK-A-025 | Integrar aceptación de fuente FDW y QR | A-012/A-016 | 23–25 | Snapshot local de tarifa/ticket; QR con acceso autorizado | Backlog | — |
| [ ] | TASK-A-026 | Pruebas M–M completas, fallas y conciliación | A-009/A-011/A-023 | 24–25 | Partición/reconexión del esquema definitivo, sin loops ni auditoría duplicada, sin redirigir dueño | Backlog | — |
| [ ] | TASK-A-027 | Pruebas acumulativas de dominio/SQL/API y concurrencia | Incremental por módulo; cierre tras A-026 | 18–27 | Escenarios TEST, GOLD integrales y PostgreSQL real; no posponer pruebas hasta el final | Backlog | — |
| [ ] | TASK-A-028 | Pipeline, staging, TLS y configuración | A-008/A-011 | 26–27 | Checkout limpio desplegable y smoke test; secretos externos | Backlog | — |
| [ ] | TASK-A-029 | Respaldo, restauración y runbooks | A-026/A-028 | 26–28 | Restauración aislada cronometrada con cifras y archivos conciliados | Backlog | — |
| [ ] | TASK-A-030 | Rendimiento, conexiones y observabilidad | A-024/A-028 | 27–28 | Carga/dataset declarados; límites y resultados auténticos | Backlog | — |
| [ ] | TASK-A-031 | OCR supervisado si se aprueba el núcleo | A-016/A-027 | 25–28 opcional | Propuesta revisable, sin confirmar importes automáticamente | Backlog | — |
| [ ] | TASK-A-032 | Dossier académico, manual SQL y exposición | A-027..A-030 | 29–31 | Cada AC enlaza artefacto y demo ejecutada | Backlog | — |
| [ ] | TASK-A-033 | Fuentes, README y Graphify final consolidado | A-032/J-022 | 29–31 | Trazabilidad de ambos, casillas con evidencia, grafo sobre revisión integrada y release verificable | Backlog | — |

### Jared — frontend e integración de experiencia

| Estado | ID | Tarea/entregable | Depende de | Ventana (oct) | Criterio de aceptación | Kanban | Evidencia |
|---|---|---|---|---|---|---|---|
| [ ] | TASK-J-001 | Entender negocio, actores y términos | A-002 | 11–12 | Flujos y preguntas documentados; distingue operación/pago/entrega | Listo | — |
| [ ] | TASK-J-002 | Wireframes y arquitectura de información | J-001/A-003 | 11–12 | Recorrido compra→venta→liquidación→pago y excepciones | Listo | base: docs/ui/flows-and-screens.md |
| [ ] | TASK-J-003 | Tokens y componentes visuales accesibles | J-002 | 12–14 | Tablas, formularios, feedback y jerarquía consistentes | Backlog | — |
| [ ] | TASK-J-004 | React/TS/Vite, router y build | A-007/J-003 | 13–14 | Proyecto reproducible y separación por funciones | Backlog | — |
| [ ] | TASK-J-005 | Cliente tipado, mocks y errores del contrato | A-007/J-004 | 13–14 | Mocks identificados; formato decimal y 401/403/409/422/503 | Backlog | — |
| [ ] | TASK-J-006 | Sesión, navegación y sede autorizada | A-013/J-005 | 14–15 | Cookie/CSRF integrados; permiso denegado sin revelar datos | Backlog | — |
| [ ] | TASK-J-007 | Contrapartes y predios | A-014/J-006 | 15–16 | Captura/búsqueda/paginación con validación | Backlog | — |
| [ ] | TASK-J-008 | Ficha animal, ciclos e inventario | A-014/A-017 | 16–18 | Identidad permanente, posiciones históricas y disponibilidad claras | Backlog | — |
| [ ] | TASK-J-009 | Captura de compra y condiciones por lote | A-015/J-007 | 16–18 | Borrador por pasos; precio por kg/cabeza y versión | Backlog | — |
| [ ] | TASK-J-010 | Pesajes, archivos y revisión | A-016/J-009 | 17–18 | Conjunto, unidad, evidencia, incompatibilidad y corrección visibles | Backlog | — |
| [ ] | TASK-J-011 | Selección de venta y reservas | A-019/J-008 | 19–20 | Expiración/conflicto real y recarga sin doble confirmación | Backlog | — |
| [ ] | TASK-J-012 | Simulador y detalle explicable de liquidación | A-019/J-010 | 19–21 | Fórmula, costos, ajustes, saldo y estado de entrega separados | Backlog | — |
| [ ] | TASK-J-013 | Cobros/pagos y aplicación guiada | A-020/J-012 | 20–22 | Anticipo, disponible y saldos correctos; reintento seguro | Backlog | — |
| [ ] | TASK-J-014 | Ajustes, devoluciones de dinero y periodos | A-021/A-022 | 21–23 | Motivo, autorización y versiones; muestra GOLD-07 sin ambigüedad | Backlog | — |
| [ ] | TASK-J-015 | Recepciones, entregas y expediente temporal | A-018/A-023 | 22–24 | Eventos verificables, documentos privados y estados físicos claros | Backlog | — |
| [ ] | TASK-J-016 | Cartera, margen y QR interno | A-024/A-025 | 23–25 | Datos reales de API, corte/provisionalidad y navegación autorizada | Backlog | — |
| [ ] | TASK-J-017 | Estados de fuente caída/sincronización/conflicto | A-026/J-016 | 24–26 | Mensajes accionables; nunca confirma una escritura fallida | Backlog | — |
| [ ] | TASK-J-018 | Responsive, teclado y accesibilidad | J-006..J-017 | 25–28 | Flujo principal usable en móvil y teclado, sin cortes de información | Backlog | — |
| [ ] | TASK-J-019 | Pruebas E2E integradas con Aldo | Recorrido con API real/J-017; coordina A-027 | 26–28 | Compra/venta/pago, errores y permisos con backend real | Backlog | — |
| [ ] | TASK-J-020 | UI de OCR sólo si el extra está implementado | A-031/J-010 | 25–28 opcional | Datos propuestos y revisión humana obligatoria | Backlog | — |
| [ ] | TASK-J-021 | Manual, capturas auténticas y demo | J-018/J-019 | 29–31 | Recorrido reproducible, sin pantallas ficticias presentadas como integración | Backlog | — |
| [ ] | TASK-J-022 | README, contexto frontend y actualización de grafo | J-021 | 29–31 | Pantallas→API→reglas enlazadas y evidencia lista; A-033 consolida después el grafo final | Backlog | — |

### Listas por responsable

**Aldo**

- [ ] TASK-A-001 — Inventario del repo/herramientas y matriz AC
- [ ] TASK-A-002 — Negocio, glosario, reglas y GOLD
- [ ] TASK-A-003 — MER Chen y matriz de relaciones
- [ ] TASK-A-004 — Modelo relacional, diccionario y normalización
- [ ] TASK-A-005 — Arquitectura, ADR y plan de despliegue
- [ ] TASK-A-006 — Contexto Markdown, README y grafo inicial
- [ ] TASK-A-007 — OpenAPI, errores y ejemplos para Jared
- [ ] TASK-A-008 — Backend modular y build reproducible
- [ ] TASK-A-009 — DDL/Flyway, claves, índices y seed sintético
- [ ] TASK-A-010 — Roles PostgreSQL, grants y guardas de dueño
- [ ] TASK-A-011 — Compose A/B + Pgpool y experimento M–M mínimo
- [ ] TASK-A-012 — Tercero simulado y FDW sólo lectura
- [ ] TASK-A-013 — Autenticación y permisos por sede
- [ ] TASK-A-014 — Maestros, animal e identificaciones centrales
- [ ] TASK-A-015 — Operaciones, lotes y versiones contractuales
- [ ] TASK-A-016 — Documentos, revisión y pesajes
- [ ] TASK-A-017 — ConfirmarCompra y asignar costo inicial
- [ ] TASK-A-018 — Movimientos, recepción, entrega y baja
- [ ] TASK-A-019 — Reservas, expiración y ConfirmarVenta
- [ ] TASK-A-020 — Pagos, anticipos y aplicaciones
- [ ] TASK-A-021 — Ajustes, reversos y reembolsos
- [ ] TASK-A-022 — Costo tardío, valoración y periodos
- [ ] TASK-A-023 — Auditoría, outbox/inbox y reintentos
- [ ] TASK-A-024 — Consultas de cartera, margen e inventario
- [ ] TASK-A-025 — Integrar aceptación de fuente FDW y QR
- [ ] TASK-A-026 — Pruebas M–M completas, fallas y conciliación
- [ ] TASK-A-027 — Pruebas acumulativas de dominio/SQL/API y concurrencia
- [ ] TASK-A-028 — Pipeline, staging, TLS y configuración
- [ ] TASK-A-029 — Respaldo, restauración y runbooks
- [ ] TASK-A-030 — Rendimiento, conexiones y observabilidad
- [ ] TASK-A-031 — OCR supervisado si se aprueba el núcleo
- [ ] TASK-A-032 — Dossier académico, manual SQL y exposición
- [ ] TASK-A-033 — Fuentes, README y Graphify final consolidado

**Jared**

- [ ] TASK-J-001 — Entender negocio, actores y términos
- [ ] TASK-J-002 — Wireframes y arquitectura de información
- [ ] TASK-J-003 — Tokens y componentes visuales accesibles
- [ ] TASK-J-004 — React/TS/Vite, router y build
- [ ] TASK-J-005 — Cliente tipado, mocks y errores del contrato
- [ ] TASK-J-006 — Sesión, navegación y sede autorizada
- [ ] TASK-J-007 — Contrapartes y predios
- [ ] TASK-J-008 — Ficha animal, ciclos e inventario
- [ ] TASK-J-009 — Captura de compra y condiciones por lote
- [ ] TASK-J-010 — Pesajes, archivos y revisión
- [ ] TASK-J-011 — Selección de venta y reservas
- [ ] TASK-J-012 — Simulador y detalle explicable de liquidación
- [ ] TASK-J-013 — Cobros/pagos y aplicación guiada
- [ ] TASK-J-014 — Ajustes, devoluciones de dinero y periodos
- [ ] TASK-J-015 — Recepciones, entregas y expediente temporal
- [ ] TASK-J-016 — Cartera, margen y QR interno
- [ ] TASK-J-017 — Estados de fuente caída/sincronización/conflicto
- [ ] TASK-J-018 — Responsive, teclado y accesibilidad
- [ ] TASK-J-019 — Pruebas E2E integradas con Aldo
- [ ] TASK-J-020 — UI de OCR sólo si el extra está implementado
- [ ] TASK-J-021 — Manual, capturas auténticas y demo
- [ ] TASK-J-022 — README, contexto frontend y actualización de grafo

