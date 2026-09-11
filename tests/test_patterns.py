import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from calibration_patterns import Pattern, PRESETS, generate_pattern, object_points

NS = {'s': 'http://www.w3.org/2000/svg'}


class PatternTests(unittest.TestCase):
    def test_original_geometry_and_background(self):
        with tempfile.TemporaryDirectory() as d:
            path = generate_pattern(Path(d) / 'target.svg')
            svg = ET.parse(path).getroot()
            self.assertEqual(svg.attrib['width'], '297mm')
            background = svg.find('s:rect', NS)
            self.assertEqual(background.attrib, dict(x='0', y='0', width='297', height='420', fill='black', stroke='none'))
            circles = svg.findall('.//s:circle', NS)
            self.assertEqual(len(circles), 168)
            actual = {(float(c.get('cx')), float(c.get('cy')), float(c.get('r'))) for c in circles}
            expected = {(28.5 + 16*(2*c+r%2), 50+16*r, 6.4) for r in range(21) for c in range(8)}
            self.assertEqual(actual, expected)
            self.assertEqual(svg.find('s:g', NS).get('fill'), 'white')
            self.assertTrue(path.with_suffix('.csv').exists())
            self.assertTrue(path.with_suffix('.json').exists())

    def test_validation(self):
        for args in [dict(rows=0), dict(columns=1.5), dict(spacing_mm=float('nan')),
                     dict(radius_ratio=1), dict(page_width_mm=20)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                Pattern(**args)

    def test_coordinates_and_checkerboard(self):
        self.assertEqual(object_points(Pattern())[8], (16, 16, 0))
        p = PRESETS['checkerboard_7x9_20mm_letter_inverted']
        self.assertEqual(len(object_points(p)), 48)
        self.assertEqual(object_points(p)[-1], (100, 140, 0))

    def test_presets_and_normal_polarity(self):
        with tempfile.TemporaryDirectory() as d:
            for name, p in PRESETS.items():
                generate_pattern(Path(d) / f'{name}.svg', p)
            path = generate_pattern(Path(d) / 'normal.svg', Pattern(kind='circles', inverted=False))
            svg = ET.parse(path).getroot()
            self.assertEqual(svg.find('s:rect', NS).get('fill'), 'white')
            self.assertEqual(svg.find('s:g', NS).get('fill'), 'black')


if __name__ == '__main__':
    unittest.main()
