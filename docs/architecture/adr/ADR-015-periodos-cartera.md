# ADR-015: Reconocimiento y cierres históricos

- Estado: aceptado para implementación local por encargo del usuario · 2026-10-11

## Decisión

Periodos mensuales calendario por empresa/sede America/Mexico_City, uno abierto y rangos consecutivos sin solapamiento. Todo hecho que cambia valoración/cartera conserva periodo y fecha de reconocimiento, además de fecha documental y registro UTC. Lock común antes de recursos financieros. Cierre/versiones inmutables. Reapertura sólo último cerrado sin periodo posterior ni abierto. Perdedor frente al cierre recibe BV025 sin efecto, cambia periodo sólo mediante intención explícita nueva.

## Validación

Implementación y pruebas pendientes al registrar esta decisión; ver [evidencia](../../testing/evidence.md). La revisión humana permanece pendiente.
