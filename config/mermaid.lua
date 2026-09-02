--[[
Shared by Quarto and vanilla Pandoc, and loaded by all four recipes rather than
two of them: a mermaid diagram is content, not a PDF-only concern like
`absolute-links.lua`.

A ``` mermaid ``` block is replaced by the picture rendered from it. Which
picture depends on the writer, because the three targets can each read a
different thing:

  html   the SVG's text, INLINED into the page. An <img> would not do: an SVG
         referenced by <img> is a document of its own with no access to the
         page's @font-face rules, and external subresource loads are blocked
         inside it, so its text would be drawn in a fallback face. Inlined, the
         `font-family: TeX Gyre Schola` inside the SVG resolves against the
         faces `assets/fonts.css` already declares, exactly as body text does.
  typst  the same SVG, as a file. Typst resolves the family named inside it
         against TYPST_FONT_PATHS and embeds real glyphs -- so the picture is
         drawn from the same bytes the browser gets.
  latex  a PDF, because \includegraphics cannot read SVG without shell-escape
         and Inkscape. It is derived from that same SVG by typst, so the two
         artifacts cannot disagree about the picture, and it is built rather
         than committed: only the SVG needs a browser to make, so only the SVG
         is in the repository. The Makefile derives it with a pattern rule and
         Quarto with a `pre-render`; both call `scripts/render_diagrams.py`.

The artifact is named by the SHA-1 of the diagram source, which is what makes a
checked-in picture impossible to leave stale: editing a diagram changes its
name, the old file no longer answers, and the render stops with the message
below rather than shipping the previous drawing. `pandoc.utils.sha1` and
Python's `hashlib.sha1` are given the same string -- the code block's text as
pandoc parses it -- so the filter and the generator always agree on the name.

Where the artifacts are is worked out rather than configured, and neither
obvious answer works. The input document's directory is wrong because Quarto
does not render the source in place -- it hands pandoc a copy in a session
directory under /tmp, so `src/mermaid.md` arrives as a temporary file with no
`diagrams/` beside it. The working directory is wrong because the two pipelines
do not share one: Quarto renders from `src/`, the Makefile from the repository
root, so the same relative path cannot name the directory in both.

What is fixed is this file's own position in the repository, so that is what is
used: `src/diagrams/` is found relative to `config/`, and then made relative to
the working directory again. Both halves are needed. The absolute path is what
finds the file here; the relative one is what the PDF writers can be given,
because LaTeX resolves a graphic through kpathsea from the working directory and
Typst refuses outright to read outside the root it was started in.
]]

local DIAGRAMS = { "..", "src", "diagrams" }
local NAME_LENGTH = 12

-- `pandoc.path.normalize` keeps `..` components, and both consumers of the
-- result reject them: Typst reads a `..` as an attempt to escape its root and
-- refuses the file outright, and `make_relative` cannot compare a path that
-- still has them against the working directory. So they are resolved here.
local function resolve(path)
  local working = pandoc.system.get_working_directory()
  if not pandoc.path.is_absolute(path) then
    path = pandoc.path.join({ working, path })
  end
  local parts = {}
  for part in path:gmatch("[^" .. pandoc.path.separator .. "]+") do
    if part == ".." then
      table.remove(parts)
    elseif part ~= "." then
      parts[#parts + 1] = part
    end
  end
  return pandoc.path.separator .. table.concat(parts, pandoc.path.separator)
end

local function directory()
  local here = pandoc.path.directory(PANDOC_SCRIPT_FILE)
  local absolute = resolve(pandoc.path.join({ here, table.unpack(DIAGRAMS) }))
  local ok, relative = pcall(pandoc.path.make_relative, absolute, pandoc.system.get_working_directory())
  return (ok and relative) or absolute
end

local function artifact(code, extension)
  local name = "mermaid-" .. pandoc.utils.sha1(code):sub(1, NAME_LENGTH)
  return pandoc.path.join({ directory(), name .. "." .. extension })
end

local function open(path)
  local handle = io.open(path, "rb")
  if not handle then
    error(
      "no rendered diagram at " .. path ..
      "\nThe diagram source changed, or has never been rendered." ..
      "\nRun `pixi run render-diagrams` and commit the SVG it draws."
    )
  end
  return handle
end

local function read(path)
  local handle = open(path)
  local contents = handle:read("a")
  handle:close()
  return contents
end

-- The picture the PDF writers point at is opened and closed without being read,
-- so that a missing artifact fails here, with the message above, rather than
-- inside LaTeX or Typst as a file-not-found for a name nothing explains.
local function image(code, extension)
  local path = artifact(code, extension)
  open(path):close()
  return pandoc.Para({ pandoc.Image({}, path) })
end

return {
  {
    CodeBlock = function(block)
      if not block.classes:includes("mermaid") then
        return nil
      end
      if FORMAT:match("^html") then
        return pandoc.RawBlock("html", read(artifact(block.text, "svg")))
      elseif FORMAT == "typst" then
        return image(block.text, "svg")
      elseif FORMAT == "latex" then
        return image(block.text, "pdf")
      end
      -- Any other writer keeps the source, which is the only honest fallback:
      -- the block still says what the diagram is.
      return nil
    end,
  },
}
