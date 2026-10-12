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

No se cambiaron: `api.ts`, idempotencia/reintentos, AbortController por sede, almacenamiento (sessionStorage sólo clave+huella), cálculo de importes (todo viene de la API), textos de botones/etiquetas usados por E2E.
