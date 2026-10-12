# Informe final — campaña UI/UX + QA (S1 + S2)

**Fecha:** 12-oct-2026 · **Ejecutor:** Claude Code 2.1.296, modelo coordinador `claude-opus-5-5`; agentes: revisor de coherencia (`sonnet`) y revisor de seguridad estática (`opus`), ambos sólo lectura · **Responsables humanos:** Aldo (backend/BD/infra), Jared (frontend) — **revisión humana pendiente** · **Coste extra activado:** ninguno (sin API de pago, sin cambio de proveedor ni créditos).

## 1. Revisión inicial y final
- Inicio: `main` = `origin/main` = `38ccdc3` (posterior al `92d3d41` auditado), árbol limpio salvo la carpeta del encargo (`docs/TAREAS NUEVAS PARA CLAUDE /`, no versionada a propósito).
- Trabajo en la rama local `feature/uiux-qa-claude`: S1 en `368e4d6`; S2 en el commit siguiente. **Sin push, merge ni despliegue público.** Ningún cambio preexistente se perdió.

## 2. Estado y tiempo
| Bloque | Estado | Tiempo activo estimado | Notas |
|---|---|---|---|
| S1 UI/UX | S1_DONE (técnico) | ≈180 min (incluye ≈30 de preparación) | Dentro de 300 |
| S2 coherencia/QA | S2_SAFE_PARTIAL | ≈175 min | Dentro de 300; incluye V14; pendientes priorizados abajo |

Continuidad: los checkpoints (`tools/claude/checkpoint.py`, estado privado en `~/.local/state/bovicierre-claude/`) y `docs/continuity/NEXT_SESSION.md` se mantuvieron desde el inicio. **No hubo corte por cuota** en esta sesión, así que la continuación nativa al reset **no se ejercitó**; la opción *Continue automatically at usage limit* no estaba activada en la configuración de usuario y no se activó por atajo. S2 se ejecutó a continuación de S1 porque el usuario lo pidió explícitamente y no había hora de reset verificable.

## 3. Rediseño (S1)
Identidad bovina sobre la app real: tokens verde/tierra, Inter local (OFL), marca e iconos SVG originales, dos fotos de dominio público de Wikimedia Commons con licencia/hash registrados ([asset-register](../ui/asset-register.md)), insignias con color **y** forma que separan estado comercial, físico y de pago, saldo de liquidación destacado, UUID en monoespaciado. Comparación auténtica antes/después en 390/768/1440 px para acceso, sede, bandeja, captura, inventario, pesajes, liquidación, pagos, expediente, cartera y margen: [compare/](../testing/evidence/ui-redesign/20261012T0214/compare/). Detalle: [brief](../ui/redesign-brief.md), [decisiones UXD-01..11](../ui/redesign-decisions.md), [sistema visual](../ui/design-system.md). No revisado: lector de pantalla, teléfono físico, axe, partición de `screens.tsx`.

## 4. Herramientas, mods y modelos
Registrados en scope usuario: MCP `api-anything` (Connected), skills `ui-ux-pro-max` y `api-anything` (cargadas; UI UX Pro Max usada). Reutilizados: ECC 2.2.2, Ponytail 4.9.0, chrome-devtools-mcp 1.9.0, Graphify 0.9.49, Playwright 1.58.2. Instalado: k6 v1.0.0 (checksum verificado). Mods propios `bovicierre-workbench` 0.1.1 (sesión/cuota y evidencia): validados `--strict`, 6/6 pruebas, instalados desde el marketplace local `bovicierre-local`; carga en sesión **verificada** por el usuario (`/reload-plugins`, `/bovi-status` → «Campaña: campaña autorizada. 5h 71%…») → UQ-003 cerrada. Inventario: [claude-tooling](../development/claude-tooling.md), [manifiesto reversible](../development/claude-installation-manifest.md).

## 5. Divergencias corregidas
| ID | Qué | Por qué | Prueba |
|---|---|---|---|
| DIV-01 / SF-20 | UNIQUE inline `*_key` → 500 en vez de 409 | RN-003: duplicados deben ser conflicto, sin fuga SQL; la carga lo reprodujo | `ContractTest`, dinámico 409 |
| DIV-03 | RN-023: sólo 4 de 13 tablas inmutables con prueba | Hechos confirmados no se reescriben | `db/tests/immutability.py` 26/26 BV016 |
| SF-01 | ADMIN de una sede administraba usuarios de otra | Autorización por sede en servidor | dinámico 404, usuario de A intacto |
| DIV-04 (V14) | Estados terminales (`operacion` CONFIRMADA/ANULADA/CANCELADA, `gasto_operacion` APROBADO, `pago` VALIDADO/REVERTIDO, `posicion_inventario` CERRADA_VENTA/BAJA) sólo protegidos por el código; borrar un pago VALIDADO se permitía | Hechos confirmados inmutables en la base | `immutability.py` 44/44 (fase roja previa 13 fallos) |
| SF-08 (V14) | `search_path` sin `pg_temp`; TEMP para PUBLIC | Sombreado de catálogos | `security.sql` en A/B y restaurada; `CREATE TEMP` → 42501 |
| SF-02 / SF-03 / SF-04 / SF-05 / SF-17 / SF-21 | Login sin límite; sesiones anónimas de 30 min; sin CSP/XFO; JSON sin límite; regex del mod; vite vulnerable (dev) | Ver [findings](../security/findings.md) | `LoginThrottleTest` 4/4, dinámico, E2E sin violaciones CSP |

