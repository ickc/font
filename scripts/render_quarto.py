#!/usr/bin/env python3
"""Render every source document to the four Quarto artifacts."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = sorted((ROOT / "src").glob("*.md"))


def run(*arguments: str) -> None:
    subprocess.run(arguments, cwd=ROOT, check=True)


def main() -> None:
    if not SOURCES:
        raise SystemExit("No Markdown files found directly under src/")

    # The project render creates the website's canonical MathML pages and all
    # Quarto support assets. Subsequent single-file renders retain that output.
    run("quarto", "render", "src")

    variants = (
        (
            "html",
            "-mathjax.html",
            "config/html-mathjax.yaml",
            "includes/mathjax-schola.html",
        ),
        ("pdf", "-lualatex.pdf", "config/pdf-lualatex.yaml", None),
        ("typst", "-typst.pdf", "config/pdf-typst.yaml", "../config/fonts.typ"),
    )
    for source in SOURCES:
        for output_format, suffix, metadata, header in variants:
            arguments = [
                "quarto",
                "render",
                str(source.relative_to(ROOT)),
                "--to",
                output_format,
                "--output",
                source.stem + suffix,
                "--no-clean",
                "--metadata-file",
                metadata,
            ]
            if header:
                arguments.extend(("--include-in-header", header))
            if output_format == "pdf":
                # Quarto otherwise prefers a globally discovered TinyTeX over
                # the host TeX Live. Resolve the active Pixi-shell engine so
                # Quarto and vanilla Pandoc use the same installation.
                engine = shutil.which("lualatex")
                if not engine:
                    raise SystemExit("lualatex was not found; install TeX Live first")
                arguments.append(f"--pdf-engine={engine}")
            run(*arguments)
            rendered = source.parent / (source.stem + suffix)
            destination = ROOT / "src" / "docs" / rendered.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(rendered, destination)


if __name__ == "__main__":
    main()
