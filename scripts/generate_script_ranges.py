#!/usr/bin/env python3
"""Generate the Unicode script table that bin/auto-lang.lua reads."""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path


ROOT = Path(os.environ.get("PIXI_PROJECT_ROOT", Path(__file__).resolve().parents[1]))
DESTINATION = ROOT / "bin" / "script-ranges.lua"

# Pinned: a released version of the Unicode Character Database is immutable, so
# the generated table changes only when this line does. The checked-in output is
# what the build reads; nothing downloads anything at render time.
VERSION = "15.0.0"
UCD = f"https://www.unicode.org/Public/{VERSION}/ucd/"
# The cache is per release, so raising VERSION fetches that release rather than
# relabelling the files an earlier one left behind under the same names.
CACHE = ROOT / ".cache" / "unicode" / VERSION
FILES = [
    "Scripts.txt",
    "ScriptExtensions.txt",
    "PropertyValueAliases.txt",
    "extracted/DerivedBidiClass.txt",
]

# Every script the database defines is generated, rather than a list chosen
# here. A script left out would not merely be unmappable: the filter would see
# its code points as neutral, and a Cherokee word between two Hebrew ones would
# be swallowed by the Hebrew run rather than ending it. Common and Inherited
# are not scripts and are exactly what the filter treats as neutral.
NOT_SCRIPTS = {"Common", "Inherited", "Unknown"}


def fetch(name: str) -> str:
    path = CACHE / name.rsplit("/", 1)[-1]
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(
            UCD + name, headers={"User-Agent": "font-pattern/0.1"}
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            path.write_bytes(response.read())
    return path.read_text(encoding="utf-8")


def records(text: str):
    """Yield (first, last, value) for each data line of a UCD file."""
    for line in text.splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        field, _, value = line.partition(";")
        first, _, last = field.strip().partition("..")
        low = int(first, 16)
        yield low, int(last, 16) if last else low, value.strip()


def merge(ranges: list[tuple[int, int]]) -> list[list[int]]:
    """Sort and coalesce ranges so the filter can binary-search them."""
    merged: list[list[int]] = []
    for low, high in sorted(ranges):
        if merged and low <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], high)
        else:
            merged.append([low, high])
    return merged


def render(name: str, ranges: list[list[int]]) -> str:
    body = ", ".join(f"{{0x{low:04X},0x{high:04X}}}" for low, high in ranges)
    return f"    {name} = {{{body}}},"


def render_flat(entries: list[tuple[int, int, str]], per_line: int = 4) -> list[str]:
    """One sorted table of every strong range, for a single binary search."""
    cells = [f'{{0x{low:04X},0x{high:04X},"{name}"}},' for low, high, name in entries]
    return [
        "    " + " ".join(cells[start : start + per_line])
        for start in range(0, len(cells), per_line)
    ]


def main() -> None:
    aliases = {}
    for line in fetch("PropertyValueAliases.txt").splitlines():
        fields = [field.strip() for field in line.split("#")[0].split(";")]
        if len(fields) >= 3 and fields[0] == "sc":
            aliases[fields[1]] = fields[2]

    # Script: the code point's own script.
    strong: dict[str, list[tuple[int, int]]] = {}
    # Script=Inherited: combining marks and the like, which UAX #24 gives the
    # script of the character they follow. They are not a script of their own,
    # so they are kept apart from `strong` rather than added to it.
    inherited: list[tuple[int, int]] = []
    for low, high, value in records(fetch("Scripts.txt")):
        if value not in NOT_SCRIPTS:
            strong.setdefault(value, []).append((low, high))
        elif value == "Inherited":
            inherited.append((low, high))
    names = sorted(strong)

    # Script_Extensions: code points that belong with scripts other than the one
    # their own Script property names -- 。 and 」 with Han, the Arabic-Indic
    # digits with Thaana. UAX #24 is what makes these follow their neighbours
    # instead of interrupting them.
    extensions: dict[str, list[tuple[int, int]]] = {}
    for low, high, value in records(fetch("ScriptExtensions.txt")):
        for code in value.split():
            name = aliases.get(code, code)
            if name not in NOT_SCRIPTS:
                extensions.setdefault(name, []).append((low, high))

    # A script is right-to-left when its own code points are bidi class R or AL.
    rtl_points: set[int] = set()
    for low, high, value in records(fetch("extracted/DerivedBidiClass.txt")):
        if value in {"R", "AL"}:
            rtl_points.update(range(low, high + 1))
    rtl = [
        name
        for name in names
        if any(
            point in rtl_points
            for low, high in strong[name]
            for point in range(low, high + 1)
        )
    ]

    # Sorted and coalesced across scripts, so the filter answers "which script,
    # if any, owns this code point" with one search rather than one per script.
    flat: list[tuple[int, int, str]] = []
    for name in names:
        for low, high in merge(strong[name]):
            flat.append((low, high, name))
    flat.sort()
    coalesced: list[tuple[int, int, str]] = []
    for low, high, name in flat:
        if coalesced and coalesced[-1][2] == name and low <= coalesced[-1][1] + 1:
            coalesced[-1] = (coalesced[-1][0], max(coalesced[-1][1], high), name)
        else:
            coalesced.append((low, high, name))

    lines = [
        "-- Generated by scripts/generate_script_ranges.py; do not edit.",
        f"-- Derived from the Unicode {VERSION} Character Database: Scripts.txt,",
        "-- ScriptExtensions.txt, PropertyValueAliases.txt and",
        "-- extracted/DerivedBidiClass.txt.",
        "",
        "return {",
        f'  version = "{VERSION}",',
        "  -- Every script the database names, so a document's `auto-lang` map",
        "  -- can be told from a typo.",
        "  names = { " + ", ".join(f"{name} = true" for name in names) + " },",
        "  -- Scripts written right to left.",
        "  rtl = { " + ", ".join(f"{name} = true" for name in rtl) + " },",
        "  -- Every code point whose Script property is a script rather than",
        "  -- Common or Inherited, as {first, last, script} sorted by first.",
        "  strong = {",
        *render_flat(coalesced),
        "  },",
        "  -- Code points whose Script is Inherited: they take the script of",
        "  -- the character before them rather than ending its run.",
        "  " + render("inherited", merge(inherited)).strip(),
        "  -- Code points whose Script_Extensions include this script.",
        "  ext = {",
        *(render(name, merge(extensions[name])) for name in sorted(extensions)),
        "  },",
        "}",
        "",
    ]
    DESTINATION.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {DESTINATION} from the Unicode {VERSION} database")


if __name__ == "__main__":
    main()
