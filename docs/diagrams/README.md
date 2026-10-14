# Diagramas

Fuentes editables `.drawio` (mxGraph con objetos y conectores reales, se abren en draw.io / diagrams.net) en `sources/`; exportes vectoriales SVG y PDF en `exports/`. Las fuentes se generan de forma reproducible con `tools/diagramas/gen_mer.py` (láminas 1–6) y `tools/diagramas/gen_relacional.py` (lámina 7); después pueden editarse a mano en draw.io (si se edita a mano, no volver a ejecutar el generador sobre ese archivo sin conservar los cambios).

## Revisión visual y direcciones · v0.2 (2026-10-11)

- [Todas las láminas numeradas](exports/laminas-numeradas.pdf): 11 páginas con marcadores (láminas 1–6 y las cinco páginas de la 7).
- Conectores ortogonales por espacios libres, mayor contraste, saltos en cruces y etiquetas separadas de cajas y entre sí. Las relaciones recursivas conservan dos recorridos y sus roles.
- **Chen con indicación adicional de máximo uno:** la punta apunta de la entidad al rombo cuando su participación tiene máximo 1. Máximo N queda sin punta; el rango `(mín,máx)` sigue siendo explícito. La línea doble conserva la participación total. En la vista general, sin cardinalidades, las puntas siguen el verbo `A → relación → B`; su leyenda lo distingue.
- **Relacional:** el triángulo central sigue `FK → clave referenciada`; los extremos mantienen la pata de gallo, opcionalidad y unicidad. La unicidad se determina con la clave completa, no con una columna aislada de una UK compuesta. En la lámina 7, las referencias entre páginas siguen indicadas por `[pN]`.
- La vista general corrige `LoteOperacion → recibe → Pesaje`, y el sentido de lectura de `rige para`, `es seleccionada en` y `proviene de`, conforme a la matriz de relaciones.
- PDF completos: A0 horizontal **1189 × 841 mm**. Lámina 1: A2; restantes numeradas: A3. Todos conservan vectores y texto seleccionable. Cada PDF individual contiene una página; se corrigió la exportación de la lámina 7 que antes incluía páginas posteriores.

Regeneración (Python 3, Docker con la imagen existente y PyMuPDF):
```bash
python3 tools/diagramas/gen_mer.py
python3 tools/diagramas/gen_mer_completo.py
python3 tools/diagramas/gen_relacional.py
python3 tools/diagramas/gen_relacional_completo.py
python3 -m unittest discover -s tools/diagramas -p 'test_*.py'
python3 tools/diagramas/exportar.py
```

Las puntas centrales y etiquetas tienen posición fija para la exportación: después de mover manualmente una línea, ajustar también su punta/etiqueta o regenerar. Conservar cambios manuales antes de ejecutar generadores. La revisión semántica humana sigue pendiente; las pruebas de dibujo no validan una BD implementada. Convenciones de los extremos: [documentación oficial de draw.io](https://www.drawio.com/docs/tutorials/crows-foot-notation/).

## Láminas completas (una sola hoja cada una, A0)
| Archivo | Contenido | Notación | Generador |
|---|---|---|---|
| `mer-completo.drawio` → `exports/mer-completo.pdf/.svg` | **MER conceptual completo**: 31 entidades, atributos (clave, parcial, derivado), 37 relaciones con verbo, cardinalidad (mín,máx) junto a la entidad, participación total (línea doble), débiles e identificantes (doble rectángulo / doble rombo), recursivas con roles | Chen/EER | `tools/diagramas/gen_mer_completo.py` |
| `relacional-completo.drawio` → `exports/relacional-completo.pdf/.svg` | **Modelo lógico relacional completo**: 42 tablas con todas sus columnas, tipo, PK/FK/UK/NN; 83 FK conectadas columna a columna | Pata de gallo (IE): extremo padre ‖ (1) u o\| (0..1) según NOT NULL; extremo hijo o< (0..N) u o\| (FK única); continua = identificante, discontinua = no identificante | `tools/diagramas/gen_relacional_completo.py` desde `tools/esquema/esquema.py` |

Decisiones: el MER completo omite las tablas técnicas (outbox, inbox, idempotencia, infra.*) porque no son conceptos de negocio; el relacional completo sí las incluye en el carril "Soporte técnico". `tools/esquema/esquema.py` es representación del esquema lógico y alimenta el diagrama; `db/migrations/` es la autoridad del DDL físico (ADR-016), no se genera ciegamente desde metadata; `python3 tools/esquema/esquema.py` verifica que toda FK apunte a columnas existentes con la misma aridad.

## Láminas por dominio (detalle, A3)
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

## Sincronización final V11

Relacional completo42tablas/83FK y cinco módulos incorporan periodo/fecha de reconocimiento, naturaleza de pago, leases locales y origen/destino documental. PDF/SVG A0/A3 regenerados, texto/vector conservados, combinado11p; inspección visual del coordinador y cinco pruebas de herramientas. La comparación catálogo A/B cubre columnas/tipos/NN/PK/UK/FK declaradas; no todas las restricciones de negocio. Revisión humana/impresión pendiente.

> **Vigencia (14-oct-2026):** las láminas MER y relacionales siguen correspondiendo al esquema en **V26**: V19–V26 no cambian tablas, columnas ni relaciones (sólo funciones, triggers y roles). Catálogo A/B comparado: 42 tablas, 0 diferencias.
