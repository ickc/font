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

--- The script a code point's own Script property names, or nil for none.
-- One search over every strong range in the database, which is why the table
-- is generated flat and sorted rather than one list per script.
local function own_script(codepoint)
  local low, high = 1, #unicode.strong
  while low <= high do
    local middle = (low + high) // 2
    local range = unicode.strong[middle]
    if codepoint < range[1] then
      high = middle - 1
    elseif codepoint > range[2] then
      low = middle + 1
    else
      return range[3]
    end
  end
  return nil
end

--- Classify one code point.
-- "script"  its own script, whether or not the document maps it
-- "tied"    belonging with the mapped scripts in the set by Script_Extensions
-- "neutral" everything else: spaces, digits, ASCII punctuation
-- Answers are memoised: a search over every script for every code point of a
-- long document is a lot of searching for an alphabet's worth of answers.
local memo = {}

local function classify(codepoint)
  local cached = memo[codepoint]
  if cached then return cached[1], cached[2] end

  local kind, value = "neutral", nil
  local own = own_script(codepoint)
  if own and mapped[own] then
    kind, value = "script", own
  else
    -- Script_Extensions is consulted for every code point the document does
    -- not already own outright, not only for the Common and Inherited ones.
    -- The Arabic-Indic digits are Script=Arabic and also written in Thaana, so
    -- in a Dhivehi document a digit between two Thaana words has to continue
    -- the run rather than end it as unmapped Arabic would.
    for script in pairs(mapped) do
      if contains(unicode.ext[script] or {}, codepoint) then
        kind = "tied"
        value = value or {}
        value[script] = true
      end
    end
    -- Otherwise a script of its own, mapped or not, still ends a run.
    if kind == "neutral" and own then kind, value = "script", own end
  end
  memo[codepoint] = { kind, value }
  return kind, value
end

--- Split a string into maximal runs of one mapped script.
-- Returns a list of `{text=..., script=...}`, `script` absent for the text
-- between runs, which is marked `foreign` when it is another script's own text
-- rather than neutral. Neutral code points join a run only when it continues
-- on the other side of them, which is what keeps a Hebrew phrase whole without
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
      -- Another script's own text ends the run rather than joining it, so it
      -- is kept apart from the neutral text that may sit either side of it.
      close()
      drain()
      pieces[#pieces + 1] = { text = char, foreign = true }
    else
      pending[#pending + 1] = { char = char, tied = value }
    end
  end
  close()
  drain()

  local merged = {}
  for _, piece in ipairs(pieces) do
    local last = merged[#merged]
    if last and not last.script and not piece.script
      and last.foreign == piece.foreign then
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

-- Inline containers that carry nothing of their own, so what is inside them
-- decides which run they belong to. Note is deliberately absent: its content
-- is a separate flow, and absorbing it would stop the filter descending into
-- it. Code, maths and raw inlines are absent because their text is not prose.
local transparent = {
  Emph = true, Link = true, Quoted = true, SmallCaps = true, Span = true,
  Strikeout = true, Strong = true, Subscript = true, Superscript = true,
  Underline = true,
}

--- Which run a container belongs to, from the text inside it.
-- Returns the script when everything script-bearing inside is that one mapped
-- script, nil when there is nothing script-bearing at all, and false when the
-- container has to stay opaque: another script, prose that is not prose, or a
-- language somebody has already written by hand.
local function content_script(inline)
  local found, opaque = nil, false

  local function scan(items)
    for _, item in ipairs(items) do
      if opaque then return end
      local kind = item.t
      if kind == "Str" then
        for _, codepoint in utf8.codes(item.text) do
          local class, value = classify(codepoint)
          if class == "script" and (not mapped[value] or (found and found ~= value)) then
            opaque = true
            return
          elseif class == "script" then
            found = value
          end
        end
      elseif kind == "Space" or kind == "SoftBreak" or kind == "LineBreak" then
        -- Neutral, exactly as at the top level.
      elseif transparent[kind] and not (kind == "Span" and item.attributes.lang) then
        scan(item.content)
      else
        opaque = true
        return
      end
    end
  end

  scan(inline.content)
  if opaque then return false end
  return found
end

--- Group an inline list, so a run survives what sits inside it.
-- Spaces keep a run going, and so does a container holding nothing but the
-- run's own script -- otherwise the fullwidth colon before an emphasised or
-- quoted Chinese phrase would fall outside the span and lose its font.
-- Anything else ends the run; its own inline list is visited in its own right.
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
        if piece.foreign then
          close()
          out:insert(pandoc.Str(piece.text))
        else
          add(pandoc.Str(piece.text), piece.script)
        end
      end
    elseif transparent[inline.t] and not (inline.t == "Span" and inline.attributes.lang) then
      local content = content_script(inline)
      if content == false then
        close()
        out:insert(inline)
      else
        add(inline, content)
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
        if unicode.names[script] then
          languages[script] = pandoc.utils.stringify(tag)
          mapped[script] = true
        else
          io.stderr:write(
            "[WARNING] auto-lang: no Unicode script named " .. script ..
            " in bin/script-ranges.lua\n")
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
