PANDOC ?= pandoc
OUTPUT_DIR := pandoc-output
# `src/*.md`, never `src/*.qmd`. The one .qmd here holds a Quarto executable
# cell, and pandoc does not merely ignore one -- its attribute parser rejects
# the dotless `{mermaid}`, the fence stops being a code block, and the diagram
# collapses into a run-on inline code span in the middle of the prose. Excluding
# it by glob is what keeps that out of these four artifacts. See
# src/mermaid-quarto.qmd, which documents the pattern it belongs to.
SOURCES := $(wildcard src/*.md)
NAMES := $(patsubst src/%.md,%,$(SOURCES))
HTML_MATHML := $(addprefix $(OUTPUT_DIR)/,$(addsuffix .html,$(NAMES)))
HTML_MATHJAX := $(addprefix $(OUTPUT_DIR)/,$(addsuffix -mathjax.html,$(NAMES)))
PDF_LUALATEX := $(addprefix $(OUTPUT_DIR)/,$(addsuffix -lualatex.pdf,$(NAMES)))
PDF_TYPST := $(addprefix $(OUTPUT_DIR)/,$(addsuffix -typst.pdf,$(NAMES)))

# Every staged file, not just the stylesheet that names them. `pixi run setup`
# stages the web fonts, and an HTML build succeeds without them, so the two can
# legitimately happen in either order; a target listing only fonts.css would
# then stay up to date while the fonts it names were never copied. The wildcard
# is re-expanded on every run, so a newly staged or replaced font becomes a
# prerequisite as soon as it exists.
ASSETS := $(wildcard src/assets/*)
STAGED_ASSETS := $(patsubst src/assets/%,$(OUTPUT_DIR)/assets/%,$(ASSETS))

# A recipe's configuration is one of its inputs, exactly as its source document
# is: editing a defaults file, the Typst font rules, the link filter, or the
# shared MathJax header has to rebuild whatever it changes.
# `mermaid.lua` is in every recipe's configuration, and so are the pictures it
# substitutes: a re-drawn diagram is a new input to each of the four, exactly as
# an edited source document is. The wildcard is re-expanded on every run, so a
# diagram drawn since the last build becomes a prerequisite as soon as it exists
# -- and one that has *not* been drawn is a missing file the filter names, not a
# silently stale drawing. See config/mermaid.lua.
#
# Only the SVGs are checked in, and they are what all four recipes wait on. The
# PDF that LuaLaTeX reads instead is derived from its SVG by the rule below, so
# it belongs to that recipe alone -- and it is named by transforming the SVG list
# rather than by a second wildcard, because a wildcard cannot see a file make has
# not derived yet.
DIAGRAM_SVGS := $(wildcard src/diagrams/*.svg)
DIAGRAM_PDFS := $(patsubst %.svg,%.pdf,$(DIAGRAM_SVGS))
MERMAID_CONFIG := config/mermaid.lua $(DIAGRAM_SVGS)

MATHML_CONFIG := config/pandoc-html-mathml.yaml $(MERMAID_CONFIG)
MATHJAX_CONFIG := config/pandoc-html-mathjax.yaml $(MERMAID_CONFIG) \
	src/_extensions/mathjax4/mathjax-schola.html
LUALATEX_CONFIG := config/pandoc-pdf-lualatex.yaml config/absolute-links.lua $(MERMAID_CONFIG) $(DIAGRAM_PDFS)
TYPST_CONFIG := config/pandoc-pdf-typst.yaml config/absolute-links.lua config/fonts.typ $(MERMAID_CONFIG)

.PHONY: all clean

# Each recipe writes straight to $@. Without this, pandoc failing partway
# through -- a missing font, a TeX error, an interrupted run -- leaves a
# truncated file that is newer than its source, so the next `make all` reports
# it up to date and the broken artifact ships.
.DELETE_ON_ERROR:

all: $(HTML_MATHML) $(HTML_MATHJAX) $(PDF_LUALATEX) $(PDF_TYPST)

$(OUTPUT_DIR) $(OUTPUT_DIR)/assets:
	mkdir -p $@

$(OUTPUT_DIR)/assets/%: src/assets/% | $(OUTPUT_DIR)/assets
	cp $< $@

$(OUTPUT_DIR)/%.html: src/%.md $(MATHML_CONFIG) $(STAGED_ASSETS)
	$(PANDOC) $< --defaults=config/pandoc-html-mathml.yaml --output=$@

$(OUTPUT_DIR)/%-mathjax.html: src/%.md $(MATHJAX_CONFIG) $(STAGED_ASSETS)
	$(PANDOC) $< --defaults=config/pandoc-html-mathjax.yaml --output=$@

$(OUTPUT_DIR)/%-lualatex.pdf: src/%.md $(LUALATEX_CONFIG) | $(OUTPUT_DIR)
	$(PANDOC) $< --defaults=config/pandoc-pdf-lualatex.yaml --output=$@

$(OUTPUT_DIR)/%-typst.pdf: src/%.md $(TYPST_CONFIG) | $(OUTPUT_DIR)
	$(PANDOC) $< --defaults=config/pandoc-pdf-typst.yaml --output=$@

# LuaLaTeX is the one writer that cannot be handed the SVG: \includegraphics
# reads none without --shell-escape and an Inkscape installation. It gets this
# instead, derived from the checked-in SVG by typst -- already pinned here as a
# PDF engine, so no dependency is added and the two pictures cannot disagree.
# That derivation is why these PDFs are gitignored rather than committed: it
# needs neither a browser nor a network, which is the entire reason the SVGs
# beside them are committed. See scripts/render_diagrams.py.
src/diagrams/%.pdf: src/diagrams/%.svg
	python scripts/render_diagrams.py --pdf $<

clean:
	rm -rf pandoc-output src/docs src/.quarto src/_freeze
	rm -f src/*-mathjax.html src/*-lualatex.pdf src/*-typst.pdf src/*.tex src/*.log
	rm -f src/diagrams/*.pdf
