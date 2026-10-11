# ADR-017: Despliegue inicial preparado

- Estado: aceptado para implementación local por encargo del usuario · 2026-10-11

## Decisión

Una empresa por despliegue, VM Linux DockerCompose+Caddy preparada; ejecución actual localhost. Dos nodos en una máquina son topología académica, no redundancia física. Sin publicación/push/contratación. Secretos externos privados, puertosloopback, archivos fuerawebroot. Restauración aislada ejecutada antes de afirmar recuperación.

## Validación

Implementación y pruebas pendientes al registrar esta decisión; ver [evidencia](../../testing/evidence.md). La revisión humana permanece pendiente.
