--[[
  Açık Matematik — ortak Pandoc/Quarto filtresi

  İki iş yapar:

  1) Callout (not / ipucu / uyarı) başlıklarındaki emojileri temizler.
     Kaynak dosyalarda başlık emojili yazılabilir; çıktıda sade görünür.

  2) Katlanabilir "Çözüm" ve "İspat" bloklarını, Bootstrap akordiyonu yerine
     tarayıcının kendi <details> öğesine çevirir.

     Gerekçe: callout kutusu içine gömülü ikinci bir kutu, mobilde çift
     çerçeve ve çift girinti oluşturup okunaksız hale geliyordu. <details>
     hem çok daha az işaretleme üretir, hem JavaScript gerektirmez, hem de
     ekran okuyucularda doğru şekilde "genişletilebilir bölge" olarak duyulur.

  Not: Quarto callout'ları okuma aşamasında özel bir AST düğümüne çevirdiği
  için bunlar normal bir Div filtresiyle yakalanamaz; aşağıdaki `Callout`
  işleyicisi Quarto'nun özel düğüm API'sini kullanır.
]]

-- ---------------------------------------------------------------- yardımcılar

-- Emoji ve süsleme sembollerini kapsayan kod noktası aralıkları.
-- Matematik operatörleri (U+2200–U+22FF) ve oklar (U+2190–U+21FF) bilinçli
-- olarak DIŞARIDA bırakıldı; başlıklarda geçebilirler.
local emoji_araliklari = {
  { 0x1F000, 0x1FAFF },  -- emoji blokları
  { 0x2600,  0x27BF  },  -- çeşitli semboller, dingbatlar
  { 0x2300,  0x23FF  },  -- teknik semboller
  { 0x2B00,  0x2BFF  },  -- geometrik şekiller
  { 0xFE00,  0xFE0F  },  -- varyasyon seçiciler
  { 0x1F1E6, 0x1F1FF },  -- bayrak harfleri
  { 0x200D,  0x200D  },  -- zero-width joiner
}

local function emoji_mi(kod)
  for _, aralik in ipairs(emoji_araliklari) do
    if kod >= aralik[1] and kod <= aralik[2] then return true end
  end
  return false
end

local function emojileri_sil(metin)
  local parcalar = {}
  for _, kod in utf8.codes(metin) do
    if not emoji_mi(kod) then
      parcalar[#parcalar + 1] = utf8.char(kod)
    end
  end
  local temiz = table.concat(parcalar)
  return (temiz:gsub("^%s+", ""):gsub("%s+$", ""))
end

-- Quarto'nun Callout düğümünde başlık tek bir Block (genellikle Plain)
-- olarak tutuluyor; elle kurulan durumlarda Inlines da olabilir.
-- Her iki durumu da Inlines'a indirger.
local function baslik_inlines(baslik)
  if baslik == nil then return nil end
  if baslik.t == "Plain" or baslik.t == "Para" then
    return baslik.content
  end
  return baslik
end

-- Inlines içindeki metinlerden emojileri temizler, boşalan Str'leri atar.
local function inlinelari_temizle(inlines)
  local sonuc = pandoc.List({})
  for _, il in ipairs(inlines) do
    if il.t == "Str" then
      local temiz = emojileri_sil(il.text)
      if temiz ~= "" then sonuc:insert(pandoc.Str(temiz)) end
    else
      sonuc:insert(il)
    end
  end
  -- Baştaki boşlukları at (emoji silinince yalnız kalmış olabilirler)
  while #sonuc > 0 and (sonuc[1].t == "Space" or sonuc[1].t == "SoftBreak") do
    sonuc:remove(1)
  end
  while #sonuc > 0 and (sonuc[#sonuc].t == "Space" or sonuc[#sonuc].t == "SoftBreak") do
    sonuc:remove(#sonuc)
  end
  return sonuc
end

local function html_kacis(metin)
  return (metin:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

-- Katlanabilir bloğun başlığı "Çözüm" mü "İspat" mı? Değilse nil.
-- İkinci dönüş değeri blok türüdür; CSS'te açılır kapanır üçgenin yönünü
-- belirlemek için kullanılır (Çözüm örnekle, İspat teoremle aynı sembolü alır).
local function katlanir_basligi(baslik_metni)
  local kucuk = pandoc.text.lower(baslik_metni)
  if kucuk:find("^çözüm") then return "Çözüm", "cozum" end
  if kucuk:find("^ispat") or kucuk:find("^i̇spat") then
    -- "İspat: bu formüller nereden geliyor?" gibi açıklamalı başlıkları koru
    return baslik_metni, "ispat"
  end
  return nil
end

-- <details> bloğu üret
local function detay_bloklari(baslik, icerik, tur)
  local sinif = "katlanir katlanir--" .. (tur or "ispat")
  local ac = pandoc.RawBlock("html",
    '<details class="' .. sinif .. '">' ..
    '<summary class="katlanir-baslik">' .. html_kacis(baslik) .. '</summary>' ..
    '<div class="katlanir-govde">')
  local kapa = pandoc.RawBlock("html", '</div></details>')

  local bloklar = pandoc.List({ ac })
  -- Callout düğümünde içerik tek bir Block olarak da gelebiliyor,
  -- elle yazılan Div'lerde ise Blocks listesi olarak geliyor.
  if icerik.t ~= nil then
    bloklar:insert(icerik)
  else
    bloklar:extend(icerik)
  end
  bloklar:insert(kapa)
  return bloklar
end

-- --------------------------------------------------------- Quarto Callout'ları

function Callout(el)
  local baslik_metni = el.title and pandoc.utils.stringify(el.title) or ""
  local temiz_baslik = emojileri_sil(baslik_metni)

  -- 1) Katlanabilir Çözüm / İspat blokları -> <details>
  if el.collapse then
    local katlanir, tur = katlanir_basligi(temiz_baslik)
    if katlanir then
      return detay_bloklari(katlanir, el.content, tur)
    end
  end

  -- 2) Diğer callout'ların başlığındaki emojileri temizle
  if el.title and temiz_baslik ~= baslik_metni then
    local temiz = inlinelari_temizle(baslik_inlines(el.title))
    if el.title.t == "Plain" or el.title.t == "Para" then
      el.title = pandoc.Plain(temiz)
    else
      el.title = pandoc.Inlines(temiz)
    end
    return el
  end

  return nil
end

-- ---------------------------------------------- Elle yazılan .cozum / .ispat

-- Yeni içerik yazarken callout kullanmadan doğrudan bu sınıflar tercih
-- edilebilir:  ::: {.cozum}  …  :::
function Div(el)
  local baslik, tur
  if el.classes:includes("cozum") then
    baslik = el.attributes["baslik"] or "Çözüm"
    tur = "cozum"
  elseif el.classes:includes("ispat") then
    baslik = el.attributes["baslik"] or "İspat"
    tur = "ispat"
  end

  if baslik then
    return detay_bloklari(baslik, el.content, tur)
  end
  return nil
end
