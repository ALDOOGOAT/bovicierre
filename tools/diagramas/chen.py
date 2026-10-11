"""Mini-DSL para generar láminas Chen/EER en formato draw.io (mxGraph) con objetos y conectores reales.

Los .drawio generados son la fuente editable; este script sólo los hace reproducibles.
Uso: python3 tools/diagramas/gen_mer.py  → docs/diagrams/sources/*.drawio
"""
from xml.sax.saxutils import escape

VERSION = "v0.1"
FECHA = "2026-10-10"

COLORES = {
    "org": "#dae8fc", "ope": "#d5e8d4", "inv": "#fff2cc",
    "liq": "#f8cecc", "evi": "#e1d5e7", "none": "#ffffff",
}
BASE = "html=1;whiteSpace=wrap;fontFamily=Helvetica;fontSize=12;strokeColor=#000000;strokeWidth=1.2;"


class Pagina:
    def __init__(self, nombre, ancho, alto):
        self.nombre, self.ancho, self.alto = nombre, ancho, alto
        self.celdas, self.geo, self._n = [], {}, 0

    def _id(self, base):
        self._n += 1
        return f"{base}_{self._n}"

    def _vertex(self, cid, valor, estilo, x, y, w, h, padre="1"):
        self.geo[cid] = (x, y, w, h)
        self.celdas.append(
            f'<mxCell id="{cid}" value="{escape(valor, {chr(34): "&quot;"})}" style="{estilo}" vertex="1" parent="{padre}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return cid

    # --- símbolos Chen ---
    def entidad(self, cid, nombre, x, y, debil=False, dom="none", w=150, h=50):
        estilo = BASE + f"fillColor={COLORES[dom]};fontStyle=1;"
        estilo += "shape=ext;double=1;margin=4;" if debil else "rounded=0;"
        return self._vertex(cid, nombre, estilo, x, y, w, h)

    def relacion(self, cid, verbo, x, y, identificante=False, w=130, h=70):
        estilo = BASE + "shape=rhombus;fillColor=#ffffff;fontSize=11;"
        self._vertex(cid, verbo, estilo, x, y, w, h)
        if identificante:  # rombo interior: doble rombo
            m = 7
            self._vertex(self._id(cid + "_in"), "", BASE + "shape=rhombus;fillColor=none;connectable=0;",
                         x + m * 1.6, y + m, w - 2 * m * 1.6, h - 2 * m)
        return cid

    def atributo(self, duenio, nombre, x, y, clave=False, parcial=False, derivado=False, w=110, h=34):
        cid = self._id(duenio + "_a")
        if clave:
            valor = f"<u>{escape(nombre)}</u>"
        elif parcial:
            valor = f'<span style="text-decoration: underline dashed;">{escape(nombre)}</span>'
        else:
            valor = escape(nombre)
        estilo = BASE + "ellipse;fillColor=#ffffff;fontSize=11;" + ("dashed=1;" if derivado else "")
        self.geo[cid] = (x, y, w, h)
        self.celdas.append(
            f'<mxCell id="{cid}" value="{escape(valor, {chr(34): "&quot;"})}" style="{estilo}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        self.linea(cid, duenio)
        return cid

    def atributos(self, duenio, lista, lado="top", sep=118, dist=70):
        """lista: [(nombre, tipo)] tipo ∈ {'', 'k', 'p', 'd'}"""
        x, y, w, h = self.geo[duenio]
        n = len(lista)
        for i, (nom, t) in enumerate(lista):
            off = (i - (n - 1) / 2) * sep
            if lado == "top":
                ax, ay = x + w / 2 + off - 55, y - dist
            elif lado == "bottom":
                ax, ay = x + w / 2 + off - 55, y + h + dist - 34
            elif lado == "left":
                ax, ay = x - dist - 110, y + h / 2 + off * 0.42 - 17
            else:
                ax, ay = x + w + dist, y + h / 2 + off * 0.42 - 17
            self.atributo(duenio, nom, ax, ay, clave=t == "k", parcial=t == "p", derivado=t == "d")

    def linea(self, a, b, card=None, total=False, pos=-0.55, etiqueta_dy=-12, extra="", puntos=None):
        cid = self._id("e")
        estilo = "endArrow=none;html=1;rounded=0;strokeColor=#000000;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;"
        estilo += ("shape=link;strokeWidth=1;width=4;" if total else "strokeWidth=1.2;") + extra
        self.celdas.append(
            f'<mxCell id="{cid}" value="" style="{estilo}" edge="1" parent="1" source="{a}" target="{b}">'
            f'<mxGeometry relative="1" as="geometry">'
            + (("<Array as=\"points\">" + "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in puntos) + "</Array>") if puntos else "")
            + '</mxGeometry></mxCell>')
        if card:
            self.celdas.append(
                f'<mxCell id="{cid}_l" value="{escape(card)}" style="edgeLabel;html=1;align=center;verticalAlign=middle;'
                f'resizable=0;points=[];fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" vertex="1" connectable="0" parent="{cid}">'
                f'<mxGeometry x="{pos}" y="{etiqueta_dy}" relative="1" as="geometry"><mxPoint as="offset"/></mxGeometry></mxCell>')
        return cid

    def une(self, entidad, relacion, card, total=False, pos=-0.55, extra=""):
        """Entidad—relación con (mín,máx) junto a la entidad."""
        return self.linea(entidad, relacion, card, total, pos, extra=extra)

    def centro(self, cid):
        x, y, w, h = self.geo[cid]
        return x + w / 2, y + h / 2

    def rel_entre(self, cid, verbo, a, b, card_a=None, card_b=None, total_a=False, total_b=False,
                  ident=False, dx=0, dy=0, w=130, h=70):
        """Rombo en el punto medio entre a y b (más desplazamiento) y sus dos líneas."""
        (ax, ay), (bx, by) = self.centro(a), self.centro(b)
        self.relacion(cid, verbo, (ax + bx) / 2 - w / 2 + dx, (ay + by) / 2 - h / 2 + dy, ident, w, h)
        self.une(a, cid, card_a, total_a)
        self.une(b, cid, card_b, total_b)
        return cid

    def recursiva(self, cid, verbo, ent, rol1, rol2, lado="right", dist=60, w=120, h=64):
        """Relación recursiva: rombo al costado y dos conectores separados (roles)."""
        x, y, ew, eh = self.geo[ent]
        if lado == "right":
            rx, ry = x + ew + dist, y + eh / 2 - h / 2
            e1, e2 = "exitX=1;exitY=0.2;entryX=0.5;entryY=0;", "exitX=1;exitY=0.8;entryX=0.5;entryY=1;"
        elif lado == "left":
            rx, ry = x - dist - w, y + eh / 2 - h / 2
            e1, e2 = "exitX=0;exitY=0.2;entryX=0.5;entryY=0;", "exitX=0;exitY=0.8;entryX=0.5;entryY=1;"
        else:  # bottom
            rx, ry = x + ew / 2 - w / 2, y + eh + dist
            e1, e2 = "exitX=0.2;exitY=1;entryX=0;entryY=0.5;", "exitX=0.8;exitY=1;entryX=1;entryY=0.5;"
        self.relacion(cid, verbo, rx, ry, w=w, h=h)
        self.une(ent, cid, rol1, extra=e1 + "edgeStyle=orthogonalEdgeStyle;", pos=-0.3)
        self.une(ent, cid, rol2, extra=e2 + "edgeStyle=orthogonalEdgeStyle;", pos=-0.3)
        return cid

    def ref(self, cid, nombre, lamina, x, y, debil=False, w=150, h=50):
        """Entidad definida en otra lámina: borde discontinuo y referencia."""
        estilo = BASE + "fillColor=#ffffff;fontStyle=1;dashed=1;"
        estilo += "shape=ext;double=1;margin=4;" if debil else "rounded=0;"
        return self._vertex(cid, f"{nombre}<br><span style='font-weight:normal;font-size:10px'>(ver lámina {lamina})</span>",
                            estilo, x, y, w, h)

    def nota(self, texto, x, y, w=260, h=60, tam=11):
        return self._vertex(self._id("nota"), texto,
                            BASE + f"shape=note;size=12;fillColor=#f5f5f5;align=left;verticalAlign=top;spacing=6;fontSize={tam};",
                            x, y, w, h)

    def texto(self, texto, x, y, w, h, tam=12, negrita=False, alinear="left"):
        return self._vertex(self._id("t"), texto,
                            f"text;html=1;whiteSpace=wrap;fontFamily=Helvetica;fontSize={tam};align={alinear};verticalAlign=top;"
                            + ("fontStyle=1;" if negrita else ""), x, y, w, h)

    def marco(self, titulo, subtitulo, etiqueta="MER conceptual · notación Chen/EER (mín,máx) junto a la entidad"):
        self._vertex(self._id("marco"), "", "rounded=0;fillColor=none;strokeColor=#666666;strokeWidth=1;connectable=0;",
                     10, 10, self.ancho - 20, self.alto - 20)
        self.texto(f"<b>BoviCierre — {escape(titulo)}</b><br><span style='font-size:11px'>{escape(subtitulo)}</span>",
                   30, 22, 900, 44, tam=18)
        self.texto(f"{etiqueta}<br>{VERSION} · {FECHA} · Fuente: docs/database/",
                   self.ancho - 430, 22, 400, 40, tam=10, alinear="right")

    def leyenda(self, x, y):
        self.texto("<b>Leyenda</b>", x, y, 200, 20, tam=12)
        yy = y + 26
        self._vertex(self._id("lg"), "Entidad fuerte", BASE + "rounded=0;fontSize=10;", x, yy, 100, 30)
        self._vertex(self._id("lg"), "Entidad débil", BASE + "shape=ext;double=1;margin=3;fontSize=10;", x + 110, yy, 100, 30)
        yy += 40
        self._vertex(self._id("lg"), "relación", BASE + "shape=rhombus;fontSize=10;", x, yy, 100, 44)
        self.relacion(self._id("lgr"), "identif.", x + 110, yy, identificante=True, w=110, h=44)
        yy += 54
        self._vertex(self._id("lg"), "<u>clave</u>", BASE + "ellipse;fontSize=10;", x, yy, 64, 26)
        self._vertex(self._id("lg"), '<span style="text-decoration: underline dashed;">parcial</span>', BASE + "ellipse;fontSize=10;", x + 72, yy, 64, 26)
        self._vertex(self._id("lg"), "derivado", BASE + "ellipse;dashed=1;fontSize=10;", x + 144, yy, 64, 26)
        yy += 36
        self.texto("═ participación total &nbsp; ─ parcial<br>(mín,máx): instancias de la relación<br>en que participa UNA instancia de la<br>entidad junto a la que se escribe.<br>Borde discontinuo: definida en otra lámina.",
                   x, yy, 230, 80, tam=10)

    def xml(self):
        return (f'<diagram id="{escape(self.nombre)}" name="{escape(self.nombre)}">'
                f'<mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="0" '
                f'fold="1" page="1" pageScale="1" pageWidth="{self.ancho}" pageHeight="{self.alto}" background="#ffffff" math="0" shadow="0">'
                f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{"".join(self.celdas)}</root></mxGraphModel></diagram>')


def guardar(ruta, paginas):
    contenido = ('<mxfile host="bovicierre-gen" agent="tools/diagramas/gen_mer.py" version="24.0.0">'
                 + "".join(p.xml() for p in paginas) + "</mxfile>\n")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
