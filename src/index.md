---
# Metadata used by both Quarto and vanilla Pandoc.
title: "Reusable multilingual Pandoc + Quarto documents"
lang: en
toc: true
toc-depth: 3

# Quarto-only render recipes. Vanilla Pandoc ignores this `format` map and uses
# the four explicit defaults files under ../config/ through the root Makefile.
format:
  html:
    output-file: index.html
    html-math-method: mathml
    css: assets/fonts.css
    theme:
      light: flatly
      dark: darkly
    respect-user-color-scheme: true
    code-copy: true
    code-overflow: wrap
    email-obfuscation: javascript
    format-links:
      - text: MathJax 4 HTML
        href: index-mathjax.html
        icon: filetype-html
      - pdf
      - typst
  mathjax4-html:
    output-file: index-mathjax.html
    css: assets/fonts.css
    theme:
      light: flatly
      dark: darkly
    respect-user-color-scheme: true
    code-copy: true
    code-overflow: wrap
    email-obfuscation: javascript
    format-links:
      - text: MathML HTML
        href: index.html
        icon: filetype-html
      - pdf
      - typst
  pdf:
    output-file: index-lualatex.pdf
    pdf-engine: lualatex
    latex-tinytex: false
    mainfont: TeX Gyre Schola
    mathfont: TeX Gyre Schola Math
    monofont: JetBrains Mono
    babelfonts:
      greek: Gentium
      hebrew: Ezra SIL
      # Font filename stem: OSFONTDIR finds the Regular and Bold files.
      chinese-hant: NotoSansCJKtc
  typst:
    output-file: index-typst.pdf
    mainfont: TeX Gyre Schola
    mathfont: TeX Gyre Schola Math
    codefont: JetBrains Mono
    include-in-header: ../config/fonts.typ
---

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

## Examples

- [Multilingual text samples](multilingual.md)
- [Mathematics sample](math.md)

Quarto publishes into `src/docs/`. The independent Makefile publishes the
same four artifacts into `pandoc-output/`.

## Quick start

```sh
pixi run setup
pixi run build
pixi run pandoc-build
```

`setup` is an explicit, one-time machine setup. It installs desktop fonts
directly into the conventional per-user font directory
(`$XDG_DATA_HOME/fonts`, normally `~/.local/share/fonts`, on Linux;
`~/Library/Fonts` on macOS). Those parent directories—not a specially named
project subdirectory—are what make the fonts discoverable to desktop
applications. The Linux installer refreshes Fontconfig's cache. Pixi also sets
`TYPST_FONT_PATHS` to that directory so Typst's lookup is explicit. For
LuaLaTeX, `OSFONTDIR` exposes the same tree to fontspec; the LuaLaTeX recipes
use the `NotoSansCJKtc` filename stem so Regular and Bold resolve reliably.

Browser fonts are staged under `src/assets/`, which publishes them at
`https://font.kolen.dev/assets/`. The setup also downloads the pinned CTAN
`selnolig` package into `.cache/texmf`. Pandoc's LuaLaTeX template loads that
package when `lang` metadata is present, but minimal TeX Live installations may
not provide it. `scripts/activate.sh` prepends the project-local tree to TeX's
`.sty` and Lua-module searches while retaining their normal system paths.

`build`, `pandoc-build`, and `serve` never install anything. If setup has not
been run, rendering fails at the missing font or TeX dependency. To preview the
Quarto website after setup, run `pixi run serve`. To remove generated outputs,
run `pixi run clean`.

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

Each Quarto source declares all four outputs in its own `format` map. This map
is Quarto-specific; vanilla Pandoc reads the shared top-level metadata and
ignores `format`. The
`mathjax4-html` key comes from the small local extension under
`src/_extensions/mathjax4/`; it exists solely so the source can list two HTML
formats without duplicate YAML keys. `output-file` gives each format a stable
name, and format-specific `format-links` generate the sibling-download links
in both HTML variants.

LuaLaTeX uses Pandoc's `babelfonts` map, while Typst uses its `codefont`
variable and Unicode coverage rules. The four matching vanilla-Pandoc defaults
under `config/` are deliberately self-contained: each repeats its reader,
writer, table-of-contents, language, and renderer/engine settings so it can be
copied as a complete recipe. This retains one Markdown source without loading
LaTeX's heavier `luatexja` CJK stack.

## Which files belong to which tool

| Consumer | Files |
|---|---|
| Both | `src/*.md` content and shared metadata, `src/assets/fonts.css`, `config/fonts.typ`, `scripts/activate.sh`, font and TeX setup scripts |
| Quarto only | `src/_quarto.yml`, each source's `format` map, `src/_extensions/mathjax4/_extension.yml` |
| Vanilla Pandoc only | `Makefile`, the four `config/pandoc-*.yaml` defaults files |

`src/_extensions/mathjax4/mathjax-schola.html` is shared: Quarto reaches it
through the extension and the vanilla-Pandoc MathJax defaults file includes it
directly.

## Adding documents

Add another `.md` file directly under `src/`, copy the full Quarto `format` and
`format-links` maps from `src/index.md`, and adjust its four `output-file`
basenames. Do not factor the repeated map into shared metadata: keeping each
source self-contained makes every Quarto combination visible at the point of
use. Both `pixi run build` and the Makefile discover source files automatically.
Reserve names ending in `-mathjax`, `-lualatex`, and `-typst` for generated
files.

`src/index.md` is the canonical project introduction and site homepage. The
root `README.md` symlink makes the same source the repository README.

## Font sources and licensing

- TeX Gyre Schola and TeX Gyre Schola Math come from CTAN (GUST Font License).
- Noto Sans CJK TC comes from the official Noto CJK repository (SIL OFL 1.1).
  Browser output uses Google Fonts' `Noto Sans TC` CDN family and local PDF
  output uses `Noto Sans CJK TC`.
- Gentium 7.000 comes from SIL. It has comprehensive monotonic and polytonic
  Greek support. The desktop TTFs and official WOFF2 files are SIL OFL 1.1.
- Ezra SIL 2.51 comes from SIL. It is designed after the Biblia Hebraica
  Stuttgartensia and includes Biblical Hebrew points and cantillation. The
  desktop TTF and official WOFF file are SIL OFL 1.1.
- JetBrains Mono comes from the official v2.304 release (SIL OFL 1.1).

Gentium and Ezra SIL replace SBL Greek and SBL Hebrew. Besides removing the
non-commercial restriction, the pair has compatible scholarly, calligraphic
serif forms that sit naturally beside TeX Gyre Schola. The repository stages
SIL's official web-font files rather than modifying them.

Generated font binaries and documents are ignored by Git. Run `pixi run setup`
once on a new authoring or deployment machine; subsequent builds reuse the
installed and staged files.

LuaLaTeX itself must be installed by the host TeX Live distribution. Quarto's
`latex-tinytex: false` selects that host installation, and vanilla Pandoc finds
`lualatex` through `PATH`; no engine-selection wrapper is needed. The build does
not attempt to replace the operating system's TeX Live installation.
