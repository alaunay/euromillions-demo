"""Tests for make_demo.py."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.dom.minidom import parseString

import make_demo


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.svg = make_demo.build()

    def test_output_is_well_formed(self):
        parseString(self.svg)

    def test_output_is_a_svg(self):
        self.assertTrue(self.svg.startswith("<svg "))
        self.assertTrue(self.svg.rstrip().endswith("</svg>"))

    def test_output_animates(self):
        self.assertGreaterEqual(self.svg.count("<animate "), 8)
        self.assertIn('repeatCount="indefinite"', self.svg)

    def test_output_holds_both_draws(self):
        self.assertIn("4 8 13 36 46", self.svg)
        self.assertIn("17 19 20 27 48", self.svg)
        self.assertIn("Numéros:", self.svg)

    def test_output_uses_the_euromillions_palette(self):
        self.assertIn(make_demo.NUMBERS, self.svg)
        self.assertIn(make_demo.STARS, self.svg)


class CliTest(unittest.TestCase):
    def test_writes_the_requested_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "nested" / "demo.svg"
            subprocess.run(
                [sys.executable, "make_demo.py", str(target)],
                check=True,
                capture_output=True,
            )
            self.assertEqual(target.read_text(encoding="utf-8"), make_demo.build())

    def test_writes_demo_svg_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [sys.executable, str(Path("make_demo.py").resolve())],
                check=True,
                capture_output=True,
                cwd=tmp,
            )
            self.assertTrue((Path(tmp) / "demo.svg").exists())


if __name__ == "__main__":
    unittest.main()
