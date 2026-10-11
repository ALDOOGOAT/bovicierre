# ADR-010: Despliegue, respaldos y límites de disponibilidad
- Estado: propuesto · 2026-10-10
## Alternativas
1. Kubernetes — sobredimensionado.
2. **Docker Compose + Caddy en un VPS**, respaldos fuera del host.
## Decisión
Opción 2. Demo: dumps lógicos con corte y conciliación + restauración aislada medida. Piloto: backup base + archivo WAL por nodo antes de prometer RPO 15 min / RTO 2 h.
## Consecuencias
+ Reproducible y barato. − Un solo host es un único dominio de fallo; no hay alta disponibilidad.
