"""The renderer: spec loading, validation, and SVG output."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from xml.sax.saxutils import escape

from .i18n import _

DEFAULTS: Dict[str, Any] = {
    "title": "terminal",
    "width": 720,
    "title_bar": 40,
    "first_line": 72,
    "line_height": 28,
    "left": 28,
    "prompt_width": 18,
    "value_column": 112,
    "font_size": 15,
    "char_width": 9.0,
    "typing": 0.055,
    "start": 0.35,
    "line_pause": 0.35,
    "session_pause": 0.6,
    "hold": 7.0,
    "colors": {
        "background": "#0d1117",
        "title_background": "#161b22",
        "title_text": "#8b949e",
        "prompt": "#3fb950",
        "command": "#c9d1d9",
        "label": "#8b949e",
    },
    "sessions": [],
}


def merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively overlay ``override`` on ``base``."""
    result = dict(base)

    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = value

    return result


def load(path: str) -> Dict[str, Any]:
    """Read a spec file and merge it with the defaults."""
    with open(path, encoding="utf-8") as handle:
        spec = json.load(handle)

    if not isinstance(spec, dict):
        raise ValueError(_("the spec must be a JSON object"))

    return merge(DEFAULTS, spec)


def validate(spec: Dict[str, Any]) -> None:
    """Reject a spec that cannot be rendered, with a precise message."""
    if not isinstance(spec, dict):
        raise ValueError(_("the spec must be a JSON object"))

    if not isinstance(spec.get("title"), str):
        raise ValueError(_("'title' must be a string"))

    sessions = spec.get("sessions")
    if not isinstance(sessions, list) or not sessions:
        raise ValueError(_("'sessions' must be a non-empty list"))

    for index, session in enumerate(sessions):
        if not isinstance(session, dict):
            raise ValueError(_("session %(index)d must be an object") % {"index": index})
        if not isinstance(session.get("command"), str):
            raise ValueError(_("session %(index)d: 'command' must be a string") % {"index": index})

        outputs = session.get("outputs")
        if not isinstance(outputs, list):
            raise ValueError(_("session %(index)d: 'outputs' must be a list") % {"index": index})

        for offset, output in enumerate(outputs):
            for field in ("label", "value", "color"):
                if not isinstance(output.get(field), str):
                    raise ValueError(
                        _("session %(index)d output %(offset)d: '%(field)s' must be a string")
                        % {"index": index, "offset": offset, "field": field}
                    )


def text(x: float, y: float, value: str, fill: str, extra: str = "") -> str:
    return f'<text x="{x}" y="{y}" fill="{fill}"{extra}>{escape(value)}</text>'


def timed(duration: float) -> str:
    return f'dur="{duration}s" repeatCount="indefinite"'


class Layout:
    """Where the lines sit, and the length of the animation cycle."""

    def __init__(self, spec: Dict[str, Any]) -> None:
        self.spec = spec
        self.rows: int = sum(1 + len(session["outputs"]) for session in spec["sessions"])
        self.rows += max(len(spec["sessions"]) - 1, 0)
        self.height: int = spec["first_line"] + (self.rows - 1) * spec["line_height"] + 66
        self.y: Dict[Any, int] = {}
        self.begin: Dict[int, float] = {}
        self.end: Dict[int, float] = {}
        self.cycle: float = 0.0
        self.place()

    def place(self) -> None:
        first = self.spec["first_line"]
        step = self.spec["line_height"]
        start = self.spec["start"]
        pause = self.spec["line_pause"]
        typing = self.spec["typing"]

        y = first
        t = start
        last = len(self.spec["sessions"]) - 1

        for index, session in enumerate(self.spec["sessions"]):
            self.y[index] = y
            self.begin[index] = t
            self.end[index] = t + len(session["command"]) * typing
            t = self.end[index]

            for offset in range(len(session["outputs"])):
                y += step
                t += pause if offset else pause * 0.43
                self.y[(index, offset)] = y

            y += step * 2
            t += self.spec["session_pause"] if index < last else 0.0

        self.cycle = t + self.spec["hold"]

    def prompt_x(self) -> float:
        return float(self.spec["left"] + self.spec["prompt_width"])

    def value_x(self) -> float:
        return float(self.spec["value_column"])


def key(time: float, cycle: float) -> float:
    return round(time / cycle, 4)


def fade_in(at: float, cycle: float) -> str:
    return (
        f'<animate attributeName="opacity" values="0;1" '
        f'keyTimes="0;{key(at, cycle)}" {timed(cycle)} calcMode="discrete"/>'
    )


