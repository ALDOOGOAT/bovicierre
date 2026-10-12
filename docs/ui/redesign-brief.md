# Brief del rediseño S1 — BoviCierre

**Fecha:** 12-oct-2026 · **Encargo:** `docs/TAREAS NUEVAS PARA CLAUDE /BoviCierre_Megaprompt_Claude_UIUX_QA.md` §7 · **Ejecutor:** agente Claude Opus 5.5 · **Responsable humano del frontend:** Jared (revisión pendiente).

## Objetivo
Centro de operaciones para la compraventa de bovinos en pie: sobrio, especializado y legible para cifras. No es landing ni catálogo. Se evoluciona la identidad existente (verde, B2B) sin cambiar stack ni flujos.

## Auditoría inicial (app real, 15180, datos DEMO)
Capturas "antes" en 390/768/1440 px: [`docs/testing/evidence/ui-redesign/20261012T0214/before/`](../testing/evidence/ui-redesign/20261012T0214/before/) (46 capturas, sin desbordamiento horizontal global).

| Impacto | Hallazgo | Pantallas |
|---|---|---|
| Error de interpretación | Todas las insignias de estado con el mismo color verde: BORRADOR o PENDIENTE se veían igual que CONFIRMADA; el estado de entrega no tenía insignia | Bandeja, inventario, pagos, pesajes |
| Fricción | Filas de 68 px y padding generoso: ~19 operaciones por pantalla de 1440×2000 | Listas |
| Jerarquía | Liquidación: el saldo pendiente se mezclaba visualmente con el resto del panel; el desglose no destacaba el total | Liquidación |
| Jerarquía | Identificadores UUID con la misma tipografía que los datos de negocio | Inventario, pagos, cartera |
| Estética / identidad | Tipografía de sistema (Ubuntu en la máquina), monograma "B" abstracto, sin imagen ni rasgo ganadero | Acceso, sede, shell |
| Fricción | Descripción genérica "Información y acciones…" en 11 pantallas | Expediente, pesajes, etc. |

Respuestas HTTP esperadas no se contaron como fallos (401 inicial de `/sesion/actual`, 409 de pruebas negativas).

Línea base de esfuerzo observado (demo, no entrevista): crear una operación exige elegir tipo, buscar/seleccionar contraparte por nombre y fecha (3 campos + 1 búsqueda), sin UUID manuales; navegar a liquidación requiere 2 clics desde la lista. Se conserva.

## Dirección visual implementada
- Verde profundo `#1E4D3A`/`#123326`, blanco cálido `#F7F5EF`, neutros tierra `#6B4F2E`/`#F3EBDD`.
- Inter Variable local (OFL), cifras tabulares; importes alineados a la derecha con MXN explícito.
- Sidebar verde oscuro con iconos lineales originales; barra superior con sede activa explícita y avatar.
- Insignias con color **y forma** (círculo, aro, rombo, guion) para no depender sólo del color.
- Fotografías editoriales de dominio público sólo en acceso y selección de sede ([registro](asset-register.md)).
- Resumen de saldo de la liquidación como bloque verde destacado; desglose con total en negrita.

## Fuera de alcance de S1
Cambios de API, de cálculo o de reglas; nuevos KPIs; fotos por animal; modo oscuro; migración de router.

Referencias consultadas: [references.md](references.md) (existente) y UI UX Pro Max (`search.py 'financial table readability' --domain ux`): desplazamiento propio de tablas y separadores de miles, ya presentes.
