import argparse
from pathlib import Path
from . import PRESETS, generate_pattern


def main():
    parser = argparse.ArgumentParser(description='Generate inverted calibration SVGs and object coordinates.')
    parser.add_argument('--preset', choices=['all', *PRESETS], default='all')
    parser.add_argument('--output-dir', type=Path, default=Path('patterns'))
    args = parser.parse_args()
    for name in PRESETS if args.preset == 'all' else [args.preset]:
        print(generate_pattern(args.output_dir / f'{name}.svg', PRESETS[name]))


if __name__ == '__main__':
    main()
