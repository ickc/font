#!/bin/sh

# Pixi sources this file, so HOME expansion is reliable on both supported OSes.
case "$(uname -s)" in
  Darwin) font_pattern_dir="$HOME/Library/Fonts/font-kolen-dev" ;;
  Linux) font_pattern_dir="$HOME/.local/share/fonts/font-kolen-dev" ;;
  *) font_pattern_dir="$PIXI_PROJECT_ROOT/.fonts" ;;
esac

export FONT_PATTERN_FONT_DIR="$font_pattern_dir"
if [ -n "${TYPST_FONT_PATHS:-}" ]; then
  export TYPST_FONT_PATHS="$font_pattern_dir:$TYPST_FONT_PATHS"
else
  export TYPST_FONT_PATHS="$font_pattern_dir"
fi

# Pandoc's LuaLaTeX template loads selnolig. The setup-tex-support task stages
# it here for minimal TeX Live installations while the trailing colon retains
# the platform's normal TeX and Lua search paths.
export TEXINPUTS="$PIXI_PROJECT_ROOT/.cache/texmf//:${TEXINPUTS:-}"
export LUAINPUTS="$PIXI_PROJECT_ROOT/.cache/texmf//:${LUAINPUTS:-}"

unset font_pattern_dir