def typing(width: float, start: float, end: float, cycle: float) -> str:
    return (
        f'<animate attributeName="width" values="0;0;{width};{width}" '
        f'keyTimes="0;{key(start, cycle)};{key(end, cycle)};1" {timed(cycle)}/>'
    )


def cursor_move(x: float, begin: float, end: float, width: float, cycle: float) -> str:
    return (
        f'<animate attributeName="x" values="{x};{x};{x + width};{x + width}" '
        f'keyTimes="0;{key(begin, cycle)};{key(end, cycle)};1" {timed(cycle)}/>'
    )


def cursor_visibility(begin: float, hide: float, cycle: float) -> str:
    start = max(begin - 0.3, 0.0)

    if hide >= cycle:
        return (
            f'<animate attributeName="opacity" values="0;1;1" '
            f'keyTimes="0;{key(start, cycle)};1" {timed(cycle)} calcMode="discrete"/>'
        )

    return (
        f'<animate attributeName="opacity" values="0;1;1;0" '
        f'keyTimes="0;{key(start, cycle)};{key(hide, cycle)};1" '
        f'{timed(cycle)} calcMode="discrete"/>'
    )


def build(spec: Optional[Dict[str, Any]] = None) -> str:
    """Render a spec, or the defaults, into an SVG document."""
    if spec is None:
        spec = merge(DEFAULTS, {})

    validate(spec)

    layout = Layout(spec)
    cycle = layout.cycle
    colors = spec["colors"]
    font_size = spec["font_size"]
    char_width = spec["char_width"]
    prompt_x = layout.prompt_x()
    value_x = layout.value_x()
    width = spec["width"]
    height = layout.height
    last = len(spec["sessions"]) - 1

    out: List[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
    )
    out.append('<title id="title">Terminal session</title>')
    out.append(
        '<desc id="desc">A terminal types a command, prints the result, then types '
        "another command.</desc>"
    )

    out.append("<defs>")
    for index, session in enumerate(spec["sessions"]):
        y = layout.y[index]
        command_width = len(session["command"]) * char_width
        out.append(
            f'<clipPath id="typing-{index}"><rect x="{prompt_x}" y="{y - 14}" width="0" '
            f'height="22">{typing(command_width, layout.begin[index], layout.end[index], cycle)}'
            "</rect></clipPath>"
        )
    out.append("</defs>")

    out.append(f'<rect width="{width}" height="{height}" rx="12" fill="{colors["background"]}"/>')
    out.append(
        f'<rect width="{width}" height="{spec["title_bar"]}" rx="12" '
        f'fill="{colors["title_background"]}"/>'
    )
    out.append(
        f'<rect y="{spec["title_bar"] - 12}" width="{width}" height="12" '
        f'fill="{colors["title_background"]}"/>'
    )
    for index, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        out.append(
            f'<circle cx="{24 + index * 20}" cy="{spec["title_bar"] // 2}" r="6" fill="{color}"/>'
        )
    out.append(
        text(
            width / 2,
            25,
            spec["title"],
            colors["title_text"],
            ' text-anchor="middle" font-size="12"',
        )
    )

    out.append(
        '<g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
        f'font-size="{font_size}">'
    )

    for index, session in enumerate(spec["sessions"]):
        y = layout.y[index]
        begin = layout.begin[index]
        end = layout.end[index]
        command_width = len(session["command"]) * char_width
        hide = layout.begin[index + 1] if index < last else cycle

        if index:
            out.append(f'<g opacity="0">{fade_in(max(begin - 0.3, 0.0), cycle)}')
            out.append(text(spec["left"], y, "$", colors["prompt"]))
            out.append("</g>")
        else:
            out.append(text(spec["left"], y, "$", colors["prompt"]))

        out.append(f'<g clip-path="url(#typing-{index})">')
        out.append(text(prompt_x, y, session["command"], colors["command"]))
        out.append("</g>")
        out.append(
            f'<rect x="{prompt_x}" y="{y - 13}" width="8" height="{font_size + 4}" '
            f'fill="{colors["command"]}" opacity="0">'
            f"{cursor_visibility(begin, hide, cycle)}"
            f"{cursor_move(prompt_x, begin, end, command_width, cycle)}"
            "</rect>"
        )

        for offset, output in enumerate(session["outputs"]):
            at = end + spec["line_pause"] * (1 if offset else 0.43)
            out.append(f'<g opacity="0">{fade_in(at, cycle)}')
            out.append(
                text(
                    spec["left"],
                    layout.y[(index, offset)],
                    output["label"],
                    colors["label"],
                )
            )
            out.append(
                text(
                    value_x,
                    layout.y[(index, offset)],
                    output["value"],
                    output["color"],
                )
            )
            out.append("</g>")

    out.append("</g>")
    out.append("</svg>")
    return "\n".join(out) + "\n"
