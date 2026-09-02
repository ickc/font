#!/usr/bin/env python3
"""Format markdown files by normalizing their body through pandoc.

The body of each file is read and written back by pandoc, so the result is
whatever pandoc considers canonical. Filters given with ``-F`` run as part of
that round trip, which lets a filter rewrite the source rather than only the
rendered output.

YAML front matter is deliberately kept away from pandoc's *writer* and copied
through untouched. Pandoc parses metadata values as markdown and re-escapes
them on the way out, which corrupts Quarto configuration: a listing's
``contents: "*.md"`` comes back as ``contents: \\*.md``. It also sorts keys and
drops quoting. The only front matter change this tool makes is the one
requested by ``--derive-output-file``.

The reader still sees it. The front matter is handed to pandoc as a
``--metadata-file``, so a filter can read the document's own configuration,
and the body is converted without ``--standalone``, so none of it is written
back out. A filter that rewrites the source is otherwise blind to the very
metadata that tells it what to do.

Inputs may be files, directories, or glob patterns. A directory is expanded
with ``--pattern`` (default ``**/*.md``), so ``md_formatter.py src`` formats
every markdown file underneath it.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

DEFAULT_PATTERN = "**/*.md"

# --wrap=preserve keeps the author's semantic line breaks; reflowing them would
# bury real edits in unrelated rewrapping.
COMMON_ARGS: list[str] = [
    "--wrap=preserve",
    "--columns=120",
    "--markdown-headings=atx",
]

FRONT_MATTER_RE = re.compile(r"\A---\n(?P<meta>.*?\n)---\n(?P<body>.*)\Z", re.DOTALL)
NUMBERED_RE = re.compile(r"\A\d\d-(?P<name>.+)\Z")

# Pages whose filename is fixed by something other than this convention, and so
# carry no ``NN-`` prefix: ``index`` is the section landing page, and ``404`` is
# the not-found page, which Quarto renders to ``404.html`` at the project root
# for the web server to serve on any unmatched URL. Both are named by contract,
# so neither is ordered and neither may be renumbered.
UNNUMBERED_STEMS = frozenset({"index", "404"})


def split_front_matter(text: str) -> tuple[str | None, str]:
    """Return the front matter body (without delimiters) and the markdown body."""
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None, text
    return match.group("meta"), match.group("body")


def join_front_matter(meta: str | None, body: str) -> str:
    if meta is None:
        return body
    return f"---\n{meta}---\n\n{body}"


def derive_output_file(meta: str | None, path: Path) -> str | None:
    """Set ``output-file`` from the filename, dropping the ``NN-`` order prefix.

    The prefix orders the sidebar and section listings but must not reach the
    URL, so pages declare the name they render to. The extension is omitted so
    that Quarto appends the one belonging to each output format -- with it, a
    second format would render ``name.html.pdf``.
    """
    numbered = NUMBERED_RE.match(path.stem)
    if not numbered:
        return meta

    entry = f"output-file: {numbered.group('name')}"
    if meta is None:
        return entry + "\n"

    lines = meta.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("output-file:"):
            lines[index] = entry
            break
    else:
        after_title = next((i + 1 for i, l in enumerate(lines) if l.startswith("title:")), 0)
        lines.insert(after_title, entry)
    return "\n".join(lines) + "\n"


def filter_args(filters: Sequence[str]) -> list[str]:
    """Map each filter onto the pandoc flag matching its kind."""
    args: list[str] = []
    for name in filters:
        args.extend(["--lua-filter" if name.endswith(".lua") else "--filter", name])
    return args


def run_pandoc(body: str, args: argparse.Namespace, metadata: Path | None) -> str:
    command = [
        "pandoc",
        *COMMON_ARGS,
        "--from",
        args.source_format,
        "--to",
        args.format,
        *filter_args(args.filters),
    ]
    if metadata is not None:
        command.append(f"--metadata-file={metadata}")
    result = subprocess.run(command, input=body, capture_output=True, text=True, check=True)
    return result.stdout


def format_body(body: str, meta: str | None, args: argparse.Namespace) -> str:
    """Convert the body, with the document's front matter readable by filters."""
    if meta is None:
        return run_pandoc(body, args, None)
    with tempfile.TemporaryDirectory() as directory:
        metadata = Path(directory) / "metadata.yaml"
        metadata.write_text(meta, encoding="utf-8")
        return run_pandoc(body, args, metadata)


def format_file(path: Path, args: argparse.Namespace) -> bool:
    """Rewrite ``path`` in place. Returns True if the contents changed."""
    before = path.read_text()
    meta, body = split_front_matter(before)

    body = format_body(body, meta, args)
    if args.derive_output_file:
        meta = derive_output_file(meta, path)

    after = join_front_matter(meta, body)
    if after == before:
        return False
    if not args.check:
        path.write_text(after)
    return True


def misnamed(paths: Sequence[Path]) -> list[Path]:
    """Pages that are neither named by contract nor an NN- prefixed content page.

    Such a file still renders, but its position in the sidebar and in its
    section's listing would be decided by plain alphabetical order rather than
    by the numbering, so the convention is enforced rather than assumed.
    """
    return [p for p in paths if p.stem not in UNNUMBERED_STEMS and not NUMBERED_RE.match(p.stem)]


def resolve_paths(inputs: Sequence[str], pattern: str) -> list[Path]:
    """Expand files, directories, and glob patterns into a sorted file list."""
    paths: set[Path] = set()
    for raw in inputs:
        candidate = Path(raw)
        if candidate.is_dir():
            paths.update(p for p in candidate.glob(pattern) if p.is_file())
        elif candidate.is_file():
            paths.add(candidate)
        else:
            paths.update(p for p in Path().glob(raw) if p.is_file())
    return sorted(paths)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("inputs", nargs="+", metavar="PATH", help="files, directories, or glob patterns")
    parser.add_argument("-t", dest="format", default="markdown", help="pandoc output format (default: markdown)")
    parser.add_argument("-f", dest="source_format", default="markdown", help="pandoc input format (default: markdown)")
    parser.add_argument("-F", dest="filters", nargs="*", default=[], metavar="FILTER", help="filters passed to pandoc")
    parser.add_argument("--pattern", default=DEFAULT_PATTERN, help=f"glob used for directories (default: {DEFAULT_PATTERN})")
    parser.add_argument("--derive-output-file", action="store_true", help="set output-file from the NN- prefixed filename")
    parser.add_argument("--check", action="store_true", help="report files needing formatting instead of writing them")
    return parser.parse_args(argv)


def main(argv: Sequence[str] = tuple(sys.argv[1:])) -> int:
    args = parse_args(argv)

    paths = resolve_paths(args.inputs, args.pattern)
    if not paths:
        print(f"No files matched: {' '.join(args.inputs)}", file=sys.stderr)
        return 1

    if args.derive_output_file:
        offenders = misnamed(paths)
        if offenders:
            allowed = " or ".join(f"'{stem}.md'" for stem in sorted(UNNUMBERED_STEMS))
            print(f"Expected {allowed} or an 'NN-name.md' numbered page:", file=sys.stderr)
            for path in offenders:
                print(f"  {path}", file=sys.stderr)
            return 1

    changed = [path for path in paths if format_file(path, args)]

    if args.check:
        if changed:
            print("Needs formatting:", file=sys.stderr)
            for path in changed:
                print(f"  {path}", file=sys.stderr)
            return 1
        print(f"All {len(paths)} files are formatted.")
        return 0

    for path in changed:
        print(f"formatted {path}")
    print(f"{len(changed)} of {len(paths)} files changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
