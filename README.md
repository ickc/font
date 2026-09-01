# Reusable multilingual Pandoc + Quarto documents

This repository is a working, single-source pattern for documents containing
English, Traditional Chinese, polytonic Greek, Biblical Hebrew, mathematics,
and code. Every Markdown file in `src/` is rendered four ways by both Quarto
and vanilla Pandoc:

| Output | Math renderer / PDF engine |
|---|---|
| `name.html` | native MathML |
| `name-mathjax.html` | MathJax 4, `mathjax-schola` |
| `name-lualatex.pdf` | LuaLaTeX |
| `name-typst.pdf` | Typst |

Quarto publishes into `src/docs/`. The independent Makefile publishes the
same four artifacts into `pandoc-output/`.

## Quick start

```sh
pixi run download-fonts
pixi run build
pixi run pandoc-build
```

`download-fonts` installs desktop fonts into the conventional per-user font
directory (`~/.local/share/fonts/font-kolen-dev` on Linux or
`~/Library/Fonts/font-kolen-dev` on macOS) and stages browser fonts below
`src/assets/fonts/`. Pixi also sets `TYPST_FONT_PATHS` to that directory, so
Typst does not depend on platform font-cache behaviour.

To preview the Quarto website, run `pixi run serve`. To remove generated
outputs, run `pixi run clean`.

## Authoring convention

Use semantic language spans in otherwise ordinary Pandoc Markdown:

```markdown
[καὶ εἶπεν ὁ θεός]{lang=el}

[וַיֹּאמֶר אֱלֹהִים]{lang=he dir=rtl}

[神說：「要有光」。]{lang=zh-Hant}
```

The same markup becomes HTML `lang`/`dir` attributes and LaTeX
`\foreignlanguage` calls. Pandoc's Typst writer currently discards span
attributes, so `config/fonts.typ` selects the three non-Latin fonts by Unicode
script coverage. This is a Typst header rule, not an AST filter; no Lua filter
is required.

Font metadata lives in format-specific files under `config/`, not in every
source document. LuaLaTeX uses Pandoc's `babelfonts` map, while Typst uses its
`codefont` variable and Unicode coverage rules. This retains one Markdown
source without loading LaTeX's heavier `luatexja` CJK stack.

## Adding documents

Add another `.md` file directly under `src/`. `scripts/render_quarto.py` and
the Makefile discover it automatically. Reserve names ending in `-mathjax`,
`-lualatex`, and `-typst` for generated files.

## Font sources and licensing

- TeX Gyre Schola and TeX Gyre Schola Math come from CTAN (GUST Font License).
- Noto Sans CJK TC comes from the official Noto CJK repository (SIL OFL 1.1).
  Browser output uses Google Fonts' `Noto Sans TC` CDN family and local PDF
  output uses `Noto Sans CJK TC`.
- JetBrains Mono comes from the official v2.304 release (SIL OFL 1.1).
- SBL Greek and SBL Hebrew come directly from the Society of Biblical
  Literature.

The SBL fonts have a special EULA: free use and web embedding are limited to
non-commercial purposes; commercial use requires a license. The EULA also
forbids redistribution of modified versions, so this project deliberately
serves the original TTFs rather than converted WOFF2 files and deploys a copy
of the EULA beside them. Running an SBL download task installs the font and
therefore constitutes acceptance of that EULA. Do not deploy this pattern for
commercial use until you have obtained the required SBL license.

Generated font binaries and documents are ignored by Git. A deployment build
must run `pixi run download-fonts` before `pixi run build` so the web-font
assets are present in `src/docs/assets/fonts/`.

LuaLaTeX itself must be installed by the host TeX Live distribution. The build
stages the small `selnolig` package expected by Pandoc's default template, but
does not attempt to replace the operating system's TeX Live installation.
