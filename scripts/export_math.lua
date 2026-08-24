--[[
  Açık Matematik — math fixes for the exported formats (PDF via Typst,
  EPUB, DOCX)

  Pandoc converts the LaTeX math of the notes on the fly (to Typst, MathML
  or OMML). A few constructs used in the notes do not survive that:

    * \tag{…} — pandoc's math parser rejects it, so the whole equation
      would be emitted as raw TeX source. For Typst the equation is
      re-emitted as raw Typst with the tag as its numbering; for EPUB/DOCX
      the tag is appended to the equation as "(…)" text.
    * \begin{vmatrix} — becomes mat(delim: "||", …) in Typst, which rejects
      the two-character delimiter; rewritten as \left|\begin{matrix}….
    * \begin{array}{ccc|c} (augmented matrices, Cayley tables) — loses its
      grid, rules and alignment in Typst; every array is converted here into
      a Typst mat(...) whose augment lines reproduce the "|" column rules and
      the \hline row rules.
    * a few amssymb macros pandoc does not know (\diagup, \diagdown).

  The filter is a no-op for the website (HTML) build.
]]

if FORMAT:match("^html") then
  return {}
end

local TYPST = FORMAT == "typst"

-- ------------------------------------------------------------- helpers

local function trim(s)
  return (s:gsub("^%s+", ""):gsub("%s+$", ""))
end

-- Macros pandoc does not know are passed to Typst verbatim, where they
-- become "unknown variable" errors. Map the ones used in the notes.
local MACROS = {
  ["\\diagup"] = "/",
  ["\\diagdown"] = "\\backslash",
}

local function fix_tex(tex)
  tex = tex:gsub("\\begin{vmatrix}", "\\left|\\begin{matrix}")
  tex = tex:gsub("\\end{vmatrix}", "\\end{matrix}\\right|")
  for macro, replacement in pairs(MACROS) do
    -- a backslash is not magic in Lua patterns, so the macro can be used as is
    tex = tex:gsub(macro .. "(%A)", function(after)
      return replacement .. after
    end)
    tex = tex:gsub(macro .. "$", replacement)
  end
  return tex
end

-- Find "\tag{…}" (or \tag*{…}) with balanced braces. Returns the tag's
-- inner TeX (math delimiters removed, e.g. "\ast" or "3") and the TeX with
-- the whole \tag{…} cut out; nil when there is no tag.
local function extract_tag(tex)
  local start, brace = tex:find("\\tag%*?{")
  if not start then return nil end
  local depth, i = 1, brace + 1
  while i <= #tex and depth > 0 do
    local c = tex:sub(i, i)
    if c == "{" then depth = depth + 1 elseif c == "}" then depth = depth - 1 end
    i = i + 1
  end
  if depth ~= 0 then return nil end
  local tag = trim(tex:sub(brace + 1, i - 2):gsub("%$", ""))
  return tag, tex:sub(1, start - 1) .. tex:sub(i)
end

-- LaTeX -> Typst through pandoc's own writer. Returns the bare Typst math
-- source (without the surrounding $ … $).
local function typst_math_source(tex, display)
  local kind = display and "DisplayMath" or "InlineMath"
  local doc = pandoc.Pandoc({ pandoc.Plain({ pandoc.Math(kind, tex) }) })
  local out = trim(pandoc.write(doc, "typst"))
  out = out:gsub("^%$%s*", ""):gsub("%s*%$$", "")
  return out
end

