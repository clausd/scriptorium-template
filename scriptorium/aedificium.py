"""Bridge from the *scriptorium* (this code lab) to the *aedificium* notebook.

The scriptorium is the writing-room beneath the library: where worked examples,
models, and notebooks are produced. The aedificium (a sibling git checkout) is
the library of finished notes, lexicon entries, and PDFs. This module lets code
and notebooks *read from* and *write figures back into* that library, so the
loop closes: code -> figure in assets/ -> a card embeds it -> a notebook can
re-quote the card.

Layout assumed (override with the AEDIFICIUM_DIR env var):

    prj/misc/
      aedificium/     # the notebook (notes/, lexicon/, pdfs/, assets/, ...)
      scriptorium/    # this repo

Typical use in a notebook::

    from scriptorium import aedificium
    aedificium.note("2026-06-14-1954-statistical-view-curriculum")   # show prose
    aedificium.define("fisher-information")                          # show a definition
    ref = aedificium.figure(fig, "fisher-spectrum")                  # save -> assets/
    print(ref)   # ![fisher-spectrum](assets/fisher-spectrum.png) — paste into a card
"""

from __future__ import annotations

import os
import re
from pathlib import Path

__all__ = ["root", "note", "define", "figure", "link", "search"]


# --------------------------------------------------------------------------- #
# Locating the library
# --------------------------------------------------------------------------- #
def root() -> Path:
    """Path to the aedificium repo. Override with $AEDIFICIUM_DIR."""
    env = os.environ.get("AEDIFICIUM_DIR")
    if env:
        p = Path(env).expanduser().resolve()
    else:
        # default: sibling directory next to this repo's root
        p = (Path(__file__).resolve().parents[2] / "aedificium").resolve()
    if not (p / "notes").is_dir():
        raise FileNotFoundError(
            f"aedificium library not found at {p!r}. "
            "Set the AEDIFICIUM_DIR environment variable to its path."
        )
    return p


# --------------------------------------------------------------------------- #
# Reading cards
# --------------------------------------------------------------------------- #
_TAG_RE = re.compile(r"(?<!\S)#[a-z][a-z0-9_]*(?::\S+)?")


def _strip_tags(text: str) -> str:
    """Remove inline machine tags (#bug, #key:value) the way the UI hides them."""
    cleaned = "\n".join(
        line for line in text.splitlines()
        # drop lines that are *only* tags; otherwise strip tags inline
        if _TAG_RE.sub("", line).strip() or not line.strip()
    )
    return _TAG_RE.sub("", cleaned).rstrip() + "\n"


def _read(path: Path, *, strip_tags: bool, display: bool):
    text = path.read_text(encoding="utf-8")
    if strip_tags:
        text = _strip_tags(text)
    if display:
        try:
            from IPython.display import Markdown, display as _disp  # type: ignore
            _disp(Markdown(text))
            return None
        except Exception:
            pass
    return text


def note(slug: str, *, strip_tags: bool = True, display: bool = True):
    """Load a note card from aedificium/notes/.

    `slug` may be the bare slug or the filename (with or without .md). In a
    notebook the markdown (incl. LaTeX) is rendered inline; otherwise the text
    is returned.
    """
    notes = root() / "notes"
    name = slug if slug.endswith(".md") else f"{slug}.md"
    path = notes / name
    if not path.exists():
        matches = sorted(notes.glob(f"*{slug}*.md"))
        if not matches:
            raise FileNotFoundError(f"no note matching {slug!r} in {notes}")
        path = matches[0]
    return _read(path, strip_tags=strip_tags, display=display)


def define(term: str, *, strip_tags: bool = True, display: bool = True):
    """Load a lexicon entry from aedificium/lexicon/<slug>.md."""
    lex = root() / "lexicon"
    name = term if term.endswith(".md") else f"{term}.md"
    path = lex / name
    if not path.exists():
        matches = sorted(lex.glob(f"*{term}*.md"))
        if not matches:
            raise FileNotFoundError(f"no lexicon entry matching {term!r} in {lex}")
        path = matches[0]
    return _read(path, strip_tags=strip_tags, display=display)


def search(query: str, limit: int = 20) -> list[str]:
    """Grep notes + lexicon for `query`; return relative paths (cheap helper)."""
    hits: list[str] = []
    base = root()
    for sub in ("notes", "lexicon", "pdfs"):
        for path in sorted((base / sub).glob("*.md")):
            try:
                if query.lower() in path.read_text(encoding="utf-8").lower():
                    hits.append(str(path.relative_to(base)))
            except OSError:
                continue
            if len(hits) >= limit:
                return hits
    return hits


# --------------------------------------------------------------------------- #
# Writing figures back into the library
# --------------------------------------------------------------------------- #
def figure(fig, name: str, *, fmt: str = "png", dpi: int = 144, **savefig) -> str:
    """Save a matplotlib figure into aedificium/assets/ and return a card ref.

    Returns the markdown image reference to paste into a card, e.g.
    ``![fisher-spectrum](assets/fisher-spectrum.png)``. The card and the figure
    then live in the *aedificium* repo (which the server auto-commits), while
    the code that made it stays here.
    """
    slug = re.sub(r"[^a-z0-9._-]+", "-", name.lower()).strip("-")
    assets = root() / "assets"
    assets.mkdir(exist_ok=True)
    out = assets / f"{slug}.{fmt}"
    savefig.setdefault("bbox_inches", "tight")
    fig.savefig(out, dpi=dpi, **savefig)
    return f"![{slug}](assets/{out.name})"


# --------------------------------------------------------------------------- #
# Links
# --------------------------------------------------------------------------- #
def link(slug: str, *, base_url: str = "http://localhost:8788") -> str:
    """A URL that opens the matching card in the running aedificium UI."""
    return f"{base_url}/?open={slug}"
