---
title: "Multilingual font sample"
lang: en
toc: true
toc-depth: 3
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
    pdf-engine: lualatex
    latex-tinytex: false
    mainfont: TeX Gyre Schola
    mathfont: TeX Gyre Schola Math
    monofont: JetBrains Mono
    babelfonts:
      greek: Gentium
      hebrew: Ezra SIL
      chinese-hant: Noto Sans CJK TC
  typst:
    output-file: multilingual-typst.pdf
    mainfont: TeX Gyre Schola
    mathfont: TeX Gyre Schola Math
    codefont: JetBrains Mono
    include-in-header: ../config/fonts.typ
---

# Text samples

[וַיֹּ֥אמֶר אֱלֹהִים יְהִ֣י א֑וֹר וַֽיְהִי־אֽוֹר׃]{lang=he dir=rtl}

[καὶ εἶπεν ὁ θεός Γενηθήτω φῶς. καὶ ἐγένετο φῶς.]{lang=el}

And God said, Let there be light: and there was light.

[神說：「要有光」，就有了光。]{lang=zh-Hant}
