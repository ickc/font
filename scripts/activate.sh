#!/bin/sh

# Use each platform's conventional per-user font directory so desktop apps can
# discover the installed fonts. No project-named child directory is required.
case "$(uname -s)" in
  Darwin) font_pattern_dir="$HOME/Library/Fonts" ;;
  Linux) font_pattern_dir="${XDG_DATA_HOME:-$HOME/.local/share}/fonts" ;;
  *) font_pattern_dir="$PIXI_PROJECT_ROOT/.fonts" ;;
esac

export FONT_PATTERN_FONT_DIR="$font_pattern_dir"
if [ -n "${TYPST_FONT_PATHS:-}" ]; then
  export TYPST_FONT_PATHS="$font_pattern_dir:$TYPST_FONT_PATHS"
else
  export TYPST_FONT_PATHS="$font_pattern_dir"
fi

# Let LuaTeX/fontspec resolve filename-based font names in the user font tree.
# NotoSansCJKtc avoids a broken luaotfload family-name record for this CFF font.
export OSFONTDIR="$font_pattern_dir//${OSFONTDIR:+:$OSFONTDIR}:"

# Pandoc's LuaLaTeX template loads selnolig. setup-tex-support stages it in this
# project-local TEXMF tree for minimal TeX Live installations. Kpathsea's `//`
# searches recursively; the final empty component (`:`) adds its default paths.
export TEXINPUTS="$PIXI_PROJECT_ROOT/.cache/texmf//${TEXINPUTS:+:$TEXINPUTS}:"
export LUAINPUTS="$PIXI_PROJECT_ROOT/.cache/texmf//${LUAINPUTS:+:$LUAINPUTS}:"

unset font_pattern_dir
