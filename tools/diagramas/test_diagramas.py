"""Regresiones del trazado y de la cardinalidad de claves compuestas.

Ejecutar: python3 -m unittest discover -s tools/diagramas -p 'test_*.py'
"""
import unittest
from gen_relacional_completo import TABLAS, marcas_fk
from rutas import buscar, simplificar


class DiagramasTest(unittest.TestCase):
    def test_mer_conserva_autorrelaciones_documento_y_ajuste(self):
        from gen_mer_completo import construir
        import xml.etree.ElementTree as ET
        graph = construir()
        cells = ET.fromstring('<root>' + ''.join(graph.celdas) + '</root>')
        values = ' '.join(cell.get('value', '') for cell in cells.iter('mxCell'))
        self.assertIn('reemplaza', values)
        self.assertIn('sustituto (0,1)', values)
        by_id = {cell.get('id'): cell for cell in cells.iter('mxCell')}
        self.assertEqual(by_id['revierte_aju'].get('value'), 'revierte')
        edges = list(cells.iter('mxCell'))
        for entity, relation in [('doc', 'reemplaza_doc'), ('aju', 'revierte_aju')]:
            links = [cell for cell in edges if cell.get('source') == entity and cell.get('target') == relation]
            self.assertEqual(len(links), 2, (entity, relation))

    def test_rodea_obstaculo(self):
        blocked = {(4, y) for y in range(2, 9)}
        path = buscar({(1, 5)}, {(8, 5)}, blocked, (0, 0, 10, 10), {})
        self.assertEqual(path[0], (1, 5))
        self.assertEqual(path[-1], (8, 5))
        self.assertFalse(set(path) & blocked)
        self.assertTrue(all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in zip(path, path[1:])))

    def test_no_inventa_ruta_si_no_hay_salida(self):
        with self.assertRaises(ValueError):
            buscar({(0, 0)}, {(2, 2)}, {(0, 1), (1, 0)}, (0, 0, 2, 2), {})

    def test_simplifica_sin_perder_codo(self):
        self.assertEqual(simplificar([(0, 0), (1, 0), (2, 0), (2, 1)]), [(0, 0), (2, 0), (2, 1)])

    def test_cardinalidad_de_claves_completas(self):
        by = {t[1]: t for t in TABLAS}
        cases = [
            ('animal', ['empresa_id', 'sede_operadora_id'], ('ERzeroToMany', 'ERmandOne', False)),
            ('liquidacion', ['empresa_id', 'sucursal_id', 'operacion_id'], ('ERzeroToOne', 'ERmandOne', False)),
            ('documento', ['empresa_id', 'sucursal_id', 'documento_previo_id'], ('ERzeroToOne', 'ERzeroToOne', False)),
            ('membresia_usuario', ['empresa_id', 'sucursal_id'], ('ERzeroToMany', 'ERmandOne', True)),
        ]
        for table, columns, expected in cases:
            with self.subTest(table=table):
                self.assertEqual(marcas_fk(by[table], columns), expected)


if __name__ == '__main__':
    unittest.main()
