--[[
  Açık Matematik — cross-book links in the exported formats (PDF/EPUB/DOCX)

  A course that is split into several books links from one book into another
  with a relative address, for example from Analiz 2 into Analiz 1:

      [Analiz 1](../analiz-1/mutlak-deger.html#thm-ucgen-esitsizligi)

  On the website that is exactly right. In print it is not. Quarto's Typst
  writer reads a link whose target carries a fragment as a reference to a label
  inside the same document and writes

      #link(<thm-ucgen-esitsizligi>)[Analiz 1]

  The label belongs to the other book, so Typst stops with "label does not
  exist in the document" and the PDF is never produced. In EPUB the link
  survives but points at a file the reader does not have.

  For every non-HTML output this filter turns such a link into the address of
  the page on the site, which is what a reader of the PDF actually needs.

  The filter is a no-op for the website (HTML) build.
]]

if FORMAT:match("^html") then
  return {}
end

-- Books are published under /dersler/<course>/ (see scripts/build.py).
local SITE = "https://acik-matematik.com/dersler/"

function Link(el)
  local course, rest = el.target:match("^%.%./([%w%-]+)/(.*)$")
  if course then
    el.target = SITE .. course .. "/" .. rest
  end
  return el
end
