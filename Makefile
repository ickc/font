PANDOC ?= pandoc
OUTPUT_DIR := pandoc-output
SOURCES := $(wildcard src/*.md)
NAMES := $(patsubst src/%.md,%,$(SOURCES))
HTML_MATHML := $(addprefix $(OUTPUT_DIR)/,$(addsuffix .html,$(NAMES)))
HTML_MATHJAX := $(addprefix $(OUTPUT_DIR)/,$(addsuffix -mathjax.html,$(NAMES)))
PDF_LUALATEX := $(addprefix $(OUTPUT_DIR)/,$(addsuffix -lualatex.pdf,$(NAMES)))
PDF_TYPST := $(addprefix $(OUTPUT_DIR)/,$(addsuffix -typst.pdf,$(NAMES)))

.PHONY: all clean

all: $(HTML_MATHML) $(HTML_MATHJAX) $(PDF_LUALATEX) $(PDF_TYPST)

$(OUTPUT_DIR):
	mkdir -p $@

$(OUTPUT_DIR)/assets/fonts.css: src/assets/fonts.css | $(OUTPUT_DIR)
	mkdir -p $(OUTPUT_DIR)/assets
	cp src/assets/* $(OUTPUT_DIR)/assets/

$(OUTPUT_DIR)/%.html: src/%.md $(OUTPUT_DIR)/assets/fonts.css
	$(PANDOC) $< --defaults=config/pandoc-html-mathml.yaml --output=$@

$(OUTPUT_DIR)/%-mathjax.html: src/%.md $(OUTPUT_DIR)/assets/fonts.css
	$(PANDOC) $< --defaults=config/pandoc-html-mathjax.yaml --output=$@

$(OUTPUT_DIR)/%-lualatex.pdf: src/%.md | $(OUTPUT_DIR)
	$(PANDOC) $< --defaults=config/pandoc-pdf-lualatex.yaml --output=$@

$(OUTPUT_DIR)/%-typst.pdf: src/%.md | $(OUTPUT_DIR)
	$(PANDOC) $< --defaults=config/pandoc-pdf-typst.yaml --output=$@

clean:
	rm -rf pandoc-output src/docs src/.quarto src/_freeze
	rm -f src/*-mathjax.html src/*-lualatex.pdf src/*-typst.pdf src/*.tex src/*.log
