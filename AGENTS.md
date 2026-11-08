# AGENTS.md

Guidance for agents working in this repository.

## Project

`make_demo.py` writes the animated terminal SVG used by the euromillions
README. It builds the document in memory, then writes it to the path given
on the command line, or to `demo.svg`.

- Standard library only. Do not add a dependency.
- SMIL for the animation. No JavaScript, no media player, no GIF.
- The draw values, the colours, and the layout are constants at the top.

Run it with:

```
python3 make_demo.py OUTPUT.svg
```

## Tests

The suite uses `unittest` and needs `ruff`:

```
ruff check .
python3 -m py_compile make_demo.py test_make_demo.py
python3 -m unittest -v
```

CI runs all three, and the tests assert that the generated document is
well-formed XML, that it animates, that both draws are present, and that
the palette constants appear.

## Code conventions

- Python 3.8 or later, standard library only.
- Four spaces, double quotes.
- `ruff check` must pass with no finding.
- Keep the generated SVG valid when rendered as an `<img>`: no script, no
  external resource.

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
merge it once `checks` and `dco` are green. Direct pushes are rejected and
force pushes are disabled.

### Commit messages

- Subject in the imperative mood, no trailing period.
- Body wrapped at 72 columns, explaining the problem and the reason.
- One logical change per commit.
