--[[
Cross-document links are written root-relative: `/math.html`. That target is
already correct in HTML on any origin the site is served from -- production and
each branch preview have their own -- so no filter is involved there.

A PDF is the exception. It has no containing page, so a viewer has nothing to
resolve a relative or root-relative URI against: the format leaves that to an
optional document-level base URI that browser viewers do not supply, and such a
link is simply inert when clicked. This filter is therefore loaded by the PDF
recipes only, where `link-base` names the site the PDF is published on and every
root-relative target is expanded against it.

Only root-relative targets are touched. An absolute URL is already resolvable, a
protocol-relative `//host` names another origin, and a document-relative target
has no meaning to expand.
]]

local base = nil

return {
  -- A filter's own Meta function runs after its Link function, so reading
  -- `link-base` has to happen in a separate, earlier filter.
  {
    Meta = function(meta)
      if meta["link-base"] then
        base = (pandoc.utils.stringify(meta["link-base"]):gsub("/+$", ""))
      end
    end,
  },
  {
    Link = function(link)
      if base and link.target:sub(1, 1) == "/" and link.target:sub(2, 2) ~= "/" then
        link.target = base .. link.target
        return link
      end
    end,
  },
}
