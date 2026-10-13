# Decisiones del rediseño S1

| ID | Decisión | Motivo | Alternativa descartada | Reversible |
|---|---|---|---|---|
| UXD-01 | Reescribir `styles.css` sobre tokens únicos (`--green-*`, `--earth-*`, `--s*`, `--r-*`, `--fs-*`) conservando **todas** las clases existentes | Cambiar identidad sin tocar flujos ni selectores E2E | Librería de componentes (Tailwind/MUI): peso y reescritura | Sí (git) |
| UXD-02 | Insignias de estado con `data-tone` calculado en `src/tone.ts`; el texto sigue siendo el valor de la API | Distinguir comercial/físico/pago sin traducir ni ocultar el valor; probado en `tests/tone.test.ts` | Traducir etiquetas: rompe búsquedas `hasText` y oculta el valor real | Sí |
| UXD-03 | Forma del punto por tono (círculo/aro/rombo/guion) | Estado no sólo por color (WCAG 1.4.1) | Sólo color | Sí |
| UXD-04 | Inter Variable empaquetada localmente (subset latin, 48 KB) | Tipografía consistente entre equipos sin llamada remota | Google Fonts remoto; varias familias | Sí |
| UXD-05 | Fotos sólo en acceso y sede, `alt=""`, crédito visible en acceso | Contexto bovino sin sugerir que son animales del sistema | Foto por animal o en tablas (prohibido por el encargo) | Sí |
| UXD-06 | UUID técnicos en monoespaciado gris dentro de las tablas, texto completo | Separar identificador técnico de datos de negocio sin recortar evidencia | Truncar a 8 caracteres: perdería trazabilidad | Sí |
| UXD-07 | En ≤767 px las tablas mantienen desplazamiento propio con `min-width:680px` y `overflow-wrap:break-word` | La primera iteración partió palabras letra a letra (regresión observada en captura `iter1` 390 px, corregida en `iter2`) | Tarjetas por fila: más código y riesgo para E2E | Sí |
| UXD-08 | Objetivos de 44 px se mantienen en la navegación lateral aunque provoque scroll del sidebar en pantallas de 1000 px de alto | Política de producto de 44 px (tabletas 768–1100 px usan el sidebar) | Bajar a 38 px | Sí |
| UXD-09 | Borde de controles `#8A8574` (3.69:1 sobre blanco) | `tools/ui/contrast.py` detectó 2.07:1 con el valor inicial (<3:1, WCAG 1.4.11) | Mantener borde claro | Sí |
| UXD-10 | Componentes nuevos separados por función: `src/brand.tsx` (marca/iconos), `src/tone.ts` (tono de estado) | Reducir concentración en `App.tsx` sin reescritura total | Partir `screens.tsx` completo en S1: riesgo alto para el tiempo | Sí |
| UXD-11 | Nueva prueba visual de sólo lectura `tests_e2e/visual.spec.ts` (sin mutaciones) que captura 14 vistas × 3 anchos y falla si hay desbordamiento horizontal | Comparación antes/después reproducible | Capturas manuales | Sí |
| UXD-12 | Pase v3 (13-oct-2026) guiado por la auditoría `ecc:a11y-architect` (29 puntos) y por ingeniería inversa del CSS público de Linear, Stripe, Vercel, Mercury y AgriWebb | Profesional y vistoso con valores reales, no inventados | Copiar un tema ajeno: se tomaron valores, no identidad |
| UXD-13 | Tipografía: pesos variables 510/590/620/680, tracking −.011em en cuerpo y −.022 a −.04em en títulos; `lining-nums tabular-nums slashed-zero` en datos (Linear); `text-wrap:balance` en titulares | Jerarquía clara y cifras alineadas | Pesos 600/700 fijos |
| UXD-14 | Importes con la moneda al 60 % (`Amount`), saldo de liquidación a 42 px, cantidad y precio alineados a la derecha con separador de miles | El número es el dato; la unidad es contexto | Mantener MXN al mismo tamaño |
| UXD-15 | Movimiento: hover .25 s `cubic-bezier(.25,1,.5,1)` (Stripe), realimentación .1–.16 s y `scale(.97)` al pulsar (Linear), entrada escalonada de secciones .36 s, indicador de navegación animado, esqueleto 1.5 s (Mercury/Vercel); todo anulado con `prefers-reduced-motion` | Respuesta inmediata sin distraer | Spinner único y cambios instantáneos |
| UXD-16 | Imágenes: banda fotográfica con velo en la Bandeja, sede a dos columnas con foto 4:5, deriva lenta de la foto de acceso; patrón de héroe con foto y velo (AgriWebb) | Identidad ganadera dentro de la app, no sólo en el acceso | Ilustraciones genéricas |
| UXD-17 | Superficies: sombras en capas con borde fino (Vercel), radios 7/11/16/20 px, barra superior con desenfoque 20 px (Linear), sidebar con degradado cálido | Profundidad sutil y consistente | Sombras planas de un solo valor |
| UXD-18 | Tabla: cabecera sin recorte, valores vacíos como «—» con texto para lector, primera columna fija en móvil, botón «Abrir →» con desplazamiento al pasar | Densidad y lectura en teléfono | Tarjetas por fila (rompería pruebas que leen la primera celda) |
| UXD-19 | Accesibilidad: `document.title` por pantalla y sede, `scroll-padding-top` bajo la barra fija, foco visible en selects con chevron propio, filtros con opción «Todos» | WCAG 2.4.2, 2.4.11, 3.3.2 | — |
| UXD-20 | Tablet 768–900 px: sidebar como riel de iconos de 72 px | Evitar que la navegación ocupe 27 % del ancho | Menú hamburguesa |

No se cambiaron: `api.ts`, idempotencia/reintentos, AbortController por sede, almacenamiento (sessionStorage sólo clave+huella), cálculo de importes (todo viene de la API), textos de botones/etiquetas usados por E2E.
