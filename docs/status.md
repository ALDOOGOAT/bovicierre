# Estado del proyecto

Actualizado: 2026-10-11 · rama `feature/mvp-local`, base `af223fb`, implementación local sin publicar.

## Disponible hoy

`make academic` inicia PostgreSQL18.6 A/B/proveedor, dos Pgpool raw, Java21/SpringBoot4.1.1, React19/Vite8 y Caddy HTTP local. Interfaz: http://localhost:15180. `make demo` conserva una semilla sintética reproducible; `make stop` detiene servicios propios sin borrar volúmenes. [Manual](ui/user-manual.md), [guion](testing/demo-script.md) y [handoff](implementation/handoff.md).

Compra→inventario→reserva/venta→liquidación→pago/aplicación→cartera/margen/expediente usa API y datos persistidos. Hay lotes kg/cabeza, pesajes y versiones, documentos privados, recepción/entrega/baja, costos tardíos, bonificaciones/reembolsos y periodos con cierres históricos. Datos DEMO; sin integración sanitaria oficial ni cobros reales.

## Comprobación técnica

- Backend: 24 pruebas PASS (15 unitarias, ocho HTTP, una Testcontainers18.6 con V1–V13); [resultado](../backend/verification-result-v13.json). Las ocho HTTP se ejecutaron por Caddy15180, incluidos contenidos CSV reales.
- Frontend: 13 unitarias/build y dieciséis E2E PASS:15integrados y1caída física de proveedor (sin skips/retries); [resultado](testing/evidence/ui/bovicierre-ui-final-run.json). Chrome visible Intel,390/768/1440 y teclado; cambio de sede cancela GET anterior, resultado incierto conserva intención. [Arranque integrado](testing/evidence/integrated-compose.json).
- SQL: 157 comandos GOLD fijos y 22 guardas de versiones; carreras reales con dos conexiones/barreras, privilegios/constraints/triggers, muerte B→A/inbox, réplica/FDW y fallos reales A/B/proveedor. [Matriz con alcance por TEST](testing/evidence/sql-test-matrix.md).
- Restauración V13 aislada: pausa8,038s, recuperación28,616s; datos/archivos/hash/deduplicación conciliados, sesiones invalidadas; compra nueva1000 y replay/lookup HTTP pasan. [Registro](testing/evidence/recovery/restore-v13.json). Ensayo detenido conserva sus volúmenes; fuente integrada activa.
- Modelo lógico42tablas/83FK y catálogos A/B concordantes en columnas/tipos/nullabilidad/PK/UK/FK declaradas. MER/relacional editables y PDF/SVG revisados; comparación parcial no demuestra todas las RN.
- OpenAPI0.2.0 válido con dos advertencias de GET públicos sin4xx ficticio; 17 intercambios de sesión/lecturas reales validados. [Resultado](testing/evidence/contract-read-v13.json).
- Rendimiento:1,901comandos y replay sin duplicación;800consultas/100warmups mediantePgpool con uno y cuatro clientes, cuatro EXPLAIN. [Benchmark](../db/tests/benchmark-result.json). Caché caliente, sinHTTP/carga escritora; no capacidad niSLO comercial.

## Pendientes y límites

Revisión humana de Aldo/Jared, rúbrica original, interpretación M–M del profesor y entrevistas/precio/piloto siguen pendientes. Las55casillas originales permanecen sin marcarHecho por agentes. OCR A-031/J-020 diferido; A-028 sólo preparación local, sin staging/TLS público. CI manual preparado, no ejecutado remoto. Graphify: AST local y relectura semántica de los53documentos canónicos cambiados; integración final y rutas verificadas en graph-status. Los documentos históricos sin cambios conservan su extracción anterior.

Una empresa por despliegue; A centraliza sesiones y su caída causa503 en nuevas solicitudes autenticadas de ambas sedes. Mismo host no alta disponibilidad. Sin PITR, backup externo ni prueba de pérdida de laptop. Configuración de piloto requiere bootstrap real sinDEMO, revisión de secretos/redes/TLS, inventario inicial conciliado y ensayos sobre el servidor elegido. No hay aprobación del profesor ni cliente contratado.
