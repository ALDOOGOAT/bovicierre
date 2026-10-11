# ADR-013: Sesiones centrales y disponibilidad

- Estado: aceptado para implementación local por encargo del usuario · 2026-10-11

## Decisión

Spring Session JDBC y autorización vigente residen en A. Toda nueva petición autenticada de A/B depende de A; su caída produce 503 controlado. Una transacción B ya autorizada puede finalizar. Sustituye cualquier promesa de continuidad de sesiones B del ADR-008. Cookie HttpOnly/SameSite=Lax, CSRF también en login/logout; Secure obligatorio fuera del perfil HTTP local.

## Validación

Implementación y pruebas pendientes al registrar esta decisión; ver [evidencia](../../testing/evidence.md). La revisión humana permanece pendiente.
