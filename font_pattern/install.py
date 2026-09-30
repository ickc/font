"""Install pinned desktop fonts, and stage their browser counterparts.

What to fetch and where each file goes is data, in `fonts.toml` beside this file;
this module only knows how to download, verify, unpack and copy. It has no
dependencies outside the standard library except fontTools, and that only when a
staged file has to be recompressed into WOFF2 -- so installing desktop fonts,
which is all CI needs, runs on a bare `python3`.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import tomllib
import urllib.request
import zipfile
from importlib import resources
from pathlib import Path


def default_font_dir() -> Path:
    """The per-user font directory, which desktop applications and Typst search."""
    configured = os.environ.get("FONT_PATTERN_FONT_DIR")
    if configured:
        return Path(configured).expanduser()
    if platform.system() == "Darwin":
        return Path.home() / "Library" / "Fonts"
    if platform.system() == "Linux":
        data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        return data_home / "fonts"
    raise SystemExit("Only macOS and Linux are supported")


def default_cache_dir() -> Path:
    configured = os.environ.get("FONT_PATTERN_CACHE_DIR")
    if configured:
        return Path(configured).expanduser()
    cache_home = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return cache_home / "font-pattern"


def load_manifest(path: Path | None = None) -> dict:
    if path is None:
        text = resources.files("font_pattern").joinpath("fonts.toml").read_text(encoding="utf-8")
    else:
        text = path.read_text(encoding="utf-8")
    return tomllib.loads(text)["fonts"]


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def plain_name(name: str) -> str:
    """A manifest's file name, which must not point outside the directory it lands in."""
    if not name or name in {".", ".."} or "/" in name or "\\" in name:
        raise ValueError(f"{name!r} is not a plain file name")
    return name


def download(cache: Path, name: str, urls: list[str], sha256: str) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    destination = cache / plain_name(name)
    if destination.exists() and digest(destination) == sha256:
        return destination
    destination.unlink(missing_ok=True)
    errors: list[str] = []
    for url in urls:
        temporary = destination.with_name(destination.name + f".{os.getpid()}.part")
        temporary.unlink(missing_ok=True)
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "font-pattern/0.1"})
            with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as out:
                shutil.copyfileobj(response, out)
            actual = digest(temporary)
            if actual != sha256:
                raise RuntimeError(f"SHA-256 was {actual}, expected {sha256}")
            temporary.replace(destination)
            return destination
        except Exception as error:  # report every mirror before failing
            temporary.unlink(missing_ok=True)
            errors.append(f"{url}: {error}")
    raise RuntimeError("Could not download " + name + "\n  " + "\n  ".join(errors))


def entries(value: list) -> list[tuple[str, str | None]]:
    """Normalise manifest entries to (source, target name or None)."""
    out: list[tuple[str, str | None]] = []
    for item in value:
        if isinstance(item, str):
            out.append((item, None))
        else:
            out.append((item["from"], item.get("as")))
    return out


def resolve(source: str, downloaded: dict[str, Path], scratch: Path) -> Path:
    """A downloaded file, or a member of a downloaded zip (`archive.zip!member`)."""
    if "!" in source:
        archive, member = source.split("!", 1)
        with zipfile.ZipFile(downloaded[archive]) as bundle:
            return Path(bundle.extract(member, scratch))
    return downloaded[source]


def to_woff2(source: Path, destination: Path) -> None:
    try:
        from fontTools.ttLib import TTFont
    except ImportError as error:
        raise RuntimeError(
            f"{destination.name} is recompressed from {source.name} with fontTools, "
            "which is not installed (pip install fonttools brotli)"
        ) from error
    # Keep the source's own `head.modified` rather than stamping the time of
    # conversion, so the same inputs always produce the same bytes.
    font = TTFont(source, recalcTimestamp=False)
    font.flavor = "woff2"
    font.save(destination)
    font.close()


def place(source: Path, directory: Path, name: str | None) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / plain_name(name or source.name)
    if destination.suffix == ".woff2" and source.suffix != ".woff2":
        to_woff2(source, destination)
    else:
        shutil.copy2(source, destination)
    return destination


def install_font(name: str, spec: dict, font_dir: Path, web_dir: Path | None, cache: Path) -> None:
    downloaded = {
        item["name"]: download(cache, item["name"], item["urls"], item["sha256"])
        for item in spec["downloads"]
    }
    with tempfile.TemporaryDirectory() as temporary:
        scratch = Path(temporary)
        for source, target in entries(spec.get("install", [])):
            place(resolve(source, downloaded, scratch), font_dir, target)
        if web_dir is not None:
            for source, target in entries(spec.get("stage", [])):
                place(resolve(source, downloaded, scratch), web_dir, target)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="font-pattern", description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, help="a fonts.toml other than the bundled one")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list", help="list the fonts the manifest can install")

    install = commands.add_parser("install", help="install fonts into the desktop font directory")
    install.add_argument("fonts", nargs="+", help="font names from `font-pattern list`, or `all`")
    install.add_argument("--dir", type=Path, default=None,
                         help="desktop font directory (default: the per-user one, or $FONT_PATTERN_FONT_DIR)")
    install.add_argument("--web-dir", type=Path, default=None,
                         help="also stage browser fonts here (not staged unless given)")
    install.add_argument("--cache-dir", type=Path, default=None,
                         help="download cache (default: $XDG_CACHE_HOME/font-pattern, or $FONT_PATTERN_CACHE_DIR)")

    args = parser.parse_args(argv)
    manifest = load_manifest(args.manifest)

    if args.command == "list":
        width = max(map(len, manifest))
        for name, spec in manifest.items():
            print(f"{name:<{width}}  {spec.get('description', '')}")
        return

    names = list(manifest) if args.fonts == ["all"] else args.fonts
    unknown = [name for name in names if name not in manifest]
    if unknown:
        raise SystemExit(f"unknown font(s): {', '.join(unknown)}; see `font-pattern list`")
    font_dir = args.dir or default_font_dir()
    cache = args.cache_dir or default_cache_dir()
    for name in names:
        print(f"Installing {name} into {font_dir}")
        install_font(name, manifest[name], font_dir, args.web_dir, cache)
    if platform.system() == "Linux" and shutil.which("fc-cache"):
        subprocess.run(["fc-cache", "-f", str(font_dir)], check=True)
    print(f"Installed: {', '.join(names)}")


def run() -> None:
    try:
        main()
    except Exception as error:
        print(f"font installation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
