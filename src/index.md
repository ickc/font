---
title: "Multilingual font sample"
lang: en
---

This page is authored once and rendered by Quarto and vanilla Pandoc. Download
or inspect the sibling [MathJax 4 HTML](index-mathjax.html),
[LuaLaTeX PDF](index-lualatex.pdf), and [Typst PDF](index-typst.pdf).

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
the web-oriented Noto Sans TC family) for Chinese, SBL Greek for Greek, SBL
Hebrew for Hebrew, TeX Gyre Schola Math for formulas, and JetBrains Mono for
code.
