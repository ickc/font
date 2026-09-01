// Pandoc 3.8's Typst writer does not preserve Span attributes. Restrict each
// family to its Unicode script so TeX Gyre Schola remains the Latin face.
#show regex("\\p{Script=Greek}"): set text(font: "SBL Greek")
#show regex("\\p{Script=Hebrew}"): set text(font: "SBL Hebrew", dir: rtl)
#show regex("[\\p{Script=Han}\\p{Script=Hiragana}\\p{Script=Katakana}\\p{Bopomofo}]"): set text(font: "Noto Sans CJK TC")
