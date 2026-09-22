---
paths:
  - "styles/**"
  - "scripts/**"
  - "assets/**"
  - "_quarto.yml"
  - "_kitap-ortak.yml"
  - ".github/**"
---

# Altyapı kuralları (CSS, betikler, CI)

## CSS

- Renkleri `:root` belirteçleriyle yaz ve koyu tema karşılığını da ver. Belirteçler: `--academic-bg`, `--academic-text`, `--color-theory`, `--color-base`, `--color-practice`, `--color-remark`.
  - Aynı palet `scripts/export_figures.lua` ve `scripts/center_figures.py` içinde de var. Birini değiştirirsen üçünü birlikte güncelle.
- Mobil taşma:
  - Kaydırma kabı (`overflow-x: auto`) şunların üzerindedir: `p`, `dd`, `blockquote`, `figcaption`, `ol/ul`, `table`.
  - `li`'ye asla konmaz, çünkü madde işareti kırpılır. `body`/`html`'e de asla konmaz, çünkü yapışkan kenar çubuğu bozulur.
  - `mjx-container[display]` üzerindeki dolgu ve görünür ince kaydırma çubuğu kaldırılmaz. Dolgu yoksa formülün tepesi kesilir, çubuk yoksa taşma görünmez.
- Lua filtrelerinin ürettiği sınıf adları CSS ile sözleşmedir: `.collapsible*`, `.downloads*`, `.curriculum`, `.landing*`, `.course-list`, `.catalog-back`, `.calculator`, `.calc-*`.
- CSS ya da düzen değişikliğini ölçmeden teslim etme.
  - Genişlikler: telefon (390), tablet (768), masaüstü (1280, 1920) ve ultra geniş (2560). Açık ve koyu temaya bak.
  - Komut: `python scripts/check_layout.py dersler/<ders>/<sayfa>.html --widths 390,768,1280,1920,2560`. Betik taşma olsa da 0 döner; `SONUC` satırını oku.
  - Görsel bir şikâyette kök sebebi önce ölçerek bul.

## Derleme ve dışa aktarma

- Bir Lua filtresi ya da `_kitap-ortak.yml` değişikliği bütün kitapları yeniden derletir; önce tek kitapla dene.
- İndirilebilir dosyalar PDF (Typst) ve EPUB'dur; DOCX yoktur.
  - Her PDF sayfasının altında site adresi ve CC BY-NC-SA 4.0 lisansı bulunur (`scripts/export-assets/footer.typ`). EPUB'da `dc:rights` tanımlıdır. Export'u değiştirirken bunları koru.
  - Dosyalardaki "Bu sürüm" tarihi son commit'ten gelir.
- `_site`'ı `python -m http.server` ile sunduysan iş bitince kapat; açık kalırsa derleme `WinError 32` ile düşer.

## CI

- `.github/workflows/deploy.yml` self-hosted bir Windows runner'da çalışır.
- Adımlar yalnız `shell: powershell` ile yazılır; bash ve kurulum adımı eklenmez.
- Fork PR'larına karşı job düzeyindeki `if:` koruması ve `secrets.*` kullanımı olduğu gibi kalır. Sır değerleri asla yazdırılmaz.
- Derleme sırasında kod yürüten hiçbir şey eklenmez.

## Depo düzeni

- Depoya yalnız kalıcı ve belgelenmiş araçlar girer; tek seferlik betikler scratchpad'de kalır.
- Yeni bir altyapı dosyası (Lua filtresi, betik) eklersen nedenini kullanıcıya açıkla.
