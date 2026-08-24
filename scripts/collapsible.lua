--[[
  Açık Matematik — shared Pandoc/Quarto filter

  Three jobs:

  1) Strips emoji from callout (note / tip / warning) titles. Source files
     may put emoji in titles; the rendered output stays plain.

  2) Turns collapsible "Çözüm" (solution) and "İspat" (proof) blocks into
     the browser's native <details> element instead of a Bootstrap
     accordion.

     Rationale: a second box nested inside a callout produced a double
     frame and double indentation on mobile and became unreadable.
     <details> emits far less markup, needs no JavaScript, and is announced
     correctly by screen readers as an "expandable region".

  3) Wraps the curriculum lists on each book's index.qmd page in a single
     <div class="mufredat"> so the CSS does not have to guess the structure.

  Note: Quarto converts callouts into a custom AST node at read time, so
  they cannot be caught by an ordinary Div filter; the `Callout` handler
  below uses Quarto's custom-node API.

  The class and attribute names emitted here ("katlanir", "katlanir-baslik",
  "katlanir-govde", "mufredat", "cozum", "ispat", baslik=, acik=) are the
  public contract shared with styles/global.css and the .qmd sources; they
  are Turkish on purpose and must not be renamed here alone.
]]

-- ----------------------------------------------------------------- helpers

-- Code-point ranges covering emoji and decorative symbols.
-- Mathematical operators (U+2200–U+22FF) and arrows (U+2190–U+21FF) are
-- deliberately EXCLUDED; they may legitimately appear in titles.
local emoji_ranges = {
  { 0x1F000, 0x1FAFF },  -- emoji blocks
  { 0x2600,  0x27BF  },  -- miscellaneous symbols, dingbats
  { 0x2300,  0x23FF  },  -- technical symbols
  { 0x2B00,  0x2BFF  },  -- geometric shapes
  { 0xFE00,  0xFE0F  },  -- variation selectors
  { 0x1F1E6, 0x1F1FF },  -- regional indicator (flag) letters
  { 0x200D,  0x200D  },  -- zero-width joiner
}

local function is_emoji(code)
  for _, range in ipairs(emoji_ranges) do
    if code >= range[1] and code <= range[2] then return true end
  end
  return false
end

local function strip_emoji(text)
  local parts = {}
  for _, code in utf8.codes(text) do
    if not is_emoji(code) then
      parts[#parts + 1] = utf8.char(code)
    end
  end
  local clean = table.concat(parts)
  return (clean:gsub("^%s+", ""):gsub("%s+$", ""))
end

-- In Quarto's Callout node the title is held as a single Block (usually
-- Plain); in hand-built cases it may be Inlines. Reduce both to Inlines.
local function title_inlines(title)
  if title == nil then return nil end
  if title.t == "Plain" or title.t == "Para" then
    return title.content
  end
  return title
end

-- Strip emoji from the Str elements of an Inlines list, dropping the ones
-- that become empty.
local function clean_inlines(inlines)
  local result = pandoc.List({})
  for _, il in ipairs(inlines) do
    if il.t == "Str" then
      local clean = strip_emoji(il.text)
      if clean ~= "" then result:insert(pandoc.Str(clean)) end
    else
      result:insert(il)
    end
  end
  -- Drop leading/trailing whitespace left orphaned by a removed emoji
  while #result > 0 and (result[1].t == "Space" or result[1].t == "SoftBreak") do
    result:remove(1)
  end
  while #result > 0 and (result[#result].t == "Space" or result[#result].t == "SoftBreak") do
    result:remove(#result)
  end
  return result
end

local function html_escape(text)
  return (text:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

-- Is this collapsible block a "Çözüm" (solution) or an "İspat" (proof)?
-- Returns nil otherwise. The second return value is the block kind; the CSS
-- uses it to pick the disclosure marker (solutions share the example
-- symbol, proofs share the theorem symbol).
local function collapsible_title(title_text)
  local lower = pandoc.text.lower(title_text)
  if lower:find("^çözüm") then return "Çözüm", "cozum" end
  if lower:find("^ispat") or lower:find("^i̇spat") then
    -- Keep descriptive titles such as "İspat: bu formüller nereden geliyor?"
    return title_text, "ispat"
  end
  return nil
end

-- Build the <details> block
local function details_blocks(title, content, kind, open)
  local class = "katlanir katlanir--" .. (kind or "ispat")
  local opening = pandoc.RawBlock("html",
    '<details class="' .. class .. '"' .. (open and " open" or "") .. '>' ..
    '<summary class="katlanir-baslik">' .. html_escape(title) .. '</summary>' ..
    '<div class="katlanir-govde">')
  local closing = pandoc.RawBlock("html", '</div></details>')

  local blocks = pandoc.List({ opening })
  -- In a Callout node the content may arrive as a single Block; in
  -- hand-written Divs it is a Blocks list.
  if content.t ~= nil then
    blocks:insert(content)
  else
    blocks:extend(content)
  end
  blocks:insert(closing)
  return blocks
end

-- --------------------------------------------------------- Quarto callouts

function Callout(el)
  local title_text = el.title and pandoc.utils.stringify(el.title) or ""
  local clean_title = strip_emoji(title_text)

  -- 1) Collapsible solution / proof blocks -> <details>
  if el.collapse then
    local title, kind = collapsible_title(clean_title)
    if title then
      return details_blocks(title, el.content, kind, false)
    end
  end

  -- 2) Strip emoji from the titles of the remaining callouts
  if el.title and clean_title ~= title_text then
    local clean = clean_inlines(title_inlines(el.title))
    if el.title.t == "Plain" or el.title.t == "Para" then
      el.title = pandoc.Plain(clean)
    else
      el.title = pandoc.Inlines(clean)
    end
    return el
  end

  return nil
