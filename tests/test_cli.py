"""Tests for the command line."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from terminal_svg_demo import i18n
from terminal_svg_demo.cli import main, parse

SPEC = Path("examples/euromillions.json").resolve()

# Pin the locale: the default output must be English whatever the host
os.environ.pop("LANGUAGE", None)
os.environ.pop("LC_ALL", None)
os.environ["LANG"] = "C"


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        status = main(argv)
    return status, out.getvalue(), err.getvalue()


class ParseTest(unittest.TestCase):
    def test_positionals(self):
        parsed = parse(["prog", "spec.json", "out.svg"])
        self.assertEqual(parsed.positionals, ["spec.json", "out.svg"])
        self.assertIsNone(parsed.error)
        self.assertFalse(parsed.help)

    def test_language_forms(self):
        self.assertEqual(parse(["prog", "-l", "fr"]).language, "fr")
        self.assertEqual(parse(["prog", "--lang", "fr"]).language, "fr")
        self.assertEqual(parse(["prog", "--lang=fr"]).language, "fr")

    def test_help(self):
        self.assertTrue(parse(["prog", "-h"]).help)
        self.assertTrue(parse(["prog", "--help"]).help)

    def test_errors(self):
        self.assertEqual(parse(["prog", "-l"]).error, "needs_code")
        self.assertEqual(parse(["prog", "--nope"]).error, "unknown")


class RunTest(unittest.TestCase):
    def test_writes_the_requested_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "nested" / "demo.svg"
            status, out, _ = run(["prog", str(SPEC), str(target)])
            self.assertEqual(status, 0)
            self.assertIn("wrote:", out)
            self.assertTrue(target.exists())

    def test_writes_demo_svg_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path.cwd()
            try:
                os.chdir(tmp)
                status, _, _ = run(["prog", str(SPEC)])
            finally:
                os.chdir(cwd)
            self.assertEqual(status, 0)
            self.assertTrue((Path(tmp) / "demo.svg").exists())

    def test_help(self):
        status, out, _ = run(["prog", "--help"])
        self.assertEqual(status, 0)
        self.assertIn("usage:", out)
        self.assertIn("--lang", out)

    def test_missing_spec(self):
        status, _, err = run(["prog"])
        self.assertEqual(status, 2)
        self.assertIn("missing spec file", err)

    def test_too_many_arguments(self):
        status, _, err = run(["prog", str(SPEC), "a.svg", "b.svg"])
        self.assertEqual(status, 2)
        self.assertIn("unknown argument", err)

    def test_language_without_code(self):
        status, _, err = run(["prog", "-l"])
        self.assertEqual(status, 2)
        self.assertIn("needs a language code", err)

    def test_unknown_argument(self):
        status, _, err = run(["prog", "--nope"])
        self.assertEqual(status, 2)
        self.assertIn("unknown argument: --nope", err)

    def test_warns_on_a_missing_catalogue(self):
        status, _, err = run(["prog", "-l", "de", str(SPEC), "/dev/null"])
        self.assertEqual(status, 0)
        self.assertIn("no catalogue for de", err)


class FrenchTest(unittest.TestCase):
    def setUp(self):
        if not i18n.catalogue("fr").is_file():
            self.skipTest("the french catalogue is not built")

    def test_translates_the_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            status, out, _ = run(["prog", "-l", "fr", str(SPEC), str(Path(tmp) / "a.svg")])
            self.assertEqual(status, 0)
            self.assertIn("écrit :", out)

    def test_translates_the_help(self):
        status, out, _ = run(["prog", "-l", "fr", "--help"])
        self.assertEqual(status, 0)
        self.assertIn("utilisation :", out)
        self.assertIn("langues :", out)

    def test_translates_an_error(self):
        status, _, err = run(["prog", "-l", "fr", "--nope"])
        self.assertEqual(status, 2)
        self.assertIn("argument inconnu : --nope", err)


if __name__ == "__main__":
    unittest.main()
