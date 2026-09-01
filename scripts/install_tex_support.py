#!/usr/bin/env python3
"""Stage the small TeX package assumed by Pandoc's LuaLaTeX template."""

from __future__ import annotations

import hashlib
import io
import os
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(os.environ.get("PIXI_PROJECT_ROOT", Path(__file__).resolve().parents[1]))
DESTINATION = ROOT / ".cache" / "texmf" / "tex" / "luatex" / "selnolig"
# mirrors.ctan.org redirects to whichever mirror is nearest, and not every one
# of them presents a chain this Python can verify. install_fonts.py already
# names a fallback for exactly that reason. The redirector stays first, backed
# by two named mirrors serving the same bytes; all three are verified against
# the digest below, so a bad one fails over rather than through.
URLS = [
    "https://mirrors.ctan.org/macros/luatex/latex/selnolig.zip",
    "https://ctan.math.illinois.edu/macros/luatex/latex/selnolig.zip",
    "https://ftp.fau.de/ctan/macros/luatex/latex/selnolig.zip",
]
SHA256 = "83d15aadb1c2d354e589290ef5c5300d2becbfb9b5fa254b4754b9e86cd31291"


def fetch() -> bytes:
    errors: list[str] = []
    for url in URLS:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "font-pattern/0.1"})
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = response.read()
            actual = hashlib.sha256(payload).hexdigest()
            if actual != SHA256:
                raise RuntimeError(f"SHA-256 was {actual}, expected {SHA256}")
            return payload
        except Exception as error:  # report every mirror before failing
            errors.append(f"{url}: {error}")
    raise SystemExit("Could not download selnolig\n  " + "\n  ".join(errors))


def main() -> None:
    payload = fetch()
    DESTINATION.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for member in archive.namelist():
            if member.endswith((".sty", ".lua")):
                target = DESTINATION / Path(member).name
                target.write_bytes(archive.read(member))
    print(f"Staged selnolig in {DESTINATION}")


if __name__ == "__main__":
    main()
