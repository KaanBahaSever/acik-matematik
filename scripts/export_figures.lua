--[[
  Açık Matematik — figure filter for the exported formats (PDF/EPUB/DOCX)

  The lecture notes embed theme-aware inline SVG figures as raw HTML:

      ```{=html}
      <figure class="ders-grafik"><svg …>…</svg><figcaption>…</figcaption></figure>
      ```

  Pandoc drops raw HTML when it writes Typst, EPUB or DOCX, so the figures
  would silently vanish from the downloadable files. For every non-HTML
  output this filter:

    * extracts the <svg>, resolves the CSS colour variables to the site's
      light palette (renderers such as Typst/resvg do not know CSS vars),
    * writes the result to <project>/_export-figs/<sha1>.svg,
    * replaces the raw block with a regular, numbered pandoc Figure whose
      caption is the original <figcaption> — so "Şekil 2.3" works in print.

  Other raw HTML (the interactive calculators of a few chapters) becomes a
  one-line note instead of disappearing without a trace.

  The filter is a no-op for the website (HTML) build.
]]

-- Light-theme values of the CSS custom properties used inside the SVGs.
-- They mirror the :root block of styles/global.css.
local PALETTE = {
  ["--academic-text"] = "#2C2A27",
  ["--academic-bg"]   = "#FAF6EE",
  ["--color-theory"]  = "#2B4C7E",
  ["--color-base"]    = "#0D6E6A",
  ["--color-practice"] = "#9C3F1E",
  ["--color-remark"]  = "#5C5346",
}

local FIG_DIR_NAME = "_export-figs"

local function is_export_format()
  return not FORMAT:match("^html")
end

local function figure_dir()
  local project = quarto and quarto.project and quarto.project.directory
  if not project then return nil end
  return project .. "/" .. FIG_DIR_NAME
end

local function ensure_dir(path)
  -- create_parent=true also tolerates an existing directory; a real failure
  -- surfaces in write_file's assert with the path in the message
  pcall(pandoc.system.make_directory, path, true)
end

local function write_file(path, content)
  local f = assert(io.open(path, "wb"))
  f:write(content)
  f:close()
end

local function resolve_css_vars(svg)
  for name, hex in pairs(PALETTE) do
    svg = svg:gsub("var%(" .. name:gsub("%-", "%%-") .. "%)", hex)
  end
  -- Anything left unresolved must not break the renderer
  svg = svg:gsub("var%(%-%-[%w%-]+%)", PALETTE["--academic-text"])
  return svg
end

local function standalone_svg(svg)
  if not svg:find("xmlns=") then
    svg = svg:gsub("^<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
  end
  -- Font: Libertinus ships inside Typst itself, so the figures use the same
  -- face as the PDF text on every machine (CI included). Never put a font
  -- here that only Windows has: Typst 0.14 hung forever resolving "Georgia"
  -- for SVG text that carries a combining mark.
  if not svg:match("^<svg[^>]*font%-family=") then
    svg = svg:gsub("^<svg", '<svg font-family="Libertinus Serif, Liberation Serif, DejaVu Serif, serif"', 1)
  end
  -- Combining overline (z̄ written as z + U+0305) is not composed by Typst's
  -- SVG renderer; draw the bar as a text decoration instead.
  svg = svg:gsub("([^%s<>&;])&#773;", '<tspan text-decoration="overline">%1</tspan>')
  svg = svg:gsub("([^%s<>&;])\u{0305}", '<tspan text-decoration="overline">%1</tspan>')
  return '<?xml version="1.0" encoding="UTF-8"?>\n' .. svg
end

local function caption_inlines(html)
  if not html or html == "" then return pandoc.Inlines({}) end
  local doc = pandoc.read(html, "html")
  local inlines = pandoc.Inlines({})
  for _, block in ipairs(doc.blocks) do
    if block.content then inlines:extend(block.content) end
  end
  return inlines
end

local function convert_figure(raw)
  local svg = raw:match("(<svg.-</svg>)")
  if not svg then return nil end
  local dir = figure_dir()
  if not dir then return nil end
  ensure_dir(dir)

  local wide = raw:match('<figure class="[^"]*ders%-grafik%-genis') ~= nil
  local caption_html = raw:match("<figcaption>(.-)</figcaption>")

  local content = standalone_svg(resolve_css_vars(svg))
  local name = pandoc.sha1(content) .. ".svg"
  write_file(dir .. "/" .. name, content)

  local caption = caption_inlines(caption_html)
  local width = wide and "100%" or "78%"
  local image = pandoc.Image(caption, FIG_DIR_NAME .. "/" .. name, "", pandoc.Attr("", {}, { width = width }))
  return pandoc.Figure(
    pandoc.Plain({ image }),
    pandoc.Caption(pandoc.Plain(caption)),
    pandoc.Attr("fig-" .. pandoc.sha1(content):sub(1, 10), {}, {})
  )
end

local function is_interactive(raw)
  return raw:find("<script") or raw:find("<input") or raw:find("<form") or raw:find("<button")
end

function RawBlock(el)
  if not is_export_format() or el.format ~= "html" then return nil end
  if el.text:find('<figure class="ders%-grafik') then
    local fig = convert_figure(el.text)
    if fig then return fig end
  end
  if is_interactive(el.text) then
    return pandoc.Para({ pandoc.Emph({ pandoc.Str("(Bu etkileşimli bileşen yalnızca web sürümünde çalışır.)") }) })
  end
  -- Any other raw HTML is meaningless in print; drop it explicitly.
  return {}
end
