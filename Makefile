PANDOC ?= pandoc
OUTPUT_DIR := pandoc-output
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
#
# All four recipes load the language filter, and the filter reads its generated
# Unicode table at run time, so both are inputs to every artifact.
AUTO_LANG := config/auto-lang.lua config/script-ranges.lua
MATHML_CONFIG := config/pandoc-html-mathml.yaml $(AUTO_LANG)
MATHJAX_CONFIG := config/pandoc-html-mathjax.yaml $(AUTO_LANG) \
	src/_extensions/mathjax4/mathjax-schola.html
LUALATEX_CONFIG := config/pandoc-pdf-lualatex.yaml $(AUTO_LANG) \
	config/absolute-links.lua
TYPST_CONFIG := config/pandoc-pdf-typst.yaml $(AUTO_LANG) \
	config/absolute-links.lua config/fonts.typ

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

clean:
	rm -rf pandoc-output src/docs src/.quarto src/_freeze
	rm -f src/*-mathjax.html src/*-lualatex.pdf src/*-typst.pdf src/*.tex src/*.log
