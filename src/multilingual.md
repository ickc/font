---
# Metadata used by both Quarto and vanilla Pandoc.
title: "Multilingual font sample"
lang: en

# The document's own languages, one per Unicode script. `pixi run format` reads
# this map and writes the language spans in the body below into this file; the
# render recipes never see it. A script is not a language -- Han alone cannot
# tell zh-Hant from ja -- which is why the choice is made here, per document.
#
# The map stays after formatting rather than being consumed. Re-running the
# formatter cannot change a span that already carries a `lang`, so the result
# is frozen either way, and keeping the map means CI's `format-check` re-runs
# the algorithm against the committed result on every push.
auto-lang:
  Hebrew: he
  Greek: el
  Han: zh-Hant
toc: true
toc-depth: 3

# Quarto-only render recipes. Vanilla Pandoc ignores this `format` map and uses
# the four explicit defaults files under ../config/ through the root Makefile.
format:
  html:
    output-file: multilingual.html
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
        href: multilingual-mathjax.html
        icon: filetype-html
      - pdf
      - typst
  mathjax4-html:
    output-file: multilingual-mathjax.html
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
        href: multilingual.html
        icon: filetype-html
      - pdf
      - typst
  pdf:
    output-file: multilingual-lualatex.pdf
    filters:
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
      # For the one span below that overrides the `auto-lang` map. Pandoc turns
      # every distinct `lang` into a distinct babel language, so an override
      # needs its own entry here even when the face is the same.
      chinese-hans: NotoSansCJKtc
  typst:
    output-file: multilingual-typst.pdf
    filters:
      - ../config/absolute-links.lua
    link-base: https://font.kolen.dev
    mainfont: TeX Gyre Schola
    mathfont: TeX Gyre Schola Math
    codefont: JetBrains Mono
    include-in-header: ../config/fonts.typ
---

# Text samples

Every span below was written into this file by `pixi run format`, from lines
that were typed as plain text. Nothing runs at render time: what the four
recipes read is the ordinary Pandoc markup checked in here, which is also what
a reviewer reads in the diff.

[וַיֹּ֥אמֶר אֱלֹהִים יְהִ֣י א֑וֹר וַֽיְהִי־אֽוֹר׃]{dir="rtl" lang="he"}

[καὶ εἶπεν ὁ θεός Γενηθήτω φῶς. καὶ ἐγένετο φῶς]{lang="el"}.

And God said, Let there be light: and there was light.

[神說：「要有光」，就有了光。]{lang="zh-Hant"}

Runs inside a sentence are found the same way: [神說]{lang="zh-Hant"} was rendered
[καὶ εἶπεν ὁ θεός]{lang="el"} by the Septuagint, from the Hebrew [וַיֹּ֥אמֶר אֱלֹהִים]{dir="rtl" lang="he"}.

# Overriding the map

A script carries no more than a script: Han is written by Traditional Chinese,
Simplified Chinese and Japanese alike, and no rule can tell them apart. Where
the language is not the one the map names, write it out. The formatter leaves a
span that already carries a `lang` --- and everything inside it --- alone:

[神说："要有光。"就有了光。]{lang="zh-Hans"}

That is the fourth line above again, written the way Simplified Chinese writes
it: one Han character differs, and the rest is punctuation convention. No rule
over the script can see either, so left to the map this line would have come
out labelled zh-Hant --- the right script, the wrong language.

Nothing else in the file marks the span as different from the ones the
formatter wrote, and nothing needs to: once formatting has run, its output is
markup like any other, editable in place. Noto Sans CJK TC carries the glyphs
either way, so the override changes what the document says about the text
rather than which face draws it.
