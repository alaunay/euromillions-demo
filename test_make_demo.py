"""Tests for make_demo.py."""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.dom.minidom import parseString

import make_demo

SPEC = Path("examples/euromillions.json")


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.spec = make_demo.load(SPEC)
        self.svg = make_demo.build(self.spec)

    def test_output_is_well_formed(self):
        parseString(self.svg)

    def test_output_is_a_svg(self):
        self.assertTrue(self.svg.startswith("<svg "))
        self.assertTrue(self.svg.rstrip().endswith("</svg>"))

    def test_output_animates(self):
        self.assertGreaterEqual(self.svg.count("<animate "), 8)
        self.assertIn('repeatCount="indefinite"', self.svg)

    def test_output_holds_both_sessions(self):
        self.assertIn("4 8 13 36 46", self.svg)
        self.assertIn("17 19 20 27 48", self.svg)
        self.assertIn("Numéros:", self.svg)

    def test_output_uses_the_spec_colours(self):
        self.assertIn("#4d6bff", self.svg)
        self.assertIn("#eebb05", self.svg)
        self.assertIn("#39ff14", self.svg)

    def test_key_times_are_ordered(self):
        for match in re.finditer(r'keyTimes="([^"]*)"', self.svg):
            values = [float(value) for value in match.group(1).split(";")]
            self.assertEqual(values[0], 0.0)
            self.assertEqual(values, sorted(values))
            self.assertEqual(len(values), len(set(values)))

    def test_output_uses_the_spec_title_and_height(self):
        self.assertIn(">euromillions</text>", self.svg)
        self.assertIn('viewBox="0 0 720 306"', self.svg)


class GeneralityTest(unittest.TestCase):
    def test_a_minimal_spec_builds(self):
        spec = make_demo.merge(
            make_demo.DEFAULTS,
            {
                "title": "other",
                "sessions": [
                    {
                        "command": "echo hi",
                        "outputs": [{"label": "out:", "value": "hi", "color": "#ffffff"}],
                    }
                ],
            },
        )
        svg = make_demo.build(spec)
        parseString(svg)
        self.assertIn("echo hi", svg)
        self.assertIn(">other</text>", svg)
        self.assertIn("#ffffff", svg)


class CliTest(unittest.TestCase):
    def test_writes_the_requested_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "nested" / "demo.svg"
            subprocess.run(
                [sys.executable, "make_demo.py", str(SPEC), str(target)],
                check=True,
                capture_output=True,
            )
            self.assertEqual(target.read_text(encoding="utf-8"), make_demo.build(make_demo.load(SPEC)))

    def test_writes_demo_svg_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [sys.executable, str(Path("make_demo.py").resolve()), str(SPEC.resolve())],
                check=True,
                capture_output=True,
                cwd=tmp,
            )
            self.assertTrue((Path(tmp) / "demo.svg").exists())

    def test_refuses_a_missing_spec(self):
        self.assertEqual(make_demo.main(["make_demo.py"]), 2)


if __name__ == "__main__":
    unittest.main()
