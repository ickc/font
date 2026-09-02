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
    filters:
      - ../config/auto-lang.lua
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
    filters:
      - ../config/auto-lang.lua
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
    filters:
      - ../config/auto-lang.lua
      - ../config/absolute-links.lua
    link-base: https://font.kolen.dev
    pdf-engine: lualatex
    latex-tinytex: false
    # .github/tl_packages is the declared package set. Left on, Quarto reacts to
    # a log warning by installing babel-greek, whose greek.ldf then collides with
    # the `babelfont` setup below; without it babel uses its own el locale, which
    # is what every working build here has used.
    latex-auto-install: false
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
    filters:
      - ../config/auto-lang.lua
      - ../config/absolute-links.lua
    link-base: https://font.kolen.dev
    mainfont: TeX Gyre Schola
    mathfont: TeX Gyre Schola Math
    codefont: JetBrains Mono
    include-in-header: ../config/fonts.typ
---

This repository is a working, single-source pattern for documents containing
English, Traditional Chinese, polytonic Greek, Biblical Hebrew, mathematics,
and code. Every Markdown file in `src/` is rendered four ways by both Quarto
and vanilla Pandoc:

| Output              | Math renderer / PDF engine  |
|---------------------|-----------------------------|
| `name.html`         | native MathML               |
| `name-mathjax.html` | MathJax 4, `mathjax-schola` |
| `name-lualatex.pdf` | LuaLaTeX                    |
| `name-typst.pdf`    | Typst                       |

## Examples

- [Multilingual text samples](/multilingual.html)
- [Mathematics sample](/math.html)

Quarto publishes into `src/docs/`. The independent Makefile publishes the
same four artifacts into `pandoc-output/`.

## Quick start

``` sh
pixi run setup
pixi run build
pixi run pandoc-build
```

`setup` is an explicit, one-time machine setup. It installs desktop fonts
directly into the conventional per-user font directory
(`$XDG_DATA_HOME/fonts`, normally `~/.local/share/fonts`, on Linux;
`~/Library/Fonts` on macOS). Those parent directories---not a specially named
project subdirectory---are what make the fonts discoverable to desktop
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

Write plain text. A document says once, in its front matter, which language
each writing system stands for in it:

``` yaml
auto-lang:
  Hebrew: he
  Greek: el
  Han: zh-Hant
```

`config/auto-lang.lua` is loaded by all eight recipes and wraps every run of a
mapped script in the span an author would otherwise have written by hand:

``` markdown
[...]{lang=el}

[...]{lang=he dir=rtl}
```

Each writer therefore sees exactly what it saw when that markup was typed out:
HTML `lang` and `dir` attributes, LaTeX `\foreignlanguage` inside `\RL`, and
Typst `#text(lang: ...)`. `dir=rtl` is not configured anywhere; the filter takes
it from the bidirectional class the Unicode database gives the script.

Where a run begins and ends is a question the Unicode Character Database
already answers, so the filter asks it rather than guessing. A code point's
Script property starts and continues a run. Spaces, digits and ASCII
punctuation are neutral: they join a run only when it continues on the other
side of them, which keeps a Hebrew phrase whole without swallowing the space
that ends it. Code points that are formally Common but belong with particular
scripts --- the ideographic full stop U+3002 and the right corner bracket
U+300D, by their Script_Extensions --- join a run they merely touch. `config/script-ranges.lua` is that table, generated by
`scripts/generate_script_ranges.py` from a pinned release of the database and
checked in, so no build step downloads anything.

Nothing else in a document is touched: inline code, maths, and any span that
already carries a `lang` are left exactly as written, contents included.

### What automation cannot decide

A script is not a language. Han is written by Traditional Chinese, Simplified
Chinese and Japanese alike; Latin script says nothing at all about which
language it is writing. This is why the map is per document and explicit, and
why a hand-written span still wins --- `src/multilingual.md` demonstrates both.
Pandoc turns every distinct `lang` into a distinct babel language, so a span
that overrides the map needs its own `babelfonts` entry for the LuaLaTeX
recipes, even when the face does not change.

### Why one filter rather than three engine features

