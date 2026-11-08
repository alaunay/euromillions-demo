# euromillions-demo

Generates `demo.svg`, the animated terminal shown in the
[euromillions](https://github.com/alaunay/euromillions) README.

The animation is declarative SVG (SMIL): a plain image for every browser,
no JavaScript, no media player. Python standard library only.

## Usage

```console
$ python3 make_demo.py OUTPUT.svg
$ python3 make_demo.py            # writes demo.svg here
```

The parent directory of the target is created when needed. The output is
deterministic: same constants, same bytes.

For the euromillions repository:

```console
$ git clone https://github.com/alaunay/euromillions-demo.git
$ python3 euromillions-demo/make_demo.py euromillions/assets/demo.svg
```

The draw values and the palette are constants at the top of `make_demo.py`.

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
