"""Translation support, GNU gettext with PO catalogues."""

from __future__ import annotations

import gettext as _gettext
import os
import sys
from pathlib import Path
from typing import List, Optional

DOMAIN = "terminal-svg-demo"
LOCALE_DIR = Path(__file__).with_name("locale")


def locale_dirs() -> List[Path]:
    """Where a catalogue may live: the package, then the system data dir."""
    prefix = Path(sys.prefix)
    return [
        LOCALE_DIR,
        prefix / "share" / "terminal-svg-demo" / "locale",
        Path("/usr/share/terminal-svg-demo/locale"),
    ]


_translation: Optional[_gettext.NullTranslations] = None


def detect_language(explicit: Optional[str] = None) -> str:
    """Language from the argument, then LANGUAGE, LC_ALL, LANG, then en."""
    code = (
        explicit
        or os.environ.get("LANGUAGE")
        or os.environ.get("LC_ALL")
        or os.environ.get("LANG")
        or ""
    )
    code = code.split(":")[0].split(".")[0].split("_")[0]
    return code or "en"


def catalogue(code: str) -> Path:
    """The first catalogue for a code, or the expected path when absent."""
    for directory in locale_dirs():
        path = directory / code / "LC_MESSAGES" / f"{DOMAIN}.mo"
        if path.is_file():
            return path

    return LOCALE_DIR / code / "LC_MESSAGES" / f"{DOMAIN}.mo"


def available() -> List[str]:
    """Every language with a compiled catalogue, English first."""
    codes = ["en"]

    for directory in locale_dirs():
        if not directory.is_dir():
            continue
        for path in sorted(directory.iterdir()):
            if (path / "LC_MESSAGES" / f"{DOMAIN}.mo").is_file() and path.name not in codes:
                codes.append(path.name)

    return codes


def setup(language: Optional[str] = None) -> str:
    """Load the catalogue for a language and return its code."""
    global _translation

    code = detect_language(language)
    localedir = catalogue(code).parents[2]
    _translation = _gettext.translation(
        DOMAIN,
        localedir=str(localedir),
        languages=[code],
        fallback=True,
    )
    return code


def _(message: str) -> str:
    """Translate a msgid; English without a loaded catalogue."""
    if _translation is None:
        return message
    return _translation.gettext(message)
