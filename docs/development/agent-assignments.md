# Agentes y propiedad

2026-10-11 · checkout compartido feature/mvp-local. Humanos: Aldo backend/BD/infra; Jared frontend. Ejecución asistida no equivale a su revisión.

| Agente | Modelo real/esfuerzo | Archivos exclusivos | Entrega |
|---|---|---|---|
| /root/database | gpt-6.1-sol/high | db/**, infra/** excepto infra/caddy/** y infra/compose/application.yml; numeración Flyway | esquema/roles/comandos/topología y pruebas SQL |
| /root/backend | gpt-6.1-sol/high | backend/** | API JDBC, sesiones/CSRF, casos de uso y pruebas |
| /root/frontend | gpt-6.1-sol/high | frontend/**, docs/ui/design-system.md, flows-and-screens.md y user-manual.md | UI real, cliente y validación |
| /root | modelo de sesión heredado | OpenAPI, esquema lógico, diagramas, scripts, infra/caddy/**, infra/compose/application.yml, README y demás docs | contratos, integración, revisión y evidencia |

No hay worktrees aislados. BD es ejecutor inicial de pruebas extensivas; los demás construyen/unit-test sin otra topología masiva. Cambios compartidos se serializan mediante mensajes.
