# terminal-svg-demo

Render an animated terminal session as declarative SVG, for a README or a
documentation page.

The animation uses SMIL: a plain image for every browser, no JavaScript,
no media player, no GIF. Python standard library only.

Example of the output: the [euromillions](https://github.com/alaunay/euromillions)
README.

## Usage

```console
$ python3 make_demo.py SPEC.json OUTPUT.svg
$ python3 make_demo.py SPEC.json        # writes demo.svg here
```

The parent directory of the target is created when needed. The output is
deterministic: same spec, same bytes.

For the euromillions repository:

```console
$ git clone https://github.com/alaunay/terminal-svg-demo.git
$ python3 terminal-svg-demo/make_demo.py euromillions/assets/demo.json \
    euromillions/assets/demo.svg
```

## Spec

A JSON file. Only `sessions` is required; every other key falls back to a
default.

```json
{
  "title": "euromillions",
  "sessions": [
    {
      "command": "./euromillions.sh",
      "outputs": [
        {"label": "Numbers:", "value": "4 8 13 36 46", "color": "#4d6bff"},
        {"label": "Stars:", "value": "3 12", "color": "#eebb05"}
      ]
    }
  ],
  "colors": {
    "prompt": "#39ff14",
    "command": "#e6edf3",
    "label": "#9aa4b2"
  }
}
```

| Key | Default | Meaning |
| --- | --- | --- |
| `title` | `terminal` | text in the window title bar |
| `width` | `720` | viewport width |
| `sessions` | `[]` | commands, in order, each with its `outputs` |
| `colors.background` | `#0d1117` | window background |
| `colors.title_background` | `#161b22` | title bar |
| `colors.title_text` | `#8b949e` | title text |
| `colors.prompt` | `#3fb950` | `$` |
| `colors.command` | `#c9d1d9` | typed command and cursor |
| `colors.label` | `#8b949e` | output label |

Each output needs `label`, `value`, and its own `color`. The layout, the
typing speed, the pauses, and the height follow from the number of
sessions and outputs.

## Requirements

- Python 3.8 or later
- no third-party package

## Tests

Development needs `ruff`:

```console
$ ruff check .
$ python3 -m py_compile make_demo.py test_make_demo.py
$ python3 -m unittest -v
```

GitHub Actions runs the three on every push to `master` and on every pull
request, and checks the commit trailers on pull requests.

## Contributing

`master` only takes pull requests, and every pull request must:

- be GPG-signed, or GitHub rejects the push;
- carry `Co-authored-by` and `Signed-off-by` trailers, which the `dco`
  check enforces;
- pass the `checks` job, which runs ruff, the compile step, and the tests.

```console
$ git switch -c my-change
$ ...edit, commit, test...
$ git push -u origin my-change
$ gh pr create --fill
$ gh pr merge --squash --delete-branch
```

## License

[GPL-3.0](LICENSE), or <https://www.gnu.org/licenses/gpl-3.0.html>.
