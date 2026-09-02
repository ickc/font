# Font

A working, single-source pattern for documents containing English, Traditional
Chinese, polytonic Greek, Biblical Hebrew, mathematics, and code. Every Markdown
file in `src/` is rendered four ways — MathML HTML, MathJax 4 HTML, LuaLaTeX PDF,
and Typst PDF — by both Quarto and vanilla Pandoc, from one set of sources.

**<https://font.kolen.dev>** is the rendered site, and is the place to read this.
It is where the pattern demonstrates itself: the [multilingual][] and
[mathematics][] samples are the same Markdown shown in all four outputs.

The deployed stylesheets are a supported distribution: another site may link
`https://font.kolen.dev/assets/faces.css` rather than vendor the faces. What is
public and what it promises is [documented on the
site](https://font.kolen.dev/index.html#using-these-fonts-on-another-site).

The full introduction — how the two pipelines are wired, which file belongs to
which tool, where each font comes from, and how to add a document — is
[`src/index.md`](src/index.md), which renders as the site homepage.

```sh
pixi run setup   # one-time: install desktop fonts and TeX support
pixi run build   # Quarto site into src/docs/
pixi run serve   # preview it
```

[multilingual]: https://font.kolen.dev/multilingual.html
[mathematics]: https://font.kolen.dev/math.html
