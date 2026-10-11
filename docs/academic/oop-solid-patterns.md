# POO, SOLID y patrones

Estado: **diseño**. No existe código aún; la columna "Archivo" indica la ubicación prevista y se reemplazará por la ruta real con línea al implementar (TASK-A-008 en adelante). No se atribuye SOLID por usar Spring.

| Principio / patrón | Uso concreto previsto | Archivo previsto | Cómo se verifica |
|---|---|---|---|
| Encapsulación | `PosicionInventario` y `Liquidacion` exponen métodos de transición (`reservar`, `venderPendienteEntrega`, `darDeBaja`), sin setters públicos de estado | `backend/src/main/java/.../inventario/domain/PosicionInventario.java` | Prueba unitaria: transición inválida lanza excepción de dominio |
| Value Object | `Money` (BigDecimal escala 2, HALF_UP, moneda), `PesoKg` (escala 3, > 0), `IdentificadorAnimal` (sistema + código normalizado), `Periodo` | `.../shared/domain/` | Pruebas: escala, igualdad por valor, rechazo de negativos/NaN |
| SRP | Cálculo (SQL canónico), persistencia (adaptador JDBC), autorización (application), PDF (adaptador) separados | módulos `liquidaciones/*` | Revisión de dependencias entre paquetes |
| OCP | `EstrategiaBaseLiquidable` (POR_KG, POR_CABEZA) y `EstrategiaReparto` (POR_CABEZA, POR_PESO_MEDIDO, IMPORTE_INDIVIDUAL) seleccionadas por condición | `.../liquidaciones/domain/estrategias/` | Agregar estrategia sin tocar el controlador |
| LSP | `DocumentStorage` local y privado cumplen el mismo contrato de errores | `.../evidencia/adapters/out/` | Prueba de contrato compartida |
| ISP | Puertos pequeños: `ConsultaInventario`, `ComandosVenta`, `DocumentStorage` | `.../application/port/` | Sin repositorio genérico gigante |
| DIP | Casos de uso dependen de puertos; JDBC inyectado | `.../application/` | Pruebas de caso de uso con dobles |
| Repository / Query Object | SQL parametrizado explícito por agregado/consulta (JdbcTemplate) | `.../adapters/out/jdbc/` | Pruebas Testcontainers |
| Strategy | Ver OCP | — | Pruebas por estrategia con vectores GOLD |
| State | Enum de estados + tabla de transiciones permitidas para Operación/Reserva/Periodo | `.../operaciones/domain/EstadoOperacion.java` | Prueba de matriz de transiciones |
| Adapter | Almacenamiento de archivos, FDW (vía SQL), OCR opcional | `.../adapters/out/` | Formato externo no entra al dominio |
| Transactional Outbox | Insert en `evento_outbox` dentro del comando SQL; despachador separado; inbox deduplica | `db/migrations/`, `.../integraciones/` | TEST-24 |

## Regla de cálculo único
Los importes que se confirman los calcula la función SQL canónica (`fn_calcular_liquidacion`); la previsualización llama la misma función sin persistir. Java valida y presenta resultados con `Money`; si alguna fórmula se replica en Java, comparte los vectores GOLD como prueba de equivalencia.
