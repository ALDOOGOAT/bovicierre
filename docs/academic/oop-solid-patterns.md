# POO, responsabilidades y patrones ejecutados

Estado: implementación local en Java21. Las rutas de esta tabla existen; no se atribuyen clases o estrategias de Java que sólo figuraban en el diseño. El cálculo confirmado es SQL canónico y se prueba con PostgreSQL real.

| Concepto | Código real | Comportamiento y evidencia |
|---|---|---|
| Encapsulación/composición | `backend/src/main/java/mx/bovicierre/shared/CommandService.java` | Campos privados de autorización, JDBC y transacciones; selecciona un único propietario. Compone servicios y no expone pools al HTTP. `ApiPostgresTest` recorre compra/venta/aplicación. |
| Responsabilidad de entrada | `operaciones/CoreController.java`, `shared/JsonSupport.java` | HTTP/ETag/Idempotency-Key y validación decimal separados de los cálculos SQL. Dinero llega como cadena, se valida con BigDecimal; no se recalculan importes mediante double. `ContractTest`. |
| Puerto y adaptador, DIP | `evidencia/application/DocumentStorage.java`, `evidencia/PrivateDocuments.java` | Controller depende del puerto. El adaptador local valida contenido real, hace staging y conserva un bloqueo hasta commit; `PrivateDocumentsTest` comprueba edad, referencias y limpieza segura. No se inventa un segundo almacenamiento para demostrar polimorfismo. |
| Transacción por propietario | `shared/CommandService.java`, `db/migrations/V2__comandos.sql` y evoluciones | Una TransactionTemplate del dueño, parámetros SQL y hasta tres intentos ante 40001/40P01. Autorización en A ocurre antes y no pertenece a la transacción B. Testcontainers prueba replay/conflicto/rollback en BD nueva. |
| Outbox/inbox | `integraciones/OutboxWorker.java`, `db/migrations/` | Hecho/outbox juntos, entrega con lease local y llamada A fuera de lock financiero B; inbox deduplica. Academic prueba muerte B y acuse repetido sin duplicar pérdida. |
| Adaptador de presentación | `evidencia/SettlementPdf.java`, `reportes/CsvController.java`, `evidencia/AnimalQrController.java` | PDF controlado, CSV protege fórmulas y QR apunta a ruta autenticada. Pruebas `SettlementPdfTest`, `ExportTest`; recorrido UI real descarga/QR/refresh. |
| Autorización y sesión | `acceso/AccessService.java`, `SecurityConfiguration.java` | Roles vigentes consultados en A, CSRF y sesión JDBC central. Prueba HTTP sesión/scope y auditor UI con mutación403. No se presenta como RLS por usuario de BD. |

## Matriz SOLID (cierre académico, 13-oct-2026)

Rutas relativas a `backend/src/main/java/mx/bovicierre/`. Cada fila es código existente; donde el principio no aplica con naturalidad se dice como brecha, sin inventar clases.

| Principio | Ejemplo real o brecha | Ruta y símbolo | Explicación | Prueba | Limitación |
|---|---|---|---|---|---|
| SRP | Errores HTTP en un solo lugar | `shared/ApiErrors` (`@ExceptionHandler`) | Traduce P0001/BVxxx, 23514→422, 22P05→400 sin que los controllers conozcan SQLSTATE | `ContractTest` (CHECK `condicion_lote_base_tipo` → 422) | Clase única grande; no se divide por tipo de error |
| SRP | Restablecer contraseña | `acceso/UserController.write` | El controller valida forma y convierte a bcrypt; la persistencia y la regla de rol son de `cmd_ejecutar` (V21) | `db/tests/password_reset.py` (TEST-38), `academic.spec.ts` | La política de complejidad de contraseña es mínima (1–72 bytes) |
| OCP | Nuevos comandos sin tocar el transporte | `shared/CommandService.command(...)` | Recibe nombre de comando + payload y lo envía al dueño; agregar un comando = migración SQL + ruta, sin modificar reintentos/idempotencia | `ApiPostgresTest` | La extensión vive en SQL (`CASE` de `cmd_ejecutar`), no en clases Java |
| LSP | Sustitución por contrato del puerto | `evidencia/application/DocumentStorage` ← `evidencia/PrivateDocuments` | Cualquier implementación debe respetar `stage`/`Upload.close` (staging, hash, liberar bloqueo); el controller sólo usa el contrato | `PrivateDocumentsTest` | Hay una sola implementación productiva; no se inventa otra para “demostrar” LSP |
| ISP | Puerto mínimo | `DocumentStorage` (2 métodos + `Upload`) | El controller no ve rutas, locks ni limpieza; `CleanupMain` usa la clase concreta para mantenimiento | `PrivateDocumentsTest` | Resto de servicios no exponen interfaces porque tienen un solo consumidor (YAGNI) |
| DIP | Controllers dependen de abstracciones inyectadas | `evidencia/DocumentController(DocumentStorage, AccessService, CommandService)` | Constructor injection de Spring; el puerto está en `application`, el adaptador en infraestructura | `PrivateDocumentsTest`, recorrido UI de documentos | `AccessService`/`CommandService` son clases concretas (sin interfaz) por tener una implementación |

Patrones observables: **Command** (cada escritura es `bovi.cmd_ejecutar(..., comando, payload)` con clave de idempotencia), **Template/Retry** (`TransactionTemplate` + reintento 40001/40P01 en `CommandService`), **Outbox/Inbox** (`integraciones/OutboxWorker`), **Adapter** (`PrivateDocuments`, `SettlementPdf`, `CsvController`), **Filter/Chain of Responsibility** (`acceso/AvailabilityFilter extends OncePerRequestFilter`), **Throttle** (`acceso/LoginThrottle`, `LoginThrottleTest`). Dinero: `MoneyTypesLintTest` prohíbe `double/float` en `src/main/java`.

## Límites deliberados

Los módulos pequeños mantienen paquetes por responsabilidad, con controllers HTTP y un servicio JDBC compartido; no hay una interfaz por tabla ni setters de estados económicos. Las transiciones y las estrategias kg/cabeza/reparto viven en SQL para mantener una única autoridad. `Money`, `PesoKg` y repositorios separados previstos originalmente no existen como clases: el contrato decimal y PostgreSQL protegen precisión y estados. No se afirma OCP/LSP de todo el programa por usar Spring ni se simula herencia de animales.

La revisión académica humana del estilo y la interpretación exacta del temario siguen pendientes. [Evidencia de ejecución](../testing/evidence.md) y [guion](../testing/demo-script.md).
