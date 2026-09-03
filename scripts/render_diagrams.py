#!/usr/bin/env python3
"""Render every mermaid block in ``src/*.md`` into ``src/diagrams/``.

Two artifacts stand behind each diagram, and only one of them is in the
repository, because only one of them costs anything to make:

  ``.svg``  from mermaid-cli, which is Chrome. **Checked in.** Mermaid has no
            renderer that is not a browser -- it measures every label with
            ``getBBox()`` and lays the diagram out from what the browser answers
            -- so drawing one means running Chrome and fetching a pinned package
            from npm. Putting that in ``pixi run build`` would make a browser and
            a network fetch dependencies of the site on every machine that
            renders it, to redraw pictures that change about as often as the
            prose around them. ``bin/script-ranges.lua`` is the same trade made
            the same way.

            Its labels are real SVG ``<text>`` rather than mermaid's default HTML
            ``<foreignObject>``, because a foreign object is HTML and only a
            browser can draw it -- Typst warns and renders nothing at all. The
            family is named in the config below, and Chrome must be able to find
            it: the box widths in the SVG are measurements of TeX Gyre Schola, so
            the file is only self-consistent on a machine where ``pixi run
            setup`` has installed it.

  ``.pdf``  from typst, for LuaLaTeX, which cannot read SVG without shell-escape
            and Inkscape. **Derived at build time, and gitignored.** It is a pure
            function of the checked-in SVG, and typst is already pinned here as a
            PDF engine -- so making one needs no browser, no npm and no network,
            which is the whole reason the SVG is checked in and none of which
            applies to it. Deriving it rather than drawing it a second time is
            also what stops the two pictures from disagreeing, and it embeds a
            real CID-keyed subset where Chrome's own PDF export writes Type 3
            glyphs.

            The Makefile derives it with a pattern rule and Quarto with a
            ``pre-render``, both by calling ``--pdf`` here, so the typst
            invocation has one definition rather than three.

Each SVG is named for the SHA-1 of its diagram source, which is most of the
staleness story: an edited diagram asks for a name that does not exist yet, and
``config/mermaid.lua`` stops the render with a message saying to run this. The
name is computed from the code block's text as *pandoc* parses it -- the sources
are read through ``pandoc --to json`` rather than with a regular expression --
so the two sides cannot disagree about what was hashed.

The rest of the story is that a drawing depends on how it was drawn as well as
on what it says. The name cannot carry that: ``config/mermaid.lua`` derives the
same name and knows nothing about the renderer. So the settings below are
recorded in ``src/diagrams/renderer.json`` beside the drawings, and a change to
any of them -- the pinned mermaid-cli, the theme, the family, the background --
makes every checked-in SVG a picture of the old settings. ``--check`` says so
and this redraws all of them, where hashing the source alone would have called
them current forever.

Usage:

    python scripts/render_diagrams.py             # draw missing SVGs, derive PDFs
    python scripts/render_diagrams.py --check     # report on the SVGs, change nothing
    python scripts/render_diagrams.py --pdfs      # derive the PDFs only, no browser
    python scripts/render_diagrams.py --pdf FILE  # derive one PDF from one SVG
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterator, Sequence

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "src"
DIAGRAMS = SOURCES / "diagrams"

# The settings the drawings beside it were made with, written out in full rather
# than hashed so that `git diff` says what changed. Checked in with them.
STAMP = DIAGRAMS / "renderer.json"

# Pinned exactly rather than by range: this writes a file that is committed, so
# a renderer that moved under it would show up as an unexplained redrawing of
# every diagram in the repository.
MERMAID_CLI = "@mermaid-js/mermaid-cli@11.17.0"

NAME_LENGTH = 12

# The three settings that matter, and why.
#
#   htmlLabels     off. Mermaid's default label is an HTML <foreignObject>,
#                  which is HTML embedded in SVG: only a browser draws it, so
#                  Typst renders an empty picture and warns. Off, labels are
#                  SVG <text>, which every consumer here can read.
#   fontFamily     the whole point. It reaches the SVG as a `font-family` in the
#                  stylesheet mermaid writes into the file, which is what the
#                  browser, Typst and the derived PDF each resolve in their own
#                  way -- and what Chrome measures the label boxes with.
#   theme          `neutral`, whose palette is flat greys that sit under Schola
#                  rather than competing with it, and which reads on paper.
CONFIG = {
    "theme": "neutral",
    "htmlLabels": False,
    "flowchart": {"htmlLabels": False, "curve": "basis"},
    "fontFamily": "TeX Gyre Schola",
    "themeVariables": {"fontFamily": "TeX Gyre Schola", "fontSize": "16px"},
}

# White rather than transparent, and it is a decision about the site rather than
# about the diagram. The page has a light and a dark theme, the SVG's own colours
# are fixed at render time, and dark labels on the dark theme would be
# unreadable. A white plate reads under both, and costs nothing in a PDF, whose
# page is white already.
BACKGROUND = "white"

# `#set page(width: auto, ...)` crops the page to the picture, so the PDF has the
# SVG's own dimensions and \includegraphics needs no scaling instructions.
#
# Written beside the SVG rather than in a temporary directory, because Typst
# refuses to read outside the root it derives from its input file: from a
# temporary directory, a path to the SVG resolves against that directory and is
# simply not found.
CROP = '#set page(width: auto, height: auto, margin: 0pt, fill: none)\n#image("{svg}")\n'


def code_blocks(document: Path) -> Iterator[str]:
    """Yield the text of every mermaid code block in ``document``.

    Pandoc's own reader decides what a code block is and what its text contains,
    so that the hash computed here is the hash ``config/mermaid.lua`` computes
    from the same block.
    """
    parsed = subprocess.run(
        ["pandoc", "--from", "markdown", "--to", "json", str(document)],
        capture_output=True,
        text=True,
        check=True,
    )

    def walk(node: object) -> Iterator[str]:
        if isinstance(node, dict):
            if node.get("t") == "CodeBlock":
                (_, classes, _), text = node["c"]
                if "mermaid" in classes:
                    yield text
                return
            yield from walk(list(node.values()))
        elif isinstance(node, list):
            for item in node:
                yield from walk(item)

    yield from walk(json.loads(parsed.stdout)["blocks"])


def name_for(code: str) -> str:
    return "mermaid-" + hashlib.sha1(code.encode()).hexdigest()[:NAME_LENGTH]


def draw(code: str, svg: Path) -> None:
    """Draw ``code`` into ``svg`` with mermaid-cli. Needs npx and Chrome."""
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        (work / "diagram.mmd").write_text(code, encoding="utf-8")
        (work / "config.json").write_text(json.dumps(CONFIG), encoding="utf-8")
        subprocess.run(
            [
                "npx", "--yes", MERMAID_CLI,
                "--input", str(work / "diagram.mmd"),
                "--output", str(svg),
                "--configFile", str(work / "config.json"),
                "--backgroundColor", BACKGROUND,
                # Every diagram is inlined into one page, so the id mermaid
                # scopes its stylesheet to has to be unique per diagram. The
                # artifact name already is.
                "--svgId", svg.stem,
            ],
            check=True,
        )


def derive(svg: Path) -> Path:
    """Derive the PDF beside ``svg`` with typst. Needs neither a browser nor a network."""
    pdf = svg.with_suffix(".pdf")
    crop = svg.with_name(f".{svg.stem}.typ")
    crop.write_text(CROP.format(svg=svg.name), encoding="utf-8")
    try:
        subprocess.run(["typst", "compile", str(crop), str(pdf)], check=True)
    finally:
        crop.unlink()
    return pdf


def outdated(svg: Path) -> bool:
    """True when the PDF beside ``svg`` is missing or older than it."""
    pdf = svg.with_suffix(".pdf")
    return not pdf.exists() or pdf.stat().st_mtime < svg.stat().st_mtime


def settings() -> dict[str, object]:
    """Everything about *how* a diagram is drawn, as opposed to what it says."""
    return {"mermaid-cli": MERMAID_CLI, "background": BACKGROUND, "config": CONFIG}


def restamped() -> bool:
    """True when the drawings on disk were made with settings other than these."""
    try:
        return json.loads(STAMP.read_text(encoding="utf-8")) != settings()
    except (OSError, ValueError):
        return True


def wanted() -> dict[str, str]:
    """Every diagram the sources ask for, by artifact name."""
    diagrams: dict[str, str] = {}
    for document in sorted(SOURCES.glob("*.md")):
        for code in code_blocks(document):
            diagrams[name_for(code)] = code
    return diagrams


def main(argv: Sequence[str] = tuple(sys.argv[1:])) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="report which SVGs are missing, orphaned or drawn with old settings, and change nothing")
    mode.add_argument("--pdfs", action="store_true", help="derive every PDF from its checked-in SVG; needs no browser")
    mode.add_argument("--pdf", metavar="SVG", type=Path, help="derive one PDF from one SVG, for the Makefile's pattern rule")
    args = parser.parse_args(argv)

    # The one mode that reads no source document, so that a build never runs
    # pandoc over every source just to convert a picture it already has.
    if args.pdf:
        derive(args.pdf)
        return 0

    DIAGRAMS.mkdir(exist_ok=True)
    diagrams = wanted()

    # A drawing made with different settings is as stale as one made from a
    # different source, and its name does not say so -- the name is the hash of
    # the source alone, because `config/mermaid.lua` derives the same name and
    # cannot know about any of this. So every SVG is stale at once when the
    # stamp beside them does not match, and every one is redrawn.
    stale = restamped()

    # Only the SVGs are compared against the sources. A PDF never reaches the
    # repository, so it is neither something that can be missing nor something
    # that can be orphaned -- it is just rebuilt from whichever SVGs remain.
    missing = [name for name in diagrams if stale or not (DIAGRAMS / f"{name}.svg").exists()]
    # An SVG whose diagram was edited or deleted keeps answering to its old name
    # forever unless it is swept, and nothing else would ever notice it.
    orphans = sorted(p for p in DIAGRAMS.glob("*.svg") if p.stem not in diagrams)

    if args.check:
        if stale:
            print(
                f"stale renderer: {STAMP.relative_to(ROOT)} is missing or does not"
                " match this script's settings, so every drawing is one of the old ones",
                file=sys.stderr,
            )
        else:
            for name in missing:
                print(f"missing: {name}.svg", file=sys.stderr)
        for path in orphans:
            print(f"orphaned: {path.relative_to(ROOT)}", file=sys.stderr)
        if stale or missing or orphans:
            print("Run `pixi run render-diagrams`.", file=sys.stderr)
            return 1
        print(f"All {len(diagrams)} diagrams are rendered.")
        return 0

    if not args.pdfs:
        for name in missing:
            print(f"drawing {name}.svg")
            draw(diagrams[name], DIAGRAMS / f"{name}.svg")
        for path in orphans:
            print(f"removing {path.relative_to(ROOT)}")
            path.unlink()
            path.with_suffix(".pdf").unlink(missing_ok=True)
        # Last, so that an interrupted or failed run leaves the stamp saying the
        # drawings are the old ones -- which is true, and which the next
        # `--check` will say -- rather than claiming a redraw that did not finish.
        STAMP.write_text(json.dumps(settings(), indent=2) + "\n", encoding="utf-8")

    derived = [svg for svg in sorted(DIAGRAMS.glob("*.svg")) if outdated(svg)]
    for svg in derived:
        print(f"deriving {svg.stem}.pdf")
        derive(svg)

    if args.pdfs:
        print(f"{len(derived)} derived, {len(diagrams)} total.")
    else:
        print(f"{len(missing)} drawn, {len(derived)} derived, {len(orphans)} removed, {len(diagrams)} total.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
