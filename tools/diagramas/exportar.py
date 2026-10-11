#!/usr/bin/env python3
"""Exporta fuentes draw.io a SVG y PDF ISO; reúne las 11 láminas numeradas.

Requiere Docker (rlespinasse/drawio-export:v4.5.0) y PyMuPDF.
"""
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'docs/diagrams/sources'
OUT = ROOT / 'docs/diagrams/exports'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bovicierre-export-') as temp:
        for fmt in ('pdf', 'svg'):
            subprocess.run([
                'docker', 'run', '--rm', '-u', f'{os.getuid()}:{os.getgid()}', '-e', 'HOME=/tmp', '-w', '/data',
                '-v', f'{SOURCES}:/data:ro', '-v', f'{temp}:/out',
                'rlespinasse/drawio-export:v4.5.0', '-f', fmt, '-o', '/out',
            ], check=True)
        files = sorted(Path(temp).glob('*.pdf'))
        assert len(files) == 13, f'Esperadas 13 páginas, exportadas {len(files)}'
        combined = pymupdf.open()
        bookmarks = []
        for source in files:
            complete = source.name.startswith(('mer-completo-', 'relacional-completo-'))
            name = source.name.split('-', 2)[0] + '-completo.pdf' if complete else source.name
            mm = (1189, 841) if complete else (594, 420) if source.name.startswith('mer-01-') else (420, 297)
            src, doc = pymupdf.open(source), pymupdf.open()
            module_page = re.search(r'mer-07-relacional-p([1-5])-', source.name)
            # draw.io PDF incluye las páginas posteriores; la primera es la seleccionada.
            assert len(src) == (6 - int(module_page[1]) if module_page else 1), source.name
            page = doc.new_page(width=mm[0] * 72 / 25.4, height=mm[1] * 72 / 25.4)
            page.show_pdf_page(page.rect, src, 0)
            assert page.get_text().split() == src[0].get_text().split(), f'Texto perdido: {source.name}'
            doc.save(OUT / name, garbage=4, deflate=True)
            svg = source.with_suffix('.svg')
            assert svg.is_file(), svg.name
            shutil.copyfile(svg, (OUT / name).with_suffix('.svg'))
            if not complete:
                bookmarks.append([1, source.stem, len(combined) + 1])
                combined.insert_pdf(doc)
            src.close()
            doc.close()
        assert len(combined) == 11
        combined.set_toc(bookmarks)
        combined.save(OUT / 'laminas-numeradas.pdf', garbage=4, deflate=True)
        combined.close()
    print('13 PDF ISO y 13 SVG; láminas numeradas reunidas en 11 páginas; texto conservado')


if __name__ == '__main__':
    main()
