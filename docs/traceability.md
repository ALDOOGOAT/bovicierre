# Trazabilidad

Cadena: AC → RN → UC → ENT/REL → comando/función → API → pantalla → TEST → tarea → evidencia. Estado actualizado por incremento: los comandos SQL reales se despachan mediante `bovi.cmd_ejecutar`; las filas históricas conservan los nombres conceptuales. La tabla de ejecución de abajo indica archivos y pruebas auténticas, sin atribuir revisión humana.

| AC | RN | UC | ENT / REL | Comando / función | API | Pantalla | TEST | Tareas | Estado |
|---|---|---|---|---|---|---|---|---|---|
| AC-05 | RN-018, RN-019, RN-022 | UC-08 | ENT-12, 13, 15, 22 · REL-11, 12 | `cmd_reservar_posiciones`, `cmd_confirmar_venta`; UNIQUE parcial reserva ACTIVA y posición activa | POST /sedes/{s}/operaciones/{id}/reservas, /confirmar | 5, 6 | TEST-10, TEST-20 | A-019, J-011 | diseñado |
| AC-05 | RN-028..033 | UC-09, UC-10 | ENT-25, 26, 22 · REL-20, 30, 32 | `cmd_aplicar_pago`, `cmd_revertir_aplicacion`, `cmd_registrar_reembolso` | POST /pagos/{id}/aplicaciones, /aplicaciones/{id}/reverso, /pagos/{id}/reembolsos | 9 | TEST-04, 07, 11, 12 | A-020, A-021, J-013 | diseñado |
| AC-04 | RN-021, RN-026 | UC-06 | ENT-13, 21, 22, 23, 39 · REL-09, 16, 17, 19, 25 | `cmd_confirmar_compra`, `fn_calcular_liquidacion` | POST /operaciones/{id}/confirmar | 6, 8 | TEST-01..03 | A-017, J-009 | diseñado |
| AC-04 | RN-027, RN-039 | UC-12, UC-14 | ENT-20, 21, 37, 38, 39 · REL-19, 24, 36 | `cmd_registrar_costo_tardio`, `cmd_cerrar_periodo` | /gastos/{id}/reparto, /periodos/{id}/cierre | 12 | TEST-06, 08, 09, 35 | A-022, J-014 | diseñado |
| AC-03 | RN-001, RN-009 | UC-01 | todas (FK compuestas) | roles `bovi_*`, `trg_guarda_propietario` | /sesion/* | 1, 13 | TEST-14, 15, 16 | A-010, A-013, J-006 | diseñado |
| AC-03 | RN-023, RN-011, RN-013 | UC-05, UC-11 | ENT-16, 18, 22, 23 | `trg_inmutable_confirmado` | — | 8 | TEST-17 | A-015..A-017 | diseñado |
| AC-06 | RN-003, RN-004, RN-040, RN-041 | UC-03, UC-18 | ENT-08, 36, todas con nodo_origen | publicaciones `pub_a`/`pub_b`, suscripciones `origin=none`, `fn_validar_conciliacion_propietario` | — | 14 | TEST-13, 21..23 | A-011, A-014, A-026, J-017 | diseñado |
| AC-07 | RN-042 | UC-16 | ENT-20 (snapshot) | `postgres_fdw`, `ext_proveedor.*` | GET /integraciones/proveedor/tarifas | 6 | TEST-25 | A-012, A-025 | diseñado |
| AC-09 | RN-040 | — | — | Pgpool raw A/B | — | — | demo de conexión | A-011, A-028 | diseñado |
| AC-01, AC-02 | todas | — | ENT-01..41, REL-01..37 | migraciones | — | — | TEST-30 | A-003, A-004, A-009 | láminas v0.2 exportadas y comprobadas; revisión semántica humana pendiente |
| AC-08 | RN-034 | todos | — | módulos Java, `Money` | todas | — | TEST-01..12 vía API | A-008, A-013..A-024 | diseñado |
| — | RN-043, RN-044 | UC-06, UC-08 | ENT-29, 30, 31, 34 | outbox/inbox | — | 10 | TEST-24 | A-023 | diseñado |
| — | RN-020, RN-038 | UC-07, UC-13 | ENT-13, 14 · REL-13 | `cmd_registrar_entrega`, `cmd_registrar_baja` | POST /inventario/movimientos | 5, 10 | TEST-08, 32, 33 | A-018, J-015 | diseñado |
| — | RN-037 | UC-17 | ENT-27, 28, 40, 41 · REL-22, 23, 29 | `DocumentStorage`, revisiones | /documentos | 10 | TEST-34 | A-016, J-010 | diseñado |
| — | RN-035, RN-036 | UC-15 | vistas de reporte | `v_margen_operacion`, `v_saldo_liquidacion` | /reportes/* | 11, 12 | TEST-01, 28 | A-024, J-016 | diseñado |

Cobertura de RN por TEST: ver columna "Prueba" en `docs/domain/business-rules.md`.

Mejora UI/UX del 2026-10-11: RN-029/030/032 → UC-09/10 → pantallas 8/9 → GOLD-04A/B, GOLD-07, TEST-04/07/11/12 → TASK-J-002/J-012/J-013. Especificación y contrato implementados en `docs/ui/flows-and-screens.md`; referencias en `docs/ui/references.md`; herramientas en `docs/development/web-tools.md`. Estado: implementado y comprobado con SQL/API/UI; [matriz](testing/evidence/sql-test-matrix.md) y [nueve E2E](testing/evidence/ui/bovicierre-ui-final-run.json). Revisión humana pendiente, sin casillas Hecho.

## Trazabilidad ejecutada · 2026-10-11

| Regla / recorrido | Autoridad ejecutable | API / pantalla | Evidencia local | Límite |
|---|---|---|---|---|
| RN021/022 compra/venta | `db/migrations/V2__comandos.sql` y evoluciones, `fn_calcular_liquidacion` | confirmar; captura y pantalla8/liquidación | GOLD01/02, API y `evidence/ui/bovicierre-ui-e2e.json` según manifiesto frontend | Los nombres conceptuales cmd_confirmar_* no son funciones adicionales |
| RN028..033 dinero | cmd_ejecutar aplicar/ajustar/revertir/reembolsar | pagos/aplicaciones, liquidación y pantalla9 | GOLD04/07 y UI bonificación atómica/reembolso | No hay pagos bancarios reales |
| RN027/039 costo tardío y periodos | reparto/asiento/cierre inmutable SQL | gastos/reparto y periodos | GOLD06/08/ANUL; carrera cierre en ampliación | Corte por sede, no snapshot global A/B |
| RN043/044 muerteB→A | outbox B, inbox A, OutboxWorker | movimiento BAJA y sincronización | academic muerte/acuse repetido | Nuevas peticiones autenticadas dependen de A |
| RN001 permisos | AccessService/SecurityConfiguration y roles SQL | sesión/usuarios | HTTPCSRF, TestcontainersDDL/DELETE/hash y auditorUI403 | No RLS multiempresa |
| RN037 evidencia | DocumentStorage/PrivateDocuments, documento/revisión SQL | expediente/documentos/QR | pruebas privadas y UI PNG/QR/refresh | Revisión administrativa, no certificado sanitario |
| Pantalla8 → liquidación | `evidencia/SettlementController.java`, `CoreController` + consultaSQL | GETliquidaciones/id + comprobante | API compra/venta/saldoPDF y UI | Contrato OpenAPI no demuestra por sí solo ejecución |

Los archivos y logs se enlazan desde `docs/testing/evidence.md`; diagramas desde `docs/diagrams/README.md`. Graphify debe reextraer estas relaciones semánticas después de cerrar el incremento.
