#!/usr/bin/env python3
"""Diagrama lógico relacional COMPLETO en una sola lámina (notación pata de gallo / IE).

Fuente: tools/esquema/esquema.py. Salida: docs/diagrams/sources/relacional-completo.drawio
- Cada tabla es un contenedor con una fila por columna: claves | nombre | tipo | NN.
- Cada FK conecta la fila de la columna FK con la fila de la columna referenciada.
- Pata de gallo: lado hijo (0..N, o 0..1 si la FK es única); lado padre ‖ (exactamente 1) si la FK es NOT NULL,
  o o| (0..1) si es opcional. Línea continua = relación identificante (FK dentro de la PK); discontinua = no identificante.
"""
import pathlib, sys
from xml.sax.saxutils import escape
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "esquema"))
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from esquema import TABLAS, verificar
from chen import COLORES, VERSION, FECHA
from rutas import enrutar
import xml.etree.ElementTree as ET

OUT = pathlib.Path(__file__).resolve().parents[2] / "docs/diagrams/sources/relacional-completo.drawio"
COLOR = {"org": COLORES["org"], "ope": COLORES["ope"], "inv": COLORES["inv"], "liq": COLORES["liq"], "evi": COLORES["evi"], "tec": "#eeeeee"}
NOMBRE_MOD = {"org": "Organización e identidad (maestros · nodo A)", "ope": "Operaciones, contratos y pesajes",
              "inv": "Inventario", "liq": "Liquidaciones, costos, pagos y periodos", "evi": "Evidencia, revisión y auditoría",
              "tec": "Soporte técnico (local, no replicado salvo outbox)"}
# Carriles (columna x) y orden vertical dentro de cada carril: padres arriba.
CARRILES = [
    ("org", ["empresa", "sucursal", "rol_aplicacion", "usuario", "membresia_usuario", "parte", "predio"]),
    ("org", ["animal", "animal_identificacion", "documento", "operacion_documento", "revision_administrativa", "revision_documento", "auditoria_evento"]),
    ("ope", ["operacion", "folio_contador", "lote_operacion", "contrato_version", "condicion_lote", "pesaje", "pesaje_animal"]),
    ("inv", ["seleccion_compra", "posicion_inventario", "seleccion_venta", "reserva_venta", "movimiento_inventario"]),
    ("liq", ["periodo_cierre", "cierre_periodo_version", "liquidacion", "concepto_liquidacion", "ajuste_liquidacion", "pago", "aplicacion_pago"]),
    ("liq", ["gasto_operacion", "asignacion_costo", "asiento_valoracion"]),
    ("tec", ["evento_outbox", "clave_idempotencia", "mensaje_inbox", "infra.nodo_config", "infra.entrega_outbox", "infra.importacion_fuente"]),
]
ANCHO, FILA, CAB, GAP_X, GAP_Y, X0, Y0 = 470, 20, 30, 260, 70, 60, 160
ANCHOS = (78, 232, 160)
TITULOS = ["Organización (maestros · nodo A)", "Identidad animal · evidencia y auditoría", "Operaciones, contratos y pesajes",
           "Inventario", "Periodos, liquidaciones y pagos", "Costos y valoración", "Soporte técnico (local)"]  # claves | columna | tipo + NN


def cid(t, c=None):
    base = "t_" + t.replace(".", "_")
    return base if c is None else f"{base}__{c}"


def marcas_fk(tabla, loc):
    _, _, cols, _, uks = tabla
    pk = {c for c, _, marcas in cols if "PK" in marcas}
    scope = {c for c, _, _ in cols if c in ("empresa_id", "sucursal_id")}
    claves = [pk] + [set(uk) for uk in uks]
    cubiertas = set().union(*(set(uk) for uk in uks)) if uks else set()
    claves += [scope | {c} for c, _, marcas in cols if "UK" in marcas and c not in cubiertas and c not in pk]
    unica = any(clave <= set(loc) for clave in claves)
    nulos = any("NN" not in marcas and "PK" not in marcas for c, _, marcas in cols if c in loc)
    return "ERzeroToOne" if unica else "ERzeroToMany", "ERzeroToOne" if nulos else "ERmandOne", set(loc) <= pk


