# Plan de pruebas

La tabla inicial conserva el plan diseñado. Las ejecuciones reales están en [evidencia](evidence.md), resultados `db/tests/` y [UI](evidence/ui/frontend-ui-tests.md); no confundir presencia de IDs con cumplimiento. Herramientas: JUnit 5 + Testcontainers (PostgreSQL 18 real, nunca H2) [F47]; dos clusters reales para replicación; Playwright para E2E. Las pruebas comparan contra **cifras fijas** de GOLD (no recalculan con el mismo código).

| ID | Escenario | Resultado exigido | Nivel | Entorno | Tarea |
|---|---|---|---|---|---|
| TEST-01 | GOLD-01 operación completa | Margen 34,000; saldo 244,000; variación sin descuento implícito | SQL + API | Testcontainers | A-017/A-019/A-020 |
| TEST-02 | GOLD-02 venta parcial | Costo 4,400; margen 1,800; inventario 6,600 | SQL | Testcontainers | A-019 |
| TEST-03 | GOLD-03 redondeo | 0.34 + 0.33 + 0.33 = 1.00 | SQL + unidad Java | Testcontainers | A-017 |
| TEST-04 | GOLD-04 pago/anticipo | Saldos correctos; reintento sin doble efecto | SQL + API | Testcontainers | A-020 |
| TEST-05 | GOLD-05/09 recompra | Nuevo ciclo; nunca dos activas | SQL | Testcontainers | A-017 |
| TEST-06 | GOLD-06 costo tardío/bonificación | 4,600/6,900/1,600 y 4,520/6,780/1,680; deuda sin cambio | SQL | Testcontainers | A-022 |
| TEST-07 | GOLD-07 bonificación después del pago | Disponible 100; reembolso → 0 | SQL + API | Testcontainers | A-021 |
| TEST-08 | GOLD-08 baja | Inventario 0; pérdida 1,100 → 1,150 | SQL | Testcontainers | A-018/A-022 |
| TEST-09 | GOLD-10 cierre concurrente | Corte coherente; ajuste en periodo abierto | SQL 2 conexiones | Testcontainers | A-022 |
| TEST-10 | Dos ventas concurrentes misma posición | Una confirma, otra 409; sin liquidación parcial | SQL 2 conexiones + API | Testcontainers | A-019 |
| TEST-11 | Dos aplicaciones compiten | Nunca sobreaplica | SQL 2 conexiones | Testcontainers | A-020 |
| TEST-12 | Misma clave, payload distinto | 409; sin efecto | API | Testcontainers | A-020 |
| TEST-13 | Identificador duplicado desde A/B | Un alta canónica en A | SQL | academic | A-014 |
| TEST-14 | FK de otra empresa/sede | Rechazo en BD | SQL | Testcontainers | A-009 |
| TEST-15 | Usuario sin permiso altera sede/ID | 403/404 sin filtración | API | Testcontainers | A-013 |
| TEST-16 | Rol app/auditor DML protegido o desactivar trigger | 42501 | SQL con roles | Testcontainers | A-010 |
| TEST-17 | Editar liquidación/contrato/pesaje aprobado | Rechazo (BV016/BV012/BV013) | SQL | Testcontainers | A-015..A-017 |
| TEST-18 | Ticket grupal sin pesos individuales | Sin mediciones fabricadas | SQL | Testcontainers | A-016 |
| TEST-19 | Pesajes con composición distinta | NO_COMPARABLE | SQL | Testcontainers | A-016 |
| TEST-20 | Reserva vence durante confirmación | Revalida; no vende con reserva vencida | SQL | Testcontainers | A-019 |
| TEST-21 | Partición y escrituras de dueños distintos | Converge sin loops ni duplicados | Infra | academic | A-026 |
| TEST-22 | Caída de A | No cambia dueño; nuevas solicitudes autenticadas A/B503; transacciónB ya autorizada puede concluir | Infra + API | academic | A-026 |
| TEST-23 | Huérfanos tras sincronizar | Conciliación explícita | SQL | academic | A-026 |
| TEST-24 | Outbox enviado y caída antes del acuse | Inbox deduplica | Integración | Testcontainers | A-023 |
| TEST-25 | FDW real, DML y fuente caída | SELECT ok; DML rechazado; error controlado | SQL | academic | A-012 |
| TEST-26 | Restauración aislada | Datos, hashes y totales conciliados; tiempo registrado | Infra | academic | A-029 |
| TEST-27 | Recreación de contenedor PG18 | Persistencia | Infra | academic | A-011 |
| TEST-28 | Consultas y carga RNF | Medición real con entorno/dataset | Rendimiento | academic | A-030 |
| TEST-29 | Flujo UI completo y errores | Integrado, sin mocks ocultos | E2E | academic | J-019 |
| TEST-30 | MER ↔ relacional ↔ DDL ↔ reglas | Consistencia | Revisión + script | — | A-004/A-009 |
| TEST-31 | Grafo y trazabilidad | Reglas consultables con enlaces reales | Revisión | — | A-006/A-033 |
| TEST-32 | Reconocimiento repetido por entrega/pago/PDF | Sin segunda venta/deuda/costo | SQL + API | Testcontainers | A-018/A-020 |
| TEST-33 | Animal con baja por muerte | No habilita recompra | SQL | Testcontainers | A-018 |
| TEST-34 | Nuevo documento tras revisión | Revisión previa conserva versión | SQL | Testcontainers | A-016 |
| TEST-35 | Anulación antes de entrega con costo tardío | 1,200 a inventario; costo neto 0 | SQL | Testcontainers | A-022 |

RNF-01..10 (`docs/architecture/deployment.md` y megaprompt §13.5) se verifican con TEST-10/11 (RNF-01), TEST-14/15 (RNF-02), TEST-01..09 (RNF-03), TEST-28 (RNF-04/05), TEST-21 (RNF-06), TEST-26 (RNF-07), TEST-29 + revisión accesible (RNF-08), checkout limpio en CI (RNF-09), revisión de logs con correlation_id (RNF-10).
