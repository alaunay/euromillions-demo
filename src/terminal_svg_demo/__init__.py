"""Render an animated terminal session as declarative SVG."""

from .core import DEFAULTS, build, load, merge, validate
from .i18n import available, detect_language, setup

__all__ = [
    "DEFAULTS",
    "available",
    "build",
    "detect_language",
    "load",
    "merge",
    "setup",
    "validate",
]
