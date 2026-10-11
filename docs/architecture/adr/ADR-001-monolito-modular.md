# ADR-001: Monolito modular frente a microservicios
- Estado: propuesto · 2026-10-10 · Requisito: AC-08
## Contexto
Equipo de 2 personas, 21 días, transacciones locales que deben cubrir operación + liquidación + inventario + auditoría.
## Alternativas
1. Microservicios por dominio — transacciones distribuidas, más despliegue y observabilidad.
2. Monolito sin módulos — rápido al inicio, acoplamiento alto.
3. **Monolito modular** con paquetes por dominio y puertos.
## Decisión
Opción 3: un backend Spring Boot desplegable con 10 módulos (`overview.md` §3).
## Consecuencias
+ Una transacción local por caso de uso; despliegue simple. − Disciplina de dependencias entre módulos sin herramienta que la imponga (se revisará con ArchUnit si hay tiempo). Sin Kafka/Kubernetes.
