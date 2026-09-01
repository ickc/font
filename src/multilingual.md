---
# Metadata used by both Quarto and vanilla Pandoc.
title: "Multilingual font sample"
lang: en
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
      - ../config/md-links.lua
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
    output-file: multilingual-typst.pdf
    filters:
      - ../config/md-links.lua
    link-base: https://font.kolen.dev
    mainfont: TeX Gyre Schola
    mathfont: TeX Gyre Schola Math
    codefont: JetBrains Mono
    include-in-header: ../config/fonts.typ
---

# Text samples

[וַיֹּ֥אמֶר אֱלֹהִים יְהִ֣י א֑וֹר וַֽיְהִי־אֽוֹר׃]{lang="he" dir="rtl"}

[καὶ εἶπεν ὁ θεός Γενηθήτω φῶς. καὶ ἐγένετο φῶς.]{lang="el"}

And God said, Let there be light: and there was light.

[神說：「要有光」，就有了光。]{lang="zh-Hant"}
