---
# Metadata used by both Quarto and vanilla Pandoc.
title: "Multilingual font sample"
lang: en

# The document's own languages, one per Unicode script. config/auto-lang.lua
# reads this map and tags each run of a mapped script, so the body below is
# plain text. A script is not a language -- Han alone cannot tell zh-Hant from
# ja -- which is why the choice is made here rather than by the filter.
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
        href: multilingual-mathjax.html
        icon: filetype-html
      - pdf
      - typst
  mathjax4-html:
    output-file: multilingual-mathjax.html
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
        href: multilingual.html
        icon: filetype-html
      - pdf
      - typst
  pdf:
    output-file: multilingual-lualatex.pdf
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
      # For the one span below that overrides the `auto-lang` map. Pandoc turns
      # every distinct `lang` into a distinct babel language, so an override
      # needs its own entry here even when the face is the same.
      chinese-hans: NotoSansCJKtc
  typst:
    output-file: multilingual-typst.pdf
    filters:
      - ../config/auto-lang.lua
      - ../config/absolute-links.lua
    link-base: https://font.kolen.dev
    mainfont: TeX Gyre Schola
    mathfont: TeX Gyre Schola Math
    codefont: JetBrains Mono
    include-in-header: ../config/fonts.typ
---

# Text samples

Nothing below is marked up. Each line is plain text, and the language spans
that reach the four writers are added from the `auto-lang` map above.

וַיֹּ֥אמֶר אֱלֹהִים יְהִ֣י א֑וֹר וַֽיְהִי־אֽוֹר׃

καὶ εἶπεν ὁ θεός Γενηθήτω φῶς. καὶ ἐγένετο φῶς.

And God said, Let there be light: and there was light.

神說：「要有光」，就有了光。

Runs inside a sentence are found the same way: 神說 was rendered
καὶ εἶπεν ὁ θεός by the Septuagint, from the Hebrew וַיֹּ֥אמֶר אֱלֹהִים.

# Overriding the map

A script carries no more than a script: Han is written by Traditional Chinese,
Simplified Chinese and Japanese alike, and no rule can tell them apart. Where
the language is not the one the map names, write it out. The filter leaves that
span --- and everything inside it --- alone:

[学而时习之，不亦说乎？人不知而不愠，不亦君子乎？]{lang="zh-Hans"}

That line is Simplified. Noto Sans CJK TC carries its glyphs, so the override
changes what the document says about the text rather than which face draws it.
