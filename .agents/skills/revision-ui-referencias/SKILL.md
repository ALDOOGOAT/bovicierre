---
name: revision-ui-referencias
description: Observar referencias públicas y adaptar patrones a BoviCierre al diseñar pantallas, rediseñar flujos o resolver problemas visuales y responsive. Para cambios pequeños, reutilizar decisiones existentes.
---

1. Leer `docs/ui/flows-and-screens.md` y las reglas del flujo afectado. Consultar UI UX Pro Max para la decisión concreta; mantener el stack, componentes e identidad existentes.
2. Consultar `docs/ui/references.md`. Si falta evidencia útil, observar referencias públicas pertinentes con Chrome DevTools MCP: DOM/CSS, capturas y comportamiento. Registrar URL, fecha y qué se observó; separar inferencias y límites. Detalles de herramientas: `docs/development/web-tools.md`.
3. Justificar una adaptación que resuelva el problema y completar el flujo local con código propio. Si no hay interfaz ejecutable, mejorar su especificación sin crear un frontend ajeno al alcance. No copiar reglas financieras de las referencias: importes del servidor, confirmación económica única, entrega y pago separados.
4. Verificar flujo, estados, teclado, foco, consola y tamaños afectados (390/768/1440 como inicio). Capturas públicas sanitizadas en `docs/ui/evidence/`; material privado fuera de Git. Documentar resultados reales y límites en `docs/testing/evidence.md`.

Observar una interfaz no requiere integrar sus servicios. Para una operación externa necesaria, buscar primero API oficial y consultar API Anything sólo si aporta una vía autorizada. No importar sesiones personales automáticamente.
