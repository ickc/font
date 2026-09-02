--[[
Loaded by bin/md_formatter.py, so it rewrites the source rather than each
render. Neither Quarto nor the vanilla Pandoc recipes know about it.

Multilingual sources otherwise have to carry the language by hand:

    [וַיֹּאמֶר אֱלֹהִים]{lang=he dir=rtl}

which is markup about the writing system, not about the text. Every code point
already declares its script in the Unicode Character Database, so this filter
reads it there instead: a document maps scripts to language tags,

    auto-lang:
      Hebrew: he
      Greek: el
      Han: zh-Hant

and `pixi run format` writes each run of a mapped script into the source as
the Span the author would have written, `dir=rtl` included for the
right-to-left ones. What the four recipes then render is ordinary Pandoc
markup, checked in and reviewable in a diff.

Running it again changes nothing: a span that carries a `lang` is skipped
whole, so only text added since the last run is ever tagged.

A script is not a language: Han cannot tell zh-Hant from ja, and no rule can
tell English from French. The mapping is therefore per document and explicit,
and a hand-written span always wins -- this filter never looks inside one.

script-ranges.lua beside this file is the generated table; see
scripts/generate_script_ranges.py.
]]

local directory = PANDOC_SCRIPT_FILE:match("^(.*)[/\\][^/\\]*$") or "."
local unicode = dofile(directory .. "/script-ranges.lua")

local languages = {}  -- script -> language tag
local mapped = {}     -- script -> true, for the scripts this document maps

local function contains(ranges, codepoint)
  local low, high = 1, #ranges
  while low <= high do
    local middle = (low + high) // 2
    local range = ranges[middle]
    if codepoint < range[1] then
      high = middle - 1
    elseif codepoint > range[2] then
      low = middle + 1
    else
      return true
    end
  end
  return false
end

--- Classify one code point.
-- "script"  its own script, whether or not the document maps it
-- "tied"    Common or Inherited, but belonging with the scripts in the set
-- "neutral" everything else: spaces, digits, ASCII punctuation
-- Answers are memoised: a search over every script for every code point of a
-- long document is a lot of searching for an alphabet's worth of answers.
local memo = {}

local function classify(codepoint)
  local cached = memo[codepoint]
  if cached then return cached[1], cached[2] end

  local kind, value = "neutral", nil
  for script, ranges in pairs(unicode.strong) do
    if contains(ranges, codepoint) then
      kind, value = "script", script
      break
    end
  end
  if kind == "neutral" then
    for script in pairs(mapped) do
      if contains(unicode.ext[script], codepoint) then
        kind = "tied"
        value = value or {}
        value[script] = true
      end
    end
  end
  memo[codepoint] = { kind, value }
  return kind, value
end

--- Split a string into maximal runs of one mapped script.
-- Returns a list of `{text=..., script=...}`, `script` absent for the text
-- between runs. Neutral code points join a run only when it continues on the
-- other side of them, which is what keeps a Hebrew phrase whole without
-- swallowing the space that ends it. Script-tied ones join a run they merely
-- touch, which is what keeps 。 and 」 with the Han text they punctuate.
local function split(text)
  local pieces, run, pending = {}, nil, {}

  local function take(count)
    for index = 1, count do run.text = run.text .. pending[index].char end
    for _ = 1, count do table.remove(pending, 1) end
  end

  local function close()
    if not run then return end
    local tied = 0
    while pending[tied + 1] and pending[tied + 1].tied
      and pending[tied + 1].tied[run.script] do
      tied = tied + 1
    end
    take(tied)
    pieces[#pieces + 1] = run
    run = nil
  end

  local function drain()
    for _, item in ipairs(pending) do pieces[#pieces + 1] = { text = item.char } end
    pending = {}
  end

  for _, codepoint in utf8.codes(text) do
    local char = utf8.char(codepoint)
    local kind, value = classify(codepoint)
    if kind == "script" and mapped[value] then
      if run and run.script == value then
        take(#pending)
        run.text = run.text .. char
      else
        close()
        local first = #pending + 1
        while pending[first - 1] and pending[first - 1].tied
          and pending[first - 1].tied[value] do
          first = first - 1
        end
        local carried = ""
        for index = first, #pending do carried = carried .. pending[index].char end
        for _ = first, #pending do table.remove(pending) end
        drain()
        run = { text = carried .. char, script = value }
      end
    elseif kind == "script" then
      -- Another script's own text ends the run rather than joining it.
      close()
      drain()
      pieces[#pieces + 1] = { text = char }
    else
      pending[#pending + 1] = { char = char, tied = value }
    end
  end
  close()
  drain()

  local merged = {}
  for _, piece in ipairs(pieces) do
    local last = merged[#merged]
    if last and not last.script and not piece.script then
      last.text = last.text .. piece.text
    else
      merged[#merged + 1] = piece
    end
  end
  return merged
end

local function span(script, inlines)
  local attributes = { lang = languages[script] }
  if unicode.rtl[script] then attributes.dir = "rtl" end
  return pandoc.Span(inlines, pandoc.Attr("", {}, attributes))
end

--- Group an inline list, so a run survives the Space elements inside it.
-- Anything that is not a Str or ordinary whitespace ends the run: emphasis, a
-- link, inline code. Their own inline lists are visited in their own right.
local function group(inlines)
  local out, run, script, pending = pandoc.Inlines({}), {}, nil, {}
  local changed = false

  local function flush()
    for _, item in ipairs(pending) do out:insert(item) end
    pending = {}
  end

  local function close()
    if script then
      out:insert(span(script, pandoc.Inlines(run)))
      run, script = {}, nil
      changed = true
    end
    flush()
  end

  local function add(inline, piece_script)
    if not piece_script then
      if script then pending[#pending + 1] = inline else out:insert(inline) end
      return
    end
    if script and script ~= piece_script then close() end
    if not script then
      flush()
      script = piece_script
    end
    for _, item in ipairs(pending) do run[#run + 1] = item end
    pending = {}
    run[#run + 1] = inline
  end

  for _, inline in ipairs(inlines) do
    if inline.t == "Space" or inline.t == "SoftBreak" then
      add(inline, nil)
    elseif inline.t == "Str" then
      for _, piece in ipairs(split(inline.text)) do
        add(pandoc.Str(piece.text), piece.script)
      end
    else
      close()
      out:insert(inline)
    end
  end
  close()
  return changed and out or nil
end

return {
  -- A filter's own Meta function runs after its Inlines function, so reading
  -- the mapping has to happen in a separate, earlier filter.
  {
    Meta = function(meta)
      for script, tag in pairs(meta["auto-lang"] or {}) do
        if unicode.strong[script] then
          languages[script] = pandoc.utils.stringify(tag)
          mapped[script] = true
        else
          io.stderr:write(
            "[WARNING] auto-lang: no Unicode script named " .. script ..
            " in config/script-ranges.lua\n")
        end
      end
    end,
  },
  {
    traverse = "topdown",
    -- A hand-written language wins: leave the span, and its contents, alone.
    Span = function(element)
      if element.attributes.lang then return element, false end
    end,
    Inlines = function(inlines)
      if next(mapped) then return group(inlines) end
    end,
  },
}
