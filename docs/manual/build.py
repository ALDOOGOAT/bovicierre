#!/usr/bin/env python3
"""Compila la fuente LaTeX pública; sólo escribe el PDF de salida solicitado."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def prepare(directory):
    text = (HERE / 'source/manual.tex').read_text()
    assets = json.loads((HERE / 'source/assets.json').read_text())
    (directory / 'assets').mkdir()
    for name, relative in assets.items():
        source = (ROOT / relative).resolve()
        if Path(name).name != name or not source.is_relative_to(ROOT) or not source.is_file():
            raise ValueError('Referencia de diagrama inválida: ' + name)
        shutil.copyfile(source, directory / 'assets' / name)
    text = text.replace('@@BOVI_ROOT@@', ROOT.as_posix()).replace('@@BOVI_BUILD@@', directory.as_posix())
    if '@@BOVI_' in text:
        raise ValueError('Marcador de ruta sin resolver')
    source = directory / 'manual.tex'
    source.write_text(text)
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/pdf/BoviCierre_Manual_Integral.pdf')
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='bovicierre-manual-') as temporary:
        directory = Path(temporary)
        source = prepare(directory)
        if args.self_check:
            assert source.is_file() and len(list((directory / 'assets').glob('*.pdf'))) == 12
            assert '\\chapter{' in source.read_text() and 'Idempotency-Key' in source.read_text()
            print('PASS: fuente y doce diagramas disponibles; no se compiló ni modificó el PDF')
            return
        if not shutil.which('tectonic'):
            raise SystemExit('Falta Tectonic; consulta docs/manual/README.md')
        subprocess.run(['tectonic', str(source), '--outdir', str(directory)], check=True, cwd=ROOT)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(directory / 'manual.pdf', args.output)
        print('PDF generado: ' + str(args.output.resolve()))


if __name__ == '__main__':
    main()
