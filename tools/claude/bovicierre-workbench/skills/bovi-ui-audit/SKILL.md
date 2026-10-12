---
name: bovi-ui-audit
description: Auditoría visual/UX de la app BoviCierre real (390/768/1440 px, teclado, estados, contraste). Úsala al revisar o cambiar el frontend de BoviCierre.
---
- Navega la app local (http://127.0.0.1:15180) con credenciales DEMO desde el archivo de secretos externo; nunca las imprimas.
- Clasifica por impacto: tarea bloqueada, error de interpretación, fricción, jerarquía, estética.
- 401 inicial de sesión y 409 deliberados de pruebas negativas son esperados; regístralos como tales.
- Evidencia en `docs/testing/evidence/ui-redesign/<run-id>/`; no uses mocks para llenar capturas.
- Invariantes: importes de la API, sin cálculos monetarios nuevos en JS; estados comercial/físico/pago separados.