def main():
    verificar()
    por_nombre = {t[1]: t for t in TABLAS}
    assert sorted(n for _, ns in CARRILES for n in ns) == sorted(por_nombre), "tabla sin carril o repetida"
    celdas, aristas = [], []
    alto_max = 0
    for i, (mod, nombres) in enumerate(CARRILES):
        x, y = X0 + i * (ANCHO + GAP_X), Y0
        for n in nombres:
            _, _, cols, fks, _ = por_nombre[n]
            fk_cols = {c for loc, _, _ in fks for c in loc}
            alto = CAB + FILA * len(cols)
            celdas.append(
                f'<mxCell id="{cid(n)}" value="{escape(n)}" style="swimlane;fontStyle=1;childLayout=stackLayout;horizontal=1;startSize={CAB};'
                f'horizontalStack=0;resizeParent=1;collapsible=0;marginBottom=0;html=1;fillColor={COLOR[mod]};strokeColor=#334155;'
                f'fontFamily=Helvetica;fontSize=13;swimlaneFillColor=#ffffff;" vertex="1" parent="1">'
                f'<mxGeometry x="{x}" y="{y}" width="{ANCHO}" height="{alto}" as="geometry"/></mxCell>')
            for j, (cn, tipo, marcas) in enumerate(cols):
                claves = " ".join(k for k in ("PK", "FK", "UK") if k in marcas or (k == "FK" and cn in fk_cols))
                negrita = "fontStyle=5;" if "PK" in marcas else ""
                fila_id = cid(n, cn)
                celdas.append(
                    f'<mxCell id="{fila_id}" value="" style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;'
                    f'collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;top=0;left=0;right=0;'
                    f'bottom={1 if ("PK" in marcas and (j + 1 == len(cols) or "PK" not in cols[j + 1][2])) else 0};" '
                    f'vertex="1" parent="{cid(n)}"><mxGeometry y="{CAB + j * FILA}" width="{ANCHO}" height="{FILA}" as="geometry"/></mxCell>')
                xx = 0
                for k, (txt, w) in enumerate(zip((claves, cn, tipo + ("  NN" if "NN" in marcas else "")), ANCHOS)):
                    celdas.append(
                        f'<mxCell id="{fila_id}__{k}" value="{escape(txt)}" style="shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;'
                        f'bottom=0;right=0;align=left;spacingLeft=6;overflow=hidden;fontFamily=Helvetica;fontSize=11;'
                        f'{negrita if k < 2 else ""}{"fontStyle=1;" if k == 0 and txt else ""}" vertex="1" parent="{fila_id}">'
                        f'<mxGeometry x="{xx}" width="{w}" height="{FILA}" as="geometry"/></mxCell>')
                    xx += w
            for loc, ref, rcols in fks:
                hijo, padre, identificante = marcas_fk(por_nombre[n], loc)
                # fila a conectar: última columna "propia" de la FK (no empresa/sucursal) y su correspondiente referenciada
                k = max(range(len(loc)), key=lambda q: (loc[q] not in ("empresa_id", "sucursal_id"), q))
                src, dst = cid(n, loc[k]), cid(ref, rcols[k])
                aristas.append(
                    f'<mxCell id="fk_{len(aristas)}" value="" style="edgeStyle=entityRelationEdgeStyle;html=1;rounded=0;endSize=14;startSize=14;'
                    f'startArrow={hijo};startFill=0;endArrow={padre};endFill=0;strokeColor=#475569;strokeWidth=1.5;jumpStyle=arc;jumpSize=8;'
                    f'{"" if identificante else "dashed=1;"}" edge="1" parent="1" source="{src}" target="{dst}">'
                    f'<mxGeometry relative="1" as="geometry"/></mxCell>')
            y += alto + GAP_Y
        alto_max = max(alto_max, y)
        # rótulo de carril
        celdas.append(f'<mxCell id="lane_{i}" value="{escape(TITULOS[i])}" style="text;html=1;fontSize=14;fontStyle=1;align=left;verticalAlign=bottom;" '
                      f'vertex="1" parent="1"><mxGeometry x="{x}" y="{Y0 - 40}" width="{ANCHO}" height="30" as="geometry"/></mxCell>')
    ancho = X0 * 2 + len(CARRILES) * (ANCHO + GAP_X) - GAP_X
    alto = alto_max + 300
    marco = (f'<mxCell id="marco" value="" style="rounded=0;fillColor=none;strokeColor=#666666;connectable=0;" vertex="1" parent="1">'
             f'<mxGeometry x="20" y="20" width="{ancho - 40}" height="{alto - 40}" as="geometry"/></mxCell>'
             f'<mxCell id="titulo" value="&lt;b&gt;BoviCierre — Modelo lógico relacional completo&lt;/b&gt;&lt;br&gt;&lt;span style=&quot;font-size:13px&quot;&gt;'
             f'{len(TABLAS)} tablas · {sum(len(t[3]) for t in TABLAS)} claves foráneas · PostgreSQL 18 · {VERSION} · {FECHA} · fuente: tools/esquema/esquema.py&lt;/span&gt;" '
             f'style="text;html=1;fontSize=26;align=left;verticalAlign=top;" vertex="1" parent="1">'
             f'<mxGeometry x="60" y="40" width="2200" height="70" as="geometry"/></mxCell>')
    ley_y = alto_max + 30
    leyenda = (
        f'<mxCell id="ley" value="&lt;b&gt;Leyenda (notación pata de gallo / IE)&lt;/b&gt;&lt;br&gt;'
        f'PK clave primaria (subrayada) · FK clave foránea · UK participa en clave única · NN NOT NULL · GEN columna generada&lt;br&gt;'
        f'Extremo padre: ‖ exactamente uno (FK NOT NULL) · o| cero o uno (FK opcional). Extremo hijo: o&lt; cero o muchos · o| cero o uno (FK única)&lt;br&gt;'
        f'Línea continua: relación identificante (la FK forma parte de la PK) · discontinua: no identificante&lt;br&gt;'
        f'Triángulo central: dirección FK → clave referenciada; los símbolos de los extremos indican cardinalidad.&lt;br&gt;Todas las FK locales incluyen (empresa_id, sucursal_id); las FK a maestros incluyen empresa_id. Cada conector une la columna FK con la columna referenciada.&lt;br&gt;'
        f'Restricciones no gráficas (CHECK, UNIQUE parciales, EXCLUDE, triggers): docs/database/data-dictionary.md y administration.md" '
        f'style="text;html=1;fontSize=13;align=left;verticalAlign=top;spacing=8;strokeColor=#334155;fillColor=#f5f5f5;" vertex="1" parent="1">'
        f'<mxGeometry x="60" y="{ley_y}" width="1500" height="140" as="geometry"/></mxCell>')
    xml = (f'<mxfile host="bovicierre-gen" agent="tools/diagramas/gen_relacional_completo.py" version="24.0.0">'
           f'<diagram id="relacional-completo" name="Relacional completo"><mxGraphModel grid="1" gridSize="10" page="1" pageScale="1" '
           f'pageWidth="{ancho}" pageHeight="{alto}" background="#ffffff" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
           f'{marco}{"".join(celdas)}{"".join(aristas)}{leyenda}</root></mxGraphModel></diagram></mxfile>\n')
    OUT.write_text(ET.tostring(enrutar(ET.fromstring(xml)), encoding="unicode"), encoding="utf-8")
    print(f"generado {OUT.name}: {len(TABLAS)} tablas, {len(aristas)} FK, lienzo {ancho}x{alto}")


if __name__ == "__main__":
    main()
