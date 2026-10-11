# Diagramas

Fuentes editables `.drawio` (mxGraph con objetos y conectores reales, se abren en draw.io / diagrams.net) en `sources/`; exportes vectoriales SVG y PDF en `exports/`. Las fuentes se generan de forma reproducible con `tools/diagramas/gen_mer.py` (láminas 1–6) y `tools/diagramas/gen_relacional.py` (lámina 7); después pueden editarse a mano en draw.io (si se edita a mano, no volver a ejecutar el generador sobre ese archivo sin conservar los cambios).

| Lámina | Fuente | Contenido | Estado |
|---|---|---|---|
| 1 | `mer-01-general.drawio` (A2) | Vista por dominios, relaciones principales sin atributos | exportada, revisada |
| 2 | `mer-02-identidad.drawio` (A3) | Empresa, Sucursal, Usuario, Rol, Parte, Predio, Animal, Identificacion | exportada, revisada |
| 3 | `mer-03-operaciones.drawio` | Operacion, LoteOperacion, ContratoVersion, CondicionLote, Pesaje | exportada, revisada |
| 4 | `mer-04-inventario.drawio` | SeleccionCompra/Venta, PosicionInventario, ReservaVenta, MovimientoInventario | exportada, revisada |
| 5 | `mer-05-liquidaciones.drawio` | Liquidacion, Concepto, Ajuste, Gasto, AsignacionCosto, Asiento, Pago, AplicacionPago | exportada, revisada |
| 6 | `mer-06-evidencia.drawio` | Documento, RevisionAdministrativa, PeriodoCierre, CierrePeriodoVersion, AuditoriaEvento | exportada, revisada |
| 7 | `mer-07-relacional.drawio` (5 páginas) | Lógico relacional por módulo (no Chen), FK entre páginas como [pN] | exportada, revisada |

Exportación (draw.io CLI no instalado localmente):
```bash
docker run --rm -u $(id -u):$(id -g) -e HOME=/tmp -w /data -v "$PWD/docs/diagrams/sources":/data \
  -v "$PWD/docs/diagrams/exports":/out rlespinasse/drawio-export:v4.5.0 -f pdf -o /out   # repetir con -f svg
```

## Revisión de exportes (2026-10-10, por Claude sobre PNG renderizados)
| Criterio | Resultado |
|---|---|
| Acentos y texto | correctos (UTF-8) |
| Superposiciones | corregidas en láminas 1, 3, 4, 5 y 6 tras primera revisión; lámina 7 p4 mantiene un cruce de conector (asignacion_costo → gasto_operacion) |
| Cardinalidades | (mín,máx) junto a la entidad, tomadas de `docs/database/relationship-matrix.md` |
| Conectores | conectados a objetos (no flotantes); recursivas con dos conectores de rol |
| Blanco y negro | el significado lo dan las formas (doble rectángulo, doble rombo, línea doble, óvalo discontinuo); el color sólo agrupa dominios |
| Leyenda, fecha y versión | en cada lámina (v0.1, 2026-10-10) |
| PDF | vectorial con capa de texto (`pdftotext` extrae los rótulos); tamaño ≈ A3 horizontal (lámina 1 ≈ A2) |
| SVG | rótulos HTML: algunos visores sin soporte de `foreignObject` muestran texto de respaldo |

Pendiente: revisión humana de la semántica por Aldo antes de marcar TASK-A-003 como hecha.
