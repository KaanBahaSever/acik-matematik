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
    * a few macros pandoc does not know (\diagup, \diagdown, \cfrac,
      \hphantom).
    * \dfrac, \dbinom and \displaystyle — pandoc's Typst writer drops the
      math style, so in inline math (and in table cells) the fractions,
      sums and integrals the notes deliberately set at display size came
      out at Typst's small inline size. Each such piece is converted on its
      own and wrapped in Typst's display(...). \dbinom and \tbinom are not
      understood by pandoc at all and would be printed as raw TeX; for
      EPUB/DOCX they become a plain \binom.

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
  -- not parsed by pandoc either; the nearest forms it knows
  ["\\cfrac"] = "\\dfrac",
  ["\\hphantom"] = "\\phantom",
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

-- ------------------------------------------------- display-size pieces

-- Macros whose math style pandoc's Typst writer loses, and what they become.
local STYLE_KIND = {
  dfrac = "frac",
  dbinom = "binom",
  tbinom = "binom",
  displaystyle = "style",
}

-- The argument that starts at (or after whitespace from) index i: a {…}
-- group, a control word or a single character. Returns its TeX and the
-- index just after it, or nil when the braces do not balance.
local function read_arg(tex, i)
  while tex:sub(i, i):match("%s") do i = i + 1 end
  local c = tex:sub(i, i)
  if c == "{" then
    local depth, j = 1, i + 1
    while j <= #tex and depth > 0 do
      local d = tex:sub(j, j)
      if d == "\\" then
        j = j + 1
      elseif d == "{" then
        depth = depth + 1
      elseif d == "}" then
        depth = depth - 1
      end
      j = j + 1
    end
    if depth ~= 0 then return nil end
    return tex:sub(i + 1, j - 2), j
  elseif c == "\\" then
    local word = tex:match("^\\%a+", i) or tex:sub(i, i + 1)
    return word, i + #word
  elseif c ~= "" then
    return c, i + 1
  end
  return nil
end

-- \displaystyle acts up to the end of its group: the closing brace of the
-- enclosing {…}, a \right or \end that closes something opened before it,
-- an alignment "&" or a "\\" row break. Returns the index where it stops.
local function style_scope_end(tex, i)
  local braces, pairs_open, envs = 0, 0, 0
  while i <= #tex do
    local c = tex:sub(i, i)
    if c == "\\" then
      local word = tex:match("^\\%a+", i)
      if word == "\\left" then
        pairs_open = pairs_open + 1
      elseif word == "\\right" then
        if braces == 0 and pairs_open == 0 then return i end
        pairs_open = pairs_open - 1
      elseif word == "\\begin" then
        envs = envs + 1
      elseif word == "\\end" then
        if braces == 0 and envs == 0 then return i end
        envs = envs - 1
      elseif not word and tex:sub(i, i + 1) == "\\\\" and braces == 0 and envs == 0 then
        return i
      end
      i = i + (word and #word or 2)
    else
      if c == "{" then
        braces = braces + 1
      elseif c == "}" then
        if braces == 0 then return i end
        braces = braces - 1
      elseif c == "&" and braces == 0 and envs == 0 then
        return i
      end
      i = i + 1
    end
  end
  return i
end

local styled_to_typst

-- Cut every styled piece out of the TeX, leaving a \text{…} placeholder.
-- Returns the new TeX and a map placeholder -> Typst code, or nil when a
-- piece cannot be parsed (the equation is then left to pandoc as before).
local function cut_styled(tex)
  local pieces, buf, i, count = {}, {}, 1, 0
  while i <= #tex do
    local s, e, name = tex:find("\\(%a+)", i)
    if not s then break end
    local kind = STYLE_KIND[name]
    if not kind then
      buf[#buf + 1] = tex:sub(i, e)
      i = e + 1
    else
      buf[#buf + 1] = tex:sub(i, s - 1)
      local code, after
      if kind == "style" then
        after = style_scope_end(tex, e + 1)
        local body = tex:sub(e + 1, after - 1)
        if trim(body) ~= "" then
          code = "display(" .. styled_to_typst(body, false) .. ")"
        end
      else
        local a, j = read_arg(tex, e + 1)
        if not a then return nil end
        local b, k = read_arg(tex, j)
        if not b then return nil end
        code = kind .. "(" .. styled_to_typst(a, false) .. ", " .. styled_to_typst(b, false) .. ")"
        if name ~= "tbinom" then code = "display(" .. code .. ")" end
        after = k
      end
      if code then
        count = count + 1
        local key = "QSTYLE" .. count .. "Q"
        pieces[key] = code
        buf[#buf + 1] = "\\text{" .. key .. "}"
      end
      i = after
    end
  end
  buf[#buf + 1] = tex:sub(i)
  return table.concat(buf), pieces
end

-- LaTeX -> Typst math source like typst_math_source, but keeping the
-- display size of \dfrac, \dbinom and \displaystyle pieces and converting
-- arrays to mat(...).
styled_to_typst = function(tex, display)
  local replaced, pieces = cut_styled(tex)
  if not replaced then
    replaced, pieces = tex, {}
  end
  local out
  if replaced:find("\\begin{array}") then
    out = convert_with_arrays(replaced, display)
  else
    out = typst_math_source(replaced, display)
  end
  for key, code in pairs(pieces) do
    out = out:gsub('upright%("' .. key .. '"%)', function() return code end)
    out = out:gsub('"' .. key .. '"', function() return code end)
  end
  return out
end

local function has_styled(tex)
  for name in pairs(STYLE_KIND) do
    if tex:find("\\" .. name, 1, true) then return true end
  end
  return false
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
    -- MathML / OMML have no \dbinom or \tbinom; a plain \binom is close enough
    tex = tex:gsub("\\[dt]binom(%A)", "\\binom%1")
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
  -- In display math pandoc already sets fractions at display size, so only
  -- the binomials it cannot parse have to be rewritten there.
  local styled = has_styled(tex) and (not display or tex:find("\\[dt]binom") ~= nil)
  if not tag and not has_array and not styled then
    if tex ~= el.text then
      el.text = tex
      return el
    end
    return nil
  end

  local source = styled_to_typst(tex, display)
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
