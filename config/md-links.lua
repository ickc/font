--[[
Vanilla Pandoc keeps a relative link target such as `multilingual.md` verbatim,
so the HTML it writes points at a Markdown file that is not published beside it.
Quarto rewrites those targets to the file each source renders to -- and to the
same `.html` name from both of its HTML formats. This filter gives the Makefile's
two HTML recipes that behaviour, so one Markdown source can carry cross-document
links that resolve in both pipelines and while browsing the source on GitHub.

Only same-directory relative targets are rewritten. A URI scheme, a
protocol-relative `//host`, or a root-relative `/path` all name something this
build does not produce, so they are left exactly as written. A trailing `#anchor`
or `?query` is preserved.
]]

local function rewrite(target)
  local path, rest = target:match("^([^#?]*)(.*)$")
  if path:find("^%a[%w+.-]*:") or path:find("^//") or path:find("^/") then
    return nil
  end
  local stem = path:match("^(.+)%.md$")
  if not stem then
    return nil
  end
  return stem .. ".html" .. rest
end

function Link(link)
  local target = rewrite(link.target)
  if target then
    link.target = target
    return link
  end
end
