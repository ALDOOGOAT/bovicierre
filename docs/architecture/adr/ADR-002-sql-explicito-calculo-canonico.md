# ADR-002: SQL explícito, cálculo canónico y migraciones versionadas
- Estado: propuesto · 2026-10-10 · Requisitos: AC-03, AC-04, AC-05
## Contexto
La materia evalúa SQL, PL/pgSQL y transacciones; los importes deben ser reproducibles al centavo.
## Alternativas
1. JPA/Hibernate con `ddl-auto` — oculta SQL y no sirve como fuente del diseño.
2. **JdbcTemplate + Flyway + funciones PL/pgSQL canónicas.**
3. jOOQ — buena opción, añade generación de código.
## Decisión
Opción 2. Importes confirmados se calculan en `fn_calcular_liquidacion` (SQL) y se congelan; la previsualización llama la misma función sin persistir. Java usa BigDecimal y valida; no recalcula con otra fórmula.
## Consecuencias
+ SQL visible y evaluable; una sola fórmula. − Más SQL a mano; mapeos explícitos. Pruebas con PostgreSQL real (Testcontainers), nunca H2.
