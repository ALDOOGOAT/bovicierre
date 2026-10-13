# ADR-018 — Confianza en la credencial de aplicación (SF-09)

Estado: aceptada para el piloto, 13-oct-2026 · Decisión técnica tomada por el agente a petición del usuario; **pendiente de revisión humana de Aldo y Jared** · Relacionada: ADR-002, ADR-005, ADR-017, SF-09.

## Contexto
`bovi_app_a` y `bovi_app_b` tienen SELECT sobre las 42 tablas de `bovi` y ningún INSERT/UPDATE/DELETE (medido el 13-oct en `information_schema.role_table_grants`). Toda escritura pasa por `bovi.cmd_ejecutar` (SECURITY DEFINER), que autoriza con `fn_scope(empresa, sede, p_actor, rol)`; `p_actor` lo envía el backend tras validar la sesión HTTP. Quien obtenga la contraseña de esa credencial puede leer toda la base de su nodo y ejecutar comandos en nombre de cualquier usuario con membresía.

## Opciones
1. **Atar el actor a una sesión viva en la base**: el backend fija `SET LOCAL bovi.sesion` y `fn_scope` exige que `infra.spring_session` tenga esa sesión vigente para el `principal_name` del actor; además, retirar el SELECT directo y leer sólo por `consultar`.
2. **RLS por empresa/sede/actor** con contexto de sesión equivalente.
3. **Aceptar el riesgo residual** con controles compensatorios verificados.

## Decisión
Opción 3 para el piloto de una empresa por despliegue.

Razones: (a) las opciones 1–2 son transversales: tocan `fn_scope`, ambos nodos (las sesiones sólo existen en A), el worker de outbox, `AccessService` (que lee `membresia_usuario` directamente) y las 37 pruebas SQL que llaman a `cmd_ejecutar` sin sesión; el riesgo de regresión antes del piloto supera el beneficio. (b) El beneficio real se limita a una filtración de la contraseña sin compromiso del contenedor: si el backend se compromete, el atacante obtiene también la credencial de sesiones (`bovi_auth`) y la opción 1 deja de proteger. (c) Una empresa por despliegue acota el radio: no hay datos de otros clientes en la base.

## Controles compensatorios (verificables)
| Control | Verificación |
|---|---|
| Runtime sin DML, DDL, superusuario, BYPASSRLS ni replicación | `db/tests/security.sql` (en `make verify-sql`) |
| Sin TEMP ni sombreado de catálogo | `security.sql`, V14 (SF-08) |
| Hechos confirmados inmutables aun con DML | triggers V2/V14/V16 y `db/tests/immutability.py` |
| Credencial sólo como secreto Docker del contenedor backend; fuera de Git, logs y grafo | `infra/compose/application.yml`; escaneo de secretos por commit |
| PostgreSQL y Pgpool sin puertos publicados en producción | `infra/compose/production.example.yml` (`ports: !reset []`) |
| Toda escritura deja `auditoria_evento` con actor y `correlation_id` (forense) | trigger `hecho_inmutable` sobre `auditoria_evento` |
| Rotación de credenciales comerciales antes y después del piloto | procedimiento de `infra/compose/README.production.md` (pendiente de operar) |

## Disparadores para implementar la opción 1
Cualquiera de: más de una empresa por despliegue; acceso de terceros o integraciones a la base; exposición de PostgreSQL fuera de la red privada de Compose; requisito contractual de segregación por usuario; o un incidente de credenciales. Siguiente migración libre al momento de la decisión: V19.

## Consecuencias
SF-09 pasa a RIESGO_ACEPTADO con fecha y condiciones, no a corregido. El piloto no debe ampliarse a varias empresas por despliegue sin reabrir este ADR.
