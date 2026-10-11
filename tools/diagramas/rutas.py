"""Recorridos ortogonales por espacios libres, conservando objetos y extremos draw.io."""
import heapq
import math
import xml.etree.ElementTree as ET

PASO = 10


def estilo(cell):
    return dict(s.split('=', 1) for s in cell.get('style', '').split(';') if '=' in s)


def geometria(cell, cells):
    g = cell.find('mxGeometry')
    x, y, w, h = (float(g.get(k, 0)) for k in ('x', 'y', 'width', 'height'))
    parent = cells.get(cell.get('parent'))
    if parent is not None and parent.get('vertex') == '1':
        px, py, _, _ = geometria(parent, cells)
        x, y = x + px, y + py
    return x, y, w, h


def buscar(inicio, destinos, bloqueados, limites, usados):
    """A*: penaliza giros y carriles usados; no atraviesa cajas ni atributos."""
    meta = set(destinos)
    heuristic = lambda p: min(abs(p[0] - q[0]) + abs(p[1] - q[1]) for q in meta)
    cola, coste, padres = [], {}, {}
    for p in inicio:
        s = (*p, -1)
        coste[s] = 0
        heapq.heappush(cola, (heuristic(p), 0, s))
    while cola:
        _, c, s = heapq.heappop(cola)
        if c != coste[s]:
            continue
        x, y, anterior = s
        if (x, y) in meta:
            path = []
            while s is not None:
                path.append(s[:2])
                s = padres.get(s)
            return path[::-1]
        for d, (dx, dy) in enumerate(((1, 0), (0, 1), (-1, 0), (0, -1))):
            p = x + dx, y + dy
            if not (limites[0] <= p[0] <= limites[2] and limites[1] <= p[1] <= limites[3]) or p in bloqueados:
                continue
            n = (*p, d)
            nc = c + 1 + (2 if anterior not in (-1, d) else 0) + usados.get(p, 0) * 0.3
            if nc < coste.get(n, math.inf):
                coste[n], padres[n] = nc, s
                heapq.heappush(cola, (nc + heuristic(p), nc, n))
    raise ValueError('No existe corredor libre entre los extremos')


def simplificar(puntos):
    out = []
    for p in puntos:
        if out and p == out[-1]:
            continue
        while len(out) > 1 and ((out[-2][0] == out[-1][0] == p[0]) or (out[-2][1] == out[-1][1] == p[1])):
            out.pop()
        out.append(p)
    return out