Each output format can do some of this alone, and none of them can do all of
it. In HTML, browsers apply the bidirectional algorithm to Hebrew whether or
not it is marked, and `@font-face` can be restricted by `unicode-range`; what
that cannot produce is the `lang` attribute itself, which is what a screen
reader, a spell checker and `assets/fonts.css` all read. In LuaLaTeX, babel's
`\babelprovide[onchar=ids fonts]{hebrew}` switches fonts by script and, with
`bidi=basic`, sets Hebrew right to left correctly --- verified here against the
same samples --- but it is LuaTeX-only and leaves the other three formats
untouched. Typst needs no help with fonts at all, for the reason below.

Doing it once in the AST is what makes the same source produce the same
semantics in all four outputs, and it puts a language in the document rather
than a font in a recipe.

Pandoc's Typst writer emits `lang` from a span but not `dir`, and drops the
script subtag, so `zh-Hant` reaches Typst as `zh`. Font selection there is
therefore still `config/fonts.typ`, which picks the three non-Latin faces by
Unicode script coverage. That is a Typst header rule rather than an AST filter,
and it would work even with no spans at all.

Cross-document links are written root-relative and pointing at the published
page: `/math.html`, not `math.md`. Neither tool infers an extension or a
directory, so the target in the source is the target in the output, and a
root-relative one is already correct in HTML on whatever origin serves it --
production and every branch preview each have their own. The four HTML recipes
therefore need nothing at all. Quarto additionally normalises `/math.html` to
`./math.html`, which also makes its HTML browsable straight off the filesystem.

PDF is the exception, and the only reason `config/absolute-links.lua` exists. A
PDF has no containing page, so a viewer has nothing to resolve a root-relative
URI against: the format leaves that to an optional document-level base URI which
browser viewers do not supply, and such a link is inert when clicked. The four
PDF recipes therefore load the filter and set `link-base` to the site the PDFs
are published on, and every root-relative target is expanded against it.
Absolute and protocol-relative targets are left alone.

One consequence worth knowing: the Makefile's HTML output keeps the
root-relative form, so `pandoc-output/index.html` navigates correctly when
served from a site root but not when opened as a local file. Those artifacts
exist to demonstrate the four recipes, and the site Quarto builds is the one
that gets published.

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
writer, table-of-contents, and renderer/engine settings so it can be copied as a
complete recipe. This retains one Markdown source without loading LaTeX's
heavier `luatexja` CJK stack.

A defaults file's `metadata:` block overrides the document's own front matter
rather than filling a gap in it, so it carries only what belongs to the recipe:
the fonts. Language stays with the document, where every source already declares
it for Quarto.

## Which files belong to which tool

| Consumer | Files |
|------------------------------------------------------------|------------------------------------------------------------|
| Both | `src/*.md` content and shared metadata, `src/assets/fonts.css`, `config/fonts.typ`, `config/auto-lang.lua`, `config/script-ranges.lua`, `config/absolute-links.lua`, `scripts/activate.sh`, font, TeX and Unicode setup scripts |
| Quarto only | `src/_quarto.yml`, each source's `format` map, `src/_extensions/mathjax4/_extension.yml` |
| Vanilla Pandoc only | `Makefile`, the four `config/pandoc-*.yaml` defaults files |

`src/_extensions/mathjax4/mathjax-schola.html` is shared: Quarto reaches it
through the extension and the vanilla-Pandoc MathJax defaults file includes it
directly.

## Adding documents

Add another `.md` file directly under `src/`, copy the full Quarto `format` and
`format-links` maps from `src/index.md`, and adjust its four `output-file`
basenames. Give it an `auto-lang` map if it contains a script other than the
one its `lang` names; without one the filter is a no-op. Do not factor the repeated map into shared metadata: keeping each
source self-contained makes every Quarto combination visible at the point of
use. Both `pixi run build` and the Makefile discover source files automatically.
Reserve names ending in `-mathjax`, `-lualatex`, and `-typst` for generated
files.

`src/index.md` is the canonical project introduction and site homepage. The
root `README.md` is a short pointer to it and to the rendered site. It is a
real file rather than a symlink to this one: the links here are relative to
`src/`, and GitHub resolves a symlinked README's relative links from the
repository root, where those targets do not exist.

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
