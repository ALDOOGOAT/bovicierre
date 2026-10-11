#!/usr/bin/env python3
"""Genera el diagrama lógico relacional por módulos (docs/diagrams/sources/mer-07-relacional.drawio).

Fuente de verdad: docs/database/relational-model.md. E = empresa_id, S = sucursal_id.
Una página por módulo; las FK hacia otra página se anotan como [pN].
"""
import pathlib, sys
from xml.sax.saxutils import escape
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from chen import Pagina, guardar, COLORES

OUT = pathlib.Path(__file__).resolve().parents[2] / "docs/diagrams/sources"
LOC = ["empresa_id PK", "sucursal_id PK"]

MODULOS = [
    ("p1 Organización e identidad (nodo A)", "org", [
        ("empresa", ["id PK", "razon_social", "rfc", "estado"], []),
        ("sucursal", ["empresa_id PK FK", "id PK", "codigo UK", "nombre", "nodo_dueno"], ["empresa"]),
        ("rol_aplicacion", ["codigo PK", "descripcion"], []),
        ("usuario", ["empresa_id PK FK", "id PK", "login_normalizado UK", "hash_contrasena", "estado"], ["empresa"]),
        ("membresia_usuario", ["empresa_id PK", "sucursal_id PK FK", "usuario_id PK FK", "rol_codigo PK FK", "vigente"], ["sucursal", "usuario", "rol_aplicacion"]),
        ("parte", ["empresa_id PK FK", "id PK", "tipo_persona", "nombre", "rfc UK?"], ["empresa"]),
        ("predio", ["empresa_id PK", "id PK", "parte_responsable_id FK", "clave_upp_declarada"], ["parte"]),
        ("animal", ["empresa_id PK", "id PK", "sede_operadora_id FK", "UK(E,sede_operadora_id,id)", "situacion"], ["sucursal"]),
        ("animal_identificacion", ["empresa_id PK", "id PK", "animal_id FK", "sistema UK", "codigo_normalizado UK", "estado", "evidencia_documento_id FK [p5]"], ["animal"]),
    ]),
    ("p2 Operaciones, contratos y pesajes", "ope", [
        ("operacion", LOC + ["id PK", "tipo", "folio UK", "parte_id FK [p1]", "predio_origen/destino FK [p1]", "estado", "numero_version_aceptada FK", "version_lock"], []),
        ("folio_contador", LOC + ["tipo PK", "anio PK", "ultimo"], []),
        ("lote_operacion", LOC + ["operacion_id PK FK", "numero_lote PK"], ["operacion"]),
        ("contrato_version", LOC + ["operacion_id PK FK", "numero_version PK", "estado", "documento_id FK [p5]"], ["operacion"]),
        ("condicion_lote", LOC + ["operacion_id PK", "numero_version PK FK", "numero_lote PK FK", "unidad_precio", "precio_unitario", "pesaje_base_id FK"], ["contrato_version", "lote_operacion"]),
        ("pesaje", LOC + ["id PK", "operacion_id, numero_lote FK", "modo", "bruto_kg / tara_kg / neto_kg", "estado", "corrige_a_id FK UK"], ["lote_operacion"]),
        ("pesaje_animal", LOC + ["pesaje_id PK FK", "animal_id PK FK [p1]", "peso_individual_kg NULL"], ["pesaje"]),
    ]),
    ("p3 Inventario", "inv", [
        ("seleccion_compra", LOC + ["operacion_id PK FK [p2]", "numero_lote PK FK [p2]", "animal_id PK FK [p1]", "UK(E,S,operacion_id,animal_id)", "tipo_operacion='COMPRA'"], []),
        ("posicion_inventario", LOC + ["id PK", "animal_id FK [p1]", "numero_ciclo UK", "compra_operacion_id, compra_numero_lote FK", "estado", "UNIQUE parcial (E,animal_id) activo"], ["seleccion_compra"]),
        ("seleccion_venta", LOC + ["operacion_id PK FK [p2]", "numero_lote PK FK [p2]", "posicion_id PK FK", "UK(E,S,operacion_id,posicion_id)", "tipo_operacion='VENTA'"], ["posicion_inventario"]),
        ("reserva_venta", LOC + ["id PK", "operacion_id, numero_lote, posicion_id FK", "estado", "vence_en", "UNIQUE parcial posición ACTIVA"], ["seleccion_venta"]),
        ("movimiento_inventario", LOC + ["id PK", "posicion_id FK", "operacion_id FK [p2]", "tipo", "ocurrido_en", "reverso_de_id FK UK"], ["posicion_inventario"]),
    ]),
    ("p4 Liquidaciones, costos y pagos", "liq", [
        ("liquidacion", LOC + ["id PK", "operacion_id FK UK [p2]", "numero_version FK [p2]", "direccion", "total", "periodo_id FK [p5]"], []),
        ("concepto_liquidacion", LOC + ["liquidacion_id PK FK", "numero_concepto PK", "tipo", "importe"], ["liquidacion"]),
        ("ajuste_liquidacion", LOC + ["id PK", "liquidacion_id FK", "naturaleza", "monto", "revierte_ajuste_id FK UK"], ["liquidacion"]),
        ("gasto_operacion", LOC + ["id PK", "operacion_id FK [p2]", "naturaleza", "clasificacion", "importe", "bonifica_gasto_id FK"], []),
        ("asignacion_costo", LOC + ["id PK", "posicion_id FK [p3]", "fuente_liquidacion_id, fuente_numero_concepto FK", "fuente_gasto_id FK", "fuente_ajuste_id FK", "CHECK num_nonnulls = 1", "importe"], ["concepto_liquidacion", "gasto_operacion", "ajuste_liquidacion"]),
        ("asiento_valoracion", LOC + ["id PK", "posicion_id FK [p3]", "asignacion_id FK", "clase", "sentido", "importe", "delta_* GENERATED"], ["asignacion_costo"]),
        ("pago", LOC + ["id PK", "parte_id FK [p1]", "tipo", "importe", "estado", "pago_origen_id FK"], []),
        ("aplicacion_pago", LOC + ["id PK", "pago_id FK", "liquidacion_id FK", "importe", "naturaleza", "reverso_de_id FK UK"], ["pago", "liquidacion"]),
    ]),
    ("p5 Evidencia, periodos, auditoría y soporte técnico", "evi", [
        ("documento", LOC + ["id PK", "clave_almacenamiento UK", "sha256", "version", "documento_previo_id FK UK"], []),
        ("operacion_documento", LOC + ["operacion_id PK FK [p2]", "documento_id PK FK", "rol"], ["documento"]),
        ("revision_administrativa", LOC + ["id PK", "operacion_id FK [p2] XOR", "identificacion_id FK [p1]", "resultado", "revision_anterior_id FK"], []),
        ("revision_documento", LOC + ["revision_id PK FK", "documento_id PK FK", "resultado"], ["revision_administrativa", "documento"]),
        ("periodo_cierre", LOC + ["id PK", "desde", "hasta", "estado", "EXCLUDE gist (sin solape)"], []),
        ("cierre_periodo_version", LOC + ["periodo_id PK FK", "numero_version PK", "tipo", "hash_conciliacion"], ["periodo_cierre"]),
        ("auditoria_evento", LOC + ["id PK", "comando", "correlation_id", "nodo_origen", "cambio jsonb"], []),
        ("evento_outbox", LOC + ["id PK", "tipo_evento", "payload jsonb", "propietario_despacho"], []),
        ("clave_idempotencia (local)", LOC + ["principal_id PK", "comando PK", "clave PK", "hash_peticion", "resultado"], []),
        ("mensaje_inbox (local)", ["consumidor PK", "fuente_id PK", "event_id PK", "resultado"], []),
        ("infra.nodo_config (local)", ["nodo PK", "empresa_id", "descripcion"], []),
        ("infra.entrega_outbox (local)", ["evento_id PK", "destino PK", "intentos", "proximo_intento"], []),
        ("infra.importacion_fuente (local)", ["id PK", "fuente", "sha256 UK", "filas_leidas"], []),
    ]),
]


