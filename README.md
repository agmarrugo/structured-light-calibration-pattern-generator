# Structured-light calibration targets

Generate white-on-black calibration targets directly in Python. The included notebook replaces downloading OpenCV scripts and manually editing an SVG with imports from a small local package. The generator uses only the Python standard library (Python 3.10+).

## Start

From this directory:

```sh
python3 -m calibration_patterns
```

This generates all five presets in `patterns/`. To use the notebook:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[notebook]'
python -m jupyterlab Calibration_pattern_generation_v2.ipynb
```

Select the environment's Python kernel. In Colab, upload/unpack this repository, change into its root, then run the notebook. No network download is needed by the pattern generator itself.

## Use the functions

```python
from calibration_patterns import Pattern, generate_pattern, object_points

spec = Pattern(columns=8, rows=21, spacing_mm=16, radius_ratio=2.5,
               page_width_mm=297, page_height_mm=420,
               kind='acircles', inverted=True)
path = generate_pattern('patterns/custom.svg', spec)
points = object_points(spec)
```

Supported kinds: `acircles` (asymmetric circle grid), `circles` (symmetric grid), and `checkerboard`. Set `inverted=False` for black features on white. Outputs at the chosen filename are replaced on regeneration. SVG backgrounds are real full-page rectangles, so polarity survives export.

Presets reproduce the layouts listed in the original notebook: asymmetric circles 8×21/16 mm/A3, 7×21/15 mm/A3, 7×21/18 mm/A2, 7×21/35 mm/A1, and a 7×9/20 mm checkerboard on the original 216×279 mm page. These are starting layouts; suitability depends on your optics and capture setup.

## Geometry and calibration

For asymmetric grids, `spacing_mm` is the row step and alternating-row horizontal offset. Horizontal pitch is twice this value; diagonal spacing between adjacent rows is √2 times this value. Radius is `spacing_mm / radius_ratio`. The supplied A3 pattern has 168 circles, 6.4 mm radius, and first center (28.5, 50) mm on the page. The new target preserves all nominal circle centers and radii from your SVG but removes its extra white stroke and replaces its inset black rectangle with a full-page background.

For symmetric grids, spacing is the horizontal and vertical center pitch. For checkerboards, spacing is square side length and rows/columns count squares; the 7×9 board has 6×8 inner corners. Checkerboard polarity alternates white and black squares on the chosen page background.

Each SVG has a CSV of planar object points in millimetres (row-major, first point at the origin) and JSON with parameters and the page offset of that origin. Pair these with detected image points only after checking ordering and orientation. Geometric symmetries can make orientation ambiguous. If you use a dark-blob detector, invert the captured grayscale image or configure it to detect bright blobs for the inverted circle target.

Print at actual size / 100%, disable fit-to-page, and measure the printed spacing. Printer margins can clip the black background. These SVGs are physical planar targets; they do not generate Gray-code/phase-shift projection sequences or perform camera–projector calibration. SVG millimetres do not imply a known physical size when displayed by a projector.

## Repository layout

- `calibration_patterns/`: reusable generator, geometry, presets, and command-line entry point.
- `Calibration_pattern_generation_v2.ipynb`: modified notebook using package imports.
- `patterns/`: generated SVG, CSV, and JSON files.
- `tests/`: geometry, polarity, and validation checks.

Run checks with `python3 -m unittest discover -s tests -v`.

The modified notebook is included in this repository. No upstream Python source is vendored.
