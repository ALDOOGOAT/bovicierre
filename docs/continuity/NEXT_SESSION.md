# NEXT_SESSION — cierre académico (mandato 2.0, MEGAPROMPT_BOVICIERRE_CIERRE_ACADEMICO_CLAUDE.md)

**Estado al 13-oct-2026:** rama `feature/cierre-academico-v1` (desde `3141048`), sin push. Stack local arriba en http://localhost:15180, A/B/proveedor en V20. Respaldo previo: `~/.local/share/bovicierre-academic/backups/2026-10-13-pre-cierre`.

## Hecho en esta sesión (con pruebas reales)
- F1–F5: recibir/entregar/baja, pesaje base, evidencia, gasto y documentos sin copiar UUID (V19 `consultar` con `operacion_id` y aretes). E2E 16/16 tras adaptar selectores.
- `ApiErrors`: todo 23514 → 422 (antes `condicion_lote_base_tipo` daba 500).
- GOLD-ACAD-01/02 (`db/tests/gold_acad.py`) con las cifras del mandato; GOLD-ACAD-03 = TEST-10 reforzado; defecto reproducido y corregido en V20 (BV402).
- `make verify-sql` 41 PASS; backend 30/30; unitarias 14/14.

## Bloqueos externos
- `RUBRICA_ORIGINAL_PIZARRON.png` no está en el disco: pedirla al usuario; no afirmar inspección.
- Despliegue remoto: no hay destino/costo autorizado declarado; preflight pendiente (Railway/Vercel MCP existen pero sin autorización de gasto).

## Siguiente acción ejecutable (orden)
1. `make verify-release-local` sobre V20 y registrar evidencia; repetir `make backup`/`restore-check`.
2. Tablero de pendientes en la Bandeja (compras por recibir, entregas, cobrar/pagar) con totales del servidor; guía de primer ingreso.
3. Revisar instalación vacía/bootstrap y restablecimiento administrativo de contraseña (§8.1).
4. Evidencia de Pgpool (`SHOW POOL_NODES`), réplica A↔B con IDs, FDW caída/recuperación (`provider.spec.ts`, `db/tests/provider.py`), outage de enlace aislado.
5. Skills `.claude/skills/{bovicierre-ux,bovicierre-db-verify,bovicierre-release-academic,bovicierre-run}`; actualizar CLAUDE.md/AGENTS.md.
6. `make verify-academic`, `demo-profesor`, `evidence`, `release-academic`.
7. Docs: `docs/academic/{entrega-final,guion-defensa,preguntas-profesor,aceptacion-final}.md`, `docs/ui/competitive-review.md`, matriz académica AC-01..09, SOLID; manual PDF y diagramas; graphify.
