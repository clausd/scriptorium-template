# Sriptorium - code exploratorium for the Aedificium knowledge library

Python worked examples, models, and notebooks that produce figures and
demos for the notes kept in the sibling
[**aedificium**](https://github.com/clausd/aedificium-template) notebook. The
prose, lexicon, and PDFs live over there; the *code* that explores ideas or produces
figures for notes lives here.

This is the **open-source template**. Fork it, clone your fork next to
your aedificium checkout, and start writing.

## The two-repo pattern

```
your-workspace/
  aedificium/     # the library — notes/, lexicon/, pdfs/, assets/ (Bun UI)
  scriptorium/    # this repo   — code + notebooks that produce figures
```

They are **separate repos that know about each other** (no submodule).
Three connections:

1. **`#code:` tags in aedificium cards.** A note in aedificium points at
   a file here — e.g. `#code:examples/fisher_spectrum.py`. The tag is
   searchable in the UI and rendered as a copy/download/open-in-editor
   row on the card.
2. **Figures flow code → `aedificium/assets/`.** `aedificium.figure(fig,
   name)` saves a plot into the library's `assets/` and returns the
   `![…](assets/…)` markdown snippet for you to paste into a card. The
   card + figure are then auto-committed by the aedificium server; the
   code that made them stays here.
3. **Notebooks read from the library.** `aedificium.note(...)` and
   `aedificium.define(...)` render an aedificium card's prose or a
   lexicon definition inline in a notebook, so comprehension notebooks
   can embed the source material.

## Prerequisites

- Python ≥ 3.10. or newer
- [uv](https://github.com/astral-sh/uv) recommended (`brew install uv`),
  or plain `venv` + `pip`.
- The sibling aedificium checkout — use
  [aedificium-template](https://github.com/clausd/aedificium-template) if
  you don't have one.

## Setup

```bash
# Fork on GitHub first, then:
git clone git@github.com:clausd/scriptorium.git
cd scriptorium
uv venv && uv sync
# or: python -m venv .venv && . .venv/bin/activate && pip install -e .
```

If the aedificium library is not at `../aedificium`, tell scriptorium
where to find it:

```bash
export AEDIFICIUM_DIR=/path/to/aedificium
```

## The bridge

```python
from scriptorium import aedificium

# Render an aedificium note's prose inside a notebook
aedificium.note("2026-06-14-1954-statistical-view-curriculum")

# Render a lexicon definition
aedificium.define("fisher-information")

# Save a matplotlib figure into aedificium/assets/, get the markdown ref back
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([0, 1, 2], [0, 1, 4])
ref = aedificium.figure(fig, "my-figure")
print(ref)
# ![my-figure](assets/my-figure.png)  — paste into a card
```

Full API in `scriptorium/aedificium.py` (~150 lines, one file — read it).

## Conventions

- **Datasets stay out of git.** `data/`, `*.pt`, checkpoints are
  gitignored. Ship a `download.py` per dataset instead so anyone can
  reproduce the data.
- **One self-contained script or notebook per worked example.** Name it
  after the aedificium card it serves so the `#code:` tag is obvious.
- Either you or Claude may add code here — comprehension notebooks are
  yours; small utility scripts and worked examples are fair game.

## Layout

```
scriptorium/            the Python package (the aedificium bridge lives here)
examples/               worked scripts
notebooks/              Jupyter notebooks that read from aedificium
data/                   datasets (gitignored)
```

## GitHub setup

```bash
git remote set-url origin git@github.com:clausd/scriptorium.git
git push -u origin main
```

## License

MIT. Adapt freely.

## Credits

Original concept and implementation by
[Claus Dahl](https://github.com/clausd). Sibling of
[aedificium](https://github.com/clausd/aedificium-template).
