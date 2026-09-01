--[[
Cross-document links are written as `multilingual.md`: the target that is also
correct when reading the source on GitHub. Nothing rewrites it on its own --
pandoc passes a relative target through verbatim in every writer, and Quarto
rewrites only its own HTML -- so this filter does it for all four recipes in
both pipelines.

What it rewrites to depends on the medium, which is why `link-base` exists.

  unset   `multilingual.html`, relative. Correct for HTML, where the browser
          resolves it against the page it came from. It also keeps a local
          build, a branch preview, and production all working from one source.

  set     `<link-base>/multilingual.html`, absolute. Required for PDF. A PDF
          has no containing page, so a viewer has nothing to resolve a relative
          URI against -- the PDF specification leaves that to an optional
          document-level base URI that browser viewers do not supply, and a
          relative link simply does nothing when clicked.

Only same-directory relative targets are rewritten. A URI scheme, a
protocol-relative `//host`, or a root-relative `/path` all name something this
build does not produce, so they are left exactly as written. A trailing `#anchor`
or `?query` is preserved.
]]

local base = ""

local function rewrite(target)
  local path, rest = target:match("^([^#?]*)(.*)$")
  if path:find("^%a[%w+.-]*:") or path:find("^//") or path:find("^/") then
    return nil
  end
  local stem = path:match("^(.+)%.md$")
  if not stem then
    return nil
  end
  return base .. stem .. ".html" .. rest
end

-- Two passes, in this order deliberately: a filter's own Meta function runs
-- after its Link function, so reading `link-base` has to be a separate,
-- earlier filter.
return {
  {
    Meta = function(meta)
      if meta["link-base"] then
        base = pandoc.utils.stringify(meta["link-base"])
        if base ~= "" and not base:match("/$") then
          base = base .. "/"
        end
      end
    end,
  },
  {
    Link = function(link)
      local target = rewrite(link.target)
      if target then
        link.target = target
        return link
      end
    end,
  },
}
