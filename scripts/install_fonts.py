#!/usr/bin/env python3
"""Install pinned desktop fonts and stage their browser counterparts."""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(os.environ.get("PIXI_PROJECT_ROOT", Path(__file__).resolve().parents[1]))
CACHE = ROOT / ".cache" / "fonts"
WEB = ROOT / "src" / "assets"


def default_font_dir() -> Path:
    configured = os.environ.get("FONT_PATTERN_FONT_DIR")
    if configured:
        return Path(configured).expanduser()
    if platform.system() == "Darwin":
        return Path.home() / "Library" / "Fonts" / "font-kolen-dev"
    if platform.system() == "Linux":
        return Path.home() / ".local" / "share" / "fonts" / "font-kolen-dev"
    raise SystemExit("Only macOS and Linux are supported")


FONT_DIR = default_font_dir()


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def download(name: str, urls: list[str], sha256: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    destination = CACHE / name
    if destination.exists() and digest(destination) == sha256:
        return destination
    destination.unlink(missing_ok=True)
    errors: list[str] = []
    for url in urls:
        temporary = destination.with_suffix(destination.suffix + f".{os.getpid()}.part")
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
        except Exception as error:  # report all mirrors before failing
            temporary.unlink(missing_ok=True)
            errors.append(f"{url}: {error}")
    raise RuntimeError("Could not download " + name + "\n  " + "\n  ".join(errors))


def install(source: Path, name: str | None = None) -> Path:
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    destination = FONT_DIR / (name or source.name)
    shutil.copy2(source, destination)
    return destination


def stage(source: Path, name: str | None = None) -> Path:
    WEB.mkdir(parents=True, exist_ok=True)
    destination = WEB / (name or source.name)
    shutil.copy2(source, destination)
    return destination


TG_BASE = "https://mirrors.ctan.org/fonts"
TG_FALLBACK = "https://tex.org.uk/fonts"


def tex_gyre_schola() -> None:
    license_file = download(
        "GUST-FONT-LICENSE.txt",
        [f"{TG_BASE}/tex-gyre/doc/GUST-FONT-LICENSE.txt", f"{TG_FALLBACK}/tex-gyre/doc/GUST-FONT-LICENSE.txt"],
        "2bd69affc3da00715116f713f57eab9707e96daf3562ad0215987b15b9c16f73",
    )
    faces = {
        "texgyreschola-regular.otf": "935b82e25f56b1d1276ca82793205e8ce254fbb37ebd38bedf7388cef21fbf44",
        "texgyreschola-bold.otf": "988c7b2a0ff0eae77d1df3338751b3c47a5e759117734a375b8e7f9de80e698b",
        "texgyreschola-italic.otf": "2f45b8c394037951aaec73d947f0b0c3af715950f8f207c9f4290ba37a53a4d2",
        "texgyreschola-bolditalic.otf": "95f085da44c04817771f2a3a754b6eeb442b9a79e79f51dc3b0612e3cc0d75cc",
    }
    from fontTools.ttLib import TTFont

    for name, sha256 in faces.items():
        source = download(
            name,
            [f"{TG_BASE}/tex-gyre/opentype/{name}", f"{TG_FALLBACK}/tex-gyre/opentype/{name}"],
            sha256,
        )
        install(source)
        WEB.mkdir(parents=True, exist_ok=True)
        web_name = Path(name).with_suffix(".woff2").name
        font = TTFont(source)
        font.flavor = "woff2"
        font.save(WEB / web_name)
        font.close()
    install(license_file)
    stage(license_file)


def tex_gyre_schola_math() -> None:
    name = "texgyreschola-math.otf"
    source = download(
        name,
        [f"{TG_BASE}/tex-gyre-math/opentype/{name}", f"{TG_FALLBACK}/tex-gyre-math/opentype/{name}"],
        "fa33e0bc72f97c32ac1e943ea6a5a5a56c956ba54eb40e8904045800dae32304",
    )
    install(source)
    from fontTools.ttLib import TTFont

    WEB.mkdir(parents=True, exist_ok=True)
    font = TTFont(source)
    font.flavor = "woff2"
    font.save(WEB / "texgyreschola-math.woff2")
    font.close()


def noto_cjk_tc() -> None:
    base = "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans"
    faces = {
        "NotoSansCJKtc-Regular.otf": "dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4",
        "NotoSansCJKtc-Bold.otf": "3ee160e5015106e3ec1a394301df54fa9bbbf8a251519984aec5c0abc50840c0",
    }
    for name, sha256 in faces.items():
        install(download(name, [f"{base}/OTF/TraditionalChinese/{name}"], sha256))
    license_file = download(
        "Noto-CJK-LICENSE.txt",
        [f"{base}/LICENSE"],
        "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2",
    )
    install(license_file)
    print("Noto Sans TC browser files are supplied by Google Fonts; no local web copy is staged.")


def gentium() -> None:
    archive = download(
        "Gentium-7.000.zip",
        ["https://software.sil.org/downloads/r/gentium/Gentium-7.000.zip"],
        "313e64963ba27851356060a725d36ce01680e5c5c63f46e4b40f15741c043e21",
    )
    root = "Gentium-7.000"
    with zipfile.ZipFile(archive) as bundle, tempfile.TemporaryDirectory() as temporary:
        temp_dir = Path(temporary)
        for style in ("Regular", "Bold", "Italic", "BoldItalic"):
            ttf_member = f"{root}/Gentium-{style}.ttf"
            woff_member = f"{root}/web/Gentium-{style}.woff2"
            bundle.extract(ttf_member, temp_dir)
            bundle.extract(woff_member, temp_dir)
            install(temp_dir / ttf_member)
            stage(temp_dir / woff_member)
        license_member = f"{root}/OFL.txt"
        bundle.extract(license_member, temp_dir)
        install(temp_dir / license_member, "Gentium-OFL.txt")
        stage(temp_dir / license_member, "Gentium-OFL.txt")


def ezra_sil() -> None:
    archive = download(
        "EzraSIL-2.51-web.zip",
        ["https://software.sil.org/downloads/r/ezra/EzraSIL-2.51-web.zip"],
        "7c19544c173c91e6ac47f605dae2cfa7e61e428abdafe27cf3f225fec4406357",
    )
    root = "EzraSIL-2.51-web"
    with zipfile.ZipFile(archive) as bundle, tempfile.TemporaryDirectory() as temporary:
        temp_dir = Path(temporary)
        for member in (
            f"{root}/SILEOT.ttf",
            f"{root}/web/SILEOT.woff",
            f"{root}/Licenses.txt",
        ):
            bundle.extract(member, temp_dir)
        install(temp_dir / root / "SILEOT.ttf")
        stage(temp_dir / root / "web" / "SILEOT.woff")
        install(temp_dir / root / "Licenses.txt", "EzraSIL-Licenses.txt")
        stage(temp_dir / root / "Licenses.txt", "EzraSIL-Licenses.txt")


def jetbrains_mono() -> None:
    archive = download(
        "JetBrainsMono-2.304.zip",
        ["https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/JetBrainsMono-2.304.zip"],
        "6f6376c6ed2960ea8a963cd7387ec9d76e3f629125bc33d1fdcd7eb7012f7bbf",
    )
    with zipfile.ZipFile(archive) as bundle, tempfile.TemporaryDirectory() as temporary:
        temp_dir = Path(temporary)
        for style in ("Regular", "Bold", "Italic", "BoldItalic"):
            ttf_member = f"fonts/ttf/JetBrainsMono-{style}.ttf"
            woff_member = f"fonts/webfonts/JetBrainsMono-{style}.woff2"
            bundle.extract(ttf_member, temp_dir)
            bundle.extract(woff_member, temp_dir)
            install(temp_dir / ttf_member)
            stage(temp_dir / woff_member)
    license_file = download(
        "JetBrainsMono-OFL.txt",
        ["https://raw.githubusercontent.com/JetBrains/JetBrainsMono/v2.304/OFL.txt"],
        "30f0c136e3c88e422d0791acd97238870f9054a9729bc34cf2ff0d4ed8cac4ad",
    )
    install(license_file)
    stage(license_file)


INSTALLERS = {
    "tex-gyre-schola": tex_gyre_schola,
    "tex-gyre-schola-math": tex_gyre_schola_math,
    "noto-cjk-tc": noto_cjk_tc,
    "gentium": gentium,
    "ezra-sil": ezra_sil,
    "jetbrains-mono": jetbrains_mono,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("font", choices=[*INSTALLERS, "all"])
    args = parser.parse_args()
    selected = INSTALLERS if args.font == "all" else {args.font: INSTALLERS[args.font]}
    for name, installer in selected.items():
        print(f"Installing {name} into {FONT_DIR}")
        installer()
    if platform.system() == "Linux" and shutil.which("fc-cache"):
        subprocess.run(["fc-cache", "-f", str(FONT_DIR)], check=True)
    print(f"Installed: {', '.join(selected)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"font installation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
