# Font

A working, single-source pattern for documents containing English, Traditional
Chinese, polytonic Greek, Biblical Hebrew, mathematics, and code. Every Markdown
file in `src/` is rendered four ways — MathML HTML, MathJax 4 HTML, LuaLaTeX PDF,
and Typst PDF — by both Quarto and vanilla Pandoc, from one set of sources.

**<https://font.kolen.dev>** is the rendered site, and is the place to read this.
It is where the pattern demonstrates itself: the [multilingual][], [mathematics][]
and [diagram][] samples are the same Markdown shown in all four outputs. Mermaid
diagrams come two ways --- a [Lua filter][diagram] that reaches all eight
renderings, and [Quarto's own machinery][diagram-quarto], which is less to set
up and reaches four.

The deployed stylesheets are a supported distribution: another site may link
`https://font.kolen.dev/assets/faces.css` rather than vendor the faces. What is
public and what it promises is [documented on the
site](https://font.kolen.dev/index.html#using-these-fonts-on-another-site).

The full introduction — how the two pipelines are wired, which file belongs to
which tool, where each font comes from, and how to add a document — is
[`src/index.md`](src/index.md), which renders as the site homepage.

```sh
pixi run setup         # one-time: install desktop fonts and TeX support
pixi run setup-chrome  # one-time: the headless browser the Quarto-native page needs
pixi run build         # Quarto site into src/docs/
pixi run serve         # preview it
```

`setup-chrome` is a separate step because it is a 262 MB download that only
[`src/mermaid-quarto.qmd`][diagram-quarto] needs. It is not optional for a whole-site
build, though: `build` renders every page, so without it the render stops at
`Chrome not found`.

[multilingual]: https://font.kolen.dev/multilingual.html
[mathematics]: https://font.kolen.dev/math.html
[diagram]: https://font.kolen.dev/mermaid.html
[diagram-quarto]: https://font.kolen.dev/mermaid-quarto.html
