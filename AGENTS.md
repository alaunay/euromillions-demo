# AGENTS.md

Guidance for agents working in this repository.

## Project

`terminal-svg-demo` renders an animated terminal session as declarative
SVG, from a JSON spec.

```
src/terminal_svg_demo/core.py    spec loading, validation, rendering
src/terminal_svg_demo/cli.py     the command line
src/terminal_svg_demo/i18n.py    gettext setup and language list
po/                              translation catalogues
tools/build-locales.sh           compiles po/*.po into the package
examples/                        specs and the SVGs generated from them
tests/                           unittest suite
```

- Standard library only at runtime. Do not add a dependency.
- SMIL for the animation. No JavaScript, no media player, no GIF.
- Nothing about a particular project belongs in the code: title, sessions,
  outputs, and colours come from the spec.
- The loader accepts whole-line `//` comments. Keep that when editing the
  spec parser, and name colours in the examples.
- `examples/euromillions.json` is illustrative. It does not track the
  euromillions repository, which owns its own spec.

Run it with:

```
terminal-svg-demo examples/self-demo.json /tmp/demo.svg
```

## Tests

The suite uses `unittest`, and the development extra brings the checks:

```
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
tools/build-locales.sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/terminal_svg_demo
.venv/bin/coverage run -m unittest discover -s tests
.venv/bin/coverage report
```

Coverage must stay at or above 90 percent.

The shell scripts are checked too:

```
shellcheck tools/build-locales.sh .githooks/commit-msg
bats tests/shell
```

`tests/shell/build_locales.bats` runs the catalogue builder in a sandbox;
`tests/shell/commit_msg.bats` exercises the hook in a throwaway git
repository. CI runs the same commands on Python 3.12, the Python suite
alone on 3.10 to 3.13, and fails when the committed examples differ from a
fresh generation.

French tests skip when `tools/build-locales.sh` has not run, so build the
catalogues first.

## Code conventions

- Python 3.10 or later, standard library only.
- Four spaces, double quotes, 100 columns.
- `ruff check`, `ruff format --check`, and `mypy` must pass.
- Keep the generated SVG valid as an `<img>`: no script, no external
  resource.

## Translations

Msgids are the English strings. Every message goes through `_()` from
`i18n`. After adding or changing one:

```
xgettext --language=Python --keyword=_ --output=po/terminal-svg-demo.pot \
    src/terminal_svg_demo/*.py
msgmerge -U po/fr.po po/terminal-svg-demo.pot
tools/build-locales.sh
```

`msgfmt --check` rejects a translation whose placeholders drift.

## Changelog

`CHANGELOG.md` is generated, never hand-typed:

```
python3 tools/changelog.py vX.Y.Z --output CHANGELOG.md
```

The script groups Conventional Commits prefixes and lists the rest under
"Changes". The release workflow runs it for the tag and feeds the release
body.

## Code scanning

CodeQL runs on the Python code through the repository default setup. The
`code-scanning` job adds the shellcheck findings: `tools/shellcheck-sarif.py`
converts `shellcheck -f json1` into SARIF, which GitHub accepts.

## Metadata

`metadata.json` follows the OpenVox module metadata format: name, version,
sources, dependencies, and `operating_system_support`. Update the system
list when a supported platform changes, then run:

```
python3 tools/check-metadata.py
```

CI validates it, and the macOS and FreeBSD jobs must agree with the list.

## Repository hosting

`tools/build-repo.sh` assembles an apt repository and an rpm repository
from the release assets, signing the metadata and the packages with
`REPO_GPG_KEY_ID`. `.github/workflows/pages.yml` runs it on every published
release and deploys the result with GitHub Pages.

Secrets: `REPO_GPG_PRIVATE_KEY` (armored private key) and `REPO_GPG_KEY_ID`.
The Pages source must be "GitHub Actions". Without a key the script leaves
the metadata unsigned, which apt refuses by default.

## Releases

A `vX.Y.Z` tag triggers `.github/workflows/release.yml`, which builds both
packages and attaches them to the GitHub release. The version lives in the
tag: the workflow rewrites `debian/changelog` and the spec before the
build. The files carry `0.0.0` as an unreleased placeholder; do not treat
it as a release number.

## Packaging

`debian/` builds a Debian package with `dpkg-buildpackage -b -us -uc`, and
`packaging/rpm/terminal-svg-demo.spec` builds an RPM from a `git archive`
tarball with the `pyproject-rpm-macros`.

The two distributions place the gettext catalogues differently: Debian
inside the Python package, the RPM under `/usr/share/terminal-svg-demo`.
`i18n.locale_dirs()` searches both, plus the same path under `sys.prefix`.
Keep that list when changing the layout.

## Commit rules

### Co-authored-by is mandatory

Every commit that contains work produced with an agent must end with a
`Co-authored-by` trailer. Hard rule.

Format, after a blank line at the end of the commit body:

```
Co-authored-by: Name <email>
```

- One line per contributing agent.
- Real name and real address. Never invent an address, never use a
  placeholder.

### Signed-off-by is mandatory

Every commit must carry a `Signed-off-by` trailer, after the
`Co-authored-by` one:

```
Signed-off-by: Name <email>
```

The name and the email must match the commit committer identity, which is
`asl@launay.org` in this repository, a verified UID of the signing key.
GitHub rejects a signed commit whose email is not a UID of the key.

### Pull requests

`master` takes pull requests only. Push a branch, open a pull request, and
merge it once `checks`, `tests`, and `dco` are green. Direct pushes are
rejected and force pushes are disabled.

### Commit messages

- Subject in the imperative mood, no trailing period.
- Body wrapped at 72 columns, explaining the problem and the reason.
- One logical change per commit.
