"""Tests for the renderer."""

import re
import tempfile
import unittest
from pathlib import Path
from xml.dom.minidom import parseString

from terminal_svg_demo import DEFAULTS, build, load, merge, validate

SPEC = Path("examples/euromillions.json")


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.spec = load(str(SPEC))
        self.svg = build(self.spec)

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

    def test_output_uses_the_spec_title_and_height(self):
        self.assertIn(">euromillions</text>", self.svg)
        self.assertIn('viewBox="0 0 720 306"', self.svg)

    def test_key_times_are_ordered(self):
        for match in re.finditer(r'keyTimes="([^"]*)"', self.svg):
            values = [float(value) for value in match.group(1).split(";")]
            self.assertEqual(values[0], 0.0)
            self.assertEqual(values, sorted(values))
            self.assertEqual(len(values), len(set(values)))


class CommentTest(unittest.TestCase):
    def test_a_spec_may_hold_line_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec_file = Path(tmp) / "spec.json"
            spec_file.write_text(
                """
{
  "title": "commented",
  // the prompt is neon green
  "sessions": [
    {
      "command": "echo hi",
      // the only output
      "outputs": [{"label": "out:", "value": "hi", "color": "#ffffff"}]
    }
  ]
}
""",
                encoding="utf-8",
            )
            spec = load(str(spec_file))
            self.assertEqual(spec["title"], "commented")
            self.assertIn("echo hi", build(spec))


class GeneralityTest(unittest.TestCase):
    def test_a_minimal_spec_builds(self):
        spec = merge(
            DEFAULTS,
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
        svg = build(spec)
        parseString(svg)
        self.assertIn("echo hi", svg)
        self.assertIn(">other</text>", svg)
        self.assertIn("#ffffff", svg)

    def test_the_defaults_have_no_session(self):
        with self.assertRaises(ValueError):
            build(merge(DEFAULTS, {}))


class ValidateTest(unittest.TestCase):
    def base(self):
        return {
            "title": "t",
            "sessions": [
                {
                    "command": "c",
                    "outputs": [{"label": "l", "value": "v", "color": "#fff"}],
                }
            ],
        }

    def test_accepts_a_good_spec(self):
        validate(self.base())

    def test_rejects_a_bad_title(self):
        spec = self.base()
        spec["title"] = 3
        with self.assertRaises(ValueError):
            validate(spec)

    def test_rejects_no_session(self):
        spec = self.base()
        spec["sessions"] = []
        with self.assertRaises(ValueError):
            validate(spec)

    def test_rejects_a_session_that_is_not_an_object(self):
        spec = self.base()
        spec["sessions"] = ["nope"]
        with self.assertRaises(ValueError):
            validate(spec)

    def test_rejects_a_command_that_is_not_a_string(self):
        spec = self.base()
        spec["sessions"][0]["command"] = 3
        with self.assertRaises(ValueError):
            validate(spec)

    def test_rejects_outputs_that_are_not_a_list(self):
        spec = self.base()
        spec["sessions"][0]["outputs"] = "nope"
        with self.assertRaises(ValueError):
            validate(spec)

    def test_rejects_an_output_missing_a_field(self):
        spec = self.base()
        del spec["sessions"][0]["outputs"][0]["color"]
        with self.assertRaises(ValueError):
            validate(spec)

    def test_rejects_a_spec_that_is_not_an_object(self):
        with self.assertRaises(ValueError):
            validate([])


if __name__ == "__main__":
    unittest.main()
