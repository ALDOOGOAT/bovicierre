---
name: bovicierre-ux
description: Revisar o cambiar pantallas de BoviCierre (React en frontend/src) con lenguaje de trabajo ganadero, sin UUID visibles como dato principal, accesible y validado en navegador real a 390/768/1440. Úsala para cualquier cambio de UI, textos, estados de carga/error o recorridos de captura.
---
# UX de BoviCierre

Principios (mandato §9): términos del trabajo (“Recibir ganado”, “Registrar entrega”, “Cobrar”, “Dinero pendiente”); selectores con búsqueda en vez de pegar IDs (`OperationPicker`, `DocumentPicker`, `AnimalChecklist`, `PartyField`); errores con qué pasó, qué lo causó y cómo seguir; nunca mostrar 0 cuando no se pudo consultar; éxito sólo tras respuesta del servidor; contraseñas jamás en sessionStorage/localStorage.

Flujo:
1. Lee `docs/ui/flows-and-screens.md` y la pantalla en `frontend/src`.
2. Cambia lo mínimo; reutiliza `.metric`, `.check-row`, `.pagination`, `CommandForm`, `State`.
3. `cd frontend && npx tsc --noEmit -p .`
4. Redeplega frontend (skill bovicierre-run) y corre `BOVI_UI_TEST_URL=http://127.0.0.1:15180 npm run test:e2e -- visual.spec.ts academic.spec.ts`.
5. Abre las capturas `/tmp/bovicierre-shots/{390,768,1440}-*.png` y revísalas (plurales, desbordes, foco). Para DOM/CSS en vivo usa Chrome DevTools MCP.
6. Selectores de prueba estables: `label.check-row[data-id]`, `[data-task]`, roles y nombres accesibles.

Referencias competitivas sólo de páginas públicas (EngordaMax, Agroapp de Agryxo): `docs/ui/competitive-review.md`. Sin cuentas autenticadas ni endpoints privados.
