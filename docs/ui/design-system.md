# Sistema visual implementado

BoviCierre usa una identidad B2B sobria común a acceso, operación, inventario, dinero y control. Implementación: `frontend/src/styles.css`; pantallas y API: [flujos](flows-and-screens.md), [contrato](../api/openapi.yaml). Los datos provienen de la API de la sede autorizada; no hay gráficas, cifras ni historiales ficticios.

| Token | Valor | Uso |
|---|---|---|
| Fondo | `#F6F7F4` | Espacio de trabajo |
| Texto | `#17211B` | Lectura principal |
| Acción | `#1F5A43` | Confirmación y selección |
| Superficie | `#FFFFFF` | Formularios y tablas |
| Secundario | `#5A685F` | Contexto y etiquetas |
| Borde | `#D8E0D8` | Separación visual |
| Foco | `#B37710`, 3 px | Navegación por teclado |
| Error | `#9F2922` | Mensaje textual y campo |

Tipografía del sistema, importes completos con dígitos tabulares y moneda explícita. Escala de espacio 4/8 px; cuerpo de 14 px en escritorio, controles de 16 px en móvil. Las tablas extensas desplazan dentro de una región identificada y enfocable. Acciones con objetivo mínimo de 44 px; encabezados y campos envuelven identificadores largos. A 767 px se apilan formularios, encabezado y bloques financieros; la navegación usa un selector nativo compacto con los cuatro grupos.

Las decisiones reutilizan [referencias públicas ya verificadas](references.md): mantener importe legible, reunir evidencia de operación y separar registro de pago/aplicación. Se leyó UI UX Pro Max y se ejecutaron `search.py 'B2B financial operations dashboard' --design-system -p BoviCierre --density 8` y `search.py 'accessible forms state management' --stack react`. Su patrón promocional y modo oscuro no se adoptaron porque esta interfaz sirve al trabajo operativo; se aplican sus reglas de etiquetas, foco y controles.

Los formularios muestran el error del servidor junto al campo mediante `aria-describedby`, enfocan el resumen tras envío fallido y preservan los valores. Reintentos de comandos preservan contenido, clave y versión en sessionStorage por principal y sede, con captura bloqueada mientras el resultado sea incierto. Cada ruta incluye la sede; al cambiar de sede se desmonta su contenido y AbortController cancela los GET pendientes. Para archivos y altas de usuario se persiste únicamente clave y huella SHA256; el contenido binario o contraseña requiere nueva selección al recargar. Sesión en cookie y CSRF en memoria; no se guardan contraseñas ni tokens en localStorage. Importes y pesos conservan cadenas decimales; el navegador no suma totales.

La compilación y las pruebas unitarias son verificaciones estructurales. La verificación visual y el recorrido con API real deben registrarse por separado en [evidencia](../testing/evidence.md); no se declara prueba de teléfono físico ni rendimiento GPU a partir de la compilación.

La revisión en Chrome con GPU Intel confirmó ausencia de desplazamiento horizontal global en 390, 768 y 1440 px. Las tablas conservan desplazamiento propio; los textos accesibles de sus botones están anclados a cada botón para no extender el documento. Las capturas y los resultados del recorrido real se registran aparte del build.
