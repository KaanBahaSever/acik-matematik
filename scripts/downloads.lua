--[[
  Açık Matematik — download panel on the curriculum page (HTML only)

  scripts/export.py renders every course (or its sub-courses) to PDF / EPUB
  and leaves a manifest, dersler/<course>/_downloads.json, next to the
  course. When that manifest exists, this filter draws a panel with the
  download links at the very end of the course's index.qmd page, so the
  reader meets the opening text and the curriculum listing first.

  Without the manifest (e.g. `quarto preview` while writing) the page is
  rendered as before — nothing is inserted.

  The class names emitted here ("downloads", "downloads-title", …) are the
  contract shared with styles/global.css.
]]

local function is_curriculum_page()
  local path = quarto and quarto.doc and quarto.doc.input_file
  if not path then return false end
  return path:match("[/\\]index%.qmd$") ~= nil
end

local function read_manifest()
  local project = quarto and quarto.project and quarto.project.directory
  if not project then return nil end
  local f = io.open(project .. "/_downloads.json", "r")
  if not f then return nil end
  local text = f:read("a")
  f:close()
  local ok, data = pcall(quarto.json.decode, text)
  if not ok or type(data) ~= "table" then return nil end
  return data
end

local function html_escape(text)
  return (tostring(text):gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function human_size(bytes)
  if type(bytes) ~= "number" then return "" end
  local text
  if bytes >= 1048576 then
    text = string.format("%.1f MB", bytes / 1048576)
  else
    text = string.format("%.0f KB", bytes / 1024)
  end
  return (text:gsub("%.", ","))   -- Turkish decimal comma
end

local FORMAT_LABEL = { pdf = "PDF", epub = "EPUB" }
local FORMAT_ORDER = { "pdf", "epub" }

local function panel_html(manifest)
  local parts = {}
  parts[#parts + 1] = '<div class="downloads">'
  parts[#parts + 1] = '<p class="downloads-title">Notları indirin</p>'
  parts[#parts + 1] = '<ul class="downloads-list">'
  for _, unit in ipairs(manifest.units or {}) do
    local links = {}
    for _, fmt in ipairs(FORMAT_ORDER) do
      local file = unit.files and unit.files[fmt]
      if file and file.name then
        links[#links + 1] = string.format(
          '<a class="downloads-file" href="%s" download>%s<small>%s</small></a>',
          html_escape(file.name), FORMAT_LABEL[fmt], human_size(file.bytes))
      end
    end
    if #links > 0 then
      parts[#parts + 1] = string.format(
        '<li><span class="downloads-name">%s</span><span class="downloads-files">%s</span></li>',
        html_escape(unit.title), table.concat(links, " "))
    end
  end
  parts[#parts + 1] = '</ul>'
  parts[#parts + 1] = '</div>'
  return table.concat(parts, "\n")
end

function Pandoc(doc)
  if not FORMAT:match("^html") or not is_curriculum_page() then return nil end
  local manifest = read_manifest()
  if not manifest or not manifest.units or #manifest.units == 0 then return nil end

  doc.blocks:insert(pandoc.RawBlock("html", panel_html(manifest)))
  return doc
end
