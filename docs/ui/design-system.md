# Sistema visual implementado (v4 «ejecutivo», 14-oct-2026; base v2/v3 del 12–13-oct)

BoviCierre es un centro de operaciones para la compraventa de bovinos en pie. Implementación: `frontend/src/styles.css` (tokens en `:root`), `frontend/src/brand.tsx` (marca e iconos), `frontend/src/tone.ts` (tono de estados). Pantallas y API: [flujos](flows-and-screens.md), [contrato](../api/openapi.yaml). Los datos provienen de la API de la sede autorizada; no hay gráficas, cifras ni historiales ficticios. Motivos y alternativas: [decisiones](redesign-decisions.md); procedencia de fotos/fuente: [registro de assets](asset-register.md).

## Tokens

| Grupo | Token | Valor | Uso |
|---|---|---|---|
| Verde | `--green-900` / `-800` / `-700` | `#123326` / `#173F2F` / `#1E4D3A` | Sidebar, resumen de saldo, acción primaria |
| Verde claro | `--green-100` / `-50` | `#E3EEE6` / `#F1F6F2` | Selección, hover de filas |
| Tierra | `--earth-700` / `-500` / `-200` / `-100` | `#6B4F2E` / `#9A7448` / `#E8DCC7` / `#F3EBDD` | Eyebrows, marca, avatar, línea de tiempo |
| Neutros | `--bg` / `--surface` / `--surface-2` | `#F7F5EF` / `#FFFFFF` / `#FBFAF6` | Fondo cálido, tarjetas, encabezados de tabla y filtros |
| Texto | `--ink` / `--muted` | `#1A231D` / `#57635A` | Lectura principal / secundaria |
| Bordes | `--line` / `--line-strong` | `#E2DED3` / `#8A8574` | Separadores / borde de controles (3.69:1) |
| Estados | `--ok`, `--info`, `--warn`, `--error` (+ `-bg`, `-line`) | `#1E5B3E`, `#24507A`, `#7A5300`, `#9F2922` | Insignias y avisos |
| Foco | `--focus` | `#B37710`, 3 px (sidebar `#F2C46B`) | Navegación por teclado |
| Espacio | `--s1`…`--s10` | 4, 8, 12, 16, 20, 24, 32, 40 px | Escala 4/8 |
| Radios | `--r-sm` / `-md` / `-lg` | 6 / 10 / 14 px | Controles / bloques / paneles |
| Tipografía | `--font` | Inter Variable local (OFL) → `system-ui` | Cuerpo 15 px; h1 30 px (26 px móvil); controles móviles 16 px |

Contraste comprobado con `python3 tools/ui/contrast.py` (20 pares, todos ≥4.5:1 para texto y ≥3:1 para foco y bordes de controles, referencia WCAG 2.2). Es una verificación de tokens, no una certificación WCAG de toda la aplicación.

## Componentes y reglas
- **Shell:** sidebar verde oscuro con iconos lineales originales y grupo activo marcado con barra tierra; barra superior fija con sede activa ("Sede activa · cambiar") y avatar de iniciales. En ≤767 px la navegación es un selector nativo y la barra deja de ser fija.
- **Insignias de estado:** columnas `estado`, `estado_entrega`, `estado_pago`, `situacion`, `estado_convergencia`, `estado_revision`, `resultado`. Color + forma del marcador: positivo (círculo), en curso (aro), atención (rombo), crítico (guion), neutro. El texto es el valor exacto de la API; comercial, físico y pago se muestran como insignias separadas.
- **Tablas:** encabezado en mayúsculas pequeñas sobre `--surface-2`, filas de ~48 px, desplazamiento propio dentro de una región enfocable; en móvil `min-width:680px`. Identificadores UUID completos en monoespaciado gris. Importes a la derecha con dígitos tabulares y moneda.
- **Formularios:** etiqueta real con `*` de requerido, ayuda y error inline (`aria-describedby`), resumen enfocable tras error, borde de error doble. Filtros de lista en un bloque `--surface-2`.
- **Liquidación:** saldo pendiente en bloque verde con botón tierra; desglose con total en negrita; hechos (operación/entrega/contraparte) en rejilla separada del dinero.
- **Estados de carga/vacío/error:** spinner con texto, vacío con marca bovina, error con acción "Volver a consultar"; éxito sólo tras respuesta del servidor ("Registro confirmado por el servidor."); resultado incierto bloquea la captura y ofrece reintento con la misma clave.
- **Acceso y sede:** foto editorial de dominio público con degradado verde (texto ≥ contraste del degradado), formulario en tarjeta; selección de sede con foto de pastoreo, código, roles y disponibilidad.
- Objetivos de 44 px en botones, enlaces de navegación y filas seleccionables; `prefers-reduced-motion` desactiva animaciones y transiciones; estilos de impresión ocultan la navegación.

## Lo que no cambió
Comportamiento de `api.ts`, idempotencia y reintentos (sessionStorage sólo clave y huella por principal y sede), AbortController al cambiar de sede, sesión en cookie y CSRF en memoria, importes como cadenas decimales sin sumas en el navegador, textos de botones y etiquetas.

## Verificación registrada
`docs/testing/evidence/ui-redesign/20261012T0214/`: capturas antes/después en 390/768/1440 px (14 vistas), comparaciones lado a lado, 15 E2E con API real PASS, recorrido visual sin desbordamiento horizontal (`clientWidth`), resumen de errores HTTP esperados. Revisión de lector de pantalla y teléfono físico: **no realizadas**.

## v4 «ejecutivo» (14-oct-2026)

- **Tokens nuevos:** `--night-950/900/800/700` (cromo), `--gold-700` (texto), `--gold-500/300/100` (decorativos y fondos), `--dur-4:.5s`; `--ease` y `--ease-out` = `cubic-bezier(.16,1,.3,1)`; `--bg:#F4F2EE`; `--fs-h1:34px`.
- **Componentes:** `CountUp` (ui.tsx, sólo enteros), `MarginBars` (screens.tsx), `GuidedTour` y `HelpCenter` (guide.tsx), confirmación animada `.notice.success:before`, bandas `.page-heading.hero.compact`.
- **Imágenes por sección:** Operaciones `sede-pastoreo-fillmore`, Inventario `inventario-corral-nuevo-mexico`, Dinero `dinero-subasta-ganado`, Control `control-rancho-nocturno` (registro en `asset-register.md`).
- **Movimiento:** todo con `transform`/`opacity`; `prefers-reduced-motion` deja el estado final visible (conteo, palomita, barras).
- **Videos:** `frontend/public/videos/<id>.mp4|.vtt|-poster.jpg`; regenerar con `npx playwright test -c playwright.tools.config.ts tutorials.record.ts` (stack local arriba). Medición: `… perf.measure.ts`.

