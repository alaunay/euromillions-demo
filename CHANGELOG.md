# Changelog

All notable changes to this project. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-08

### Added

- JSON spec driving the sessions, the outputs, the colours, and the title.
- Declarative SMIL animation, no JavaScript and no dependency.
- Layout, timing, and height derived from the spec.
- Spec validation with a message naming the offending field.
- GNU gettext catalogues, with French, and a `--lang` option.
- Console script `terminal-svg-demo`, and `python -m terminal_svg_demo`.
- Tests, ruff, mypy, and coverage in CI, across Python 3.10 to 3.13.
- Self-describing demo in `examples/self-demo.svg`.
