---
title: "Multilingual font sample"
lang: en
toc: true
toc-depth: 3
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
      chinese-hant: Noto Sans CJK TC
  typst:
    output-file: index-typst.pdf
    mainfont: TeX Gyre Schola
    mathfont: TeX Gyre Schola Math
    codefont: JetBrains Mono
    include-in-header: ../config/fonts.typ
---

This page is authored once and rendered by Quarto and vanilla Pandoc. Quarto's
generated **Other Formats** section links to every sibling artifact.

# Text samples

[וַיֹּ֥אמֶר אֱלֹהִ֖ים יְהִ֣י א֑וֹר וַֽיְהִי־אֽוֹר׃]{lang=he dir=rtl}

[καὶ εἶπεν ὁ θεός· Γενηθήτω φῶς. καὶ ἐγένετο φῶς.]{lang=el}

And God said, “Let there be light,” and there was light.

[神說：「要有光」，就有了光。]{lang=zh-Hant}

# Math sample

The mass–energy relation is $E = mc^2$. A display equation exercises more of
the math face:

$$
\int_{-\infty}^{\infty} e^{-x^2}\,dx = \sqrt{\pi}.
$$

# Code sample

```python
def greeting(name: str) -> str:
    return f"Hello, {name}!"
```

# What to inspect

The text above should use TeX Gyre Schola for English, Noto Sans CJK TC (or
the web-oriented Noto Sans TC family) for Chinese, Gentium for Greek, Ezra SIL
for Hebrew, TeX Gyre Schola Math for formulas, and JetBrains Mono for code.
