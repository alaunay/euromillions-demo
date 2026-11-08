"""Command line interface."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, NamedTuple, Optional, Sequence

from . import i18n
from .core import build, load
from .i18n import _


class Parsed(NamedTuple):
    language: Optional[str]
    positionals: List[str]
    error: Optional[str]
    argument: str
    help: bool


def help_text() -> str:
    return "\n".join(
        [
            _("usage: %(prog)s [-l CODE] SPEC.json [OUTPUT.svg]") % {"prog": "terminal-svg-demo"},
            "",
            _("Render a terminal session as an animated SVG."),
            "",
            _("options:"),
            _("  -l, --lang CODE  output language"),
            _("  -h, --help       show this help"),
            "",
            _("languages: %(languages)s") % {"languages": " ".join(i18n.available())},
        ]
    )


def parse(argv: Sequence[str]) -> Parsed:
    """Split the command line, without touching the filesystem."""
    language: Optional[str] = None
    positionals: List[str] = []
    args = list(argv[1:])
    index = 0

    while index < len(args):
        argument = args[index]

        if argument in ("-l", "--lang"):
            if index + 1 >= len(args):
                return Parsed(language, positionals, "needs_code", argument, False)
            language = args[index + 1]
            index += 2
        elif argument.startswith("--lang="):
            language = argument.split("=", 1)[1]
            index += 1
        elif argument in ("-h", "--help"):
            return Parsed(language, positionals, None, "", True)
        elif argument.startswith("-") and argument != "-":
            return Parsed(language, positionals, "unknown", argument, False)
        else:
            positionals.append(argument)
            index += 1

    return Parsed(language, positionals, None, "", False)


def warn_missing_catalogue(code: str) -> None:
    if code in ("en", "C", "POSIX") or code.startswith("C."):
        return
    if i18n.catalogue(code).is_file():
        return

    print(
        _("no catalogue for %(code)s, using English") % {"code": code},
        file=sys.stderr,
    )


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    print(help_text(), file=sys.stderr)
    return 2


def main(argv: Sequence[str]) -> int:
    """Run the command line, returning the exit status."""
    parsed = parse(argv)
    code = i18n.setup(parsed.language)
    warn_missing_catalogue(code)

    if parsed.error == "needs_code":
        return fail(_("option %(option)s needs a language code") % {"option": parsed.argument})
    if parsed.error == "unknown":
        return fail(_("unknown argument: %(arg)s") % {"arg": parsed.argument})
    if parsed.help:
        print(help_text())
        return 0
    if not parsed.positionals:
        return fail(_("missing spec file"))
    if len(parsed.positionals) > 2:
        return fail(_("unknown argument: %(arg)s") % {"arg": parsed.positionals[2]})

    spec = load(parsed.positionals[0])
    target = Path(parsed.positionals[1]) if len(parsed.positionals) > 1 else Path("demo.svg")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build(spec), encoding="utf-8")
    print(_("wrote: %(path)s") % {"path": target})
    return 0


def cli() -> None:
    """Console-script entry point."""
    raise SystemExit(main(sys.argv))