def tabla(p, nombre, cols, x, y, dom):
    filas = []
    for c in cols:
        t = escape(c)
        if " PK" in c:
            t = f"<u>{t}</u>"
        filas.append(t)
    alto = 30 + 16 * len(cols)
    valor = f"<b>{escape(nombre)}</b><hr size='1'>" + "<br>".join(filas)
    estilo = (f"html=1;whiteSpace=wrap;rounded=0;align=left;verticalAlign=top;spacingLeft=6;spacingTop=4;fontFamily=Courier New;"
              f"fontSize=11;strokeColor=#000000;fillColor={COLORES[dom]};")
    cid = nombre.split(" ")[0].replace(".", "_")
    p._vertex(cid, valor, estilo, x, y, 300, alto)
    return cid, alto


def pagina(titulo, dom, tablas):
    p = Pagina(titulo, 1800, 1240)
    p.marco("Lámina 7 · Modelo lógico relacional · " + titulo[3:], "PK subrayada · FK → tabla · [pN] = FK hacia otra página · E,S = empresa_id, sucursal_id", etiqueta="Modelo lógico relacional (no Chen)")
    # Columnas por profundidad de FK dentro del módulo: referenciadas a la izquierda, dependientes a la derecha.
    clave = lambda n: n.split(" ")[0].replace(".", "_")
    refs_de = {clave(n): r for n, _, r in tablas}
    referenciadas = {r for rs in refs_de.values() for r in rs}
    prof = {}
    def profundidad(t):
        if t not in prof:
            prof[t] = 0 if not refs_de[t] else 1 + max(profundidad(r) for r in refs_de[t])
        return prof[t]
    aisladas = [n for n, _, r in tablas if not r and clave(n) not in referenciadas]
    max_prof = max(profundidad(clave(n)) for n, _, _ in tablas)
    y_col = {}
    for nombre, cols, refs in tablas:
        if nombre in aisladas:
            continue
        c = profundidad(clave(nombre))
        y = y_col.get(c, 100)
        _, alto = tabla(p, nombre, cols, 40 + 430 * c, y, dom)
        y_col[c] = y + alto + 50
    c, y = (max_prof + 1 if y_col else 0), 100
    for nombre in aisladas:
        cols = next(cs for n, cs, _ in tablas if n == nombre)
        alto = 30 + 16 * len(cols)
        if y + alto > 1150:
            c, y = c + 1, 100
        tabla(p, nombre, cols, 40 + 430 * c, y, dom)
        y += alto + 40
    for nombre, cols, refs in tablas:
        for r in refs:
            cid = p._id("fk")
            p.celdas.append(
                f'<mxCell id="{cid}" value="" style="edgeStyle=entityRelationEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;'
                f'strokeColor=#333333;strokeWidth=1.2;" edge="1" parent="1" source="{nombre.split(" ")[0].replace(".", "_")}" target="{r}">'
                f'<mxGeometry relative="1" as="geometry"/></mxCell>')
    p.texto("Flecha: FK hacia la tabla referenciada. Todas las FK locales incluyen (empresa_id, sucursal_id); las FK a maestros incluyen empresa_id. "
            "Columnas completas, tipos y restricciones: docs/database/data-dictionary.md.", 40, 1170, 1200, 40, tam=11)
    return p


def main():
    guardar(OUT / "mer-07-relacional.drawio", [pagina(t, d, tb) for t, d, tb in MODULOS])
    print("generado mer-07-relacional")


if __name__ == "__main__":
    main()
