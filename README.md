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
pixi run setup
pixi run build
pixi run pandoc-build
```

`setup` is an explicit, one-time machine setup. It installs desktop fonts into
the conventional per-user font
directory (`~/.local/share/fonts/font-kolen-dev` on Linux or
`~/Library/Fonts/font-kolen-dev` on macOS) and stages browser fonts below
`src/assets/fonts/`. It also stages the small `selnolig` package needed by
minimal TeX Live installations. Pixi sets `TYPST_FONT_PATHS` to the per-user
font directory, so Typst does not depend on platform font-cache behaviour.

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

Each Quarto source declares all four outputs in its own `format` map. The
`mathjax4-html` key comes from the small local extension under
`src/_extensions/mathjax4/`; it exists solely so the source can list two HTML
formats without duplicate YAML keys. `output-file` gives each format a stable
name, and format-specific `format-links` generate the sibling-download links
in both HTML variants.

LuaLaTeX uses Pandoc's `babelfonts` map, while Typst uses its `codefont`
variable and Unicode coverage rules. The matching vanilla-Pandoc defaults live
under `config/`. This retains one Markdown source without loading LaTeX's
heavier `luatexja` CJK stack.

## Adding documents

Add another `.md` file directly under `src/`, copy the `format` and
`format-links` maps from `src/index.md`, and adjust its four `output-file`
basenames. Both `pixi run build` and the Makefile discover source files
automatically. Reserve names ending in `-mathjax`, `-lualatex`, and `-typst`
for generated files.

The original root-level `sample.md` supplied with the template remains in
place unchanged. The runnable site source is `src/index.md`, because the
existing Quarto project root and output directory are both under `src/`.

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

LuaLaTeX itself must be installed by the host TeX Live distribution. The build
does not attempt to replace the operating system's TeX Live installation.
