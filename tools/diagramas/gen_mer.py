#!/usr/bin/env python3
"""Genera las láminas MER Chen de BoviCierre (docs/diagrams/sources/mer-*.drawio).

Las cardinalidades y participaciones provienen de docs/database/relationship-matrix.md.
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from chen import Pagina, guardar

OUT = pathlib.Path(__file__).resolve().parents[2] / "docs/diagrams/sources"
W, H = 1800, 1240  # proporción A3 horizontal


def l2_identidad():
    p = Pagina("02 Identidad, contrapartes y sedes", W, H)
    p.marco("Lámina 2 · Identidad, contrapartes y sedes", "Maestros escritos sólo en el nodo A (RN-003, ADR-005) · REL-01, 04, 26, 27, 28")
    p.entidad("empresa", "Empresa", 130, 230, dom="org")
    p.entidad("sucursal", "Sucursal (sede)", 640, 230, dom="org")
    p.relacion("administra", "administra", 400, 220)
    p.une("empresa", "administra", "(0,N)")
    p.une("sucursal", "administra", "(1,1)", total=True)
    p.atributos("empresa", [("id", "k"), ("razón social", ""), ("RFC", "")], "top")
    p.atributos("sucursal", [("id", "k"), ("código", ""), ("nombre", ""), ("nodo dueño", "")], "top")

    p.entidad("usuario", "Usuario", 250, 640, dom="org")
    p.entidad("rol", "RolAplicacion", 640, 900, dom="org")
    p.relacion("autoriza", "es autorizado<br>en … con", 640, 560, w=150, h=80)
    p.une("usuario", "autoriza", "(0,N)")
    p.une("sucursal", "autoriza", "(0,N)", pos=-0.6)
    p.une("rol", "autoriza", "(0,N)")
    p.atributo("autoriza", "vigente", 860, 580)
    p.atributos("usuario", [("id", "k"), ("login", ""), ("nombre", ""), ("estado", "")], "bottom")
    p.atributos("rol", [("código", "k"), ("descripción", "")], "bottom")

    p.entidad("animal", "Animal", 1120, 560, dom="org")
    p.relacion("opera", "opera en", 1000, 330)
    p.une("animal", "opera", "(1,1)", total=True)
    p.une("sucursal", "opera", "(0,N)")
    p.atributos("animal", [("id", "k"), ("sexo", ""), ("situación", ""), ("nacimiento declarado", "")], "right", dist=60)

    p.entidad("ident", "Identificacion", 1120, 940, dom="org")
    p.relacion("posee", "posee", 1130, 760)
    p.une("animal", "posee", "(0,N)")
    p.une("ident", "posee", "(1,1)", total=True)
    p.atributos("ident", [("id", "k"), ("sistema", ""), ("código normalizado", ""), ("estado", ""), ("vigencia", "")], "right", dist=60)

    p.entidad("parte", "Parte (contraparte)", 1180, 170, dom="org")
    p.entidad("predio", "Predio", 1500, 330, dom="org", w=130)
    p.relacion("responsable", "es responsable<br>de", 1420, 160, w=140)
    p.une("parte", "responsable", "(0,N)")
    p.une("predio", "responsable", "(0,1)")
    p.atributos("parte", [("id", "k"), ("tipo persona", ""), ("nombre", ""), ("RFC", "")], "top", sep=112, dist=62)
    p.atributos("predio", [("id", "k"), ("nombre", ""), ("clave UPP", "")], "bottom", sep=116, dist=60)

    p.nota("Todas las entidades de la lámina pertenecen a una Empresa (clave compuesta con empresa_id, RN-001); "
           "la relación se dibuja sólo para Sucursal. Parte puede comprar y vender: no hay especialización Cliente/Proveedor. "
           "Identificacion modela el código como entidad con historia (no atributo multivaluado). "
           "La sede operadora del animal es inmutable (RN-004).", 130, 1080, 620, 100)
    p.leyenda(1540, 1000)
    return p


def l3_operaciones():
    p = Pagina("03 Operaciones, lotes, condiciones y pesajes", W, H)
    p.marco("Lámina 3 · Operaciones, lotes, condiciones y pesajes", "Escritas en el nodo dueño de la sede · REL-02, 03, 05, 06, 07, 14, 15, 31")
    p.ref("parte", "Parte", 2, 130, 300)
    p.ref("sucursal", "Sucursal", 2, 130, 560)
    p.entidad("op", "Operacion", 600, 380, dom="ope")
    p.atributos("op", [("id", "k"), ("tipo", ""), ("folio", ""), ("fecha", ""), ("estado", ""), ("estado entrega", "d")], "top", sep=112)
    p.relacion("interviene", "interviene en", 360, 220)
    p.une("parte", "interviene", "(0,N)")
    p.une("op", "interviene", "(1,1)", total=True)
    p.relacion("tramita", "tramita", 360, 480)
    p.une("sucursal", "tramita", "(0,N)")
    p.une("op", "tramita", "(1,1)", total=True)

    p.entidad("lote", "LoteOperacion", 600, 760, debil=True, dom="ope")
    p.relacion("contiene", "contiene", 610, 580, identificante=True)
    p.une("op", "contiene", "(0,N)*")
    p.une("lote", "contiene", "(1,1)", total=True)
    p.atributos("lote", [("número lote", "p"), ("descripción", "")], "left", dist=50)

    p.entidad("ver", "ContratoVersion", 1200, 380, debil=True, dom="ope")
    p.relacion("conserva", "conserva", 910, 370, identificante=True)
    p.une("op", "conserva", "(0,N)*")
    p.une("ver", "conserva", "(1,1)", total=True)
    p.atributos("ver", [("número versión", "p"), ("estado", ""), ("política redondeo", ""), ("requiere recepción", "")], "top", sep=112)

    p.entidad("cond", "CondicionLote", 1200, 760, debil=True, dom="ope")
    p.relacion("establece", "establece", 1210, 580, identificante=True)
    p.une("ver", "establece", "(0,N)")
    p.une("cond", "establece", "(1,1)", total=True)
    p.relacion("rige", "rige para", 910, 750, identificante=True)
    p.une("lote", "rige", "(0,N)")
    p.une("cond", "rige", "(1,1)", total=True)
    p.atributos("cond", [("unidad precio", ""), ("precio unitario", ""), ("base de pesaje", ""), ("deducción pactada", "")], "right", dist=60)

    p.entidad("pesaje", "Pesaje", 600, 1040, dom="ope")
    p.relacion("recibe", "recibe", 610, 900)
    p.une("lote", "recibe", "(0,N)")
    p.une("pesaje", "recibe", "(1,1)", total=True)
    p.atributos("pesaje", [("id", "k"), ("modo", ""), ("bruto", ""), ("tara", ""), ("neto", "")], "bottom", sep=112, dist=62)
    p.recursiva("corrige", "corrige", "pesaje", "original (0,1)", "corrección (0,1)", lado="left", dist=110)
    p.ref("animal", "Animal", 2, 1180, 1040)
    p.relacion("comprende", "comprende", 900, 1030)
    p.une("pesaje", "comprende", "(1,N)", total=True)
    p.une("animal", "comprende", "(0,N)")
    p.atributo("comprende", "peso individual (si se midió)", 940, 940, w=160)

    p.nota("* Borrador: (0,N). Al confirmar: ≥1 lote y exactamente una versión ACEPTADA que cubre todos los lotes (RN-017, REL-05..07). "
           "CondicionLote es débil con dos propietarios de la misma operación: (operación, número versión, número lote). "
           "Variación de peso y deducción pactada son independientes (RN-015). Pesaje es fuerte: tiene identidad de ticket.",
           1420, 430, 340, 140)
    p.leyenda(1540, 1000)
    return p


def l4_inventario():
    p = Pagina("04 Inventario, selección, reserva y movimientos", W, H)
    p.marco("Lámina 4 · Inventario, selección de venta, reserva y movimientos", "Posición = ciclo de inventario de un animal (ADR-003) · REL-08..13")
    p.ref("lotec", "LoteOperacion<br>(COMPRA)", 3, 130, 220, debil=True, w=170, h=66)
    p.ref("animal", "Animal", 2, 130, 640)
    p.entidad("selc", "SeleccionCompra", 520, 430, debil=True, dom="inv")
    p.relacion("incluyec", "incluye", 330, 300, identificante=True)
    p.une("lotec", "incluyec", "(0,N)")
    p.une("selc", "incluyec", "(1,1)", total=True)
    p.relacion("essel", "es seleccionado<br>en", 330, 530, identificante=True, w=140)
    p.une("animal", "essel", "(0,N)")
    p.une("selc", "essel", "(1,1)", total=True)

    p.entidad("pos", "PosicionInventario", 900, 640, dom="inv", w=170)
    p.atributos("pos", [("id", "k"), ("número ciclo", ""), ("estado", ""), ("motivo baja", ""), ("costo vigente", "d")], "right", dist=40)
    p.relacion("origina", "origina", 720, 520)
    p.une("selc", "origina", "(0,1)*")
    p.une("pos", "origina", "(1,1)", total=True)
    p.relacion("participa", "participa en", 500, 850)
    p.une("animal", "participa", "(0,N)")
    p.une("pos", "participa", "(1,1)", total=True)

    p.ref("lotev", "LoteOperacion<br>(VENTA)", 3, 1250, 150, debil=True, w=170, h=66)
    p.entidad("selv", "SeleccionVenta", 1250, 430, debil=True, dom="inv", w=170)
    p.relacion("incluyev", "incluye", 1270, 280, identificante=True)
    p.une("lotev", "incluyev", "(0,N)")
    p.une("selv", "incluyev", "(1,1)", total=True)
    p.relacion("essv", "es seleccionada<br>en", 1030, 420, identificante=True, w=140)
    p.une("pos", "essv", "(0,N)")
    p.une("selv", "essv", "(1,1)", total=True)

    p.entidad("res", "ReservaVenta", 1260, 800, dom="inv")
    p.relacion("mantiene", "mantiene", 1270, 620)
    p.une("selv", "mantiene", "(0,N)")
    p.une("res", "mantiene", "(1,1)", total=True)
    p.atributos("res", [("id", "k"), ("estado", ""), ("vence en", "")], "right", dist=60)

    p.entidad("mov", "MovimientoInventario", 900, 1040, dom="inv", w=180)
    p.relacion("registra", "registra", 920, 860)
    p.une("pos", "registra", "(0,N)")
    p.une("mov", "registra", "(1,1)", total=True)
    p.atributos("mov", [("id", "k"), ("tipo", ""), ("ocurrido en", ""), ("custodio", "")], "left", dist=60)
    p.recursiva("revierte", "revierte", "mov", "original (0,1)", "reverso (0,1)", lado="right", dist=90)

    p.nota("* (0,1) en borrador; (1,1) tras ConfirmarCompra (REL-09). Un animal tiene a lo sumo UNA posición activa "
           "(índice único parcial, RN-006) y a lo sumo una reserva ACTIVA por posición (RN-018). "
           "\"Reservada\" se deriva de la reserva ACTIVA (DEC-01). Estados de posición: PENDIENTE_RECEPCION, DISPONIBLE, "
           "VENDIDA_PENDIENTE_ENTREGA, CERRADA_VENTA, BAJA.", 130, 1000, 560, 120)
    p.leyenda(1540, 1000)
    return p


def l5_liquidaciones():
    p = Pagina("05 Liquidaciones, costos, pagos y aplicaciones", W, H)
    p.marco("Lámina 5 · Liquidaciones, costos, pagos y aplicaciones", "Un único evento económico: CONFIRMADA (ADR-004) · REL-16..21, 25, 30, 32, 33")
    p.ref("op", "Operacion", 3, 130, 260)
    p.entidad("liq", "Liquidacion", 560, 260, dom="liq")
    p.atributos("liq", [("id", "k"), ("dirección", "")], "top", sep=112, dist=64)
    p.atributo("liq", "total", 400, 330)
    p.atributo("liq", "saldo", 400, 385, derivado=True)
    p.relacion("origina", "origina", 335, 250)
    p.une("op", "origina", "(0,1)*")
    p.une("liq", "origina", "(1,1)", total=True)

    p.entidad("conc", "ConceptoLiquidacion", 545, 560, debil=True, dom="liq", w=180)
    p.relacion("desglosa", "desglosa", 570, 400, identificante=True)
    p.une("liq", "desglosa", "(1,N)", total=True)
    p.une("conc", "desglosa", "(1,1)", total=True)
    p.atributos("conc", [("número concepto", "p"), ("tipo", ""), ("importe", "")], "left", dist=40)

    p.entidad("aju", "AjusteLiquidacion", 1000, 500, dom="liq", w=170)
    p.relacion("recibe", "recibe", 780, 370)
    p.une("liq", "recibe", "(0,N)")
    p.une("aju", "recibe", "(1,1)", total=True)
    p.atributos("aju", [("id", "k"), ("naturaleza", ""), ("monto", ""), ("motivo", "")], "right", dist=50)

    p.entidad("apl", "AplicacionPago", 1000, 160, dom="liq")
    p.relacion("abona", "abona a", 790, 150)
    p.une("liq", "abona", "(0,N)")
    p.une("apl", "abona", "(1,1)", total=True)
    p.atributos("apl", [("id", "k"), ("importe", ""), ("naturaleza", "")], "top", sep=112, dist=64)
    p.recursiva("revierte", "revierte", "apl", "original (0,1)", "reverso (0,1)", lado="bottom", dist=40)

    p.entidad("pago", "Pago", 1420, 160, dom="liq", w=130)
    p.relacion("usa", "proviene de", 1215, 150)
    p.une("apl", "usa", "(1,1)", total=True)
    p.une("pago", "usa", "(0,N)")
    p.atributos("pago", [("id", "k"), ("tipo", ""), ("importe", ""), ("estado", "")], "top", sep=96, dist=64)
    p.recursiva("reembolsa", "reembolsa", "pago", "origen (0,N)", "reembolso (0,1)", lado="right", dist=40, w=110)
    p.ref("parte", "Parte", 2, 1420, 470, w=130)
    p.relacion("realiza", "realiza", 1420, 310)
    p.une("parte", "realiza", "(0,N)")
    p.une("pago", "realiza", "(1,1)", total=True)

    p.entidad("gasto", "GastoOperacion", 200, 660, dom="liq")
    p.relacion("incurre", "incurre en", 140, 450)
    p.une("op", "incurre", "(0,N)")
    p.une("gasto", "incurre", "(1,1)", total=True)
    p.atributos("gasto", [("id", "k"), ("naturaleza", ""), ("clasificación", "")], "left", dist=40)
    p.recursiva("bonifica", "bonifica", "gasto", "original (0,N)", "bonificación (0,1)", lado="bottom", dist=50, w=110)

    p.entidad("asig", "AsignacionCosto", 560, 930, dom="liq")
    p.relacion("proviene", "proviene de<br>(exactamente 1)", 560, 760, w=150, h=80)
    p.une("conc", "proviene", "(0,N)")
    p.une("gasto", "proviene", "(0,N)")
    p.une("aju", "proviene", "(0,N)")
    p.une("asig", "proviene", "(1,1)", total=True)
    p.atributos("asig", [("id", "k"), ("método", ""), ("base", ""), ("importe", "")], "bottom", sep=112, dist=60)

    p.ref("pos", "PosicionInventario", 4, 1000, 930, w=170)
    p.relacion("asigna", "se asigna a", 790, 920)
    p.une("asig", "asigna", "(1,1)", total=True)
    p.une("pos", "asigna", "(0,N)")
    p.entidad("asi", "AsientoValoracion", 1000, 1085, dom="liq", w=170)
    p.relacion("acumula", "acumula", 1020, 1003, h=60)
    p.une("pos", "acumula", "(1,N)", total=True)
    p.une("asi", "acumula", "(1,1)", total=True)
    p.atributos("asi", [("id", "k"), ("clase", ""), ("importe", ""), ("deltas (derivados)", "d")], "right", dist=50)

    p.nota("* Borrador (0,1); CONFIRMADA (1,1): una liquidación principal por operación (REL-16). "
           "La liquidación es la obligación (DEC-05); su saldo = total + cargos − abonos − aplicaciones netas (derivado). "
           "AsignacionCosto tiene exactamente una fuente (XOR declarativo, REL-19). "
           "Reverso (revierte) ≠ reembolso (dinero real) ≠ corrección.", 1340, 680, 420, 130)
    p.leyenda(1540, 1000)
    return p


def l6_evidencia():
    p = Pagina("06 Evidencia, revisiones, periodos y auditoría", W, H)
    p.marco("Lámina 6 · Evidencia, revisiones, periodos y auditoría", "Revisión administrativa ≠ autorización sanitaria (RN-037) · REL-22..24, 29, 35..37")
    p.ref("op", "Operacion", 3, 130, 250)
    p.entidad("doc", "Documento", 640, 250, dom="evi")
    p.atributos("doc", [("id", "k"), ("tipo documental", ""), ("sha256", ""), ("versión", "")], "top", sep=112)
    p.relacion("incorpora", "incorpora", 370, 240)
    p.une("op", "incorpora", "(0,N)")
    p.une("doc", "incorpora", "(0,N)")
    p.atributo("incorpora", "rol", 380, 340, w=80)
    p.recursiva("reemplaza", "reemplaza", "doc", "previo (0,1)", "nueva versión (0,1)", lado="right", dist=60)

    p.entidad("rev", "RevisionAdministrativa", 630, 640, dom="evi", w=170)
    p.relacion("examina", "examina", 650, 440)
    p.une("rev", "examina", "(1,N)", total=True)
    p.une("doc", "examina", "(0,N)")
    p.atributo("examina", "resultado", 820, 420)
    p.atributo("examina", "observación", 820, 470)
    p.atributos("rev", [("id", "k"), ("criterio", ""), ("resultado", ""), ("revisado en", "")], "bottom", sep=112, dist=60)
    p.recursiva("sustituye", "sustituye", "rev", "anterior (0,1)", "posterior (0,1)", lado="right", dist=60)
    p.ref("ident", "Identificacion", 2, 130, 640)
    p.relacion("revisa", "revisa<br>(op. XOR ident.)", 360, 500, w=150, h=80)
    p.une("op", "revisa", "(0,N)")
    p.une("ident", "revisa", "(0,N)")
    p.une("rev", "revisa", "(1,1)", total=True)

    p.ref("usuario", "Usuario", 2, 130, 1000)
    p.entidad("aud", "AuditoriaEvento", 630, 1000, dom="evi", w=170)
    p.relacion("origina", "origina", 370, 990)
    p.une("usuario", "origina", "(0,N)")
    p.une("aud", "origina", "(0,1)")
    p.atributos("aud", [("id", "k"), ("comando", ""), ("correlación", ""), ("nodo origen", "")], "right", dist=60)

    p.entidad("per", "PeriodoCierre", 1250, 250, dom="evi")
    p.atributos("per", [("id", "k"), ("desde", ""), ("hasta", ""), ("estado", "")], "top", sep=112)
    p.entidad("cpv", "CierrePeriodoVersion", 1240, 640, debil=True, dom="evi", w=170)
    p.relacion("conserva", "conserva", 1260, 440, identificante=True)
    p.une("per", "conserva", "(0,N)")
    p.une("cpv", "conserva", "(1,1)", total=True)
    p.atributos("cpv", [("número versión", "p"), ("tipo", ""), ("hash conciliación", "")], "right", dist=50)
    p.ref("asi", "AsientoValoracion / Ajuste", 5, 1240, 860, w=190)
    p.relacion("imputa", "se imputa a", 1500, 380)
    p.une("asi", "imputa", "(1,1)", total=True)
    p.une("per", "imputa", "(0,N)")

    p.nota("Una revisión apunta a la versión exacta del documento; subir una versión nueva no altera revisiones previas (TEST-34). "
           "El estado se rotula \"revisión administrativa registrada\", nunca \"autorizado\". AuditoriaEvento se genera sólo en el nodo origen "
           "y se replica como dato. Los hechos se imputan a un periodo ABIERTO (RN-039).", 130, 790, 440, 120, tam=10)
    p.leyenda(1540, 1000)
    return p


def l1_general():
    W1, H1 = 2380, 1680  # A2 horizontal
    p = Pagina("01 Vista general por dominios", W1, H1)
    p.marco("Lámina 1 · Vista general conceptual por dominios",
            "Flechas: sentido del verbo A → relación → B; cardinalidades en láminas 2–6")
    from chen import COLORES, BASE
    for nom, dom, x, y, w, h in [("Organización e identidad (maestros, nodo A)", "org", 30, 90, 740, 680),
                                 ("Operaciones y contratos", "ope", 790, 90, 780, 680), ("Inventario", "inv", 1590, 90, 760, 680),
                                 ("Liquidaciones, costos y pagos", "liq", 30, 790, 1540, 860),
                                 ("Evidencia, periodos y auditoría", "evi", 1590, 790, 760, 860)]:
        p._vertex(p._id("dom"), f"<b>{nom}</b>", BASE + f"rounded=1;arcSize=2;fillColor={COLORES[dom]};opacity=45;"
                  "verticalAlign=top;align=left;spacingLeft=10;spacingTop=6;connectable=0;dashed=1;", x, y, w, h)
    E, D = p.entidad, p.relacion

    def R(cid, verbo, x, y, a, b, ident=False, w=130, h=64):
        D(cid, verbo, x, y, ident, w, h)
        p.linea(a, cid, extra="endArrow=open;endSize=10;")
        p.linea(cid, b, extra="endArrow=open;endSize=10;")

    # Organización e identidad
    E("empresa", "Empresa", 60, 150); E("sucursal", "Sucursal", 420, 150); E("usuario", "Usuario", 60, 330)
    E("animal", "Animal", 60, 520); E("ident", "Identificacion", 60, 690)
    E("parte", "Parte", 590, 380, w=150); E("predio", "Predio", 590, 640, w=150)
    R("r1", "administra", 240, 143, "empresa", "sucursal")
    R("r2", "es autorizado en", 225, 320, "usuario", "sucursal", w=150)
    R("r3", "opera en", 280, 430, "animal", "sucursal")
    R("r4", "posee", 70, 595, "animal", "ident")
    R("r5", "responsable de", 595, 505, "parte", "predio", w=140)
    # Operaciones
    E("op", "Operacion", 860, 150); E("lote", "LoteOperacion", 1300, 150, debil=True)
    E("ver", "ContratoVersion", 860, 400, debil=True); E("cond", "CondicionLote", 1300, 400, debil=True); E("pesaje", "Pesaje", 1300, 650)
    R("r6", "tramita", 655, 143, "sucursal", "op")
    R("r7", "interviene en", 760, 260, "parte", "op", w=140)
    R("r8", "contiene", 1085, 143, "op", "lote", ident=True)
    R("r9", "conserva", 870, 285, "op", "ver", ident=True)
    R("r10", "establece", 1085, 393, "ver", "cond", ident=True)
    R("r11", "rige para", 1310, 285, "cond", "lote", ident=True)
    R("r12", "recibe", 1310, 525, "lote", "pesaje")
    # Inventario
    E("selc", "SeleccionCompra", 1630, 150, debil=True); E("pos", "PosicionInventario", 1620, 400, w=170)
    E("selv", "SeleccionVenta", 2120, 150, debil=True, w=170); E("res", "ReservaVenta", 2130, 400); E("mov", "MovimientoInventario", 1615, 650, w=180)
    R("r13", "incluye", 1470, 143, "lote", "selc", ident=True, w=120)
    R("r14", "origina", 1640, 285, "selc", "pos")
    R("r15", "es seleccionada en", 1900, 270, "pos", "selv", ident=True)
    R("r16", "mantiene", 2140, 285, "selv", "res")
    R("r17", "registra", 1640, 525, "pos", "mov")
    # Liquidaciones
    p.ref("op2", "Operacion", "3 · dominio superior", 420, 850)
    E("liq", "Liquidacion", 860, 850); E("conc", "ConceptoLiquidacion", 845, 1090, debil=True, w=180)
    E("aju", "AjusteLiquidacion", 1300, 850, w=170); E("apl", "AplicacionPago", 1300, 1090, w=170); E("pago", "Pago", 1320, 1330, w=130)
    E("gasto", "GastoOperacion", 420, 1090); E("asig", "AsignacionCosto", 420, 1330)
    p.ref("pos2", "PosicionInventario", "4 · dominio superior", 410, 1540, w=170); E("asi", "AsientoValoracion", 860, 1540, w=170)
    R("r18", "origina", 650, 843, "op2", "liq")
    R("r19", "desglosa", 870, 968, "liq", "conc", ident=True)
    R("r20", "recibe", 1090, 843, "liq", "aju")
    R("r21", "abona a", 1090, 1000, "apl", "liq")
    R("r22", "proviene de", 1320, 1210, "apl", "pago")
    R("r23", "incurre en", 430, 968, "op2", "gasto")
    R("r24", "proviene de", 430, 1210, "asig", "gasto")
    R("r25", "se asigna a", 430, 1440, "asig", "pos2")
    R("r26", "acumula", 650, 1533, "pos2", "asi")
    # Evidencia
    E("doc", "Documento", 1630, 880); E("rev", "RevisionAdministrativa", 2120, 880, w=180)
    E("per", "PeriodoCierre", 1630, 1150); E("cpv", "CierrePeriodoVersion", 2120, 1150, debil=True, w=180)
    E("aud", "AuditoriaEvento", 1630, 1400, w=170)
    R("r27", "examina", 1860, 873, "rev", "doc")
    R("r28", "conserva", 1860, 1143, "per", "cpv", ident=True)
    R("r29", "se imputa a", 1310, 1500, "asi", "per")
    p.nota("Relaciones entre dominios que no se dibujan aquí para no saturar la vista: Pesaje comprende Animal (lámina 3), "
           "Animal participa en PosicionInventario (4), Operacion incorpora Documento y RevisionAdministrativa revisa "
           "Operacion o Identificacion (6), Usuario origina AuditoriaEvento (6). "
           "Las entidades con borde discontinuo repiten una entidad de otro dominio.", 1630, 1500, 440, 120, tam=10)
    p.leyenda(2120, 1420, lectura=True)
    return p


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for nombre, f in [("mer-01-general", l1_general), ("mer-02-identidad", l2_identidad), ("mer-03-operaciones", l3_operaciones),
                      ("mer-04-inventario", l4_inventario), ("mer-05-liquidaciones", l5_liquidaciones), ("mer-06-evidencia", l6_evidencia)]:
        guardar(OUT / f"{nombre}.drawio", [f()])
        print("generado", nombre)


if __name__ == "__main__":
    main()
