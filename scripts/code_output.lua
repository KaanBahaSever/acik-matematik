--[[
  Açık Matematik — code and output cards (HTML only)

  The programming notes write a program and its output like this:

      ```python
      print(2 + 3)
      ```

      Çıktı:

      ```text
      5
      ```

  On the page these were three loose blocks. This filter groups them into a
  single card: a "Python" strip above the code, and below it an "Çıktı"
  (output) strip followed by the output. A python block without an output
  still gets its strip, and an output that stands alone (in the problem
  chapters the code sits in the question and only the output is in the
  solution) becomes an output-only card.

  Emitted classes, a contract with styles/global.css (section "CODE AND
  OUTPUT CARDS"): code-run, code-run--output-only, code-run-label,
  code-output, code-output-label.

  The PDF and EPUB keep the plain blocks, so the filter does nothing there.
]]

local function is_html_output()
  return quarto and quarto.doc and quarto.doc.is_format("html")
end

local function is_python(block)
  return block ~= nil and block.t == "CodeBlock" and block.classes:includes("python")
end

local function is_output_label(block)
  return block ~= nil and block.t == "Para" and #block.content == 1
    and block.content[1].t == "Str" and block.content[1].text == "Çıktı:"
end

local function is_text(block)
  return block ~= nil and block.t == "CodeBlock" and block.classes:includes("text")
end

local function strip(text, class)
  return pandoc.Div({ pandoc.Plain({ pandoc.Str(text) }) }, { class = class })
end

local function output_part(code_block)
  return pandoc.Div({ strip("Çıktı", "code-output-label"), code_block },
                    { class = "code-output" })
end

function Blocks(blocks)
  if not is_html_output() then return nil end
  local result = pandoc.List({})
  local i = 1
  local changed = false
  while i <= #blocks do
    local b = blocks[i]
    if is_python(b) then
      local card = pandoc.List({ strip("Python", "code-run-label"), b })
      local step = 1
      if is_output_label(blocks[i + 1]) and is_text(blocks[i + 2]) then
        card:insert(output_part(blocks[i + 2]))
        step = 3
      end
      result:insert(pandoc.Div(card, { class = "code-run" }))
      i = i + step
      changed = true
    elseif is_output_label(b) and is_text(blocks[i + 1]) then
      result:insert(pandoc.Div({ output_part(blocks[i + 1]) },
                               { class = "code-run code-run--output-only" }))
      i = i + 2
      changed = true
    else
      result:insert(b)
      i = i + 1
    end
  end
  if changed then return result end
  return nil
end
