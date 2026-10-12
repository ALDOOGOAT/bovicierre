# Continuidad del MVP local

Actualización 2026-10-12 · rama `main`. MVP publicado en `9282b75`, seguido de `92d3d41`; ejecución del producto local. El desarrollo inicial partió de `feature/mvp-local`/`af223fb`. Coordinador y agentes BD/backend/frontend (`gpt-6.1-sol`, high) compartieron checkout con rutas exclusivas; no hubo worktrees aislados ni revisión humana.

## Estado utilizable y evidencia

- `make academic` arrancó la aplicación integrada en http://localhost:15180: Caddy/frontend/API, PostgreSQL18.6 A/B/proveedor y dos Pgpool raw. Login/bandeja real en Chrome visible Intel y consola limpia; `docs/testing/evidence/integrated-compose.json`.
- V1–V13 Flyway. Adopción del baseline3 antiguo sólo después de comparación con replay limpio; `db/tests/flyway-adoption.json`. Nunca repetir baseline manual ni editar migraciones aplicadas.
- Backend24PASS (15unit/8HTTP/1TC18.6), frontend13unit/build/15E2E y un caso de proveedor físico. Repetición HTTP por Caddy15180 PASS. SQL157GOLD/22guardas, carreras/barreras, privilegios, muerte/inbox/ACKperdido, fallosA/B/proveedor, persistencia y FDW. Matriz por TEST y límites: `docs/testing/evidence/sql-test-matrix.md`.
- Compra/inventario/reserva/venta/liquidación/cobros/pagos/costos/ajustes/reembolsos/periodos/expediente reales. KG incompleto se guarda como borrador y requiere ticket aprobado antes de acordar. Conservar clave/cuerpo/ETag durante resultado desconocido; no iniciar otra intención hasta resolverla.
- Restauración finalV13: pausa8,038s/restauración28,616s, conciliación/hash, sesiones0; compra nueva1000, replay/lookup y descarga HTTP18180 PASS. `docs/testing/evidence/recovery/restore-v13.json`.
- Modelo42tablas/83FK comparado A/B; PDF/SVG editables revisados,5pruebas herramientas. OpenAPI0.2.0 válido2warnings públicos;17intercambios schema/media/format/HTTP pasan.
- Grafo: AST local y relectura semántica de los53documentos canónicos cambiados; revisión de enlaces pantalla→API→regla y tabla→FK/MER. La integración final y sus rutas están verificadas en graph-status; no implica reextracción de documentos históricos sin cambios.

## Servicios que quedan

Fuente `bovicierre-academic`: ocho contenedores propios activos; UI loopback15180, PostgreSQL15432/15433/15434 y Pgpool19999/19998 sólo desarrollo. API contenedor interna18080; proceso Java nativo573660 terminó antes de arrancar contenedor. Vite previo15173 detenido tras verificar PID/cwd/comando propios; usar15180.

Ensayos `bovicierre-restore-20261011201119` (V6) y `bovicierre-restore-20261011205056` (V11) detenidos, volúmenes conservados. EnsayoV13 `bovicierre-restore-20261011214723` también detenido con volúmenes conservados. APIrestaurada18180 terminada. Dumps/roles/secretos/documentos: `~/.local/share/bovicierre-academic/backups/`, privados fueraGit. No `down -v`, reset/clean ni tocar servicios ajenos tendi/Dagon.

`make stop` detiene fuente y conserva datos. `make academic` vuelve a iniciar; `make dev` exige detener APIcontenedor y usa Vite15173/API18080. `make verify-api` usa15180 por defecto; se admite `BOVI_API_TEST_URL` explícita para desarrollo. `make verify-sql` modifica sólo harnessQA propio y debe coordinarse sin backup/browser concurrentes. `make backup BACKUP_DIR=<directorio nuevo privado>` pausa API/worker/uploads; requiere otros escritores en pausa y convergencia/mensajes0.

## Siguiente paso y límites

1. Aldo/Jared: revisar `docs/academic/dossier.md`, demo/manual y filas de backlog; conservar revisión humana separada. Por instrucción del usuario, las casillas técnicas verificadas llevan [x]; esto no convierte revisión pendiente en aprobación humana.
2. Profesor: confirmar rúbrica, interpretación M–M por escritores disjuntos y formato. No hay aprobación inventada.
3. Investigación: entrevistas y precio3000/sede siguen hipótesis. Para piloto hace falta bootstrap noDEMO, datos iniciales conciliados, servidor/DNS/TLS autorizados, backup fuerahost/PITR y ensayo de capacidad con dataset del negocio. Producción bloquea scriptsDEMO.
4. Herramientas: memoriaautomática allowance agotado; no reiniciar observer. MCP de esta conversación aún puede carecer Xserver: Playwright instalado con sesión gráfica funcionó. Graphify usa fragmentos/manifiestos de los53documentos cambiados; conservar el método de relectura y validar huellas antes de reutilizar caché.

No hay despliegue público, publicación de imágenes, entrevistas realizadas ni revisión humana. No se prometen HA, RPO/RTO, capacidad comercial ni autenticidad sanitaria.

## Última entrega documental

Manual integral de 239 páginas en `docs/manual/`, con fuente LaTeX y build. Guía `docs/runbooks/local-use.md`, acceso/salud comprobados en `docs/testing/evidence/local-access-2026-10-12.json`. Credenciales sólo en archivos privados: no trasladar la contraseña entregada al usuario a Git. Casillas técnicas52/55 y revisión humana55pendientes. OCR2diferidas y staging/TLSexterno pendiente. La copia de entrega `output/` y el archivo privado `.aws` quedan ignorados; no eliminarlos al publicar.
