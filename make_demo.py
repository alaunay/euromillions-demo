#!/usr/bin/env python3
"""Render an animated terminal session as declarative SVG.

The animation uses SMIL, so every renderer plays it as a plain image: no
JavaScript, no media player, no GIF.

    python3 make_demo.py SPEC.json [OUTPUT.svg]
"""

import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

DEFAULTS = {
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


def merge(base, override):
    result = dict(base)

    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = value

    return result


def load(path):
    with open(path, encoding="utf-8") as handle:
        return merge(DEFAULTS, json.load(handle))


def text(x, y, value, fill, extra=""):
    return f'<text x="{x}" y="{y}" fill="{fill}"{extra}>{escape(value)}</text>'


def timed(duration, cycle):
    return f'dur="{duration}s" repeatCount="indefinite"'


class Layout:
    """Where the lines sit, and the length of the animation cycle."""

    def __init__(self, spec):
        self.spec = spec
        self.rows = sum(1 + len(session["outputs"]) for session in spec["sessions"])
        self.rows += max(len(spec["sessions"]) - 1, 0)
        self.height = spec["first_line"] + (self.rows - 1) * spec["line_height"] + 66
        self.y = {}
        self.begin = {}
        self.end = {}
        self.cycle = 0.0
        self.place()

    def place(self):
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
                t += pause * (1 if offset else 0.43)
                self.y[(index, offset)] = y

            y += step * 2
            t += self.spec["session_pause"] if index < last else 0.0

        self.cycle = t + self.spec["hold"]

    def prompt_x(self):
        return self.spec["left"] + self.spec["prompt_width"]

    def value_x(self):
        return self.spec["value_column"]


def key(time, cycle):
    return round(time / cycle, 4)


def fade_in(at, cycle):
    return (
        f'<animate attributeName="opacity" values="0;1" keyTimes="0;{key(at, cycle)}" '
        f"{timed(cycle, cycle)} calcMode=\"discrete\"/>"
    )


def typing(width, start, end, cycle):
    return (
        f'<animate attributeName="width" values="0;0;{width};{width}" '
        f'keyTimes="0;{key(start, cycle)};{key(end, cycle)};1" {timed(cycle, cycle)}/>'
    )


def cursor_move(start, end, width, cycle):
    x = start
    return (
        f'<animate attributeName="x" values="{x};{x};{x + width};{x + width}" '
        f'keyTimes="0;{key(start, cycle)};{key(end, cycle)};1" {timed(cycle, cycle)}/>'
    )


def cursor_visibility(begin, hide, cycle):
    start = max(begin - 0.3, 0.0)
    if hide >= cycle:
        return (
            f'<animate attributeName="opacity" values="0;1;1" '
            f'keyTimes="0;{key(start, cycle)};1" '
            f"{timed(cycle, cycle)} calcMode=\"discrete\"/>"
        )
    return (
        f'<animate attributeName="opacity" values="0;1;1;0" '
        f'keyTimes="0;{key(start, cycle)};{key(hide, cycle)};1" '
        f"{timed(cycle, cycle)} calcMode=\"discrete\"/>"
    )


def build(spec=None):
    if spec is None:
        spec = merge(DEFAULTS, {})

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

    out = []
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

    out.append(f'<g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="{font_size}">')

    for index, session in enumerate(spec["sessions"]):
        y = layout.y[index]
        begin = layout.begin[index]
        end = layout.end[index]
        command_width = len(session["command"]) * char_width
        hide = layout.begin[index + 1] if index < last else cycle

        out.append(text(spec["left"], y, "$", colors["prompt"]))
        out.append(f'<g clip-path="url(#typing-{index})">')
        out.append(text(prompt_x, y, session["command"], colors["command"]))
        out.append("</g>")
        out.append(
            f'<rect x="{prompt_x}" y="{y - 13}" width="8" height="{font_size + 4}" '
            f'fill="{colors["command"]}" opacity="0">'
            f"{cursor_visibility(begin, hide, cycle)}"
            f"{cursor_move(prompt_x, end, command_width, cycle)}"
            "</rect>"
        )

        for offset, output in enumerate(session["outputs"]):
            at = end + spec["line_pause"] * (1 if offset else 0.43)
            out.append(f'<g opacity="0">{fade_in(at, cycle)}')
            out.append(text(spec["left"], layout.y[(index, offset)], output["label"], colors["label"]))
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


def main(argv):
    if len(argv) < 2:
        print("usage: make_demo.py SPEC.json [OUTPUT.svg]", file=sys.stderr)
        return 2

    spec = load(argv[1])
    target = Path(argv[2]) if len(argv) > 2 else Path("demo.svg")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build(spec), encoding="utf-8")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
