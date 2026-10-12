# Definition of Done

Una tarea está **Hecha** cuando:
1. Cumple su criterio de aceptación y la RN indicada.
2. El artefacto real existe y se revisó.
3. La prueba pertinente se ejecutó y su salida está en `docs/testing/evidence.md`.
4. Contrato/documentación coinciden con la implementación.
5. El cambio fue revisado (PR) y su evidencia registrada.
6. Trazabilidad y grafo actualizados si cambió contexto relevante.
7. No presenta un mock como integración exigida ni un despliegue pendiente como publicado. FDW contra la fuente sintética cuenta como hecho con sus pruebas y la simulación documentada.

| Tipo | Criterio adicional |
|---|---|
| Diagrama | Fuente editable + exportación SVG/PDF revisada + cardinalidades defendibles |
| BD | Migración reproducible en base limpia + prueba positiva y negativa |
| API | Contrato + autorización + persistencia real |
| Frontend | Integrado con API real + estados de error |
| Recuperación | Restauración ejecutada y conciliada, con tiempo medido |
| Documento | Contenido sustantivo (decisiones, ejemplos, enlaces) o faltante declarado |

## Casillas técnicas y aceptación humana

Por instrucción del usuario del 12-oct-2026, la casilla `[x]` del backlog y README indica **verificado local**, con enlace a evidencia. No equivale al estado formal Hecha definido arriba. La columna Revisión humana y el Kanban conservan la aceptación pendiente; no se atribuye aprobación a Aldo, Jared o el profesor. Se marcan 52 tareas técnicas; A-028 permanece pendiente externa y A-031/J-020 diferidas.
