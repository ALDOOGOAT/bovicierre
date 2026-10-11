# ADR-007: Pgpool-II en modo raw y presupuesto de conexiones
- Estado: propuesto · 2026-10-10 · Requisito: AC-09
## Contexto
La rúbrica exige Pgpool-II en el dibujo; los modos de balanceo asumen un primario único.
## Alternativas
1. Pgpool streaming/replication mode delante de ambos — enrutaría escrituras a un nodo equivocado.
2. **Una instancia Pgpool raw por nodo**, la app elige el Pgpool del dueño.
3. Sin Pgpool — no cumple AC-09.
## Decisión
Opción 2 (Pgpool 4.7.x). Presupuesto por nodo: Hikari 8, `num_init_children` 16, `max_pool` 1, + replicación y admin ≤ `max_connections` 50.
## Consecuencias
+ Cumple AC-09 sin atribuirle sincronización. − Pgpool añade un salto sin balanceo real.
