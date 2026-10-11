# Ejecución local del MVP

Encargo activo: megaprompt de Aldo del11-10-2026, apartados0–22. La especificación histórica permanece en `docs/spec/megaprompt.md`; rama `feature/mvp-local`, baseline `af223fb`.

## Incrementos ejecutados

0. Correcciones ADR013–017, identidad/periodos/claves/MER y OpenAPI0.2.0 tipado.
1. Migraciones V1–V13, roles, PostgreSQL A/B/proveedor, Pgpool raw, sesiones/CSRF, React y Caddy local ejecutados.
2. Compra, inventario, pesajes/documentos y acuerdos por lotes persistidos.
3. Reserva/venta, movimientos físicos y muerte B→A/inbox con reintento.
4. Dinero, bonificación atómica, reembolso, gastos/tardíos y cierres versionados con GOLD fijos.
5. FDW real y snapshotlocal por dueño, reportes/QR/archivos, réplica y fallosA/B/proveedor comprobados.
6. Backend24, frontend13unit/16E2E, responsive/teclado, medición QA canónica con uno y cuatro clientes y restauración finalV13 ejecutados.
7. Manual/dossier/README/modelos,55tareas con responsabilidad humana, evidencia actualizados; AST y relectura semántica de53documentos canónicos para integración final.

La evidencia por criterio prevalece sobre esta lista: [estado](../status.md), [matriz TEST](../testing/evidence/sql-test-matrix.md) y [handoff](handoff.md). No se considera aceptación humana por compilar o por revisión de agentes.

## Cierre técnico local verificado

Quince E2E mediante Caddy ejecutados, incluyendo ETag, predios, ciclos de recompra, corrección de pesajes, reportes y CSV; V13 vigente. Caída física proveedor503→200 con captura preservada y restauraciónV13 aislada ejecutadas. Grafo/caché de53documentos y rutas críticas verificados. Medición canónica con dataset mayor en QA y1/4clientes ejecutada:1,901comandos y su replay idéntico;800consultas con p95 declarado, sin SLO comercial. Extracción semántica por tres agentes de los53documentos canónicos cambiados, integrada/cacheada y rutas críticas revisadas, con evidencia en graph-status.

## Cola pendiente

Revisión Aldo/Jared y profesor/rúbrica; entrevistas/oferta/precio; bootstrap de cliente real sinDEMO, carga inicial conciliada, capacidad/backupfuera host/PITR y autorización de despliegue. A-028 parte externa pendiente; A-031/J-020 OCR diferidos. La extracción semántica final cubre documentos canónicos cambiados; su integración/cache y enlaces se registran en graph-status. El grafo no sustituye pruebas SQL.

Sin push, PR, DNS, certificados públicos, contratación o cobros en esta etapa.