def enrutar(root):
    for model in root.iter('mxGraphModel'):
        cells = {c.get('id'): c for c in model.find('root').findall('mxCell')}
        cajas, bloqueados, usados = {}, set(), {}
        etiquetas = []
        for cid, cell in cells.items():
            s = estilo(cell)
            if cell.get('vertex') != '1' or cell.get('parent') != '1' or s.get('connectable') == '0' or cell.get('connectable') == '0' or 'text;' in cell.get('style', ''):
                continue
            box = cajas[cid] = geometria(cell, cells)
            x, y, w, h = box
            for gx in range(math.floor((x - 6) / PASO), math.ceil((x + w + 6) / PASO) + 1):
                for gy in range(math.floor((y - 6) / PASO), math.ceil((y + h + 6) / PASO) + 1):
                    bloqueados.add((gx, gy))
        limites = (3, 9, int(float(model.get('pageWidth')) / PASO) - 3, int(float(model.get('pageHeight')) / PASO) - 3)
        for edge in list(cells.values()):
            if edge.get('edge') != '1':
                continue
            eid = edge.get('id')
            labels = [c for c in cells.values() if c.get('parent') == eid and c.get('vertex') == '1']
            fk = eid.startswith('fk')
            if not labels and not fk and 'open' not in edge.get('style', ''):
                continue  # Los atributos conservan sus enlaces cortos sin flecha.
            original = estilo(edge)
            endpoints = []
            for key in ('source', 'target'):
                cell = cells[edge.get(key)]
                x, y, w, h = geometria(cell, cells)
                candidates = {}
                prefix = 'exit' if key == 'source' else 'entry'
                ports = ((0, .5), (1, .5)) if fk else ((0, .5), (1, .5), (.5, 0), (.5, 1))
                if prefix + 'X' in original:
                    ports = ((float(original[prefix + 'X']), float(original[prefix + 'Y'])),) + ports
                for side in ports:
                    px, py = x + w * side[0], y + h * side[1]
                    dx, dy = ((side[0] - .5) * 2, 0) if side[0] in (0, 1) else (0, (side[1] - .5) * 2)
                    for distance in (20, 30, 40):
                        q = (round((px + dx * distance) / PASO), round((py + dy * distance) / PASO))
                        # Evita salir atravesando el óvalo de un atributo cercano.
                        between = [(round((px + dx * t) / PASO), round((py + dy * t) / PASO)) for t in range(25, distance + 1, 5)]
                        if q not in bloqueados and all(p not in bloqueados for p in between):
                            candidates[q] = (side, (px, py))
                            break
                if not candidates:
                    raise ValueError(f'{eid}: sin puerto libre en {edge.get(key)}')
                if prefix + 'X' in original:
                    wanted = (float(original[prefix + 'X']), float(original[prefix + 'Y']))
                    candidates = {p: value for p, value in candidates.items() if value[0] == wanted} or candidates
                endpoints.append(candidates)
            path = buscar(endpoints[0], endpoints[1], bloqueados, limites, usados)
            sides = [endpoints[0][path[0]], endpoints[1][path[-1]]]
            # El pequeño codo exterior mantiene los extremos sobre el objeto original.
            points = [(x * PASO, y * PASO) for x, y in path]
            a, b = sides[0][1], sides[1][1]
            first = (points[0][0], a[1]) if sides[0][0][0] in (0, 1) else (a[0], points[0][1])
            last = (points[-1][0], b[1]) if sides[1][0][0] in (0, 1) else (b[0], points[-1][1])
            points = simplificar([a, first] + points + [last, b])
            for p in path:
                usados[p] = usados.get(p, 0) + 1
            s = estilo(edge)
            s.pop('edgeStyle', None)
            s.update(rounded='0', jumpStyle='arc', jumpSize='7', strokeWidth='1.5', exitX=str(sides[0][0][0]), exitY=str(sides[0][0][1]), entryX=str(sides[1][0][0]), entryY=str(sides[1][0][1]), exitPerimeter='1', entryPerimeter='1')
            edge.set('style', ';'.join(f'{k}={v}' for k, v in s.items()) + ';')
            g = edge.find('mxGeometry')
            for child in list(g):
                g.remove(child)
            array = ET.SubElement(g, 'Array', {'as': 'points'})
            for x, y in points[1:-1]:
                ET.SubElement(array, 'mxPoint', {'x': str(x), 'y': str(y)})
            # Etiquetas cerca de la entidad, separadas de cajas y de otras etiquetas.
            for label in labels:
                width, height = max(42, len(label.get('value', '')) * 6.3), 18
                candidates = []
                for (x, y), (u, v) in zip(points, points[1:]):
                    distance = abs(u - x) + abs(v - y)
                    if distance < 20:
                        continue
                    for offset in (25, 45, 65):
                        fraction = min(offset, distance / 2) / distance
                        cx, cy = x + (u - x) * fraction, y + (v - y) * fraction
                        for separation in (15, 30, 45, 60, 90, 120):
                            for sign in (-1, 1):
                                lx = cx - width / 2 if y == v else cx + sign * (width / 2 + separation - 8) - width / 2
                                ly = cy + sign * separation - height / 2 if y == v else cy - height / 2
                                candidates.append((lx, ly, width, height))
                def libre(box):
                    x, y, w, h = box
                    return all(x + w + 3 <= a or a + aw + 3 <= x or y + h + 3 <= b or b + bh + 3 <= y for a, b, aw, bh in list(cajas.values()) + etiquetas)
                box = next((b for b in candidates if libre(b)), None)
                if box is None:
                    raise ValueError(f'{eid}: sin espacio para etiqueta')
                etiquetas.append(box)
                label.set('parent', '1')
                g_label = label.find('mxGeometry')
                g_label.attrib.clear()
                g_label.attrib.update(dict(zip(('x', 'y', 'width', 'height'), map(str, box))), **{'as': 'geometry'})
                label.set('style', 'text;html=1;align=center;verticalAlign=middle;fontSize=11;fontStyle=1;fillColor=#ffffff;strokeColor=none;')
            # shortcut: puntas y etiquetas fijas; regenerar después de cambiar el trazado.
            if fk or original.get('endArrow') == 'open':
                (x, y), (u, v) = max(zip(points, points[1:]), key=lambda pair: abs(pair[0][0] - pair[1][0]) + abs(pair[0][1] - pair[1][1]))
                rotation = math.degrees(math.atan2(v - y, u - x))
                if not fk:
                    s['endArrow'] = 'none'
                    edge.set('style', ';'.join(f'{k}={v}' for k, v in s.items()) + ';')
                marker = ET.SubElement(model.find('root'), 'mxCell', {'id': eid + '_direccion', 'value': '', 'vertex': '1', 'parent': '1', 'connectable': '0', 'style': f'shape=triangle;direction=east;rotation={rotation};fillColor={s.get("strokeColor", "#334155")};strokeColor=none;'} )
                ET.SubElement(marker, 'mxGeometry', {'x': str((x + u) / 2 - 7), 'y': str((y + v) / 2 - 5), 'width': '14', 'height': '10', 'as': 'geometry'})
    return root


if __name__ == '__main__':
    blocked = {(4, y) for y in range(2, 9)}
    route = buscar({(1, 5)}, {(8, 5)}, blocked, (0, 0, 10, 10), {})
    assert route[0] == (1, 5) and route[-1] == (8, 5)
    assert not set(route) & blocked
    assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in zip(route, route[1:]))
    assert simplificar([(0, 0), (1, 0), (2, 0), (2, 1)]) == [(0, 0), (2, 0), (2, 1)]
    print('rutas: obstáculos, extremos y simplificación OK')
