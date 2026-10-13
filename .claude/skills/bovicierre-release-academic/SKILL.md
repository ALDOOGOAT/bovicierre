---
name: bovicierre-release-academic
description: Preparar la entrega académica de BoviCierre — puerta local completa, evidencias, matriz de requisitos, guion de defensa y paquete sin secretos. Úsala al cerrar una versión, registrar evidencia o armar el paquete para el profesor.
---
# Release académico

1. `make verify-academic`: puerta local completa (`verify-release-local`) más evidencia de infraestructura. Resultado en `docs/testing/evidence/release-local/<ts>/release-gate.json`.
2. `make evidence` copia los resultados vigentes a `docs/testing/evidence/academic-release/`.
3. Respaldo y `restore-check` en directorio privado nuevo.
4. Actualiza `docs/status.md`, `docs/traceability.md`, `docs/testing/evidence.md`, `docs/academic/requirements-matrix.md` (AC-01..09) y `oop-solid-patterns.md`. IDs nuevos sin reutilizar.
5. Manual: recompilar desde fuentes y abrir el PDF para revisarlo; exit 0 no basta.
6. `make release-academic` arma `dist/` desde `git archive` con `SHA256SUMS` y escaneo de secretos.

Separar siempre: verificación técnica (automática) ≠ despliegue (sólo con destino, acceso y costo autorizados; si no, “despliegue externo bloqueado por X”) ≠ aceptación humana (Aldo, Jared, profesor; nunca la declara un agente). No enviar nada al profesor ni publicar sin autorización.
