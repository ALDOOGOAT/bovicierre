# Runbook: despliegue a staging

Estado: pendiente de servidor y credenciales (PEND-03). No existe URL pública.
1. Verificar CI verde en el commit a desplegar; anotar tag `vX.Y.Z` y digest de imágenes.
2. En el servidor: `docker compose pull` con el tag.
3. Detener workers de outbox (`docker compose stop backend`).
4. Migrar una vez por nodo: `docker compose run --rm migrate-a`, luego `migrate-b`. Sólo migraciones de expansión compatibles con la versión anterior.
5. `docker compose up -d backend frontend caddy`.
6. Smoke test: login, crear compra borrador, consultar cartera, health de ambos nodos.
7. Registrar versión, responsable, fecha y resultado en `docs/testing/evidence.md`.
