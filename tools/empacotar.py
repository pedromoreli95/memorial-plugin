#!/usr/bin/env python3
"""Gera um ZIP instalável no QGIS com a pasta memorial_plugin."""
import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent.parent
FILES = ('__init__.py', 'deps.py', 'extractor.py', 'memorial_dialog.py',
         'memorial_plugin.py', 'metadata.txt', 'icon.png', 'LICENSE', 'README.md')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destino', nargs='?', type=Path,
                        default=ROOT / 'dist' / 'memorial_plugin.zip')
    args = parser.parse_args()
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    if missing:
        parser.error('Arquivos ausentes: ' + ', '.join(missing))
    args.destino.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.destino, 'w', compression=ZIP_DEFLATED) as archive:
        for name in FILES:
            archive.write(ROOT / name, 'memorial_plugin/' + name)
    print(f'Pacote criado: {args.destino}')


if __name__ == '__main__':
    main()