end

-- ------------------------------------------ hand-written .cozum / .ispat

-- New content should prefer these classes over callouts:
--   ::: {.cozum}  …  :::
-- Optional attributes: baslik="Custom title", acik="true" (open by default).
function Div(el)
  local title, kind
  if el.classes:includes("cozum") then
    title = el.attributes["baslik"] or "Çözüm"
    kind = "cozum"
  elseif el.classes:includes("ispat") then
    title = el.attributes["baslik"] or "İspat"
    kind = "ispat"
  end

  if title then
    local open = el.attributes["acik"] == "true"
    return details_blocks(title, el.content, kind, open)
  end
  return nil
end

-- ---------------------------------------------------------- curriculum box

--[[
  The "Ders İçeriği" (course contents) lists on the books' index.qmd pages
  are written in two different shapes:

    A)  * **Group name**            B)  **Group name**
          * topic                       * topic
          * topic                       * topic

  The code below reduces both to shape B and wraps every run of consecutive
  groups in a single <div class="mufredat">. The CSS then needs no
  structural guessing (:has() chains), and the curriculum box can be drawn
  BELOW the section heading without swallowing the heading.

  Runs only on index.qmd pages; bold-paragraph + list sequences inside the
  lecture texts are left untouched.
]]

-- Quarto hands pandoc a temporary .md file, so PANDOC_STATE cannot reveal
-- the real source; Quarto's own API keeps the original path.
local function is_curriculum_page()
  local path = quarto and quarto.doc and quarto.doc.input_file
  if not path then return false end
  return path:match("[/\\]index%.qmd$") ~= nil
end

-- A Para/Plain whose only child is Strong?
local function is_label(block)
  return block ~= nil
    and (block.t == "Para" or block.t == "Plain")
    and #block.content == 1
    and block.content[1].t == "Strong"
end

-- Shape A: a bullet list whose every item is "**Group**" + a sub-list
local function is_group_list(block)
  if block == nil or block.t ~= "BulletList" or #block.content == 0 then
    return false
  end
  for _, item in ipairs(block.content) do
    if #item < 2 or not is_label(item[1]) then return false end
    if item[2].t ~= "BulletList" then return false end
  end
  return true
end

-- Shape A -> shape B: Para(Strong) + BulletList pairs
local function flatten_group_list(block)
  local result = pandoc.List({})
  for _, item in ipairs(block.content) do
    result:insert(pandoc.Para(item[1].content))
    for i = 2, #item do
      result:insert(item[i])
    end
  end
  return result
end

function Pandoc(doc)
  if not is_curriculum_page() then return nil end

  local blocks = doc.blocks
  local new_blocks = pandoc.List({})
  local i = 1

  while i <= #blocks do
    local box = pandoc.List({})

    -- Collect consecutive curriculum groups
    while true do
      if is_group_list(blocks[i]) then
        box:extend(flatten_group_list(blocks[i]))
        i = i + 1
      elseif is_label(blocks[i]) and blocks[i + 1] ~= nil
             and blocks[i + 1].t == "BulletList" then
        box:insert(pandoc.Para(blocks[i].content))
        box:insert(blocks[i + 1])
        i = i + 2
      else
        break
      end
    end

    if #box > 0 then
      new_blocks:insert(pandoc.Div(box, pandoc.Attr("", { "mufredat" })))
    else
      new_blocks:insert(blocks[i])
      i = i + 1
    end
  end

  doc.blocks = new_blocks
  return doc
end
