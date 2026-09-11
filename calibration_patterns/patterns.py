"""Explicit SVG backgrounds and geometry; no downloaded runtime scripts."""
from dataclasses import dataclass, asdict
from pathlib import Path
import csv
import json
import math
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Pattern:
    columns: int = 8
    rows: int = 21
    spacing_mm: float = 16
    radius_ratio: float = 2.5
    page_width_mm: float = 297
    page_height_mm: float = 420
    kind: str = 'acircles'
    inverted: bool = True

    def __post_init__(self):
        if self.kind not in ('acircles', 'circles', 'checkerboard'):
            raise ValueError('kind must be acircles, circles, or checkerboard')
        for name in ('columns', 'rows'):
            value = getattr(self, name)
            if type(value) is not int or value < 1:
                raise ValueError(f'{name} must be a positive integer')
        for name in ('spacing_mm', 'radius_ratio', 'page_width_mm', 'page_height_mm'):
            value = getattr(self, name)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f'{name} must be finite and positive')
        if self.kind == 'checkerboard' and min(self.columns, self.rows) < 2:
            raise ValueError('checkerboards need at least two squares on each axis')
        if self.kind != 'checkerboard':
            points = object_points(self)
            minimum = min((math.dist(a, b) for i, a in enumerate(points)
                           for b in points[i + 1:]), default=math.inf)
            if 2 * self.spacing_mm / self.radius_ratio >= minimum:
                raise ValueError('circles touch or overlap; increase radius_ratio')
        width, height, _, _ = _geometry(self)
        if width > self.page_width_mm or height > self.page_height_mm:
            raise ValueError(f'Pattern footprint {width:g} x {height:g} mm exceeds page')


def object_points(pattern):
    """Planar points in mm, row-major order, origin at first calibration point.

    acircles: (spacing*(2*column + row%2), spacing*row, 0).
    checkerboard: columns/rows count squares; points are inner corners.
    Resolve the detector's orientation before pairing image and object points.
    """
    p = pattern
    columns = p.columns - (p.kind == 'checkerboard')
    rows = p.rows - (p.kind == 'checkerboard')
    return [(p.spacing_mm * (2 * c + r % 2 if p.kind == 'acircles' else c),
             p.spacing_mm * r, 0.0)
            for r in range(rows) for c in range(columns)]


def _geometry(p):
    if p.kind == 'checkerboard':
        return p.columns * p.spacing_mm, p.rows * p.spacing_mm, 0, 0
    radius = p.spacing_mm / p.radius_ratio
    pts = object_points(p)
    return max(x for x, y, z in pts) + 2 * radius, max(y for x, y, z in pts) + 2 * radius, radius, radius


def generate_pattern(path, pattern=None):
    """Write SVG, matching object-point CSV and geometry JSON; return SVG Path."""
    p = pattern if pattern is not None else Pattern()
    path = Path(path)
    if path.suffix.lower() != '.svg':
        raise ValueError('output path must end in .svg')
    width, height, dx, dy = _geometry(p)
    x0 = (p.page_width_mm - width) / 2 + dx
    y0 = (p.page_height_mm - height) / 2 + dy
    fg, bg = ('white', 'black') if p.inverted else ('black', 'white')
    svg = ET.Element('svg', {'xmlns': 'http://www.w3.org/2000/svg',
        'width': f'{p.page_width_mm:g}mm', 'height': f'{p.page_height_mm:g}mm',
        'viewBox': f'0 0 {p.page_width_mm:g} {p.page_height_mm:g}'})
    ET.SubElement(svg, 'title').text = f'{p.kind}: {p.columns} x {p.rows}, spacing {p.spacing_mm:g} mm'
    ET.SubElement(svg, 'rect', {'x': '0', 'y': '0', 'width': f'{p.page_width_mm:g}',
        'height': f'{p.page_height_mm:g}', 'fill': bg, 'stroke': 'none'})
    group = ET.SubElement(svg, 'g', {'fill': fg, 'stroke': 'none'})
    if p.kind == 'checkerboard':
        for r in range(p.rows):
            for c in range(p.columns):
                if (r + c) % 2 == 0:
                    ET.SubElement(group, 'rect', {'x': f'{x0+c*p.spacing_mm:g}',
                        'y': f'{y0+r*p.spacing_mm:g}', 'width': f'{p.spacing_mm:g}', 'height': f'{p.spacing_mm:g}'})
        point_origin = (x0 + p.spacing_mm, y0 + p.spacing_mm)
    else:
        for x, y, z in object_points(p):
            ET.SubElement(group, 'circle', {'cx': f'{x0+x:g}', 'cy': f'{y0+y:g}',
                'r': f'{p.spacing_mm/p.radius_ratio:g}'})
        point_origin = (x0, y0)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(svg)
    ET.ElementTree(svg).write(path, encoding='utf-8', xml_declaration=True)
    with path.with_suffix('.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['index', 'x_mm', 'y_mm', 'z_mm'])
        writer.writerows((i, *point) for i, point in enumerate(object_points(p)))
    metadata = asdict(p) | {'object_point_order': 'row-major',
        'object_point_origin_on_page_mm': point_origin,
        'foreground': fg, 'background': bg,
        'circle_radius_mm': None if p.kind == 'checkerboard' else p.spacing_mm / p.radius_ratio}
    path.with_suffix('.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return path


PRESETS = {
    'acircles_8x21_16mm_a3_inverted': Pattern(),
    'acircles_7x21_15mm_a3_inverted': Pattern(columns=7, spacing_mm=15),
    'acircles_7x21_18mm_a2_inverted': Pattern(columns=7, spacing_mm=18, page_width_mm=420, page_height_mm=594),
    'acircles_7x21_35mm_a1_inverted': Pattern(columns=7, spacing_mm=35, page_width_mm=594, page_height_mm=841),
    'checkerboard_7x9_20mm_letter_inverted': Pattern(columns=7, rows=9, spacing_mm=20, page_width_mm=216, page_height_mm=279, kind='checkerboard'),
}
