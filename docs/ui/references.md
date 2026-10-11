# Referencias para liquidación y aplicación de pagos

Consulta: **2026-10-11**. Producto: BoviCierre, comercializador/acopiador con 1–2 sedes; usuarios OPE y CAJ. Problema elegido: saber qué se confirmó, qué se entregó y qué queda por cobrar/pagar sin confundir los tres hechos. La mejora es documental para TASK-J-002/J-012/J-013: aún no existe una interfaz ejecutable.

## Evidencia pública

| Fuente primaria | Observación comprobada | Adaptación propuesta |
|---|---|---|
| [CattleMax: Ranch-Related Financial Record Keeping](https://help.cattlemax.com/article/525-ranch-related-financial-record-keeping), actualización indicada: 2026-08-10 | El texto describe un área financiera con rango de fechas; tickets con comprador, fecha, pesos, precios y gastos; adjuntos asociados a ingresos/gastos. También indica que añadir animales al ticket cambia su estado a vendido. | Reunir condiciones, evidencia y desglose dentro del expediente de la operación. Mantener visibles folio, contraparte y fecha. La transición económica de BoviCierre continúa siendo ConfirmarCompra/Venta, con entrega y pago separados. |
| [AgriWebb: Sale Records (IAM)](https://help.agriwebb.com/en/articles/3638340-sale-records-iam), fecha indicada: 2026-07-23 | El texto documenta selección de animales, campos obligatorios con asterisco, modos básico/avanzado, acceso web desde la lista de animales y revisión de ingresos/costos al guardar. | Mantener identificación y conteo de posiciones a la vista; marcar campos obligatorios; mostrar detalle de conceptos después del resumen. No ocultar requisitos de confirmación ni copiar edición/borrado de hechos confirmados. |
| [Odoo 16: Payments](https://www.odoo.com/documentation/16.0/applications/finance/accounting/payments/multiple.html) | El resultado indexado por el buscador describe pagos vinculados o independientes, varios pagos por factura y un saldo restante en pagos parciales. La apertura directa de esta página y de la ruta 19.0 falló por timeout. | Separar «Registrar cobro/pago» de «Aplicar a liquidación» y mostrar disponible del pago junto al saldo de la obligación. Referencia histórica de patrón, sin adoptar conciliación bancaria ni reglas fiscales. |

**Método y límites:** CattleMax y AgriWebb se leyeron mediante extracción textual y se capturaron sus páginas públicas de ayuda con Chrome DevTools MCP; Odoo sólo mediante el extracto indexado. No se inició sesión, no se llamó a sus APIs ni se inspeccionó su interfaz privada. Las imágenes de producto incrustadas en la ayuda son evidencia documental, no una sesión interactiva de esas aplicaciones. No se comprobaron sus flujos autenticados, foco, teclado, estados vacíos/error ni rendimiento del producto.

### Capturas e inspección real

[Registro sanitizado](evidence/mcp-smoke.json): Chrome DevTools MCP **1.10.1**, Node **24.21.0**, 30 herramientas enumeradas y llamadas reales de navegación, snapshot, DOM/CSS, consola, emulación y captura exitosas. Navegador visible con perfil aislado; renderer registrado `ANGLE (Intel, Mesa Intel(R) Graphics (RPL-P), OpenGL ES 3.2)`. Capturas PNG verificadas con anchos exactos **390/768/1440** y altura 1000 px; emulación de viewport en el mismo navegador, no prueba en teléfono físico.

| Página pública | Capturas | Observación visual comprobada |
|---|---|---|
| CattleMax Help | [390](evidence/cattlemax-financial-390.png) · [768](evidence/cattlemax-financial-768.png) · [1440](evidence/cattlemax-financial-1440.png) | A 1440, categorías en lateral y artículo en panel blanco; la imagen financiera incrustada separa ingresos/gastos y ubica «Add New» arriba. A 390 desaparece el lateral, aparece menú y el texto envuelve; la imagen financiera se reduce hasta dificultar leer cifras. BoviCierre debe conservar legibilidad de sus importes, sin imitar esa reducción. CSS del título documental: Helvetica Neue, 22 px. |
| AgriWebb Help | [390](evidence/agriwebb-sale-390.png) · [768](evidence/agriwebb-sale-768.png) · [1440](evidence/agriwebb-sale-1440.png) | A 390 se observan menú, búsqueda, breadcrumbs envueltos, título y descripción, control de índice plegable y lista de datos del registro; primera vista sin desbordamiento horizontal visible. CSS del título documental: system-ui, 32 px. Es estructura de ayuda, no evidencia de las tablas internas del producto. |

Se inspeccionaron visualmente CattleMax 1440/390 y AgriWebb 390; los otros tamaños cuentan con captura y dimensiones verificadas, sin afirmar revisión visual completa. Consola de las referencias: CattleMax registra meta móvil obsoleta; AgriWebb registra aviso de fullscreen, incidencia CSP por `eval`, IDs de campo duplicados e información de Intercom. Son incidencias de páginas externas y no fallos introducidos en BoviCierre. No se copiaron código ni recursos de esas páginas al producto.

## Decisiones para BoviCierre

Son decisiones de diseño a validar con Aldo/Jared y con usuarios; las fuentes no demuestran que mejoren la usabilidad de BoviCierre.

- Encabezado estable con folio, contraparte, sede y dirección POR_COBRAR/POR_PAGAR; tres grupos etiquetados: operación, entrega y saldo. Evita un único «Completado» ambiguo.
- Primero saldo pendiente y siguiente acción permitida; después conceptos, ajustes y aplicaciones. Total de liquidación, saldo de obligación y disponible de pago llevan rótulos diferentes.
- Contexto de la liquidación conservado al registrar/aplicar; pago registrado sin aplicación se muestra como disponible, sin anunciar «liquidación pagada».
- Detalle financiero con importes del servidor y evidencia enlazada; expandir información secundaria sin ocultar campos exigidos por RN-017.
- Interfaz sobria ya definida en [flujos](flows-and-screens.md): texto e ícono además de color, MXN/kg explícitos, foco visible y acciones claras. No se fija una nueva identidad visual sin tokens ni frontend existentes.

## Verificación pendiente

Se consultó la skill local [UI UX Pro Max](../../.agents/skills/ui-ux-pro-max/SKILL.md), instalada por la tarea de herramientas. Búsqueda ejecutada: `python3 .agents/skills/ui-ux-pro-max/scripts/search.py 'error summary validation' --domain ux -n 3`. De sus resultados se adoptan resumen de errores enfocable tras envío fallido, enlaces a campos, errores inline con `aria-describedby` y anuncio accesible. El análisis de tablas realizado en la misma tarea respalda desplazamiento localizado y texto legible; importes financieros se muestran completos, nunca abreviados como «1.2K». Son recomendaciones locales, no observaciones de las páginas anteriores ni validación de usuarios.

La especificación concreta y los casos de aceptación están en [Liquidación → pago → aplicación](flows-and-screens.md#liquidación--pago--aplicación-primera-mejora-documental). Al existir frontend: capturar a 390/768/1440 px, revisar datos largos, teclado, foco, estados y consola; recorrer con API real y datos DEMO. Comparar contra GOLD-04A/B y GOLD-07 sin modificar sus importes. Reutilizar estas referencias para cambios pequeños; investigar de nuevo si cambia el problema o la fuente deja de ser válida.
