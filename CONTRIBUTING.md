# Contributing

Development notes for `terminal-svg-demo`. The user-facing documentation
is in [README.md](README.md).

- [Development](#development)
- [Tests](#tests)
- [Translations](#translations)
- [Packaging](#packaging)
- [Releases](#releases)
- [Code scanning](#code-scanning)
- [Pull requests](#pull-requests)
- [Changelog](#changelog)

## Development

```console
$ python3 -m venv .venv
$ .venv/bin/pip install -e ".[dev]"
$ tools/build-locales.sh
```

`ruff` 0.17.4, `mypy`, and `coverage` are pinned in the `dev` extra.

## Tests

```console
$ .venv/bin/ruff check .
$ .venv/bin/ruff format --check .
$ .venv/bin/mypy src/terminal_svg_demo
$ .venv/bin/coverage run -m unittest discover -s tests
$ .venv/bin/coverage report
$ shellcheck tools/build-locales.sh .githooks/commit-msg
$ bats tests/shell
```

Coverage must stay at or above 90 percent. CI runs the commands on Python
3.12, the Python suite alone on 3.10 to 3.13, and fails when the committed
examples differ from a fresh generation.

## Translations

Msgids are the English strings in `src/`. Add a language by copying the
template, filling the `msgstr` entries, and building:

```console
$ cp po/terminal-svg-demo.pot po/de.po
$ $EDITOR po/de.po
$ tools/build-locales.sh
```

`tools/build-locales.sh` runs `msgfmt --check`, which rejects a
translation whose placeholders drift from the source. After changing a
msgid, regenerate the template:

```console
$ xgettext --language=Python --keyword=_ --output=po/terminal-svg-demo.pot \
    src/terminal_svg_demo/*.py
$ msgmerge -U po/fr.po po/terminal-svg-demo.pot
```

## Packaging

Both distributions build from the repository:

```console
$ dpkg-buildpackage -b -us -uc        # Debian, needs debhelper and dh-python
$ mkdir -p rpmbuild/SOURCES
$ git archive --format=tar.gz --prefix=terminal-svg-demo-1.0.0/ \
    --output=rpmbuild/SOURCES/terminal-svg-demo-1.0.0.tar.gz HEAD
$ rpmbuild -bb packaging/rpm/terminal-svg-demo.spec --define "_topdir $PWD/rpmbuild"
```

The Debian package keeps its catalogues inside the Python package; the
RPM keeps them in `/usr/share/terminal-svg-demo`. The program looks in
both places, so either layout translates. CI builds both and attaches
them to the run.

## Releases

Cut a tag to publish the packages:

```console
$ git tag v1.1.0
$ git push origin v1.1.0
```

`.github/workflows/release.yml` builds the `.deb` and the `.rpm`, attaches
both to the GitHub release, and dispatches the shared packages repository.
The repository carries `0.0.0` as the unreleased placeholder; the workflow
takes the version from the tag and injects it before building, so nothing
needs bumping. The dispatch needs `PACKAGES_TOKEN`, a token with write
access to `alaunay/packages`; without it the daily run of that repository
picks the release up.

## Code scanning

GitHub code scanning runs CodeQL on the Python code through the repository
default setup, and shows the shellcheck findings as a second tool.
ShellCheck has no SARIF writer, so `tools/shellcheck-sarif.py` converts its
JSON output and the `code-scanning` job uploads it.

## Pull requests

`master` only takes pull requests, and every pull request must:

- be GPG-signed, or GitHub rejects the push;
- carry `Co-authored-by` and `Signed-off-by` trailers, which the `dco`
  check enforces;
- pass `checks`, `tests`, and `dco`.

```console
$ git switch -c my-change
$ ...edit, commit, test...
$ git push -u origin my-change
$ gh pr create --fill
$ gh pr merge --squash --delete-branch
```

## Changelog

[`CHANGELOG.md`](CHANGELOG.md) is generated from the git history:

```console
$ python3 tools/changelog.py v0.0.1 --output CHANGELOG.md
```

The release workflow runs the same command for the new tag and uses the
output as the release notes. Commits carrying a Conventional Commits
prefix are grouped; the rest land under "Changes".
