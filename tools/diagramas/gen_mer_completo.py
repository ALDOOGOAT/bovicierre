#!/usr/bin/env python3
"""MER conceptual COMPLETO (notación Chen/EER) en una sola lámina A0: docs/diagrams/sources/mer-completo.drawio

Entidades, atributos, relaciones con verbo, cardinalidades (mín,máx) junto a la entidad y participación total/parcial.
Cardinalidades: docs/database/relationship-matrix.md (REL-01..37).
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from chen import Pagina, guardar, BASE, COLORES

OUT = pathlib.Path(__file__).resolve().parents[2] / "docs/diagrams/sources/mer-completo.drawio"


def construir():
    p = Pagina("MER completo", 4800, 3500)
    p.marco("MER conceptual completo", "31 entidades · 37 relaciones (REL-01..37) · cardinalidad (mín,máx) junto a la entidad · lámina A0")
    E, D, U, A = p.entidad, p.relacion, p.une, p.atributos

    # ---------- Organización e identidad
    E("empresa", "Empresa", 150, 300, dom="org"); A("empresa", [("id", "k"), ("razón social", ""), ("RFC", "")], "top")
    E("sucursal", "Sucursal (sede)", 750, 300, dom="org"); A("sucursal", [("id", "k"), ("código", ""), ("nombre", ""), ("nodo dueño", "")], "top")
    D("administra", "administra", 430, 290); U("empresa", "administra", "(0,N)"); U("sucursal", "administra", "(1,1)", total=True)
    E("usuario", "Usuario", 150, 700, dom="org"); A("usuario", [("id", "k"), ("login", ""), ("estado", "")], "top", sep=110, dist=62)
    E("rol", "RolAplicacion", 560, 1000, dom="org"); A("rol", [("código", "k"), ("descripción", "")], "bottom")
    D("autoriza", "es autorizado<br>en … con", 720, 680, w=150, h=80)
    U("usuario", "autoriza", "(0,N)"); U("sucursal", "autoriza", "(0,N)", pos=-0.65); U("rol", "autoriza", "(0,N)")
    p.atributo("autoriza", "vigente", 690, 590, w=90)
    E("aud", "AuditoriaEvento", 200, 1050, dom="evi", w=170); A("aud", [("id", "k"), ("comando", ""), ("correlación", ""), ("nodo origen", "")], "bottom", sep=112)
    D("origina_aud", "origina", 190, 870, h=60); U("usuario", "origina_aud", "(0,N)"); U("aud", "origina_aud", "(0,1)")

    E("predio", "Predio", 650, 1400, dom="org"); A("predio", [("id", "k"), ("nombre", ""), ("clave UPP", "")], "bottom", sep=112)
    E("parte", "Parte (contraparte)", 1230, 1400, dom="org", w=170); A("parte", [("id", "k"), ("tipo persona", ""), ("nombre", ""), ("RFC", "")], "bottom", sep=110, dist=64)
    D("responsable", "es responsable<br>de", 920, 1390, w=140); U("parte", "responsable", "(0,N)"); U("predio", "responsable", "(0,1)")

    E("animal", "Animal", 2350, 300, dom="org"); A("animal", [("id", "k"), ("sexo", ""), ("situación", ""), ("nacimiento decl.", "")], "top", sep=112)
    D("opera", "opera en", 1550, 290); U("animal", "opera", "(1,1)", total=True); U("sucursal", "opera", "(0,N)")
    E("ident", "Identificacion", 3350, 300, dom="org"); A("ident", [("id", "k"), ("sistema", ""), ("código normalizado", ""), ("estado", ""), ("vigencia", "")], "top", sep=112)
    D("posee", "posee", 2850, 290); U("animal", "posee", "(0,N)"); U("ident", "posee", "(1,1)", total=True)

    # ---------- Operaciones, contratos y pesajes
    E("op", "Operacion", 1850, 1400, dom="ope"); A("op", [("id", "k"), ("tipo", ""), ("folio", ""), ("fecha", ""), ("estado", ""), ("estado entrega", "d")], "right", dist=50)
    D("tramita", "tramita", 1650, 620); U("sucursal", "tramita", "(0,N)"); U("op", "tramita", "(1,1)", total=True)
    D("interviene", "interviene en", 1500, 1390, w=140); U("parte", "interviene", "(0,N)"); U("op", "interviene", "(1,1)", total=True)
    E("lote", "LoteOperacion", 2550, 1400, debil=True, dom="ope"); A("lote", [("número lote", "p"), ("descripción", "")], "right", dist=40)
    D("contiene", "contiene", 2170, 1390, identificante=True); U("op", "contiene", "(0,N)*"); U("lote", "contiene", "(1,1)", total=True)
    E("ver", "ContratoVersion", 1850, 1950, debil=True, dom="ope"); A("ver", [("número versión", "p"), ("estado", ""), ("política redondeo", "")], "left", dist=40)
    D("conserva", "conserva", 1860, 1650, identificante=True); U("op", "conserva", "(0,N)*"); U("ver", "conserva", "(1,1)", total=True)
    E("cond", "CondicionLote", 2550, 1950, debil=True, dom="ope"); A("cond", [("unidad precio", ""), ("precio unitario", ""), ("base de pesaje", ""), ("deducción pactada", "")], "right", dist=40)
    D("establece", "establece", 2170, 1940, identificante=True); U("ver", "establece", "(0,N)"); U("cond", "establece", "(1,1)", total=True)
    D("rige", "rige para", 2560, 1650, identificante=True); U("lote", "rige", "(0,N)"); U("cond", "rige", "(1,1)", total=True)
    E("pesaje", "Pesaje", 2150, 850, dom="ope"); A("pesaje", [("id", "k"), ("modo", ""), ("bruto/tara", ""), ("neto", "")], "left", dist=40)
    D("recibe_p", "recibe", 2365, 1105); U("lote", "recibe_p", "(0,N)"); U("pesaje", "recibe_p", "(1,1)", total=True)
    D("comprende", "comprende", 2265, 570); U("pesaje", "comprende", "(1,N)", total=True); U("animal", "comprende", "(0,N)")
    p.atributo("comprende", "peso individual (si se midió)", 2010, 600, w=150)
    p.recursiva("corrige", "corrige", "pesaje", "original (0,1)", "corrección (0,1)", lado="bottom", dist=150, w=110)

    # ---------- Inventario
    E("selc", "SeleccionCompra", 2950, 850, debil=True, dom="inv")
    D("essel", "es seleccionado<br>en", 2650, 570, identificante=True, w=140); U("animal", "essel", "(0,N)"); U("selc", "essel", "(1,1)", total=True)
    D("incluyec", "incluye", 2765, 1105, identificante=True); U("lote", "incluyec", "(0,N)"); U("selc", "incluyec", "(1,1)", total=True)
    E("pos", "PosicionInventario", 3550, 850, dom="inv", w=170)
    A("pos", [("id", "k"), ("número ciclo", ""), ("estado", ""), ("motivo baja", ""), ("costo vigente", "d")], "top", sep=112, dist=72)
    D("origina_pos", "origina", 3240, 840); U("selc", "origina_pos", "(0,1)*"); U("pos", "origina_pos", "(1,1)", total=True)
    D("participa", "participa en", 2980, 1080, w=140)
    U("animal", "participa", "(0,N)"); U("pos", "participa", "(1,1)", total=True)
    E("selv", "SeleccionVenta", 3100, 1400, debil=True, dom="inv", w=170)
    D("incluyev", "incluye", 2830, 1390, identificante=True); U("lote", "incluyev", "(0,N)"); U("selv", "incluyev", "(1,1)", total=True)
    D("essv", "es seleccionada<br>en", 3330, 1110, identificante=True, w=140); U("pos", "essv", "(0,N)"); U("selv", "essv", "(1,1)", total=True)
    E("res", "ReservaVenta", 3100, 1950, dom="inv"); A("res", [("id", "k"), ("estado", ""), ("vence en", "")], "left", dist=40)
    D("mantiene", "mantiene", 3120, 1660); U("selv", "mantiene", "(0,N)"); U("res", "mantiene", "(1,1)", total=True)
    E("mov", "MovimientoInventario", 4300, 850, dom="inv", w=180); A("mov", [("id", "k"), ("tipo", ""), ("ocurrido en", ""), ("custodio", "")], "top", sep=112)
    D("registra", "registra", 3950, 840); U("pos", "registra", "(0,N)"); U("mov", "registra", "(1,1)", total=True)
    p.recursiva("revierte_mov", "revierte", "mov", "original (0,1)", "reverso (0,1)", lado="bottom", dist=60, w=110)

    # ---------- Liquidaciones, costos y pagos
    E("liq", "Liquidacion", 1650, 2550, dom="liq"); A("liq", [("id", "k"), ("dirección", ""), ("total", ""), ("saldo", "d")], "left", dist=40)
    D("origina_liq", "origina", 1500, 2150); U("op", "origina_liq", "(0,1)*"); U("liq", "origina_liq", "(1,1)", total=True)
    E("conc", "ConceptoLiquidacion", 1640, 3100, debil=True, dom="liq", w=180); A("conc", [("número concepto", "p"), ("tipo", ""), ("importe", "")], "left", dist=40)
    D("desglosa", "desglosa", 1660, 2820, identificante=True); U("liq", "desglosa", "(1,N)", total=True); U("conc", "desglosa", "(1,1)", total=True)
    E("aju", "AjusteLiquidacion", 2350, 2550, dom="liq", w=170); A("aju", [("id", "k"), ("naturaleza", ""), ("monto", ""), ("motivo", "")], "top", sep=112, dist=64)
    D("recibe_aju", "recibe", 2010, 2540); U("liq", "recibe_aju", "(0,N)"); U("aju", "recibe_aju", "(1,1)", total=True)
    E("apl", "AplicacionPago", 950, 2550, dom="liq"); A("apl", [("id", "k"), ("importe", ""), ("naturaleza", "")], "top", sep=112, dist=64)
    D("abona", "abona a", 1310, 2540); U("apl", "abona", "(1,1)", total=True); U("liq", "abona", "(0,N)")
    p.recursiva("revierte_aju", "revierte", "aju", "original (0,1)", "reverso (0,1)", lado="bottom", dist=70, w=110)
    p.recursiva("revierte_apl", "revierte", "apl", "original (0,1)", "reverso (0,1)", lado="bottom", dist=60, w=110)
    E("pago", "Pago", 250, 2550, dom="liq", w=140); A("pago", [("id", "k"), ("tipo", ""), ("importe", ""), ("estado", "")], "top", sep=96, dist=64)
    D("usa", "proviene de", 610, 2540); U("apl", "usa", "(1,1)", total=True); U("pago", "usa", "(0,N)")
    p.recursiva("reembolsa", "reembolsa", "pago", "origen (0,N)", "reembolso (0,1)", lado="bottom", dist=60, w=110)
    D("realiza", "realiza", 760, 1960); U("parte", "realiza", "(0,N)"); U("pago", "realiza", "(1,1)", total=True)
    E("gasto", "GastoOperacion", 2350, 3100, dom="liq"); A("gasto", [("id", "k"), ("naturaleza", ""), ("clasificación", "")], "bottom", sep=112, dist=60)
    D("incurre", "incurre en", 2120, 2240); U("op", "incurre", "(0,N)"); U("gasto", "incurre", "(1,1)", total=True)
    p.recursiva("bonifica", "bonifica", "gasto", "original (0,N)", "bonificación (0,1)", lado="right", dist=50, w=110)
    E("asig", "AsignacionCosto", 2950, 2750, dom="liq"); A("asig", [("id", "k"), ("método", ""), ("base", ""), ("importe", "")], "bottom", sep=112, dist=60)
    D("proviene", "proviene de<br>(exactamente 1)", 2050, 2830, w=150, h=80)
    U("conc", "proviene", "(0,N)"); U("gasto", "proviene", "(0,N)"); U("aju", "proviene", "(0,N)"); U("asig", "proviene", "(1,1)", total=True)
    D("asigna", "se asigna a", 3565, 2200); U("asig", "asigna", "(1,1)", total=True); U("pos", "asigna", "(0,N)")
    E("asi", "AsientoValoracion", 4150, 2700, dom="liq", w=170)
    A("asi", [("id", "k"), ("clase", ""), ("importe", ""), ("deltas (derivados)", "d")], "right", dist=40)
    D("acumula", "acumula", 3900, 1700); U("pos", "acumula", "(1,N)", total=True); U("asi", "acumula", "(1,1)", total=True)

    # ---------- Evidencia y periodos
    E("doc", "Documento", 1000, 1000, dom="evi"); A("doc", [("id", "k"), ("tipo documental", ""), ("sha256", ""), ("versión", "")], "left", dist=40)
    D("incorpora", "incorpora", 1520, 1170); U("op", "incorpora", "(0,N)"); U("doc", "incorpora", "(0,N)")
    p.recursiva("reemplaza_doc", "reemplaza", "doc", "original (0,1)", "sustituto (0,1)", lado="bottom", dist=110, w=110)
    p.atributo("incorpora", "rol", 1560, 1265, w=70)
    E("rev", "RevisionAdministrativa", 990, 560, dom="evi", w=180); A("rev", [("id", "k"), ("criterio", ""), ("resultado", "")], "left", dist=40)
    D("examina", "examina", 1010, 785, h=60); U("rev", "examina", "(1,N)", total=True); U("doc", "examina", "(0,N)")
    D("revisa", "revisa<br>(op. XOR ident.)", 1450, 420, w=150, h=80)
    U("rev", "revisa", "(1,1)", total=True); U("op", "revisa", "(0,N)")
    p.linea("ident", "revisa", "(0,N)", pos=-0.97, etiqueta_dy=14,
            extra="edgeStyle=orthogonalEdgeStyle;exitX=1;exitY=0.5;entryX=0.5;entryY=0;",
            puntos=[(3780, 325), (3780, 170), (1525, 170)])
    p.recursiva("sustituye", "sustituye", "rev", "anterior (0,1)", "posterior (0,1)", lado="right", dist=40, w=110)
    E("per", "PeriodoCierre", 3200, 3250, dom="evi"); A("per", [("id", "k"), ("desde", ""), ("hasta", ""), ("estado", "")], "bottom", sep=112, dist=60)
    D("imputa", "se imputa a", 3700, 3020); U("asi", "imputa", "(1,1)", total=True); U("per", "imputa", "(0,N)")
    D("imputa2", "se imputa a", 2780, 2950); U("aju", "imputa2", "(1,1)", total=True); U("per", "imputa2", "(0,N)")
    E("cpv", "CierrePeriodoVersion", 4150, 3250, debil=True, dom="evi", w=180)
    A("cpv", [("número versión", "p"), ("tipo", ""), ("hash conciliación", "")], "bottom", sep=116, dist=60)
    D("conserva_c", "conserva", 3700, 3240, identificante=True); U("per", "conserva_c", "(0,N)"); U("cpv", "conserva_c", "(1,1)", total=True)

    p.nota("* Mínimo 0 en borrador; al CONFIRMAR: ≥1 lote, 1 versión ACEPTADA (REL-05/06), 1 posición por selección (REL-09) y 1 liquidación principal (REL-16).<br>"
           "Reglas temporales no gráficas: máx. 1 posición activa por animal (RN-006) y 1 reserva ACTIVA por posición (RN-018).<br>"
           "Todas las entidades pertenecen a una Empresa (clave compuesta con empresa_id); la relación sólo se dibuja con Sucursal.<br>"
           "Parte puede comprar y vender: sin especialización Cliente/Proveedor. Compra/Venta = atributo tipo inmutable de Operacion.<br>"
           "AsignacionCosto tiene exactamente una fuente (Concepto, Gasto o Ajuste). Corrige ≠ revierte ≠ reembolsa.",
           150, 3220, 1350, 150, tam=12)
    p.leyenda(4500, 1950)
    return p


if __name__ == "__main__":
    guardar(OUT, [construir()])
    print("generado", OUT.name)
