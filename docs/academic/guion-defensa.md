# Guion de defensa (15 min) — ensayable

Preparación (antes de la clase, con internet): `make academic && make demo`; abrir http://localhost:15180 como `demo.admin` (contraseña por canal privado, `~/.local/share/bovicierre-academic/secrets/demo_password`). Terminal en la raíz del repo. Datos sintéticos DEMO. Si algo falla: mostrar la evidencia registrada en `docs/testing/evidence/academic-release/` en lugar de improvisar.

| Min | Qué se muestra | Acción / comando | Resultado esperado | Explicación | Si falla |
|---|---|---|---|---|---|
| 0–2 | Problema y arquitectura | Diagrama `docs/architecture/overview.md` | Navegador → Caddy → Java → Pgpool A/B → PostgreSQL A/B; FDW A→proveedor | Cierre de tratos de ganado en pie: compra, costo, venta, cobro | Usar el PDF del manual |
| 2–4 | MER → relacional → restricción | Diagramas `docs/diagrams/` y `\d bovi.condicion_lote` en psql | CHECK `condicion_lote_base_tipo` (KG exige pesaje, CABEZA lo prohíbe) | Traducción entidad→tabla, PK/FK, regla como CHECK | Mostrar `docs/database/data-dictionary.md` |
| 4–8 | Compra/costo/venta/cobro | `~/.cache/bovicierre/sql-tests/bin/python db/tests/gold_acad.py` y la Bandeja/Liquidación en UI | `PASS GOLD-ACAD-01` con 1 disponible, 11000 inventario, venta 16000, costo 11000, margen 5000, cobro 4000, saldos 12000/0; `GOLD-ACAD-02` 500 kg × 60 = 30000 sólo tras aprobar pesaje | Un solo evento económico (CONFIRMADA); entrega y cobro no duplican | Leer `db/tests/infra-evidence-result.json`/evidencia |
| 8–12 | Permisos, trigger/rollback, concurrencia, réplica, FDW | `.../python db/tests/infra_evidence.py`; carrera: `make verify-sql` (fragmento TEST-10) | Pgpool A→pg-a, B→pg-b; réplica A→B y B→A con IDs; corte de suscripción y convergencia; FDW 12000, INSERT 42501, caída 08001 y recuperación; carrera: un ganador, perdedor BV402 | Escritor exclusivo por agregado; FDW de sólo lectura | Mostrar `infra-evidence-result.json` |
| 12–14 | Java/SOLID y recuperación | `docs/academic/oop-solid-patterns.md`; `ApiErrors`, `CommandService`, `DocumentStorage` | Matriz SRP/OCP/LSP/ISP/DIP con pruebas; restore-check 13-oct: firma y hashes coinciden | SQL es la autoridad del dinero; Java orquesta | Leer evidencia de restore en `docs/testing/evidence.md` |
| 14–15 | Conclusión y límites | — | — | Mismo host (no HA), proveedor simulado, sin despliegue público autorizado, aceptación del profesor pendiente | — |

Laboratorio ampliado (sólo si el profesor lo pide): `make verify-release-local` (~4 min), `make backup`/`restore-check` (~1 min), caída de B con `docker compose ... stop pg-b` y lectura 503 BV501 en la UI. Las caídas se hacen desde la terminal del laboratorio, nunca por un endpoint web.

Preguntas preparadas: [preguntas-profesor.md](preguntas-profesor.md).