Pruebas frágiles corregidas (no regresiones del producto): `keyboard.spec.ts` dependía del idioma del sistema y de octubre de 2026; `ApiPostgresTest` buscaba la posición nueva sólo en la primera página de 100.

## 6. Pruebas (puerta local final)
`make verify-release-local` → **PASS** ([release-gate.json](../testing/evidence/release-local/20261012T0302/release-gate.json)), en serie, con la app en 15180:

| Etapa | Ejecutadas | Fallidas | Omitidas |
|---|---:|---:|---:|
| docs (cobertura, esquema, diagramas, Redocly) | exit 0 | 0 | — |
| frontend build + unitarias | 14 | 0 | 0 |
| backend (unitarias + 8 HTTP reales + 1 Testcontainers PG fresco V1–V13) | 28 | 0 | 0 |
| SQL harness (`make verify-sql`: GOLD-01..10, carreras con barreras, FDW, permisos) | 37 | 0 | 0 |
| Inmutabilidad RN-023 | 26 | 0 | 0 |
| E2E con API real (closure, additional, keyboard, visual) | 16 | 0 | 0 |
| Seguridad dinámica SEC | 63 | 0 | 0 |

La primera ejecución de la puerta fue **rechazada** por la propia puerta (la etapa de inmutabilidad no declaraba casos ejecutados); se conserva en `release-local/20261012T0259-rechazada/`. No ejecutado: `provider.spec.ts` (detiene el proveedor).

Tras V14 la puerta se repitió con carga: **PASS** — inmutabilidad 44, backend con Testcontainers limpio V1–V14, k6 8,194 peticiones sin fallos ([release-gate V14](../testing/evidence/release-local/20261012T0544/release-gate.json)).

## 7. Seguridad
Ningún crítico/alto **confirmado y no mitigado** dentro del alcance ejecutado. Abiertos: SF-09 (media, confianza en la credencial de app; decisión humana), SF-06/07/10/11 (bajas estáticas; SF-08 corregido en V14), info SF-12..19. Cobertura no ejecutada: DAST autenticado (ZAP), Semgrep/Gitleaks/Trivy, escáner Maven/Python/imágenes (INCOMPLETO, no "0 vulnerabilidades"), subida políglota. [Modelo de amenazas](../security/threat-model.md) · [plan](../security/test-plan.md) · [dependencias](../security/dependency-report.md).

## 8. Rendimiento y recuperación
Carga k6 1→5→10→20 sesiones propias (70/20/10, reflexión 0.3–0.8 s): 8,105 peticiones, p95 lectura 19.5 ms / escritura 20.0 ms, 1 error (el DIV-01 ya corregido), conciliación exacta 1,185 efectos = 1,185 filas nuevas, 0 deadlocks, 0 esperas de lock. No saturó: no prueba capacidad sostenida ni volumen de 10,000 posiciones / 100,000 hechos (no alcanzado). [Informe](../testing/evidence/performance/20261012T0242-ramp/report.md).
Recuperación **repetida tras V14**: respaldo previo y posterior; el primer `restore-check` concilió datos pero dejó TEMP para PUBLIC en la base restaurada (el ACL de base no viaja en `pg_dump`). Se corrigió `scripts/recovery.py` y el segundo ensayo concilió en 29.7 s con triggers V14 y TEMP revocado ([restore-v14](../testing/evidence/recovery/restore-v14.json)). Sin PITR ni pérdida de host.

## 9. Qué falta (separado)
- **Profesor / entrega 31-oct:** revisión humana de Aldo y Jared de S1/S2; revisar los MER/relacional contra la matriz (no se tocaron diagramas en esta campaña); `/graphify . --update` semántico de los documentos nuevos.
- **Piloto:** decidir SF-09 (RLS/contexto de actor o ADR de riesgo aceptado); DIV-06 (fórmula canónica de margen), DIV-07/08 (catálogo de códigos), DIV-12 (OpenAPI BAJA/anular); SF-06/07; escáneres SCA/DAST; carga sostenida 15–20 min y dataset grande.
- **Despliegue:** staging/TLS, backup fuera del host, PITR, HA — fuera del alcance local.

## 10. Comandos
```bash
make academic                         # levantar (conserva datos)
make verify-release-local             # puerta local completa (≈3 min)
python3 tests/security/sec_dynamic.py --out docs/testing/evidence/security/<run>/dynamic.json
BOVI_SECRET_DIR=$HOME/.local/share/bovicierre-academic/secrets k6 run tests/performance/load.js
python3 tools/claude/resume-check.py --owner <sesión>   # antes de continuar la campaña
```
Siguiente tarea concreta: ver [NEXT_SESSION](../continuity/NEXT_SESSION.md).
