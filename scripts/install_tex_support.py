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
URL = "https://mirrors.ctan.org/macros/luatex/latex/selnolig.zip"
SHA256 = "83d15aadb1c2d354e589290ef5c5300d2becbfb9b5fa254b4754b9e86cd31291"


def main() -> None:
    request = urllib.request.Request(URL, headers={"User-Agent": "font-pattern/0.1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != SHA256:
        raise SystemExit(f"selnolig SHA-256 was {actual}, expected {SHA256}")
    DESTINATION.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for member in archive.namelist():
            if member.endswith((".sty", ".lua")):
                target = DESTINATION / Path(member).name
                target.write_bytes(archive.read(member))
    print(f"Staged selnolig in {DESTINATION}")


if __name__ == "__main__":
    main()