-- Split a LaTeX array body into rows and cells, honouring nested braces
-- so that "&" and "\\" inside a {…} group are kept.
local function split_top_level(text, separator)
  local parts, depth, buf = {}, 0, {}
  local i, n = 1, #text
  while i <= n do
    local c = text:sub(i, i)
    if c == "{" then depth = depth + 1
    elseif c == "}" then depth = depth - 1 end
    if depth == 0 and text:sub(i, i + #separator - 1) == separator then
      parts[#parts + 1] = table.concat(buf)
      buf = {}
      i = i + #separator
    else
      buf[#buf + 1] = c
      i = i + 1
    end
  end
  parts[#parts + 1] = table.concat(buf)
  return parts
end

-- \begin{array}{cc|c} body \end{array}  ->  Typst mat(...) source
local function array_to_mat(spec, body)
  -- column rules: a "|" after k column letters becomes vline k
  local vlines, cols = {}, 0
  for ch in spec:gmatch(".") do
    if ch == "|" then
      if cols > 0 then vlines[#vlines + 1] = cols end
    elseif ch:match("[clr]") then
      cols = cols + 1
    end
  end

  local rows, hlines = {}, {}
  for _, raw_row in ipairs(split_top_level(body, "\\\\")) do
    local row = raw_row
    local rules = 0
    row = row:gsub("\\hline", function() rules = rules + 1; return "" end)
    if rules > 0 and #rows > 0 then hlines[#hlines + 1] = #rows end
    if trim(row) ~= "" then
      local cells = {}
      for _, cell in ipairs(split_top_level(row, "&")) do
        local src = trim(cell)
        cells[#cells + 1] = src == "" and '""' or typst_math_source(src, false)
      end
      rows[#rows + 1] = table.concat(cells, ", ")
    end
  end

  local augment = {}
  if #hlines > 0 then augment[#augment + 1] = "hline: (" .. table.concat(hlines, ", ") .. ",)" end
  if #vlines > 0 then augment[#augment + 1] = "vline: (" .. table.concat(vlines, ", ") .. ",)" end
  local opts = "delim: #none"
  if #augment > 0 then
    opts = opts .. ", augment: #(" .. table.concat(augment, ", ") .. ", stroke: 0.5pt)"
  end
  return "mat(" .. opts .. ", " .. table.concat(rows, "; ") .. ")"
end

-- Replace every array environment with a \text{…} placeholder (pandoc turns
-- it into upright("…")), convert the whole equation, then substitute the
-- generated mat(...) code for the placeholders.
local function convert_with_arrays(tex, display)
  local mats, index = {}, 0
  local replaced = tex:gsub("\\begin{array}{([^}]*)}(.-)\\end{array}", function(spec, body)
    index = index + 1
    local key = "QARRAY" .. index .. "Q"
    mats[key] = array_to_mat(spec, body)
    return "\\text{" .. key .. "}"
  end)
  local out = typst_math_source(replaced, display)
  for key, mat in pairs(mats) do
    out = out:gsub('upright%("' .. key .. '"%)', function() return mat end)
    out = out:gsub('"' .. key .. '"', function() return mat end)
  end
  return out
end

-- ------------------------------------------------------------- filter

function Math(el)
  local tex = fix_tex(el.text)
  local display = el.mathtype == "DisplayMath"
  local tag = nil
  if display then
    local found, rest = extract_tag(tex)
    if found then
      tag, tex = found, rest
    end
  end

  if not TYPST then
    -- EPUB / DOCX: keep the tag visible as ordinary math at the right
    if tag then
      tex = trim(tex) .. " \\qquad (" .. tag .. ")"
    end
    if tex ~= el.text then
      el.text = tex
      return el
    end
    return nil
  end

  local has_array = tex:find("\\begin{array}") ~= nil
  if not tag and not has_array then
    if tex ~= el.text then
      el.text = tex
      return el
    end
    return nil
  end

  local source = has_array and convert_with_arrays(tex, display) or typst_math_source(tex, display)
  local typst
  if display then
    typst = "$ " .. source .. " $"
    if tag then
      -- the tag becomes the equation's numbering, as math content so that
      -- \ast, \star, * and plain numbers all render
      local tag_src = typst_math_source(tag, false)
      typst = "#[\n#set math.equation(numbering: _ => $(" .. tag_src .. ")$)\n" .. typst .. "\n]"
    end
  else
    typst = "$" .. source .. "$"
  end
  return pandoc.RawInline("typst", typst)
end
