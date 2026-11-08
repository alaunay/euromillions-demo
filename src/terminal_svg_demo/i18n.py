"""Translation support, GNU gettext with PO catalogues."""

from __future__ import annotations

import gettext as _gettext
import os
from pathlib import Path
from typing import List, Optional

DOMAIN = "terminal-svg-demo"
LOCALE_DIR = Path(__file__).with_name("locale")

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
    return LOCALE_DIR / code / "LC_MESSAGES" / f"{DOMAIN}.mo"


def available() -> List[str]:
    """Every language with a compiled catalogue, English first."""
    codes = ["en"]

    if LOCALE_DIR.is_dir():
        for path in sorted(LOCALE_DIR.iterdir()):
            if (path / "LC_MESSAGES" / f"{DOMAIN}.mo").is_file():
                codes.append(path.name)

    return codes


def setup(language: Optional[str] = None) -> str:
    """Load the catalogue for a language and return its code."""
    global _translation

    code = detect_language(language)
    _translation = _gettext.translation(
        DOMAIN,
        localedir=str(LOCALE_DIR),
        languages=[code],
        fallback=True,
    )
    return code


def _(message: str) -> str:
    """Translate a msgid; English without a loaded catalogue."""
    if _translation is None:
        return message
    return _translation.gettext(message)
