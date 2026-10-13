---
name: bovicierre-run
description: Arrancar, reconstruir y diagnosticar el stack local de BoviCierre (PostgreSQL A/B/proveedor, Pgpool, backend Java, frontend, Caddy en 15180). Úsala cuando haya que levantar la app, aplicar migraciones, redeplegar un servicio tras un cambio o diagnosticar por qué algo no responde.
---
# Arranque y diagnóstico (receta comprobada el 13-oct-2026)

Secretos y datos privados: `~/.local/share/bovicierre-academic/{secrets,private-documents,backups}` (0700, fuera del repo). Nunca imprimas su contenido.

| Objetivo | Comando |
|---|---|
| Stack académico completo (conserva datos) | `make academic` → http://localhost:15180 |
| Semilla DEMO (sólo empresa DEMO) | `make demo` |
| Instalación vacía en volúmenes nuevos | `BOVI_INSTALL=vacia BOVI_EMPRESA="Mi rancho" BOVI_ADMIN_LOGIN=admin make academic`; contraseña inicial en `secrets/install_admin_password` |
| Aplicar migraciones nuevas (A 15432, B 15433) | `sh db/bootstrap/migrate.sh` (y con `BOVI_DB_NAME=bovicierre_gold_final` para la base de pruebas) |
| Redeplegar un servicio | `BOVI_PRIVATE_DIR=$HOME/.local/share/bovicierre-academic BOVI_SECRET_DIR=$HOME/.local/share/bovicierre-academic/secrets BOVI_UID=$(id -u) BOVI_GID=$(id -g) docker compose -p bovicierre-academic -f infra/compose/compose.academic.yml -f infra/compose/application.yml up -d --build <backend\|frontend\|caddy>` |
| Estado | `make doctor`; `docker compose -p bovicierre-academic ps` |

Diagnóstico rápido:
- 500 en la API: `docker logs bovicierre-academic-backend-1 --since 10m | grep -i error`; errores de dominio llegan como P0001 con JSON `{codigo,regla_id}` y `ApiErrors` los mapea (CHECK 23514 → 422).
- Pantalla en blanco: consola del navegador (Chrome DevTools MCP) y `/tmp/bovicierre-ui-runtime-*.json` de Playwright.
- E2E contra Caddy: `BOVI_UI_TEST_URL=http://127.0.0.1:15180` (el default 15173 es Vite dev).
- La primera prueba justo tras reiniciar Caddy puede ver el upstream frío; espera a que `/api/v1/sesion/actual` responda 401 antes de medir.

No borres volúmenes ni historial git para "limpiar"; no edites migraciones aplicadas (la siguiente es V22).
