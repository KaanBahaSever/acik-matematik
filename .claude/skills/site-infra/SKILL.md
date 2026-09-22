---
name: site-infra
description: Site tasarımı ve altyapısı değişiklikleri için kullanılır. Kapsamı styles/global.css, Lua filtreleri (collapsible, downloads, export_*), build.py ve export.py hattı, _kitap-ortak.yml ve deploy.yml'dir; bilinen tuzakları, tasarım dilini ve bütün genişliklerde doğrulamayı içerir. Kullanıcı görünümle ilgili bir şey istediğinde ya da şikâyet ettiğinde ("içerik çok geniş", "mobilde kayıyor", "formülün üstü kesik", "kutular tasarıma uymuyor") veya bir Lua filtresine, derleme/export betiğine ya da CI'a dokunulacağında kullan.
---

# Tasarım ve altyapı yordamı

Bağlayıcı kurallar `.claude/rules/altyapi.md` dosyasındadır.

## 1. Önce oku

- `styles/global.css` bölümleri:
  - PAGE GRID
  - 1 tema değişkenleri
  - 2–3 kutu stilleri
  - 3b katlanır bloklar
  - 3c bağlantılar
  - 3d callout'lar
  - 10 mobil düzen, 10b mobil içindekiler
  - 11–13 çok bölümlü dersler ve müfredat
  - 15 denklem boşlukları
  - 17 ders içi çizimler
  - 3B sahneler, indirme paneli
- İlgili Lua filtresinin baş yorumunu da oku.

## 2. CSS tuzakları

- İçerik bağlantı kuralı `#quarto-document-content a:not(...)` yüksek özgüllüklüdür. Onu ezmek için aynı öneki ve aynı `:not` korumalarını kullan.
- `:has()` içinde `:has()` geçersizdir. `:is()` geçersiz bir argümanı sessizce yutar.
- `:has()` içeren seçiciyi ayrı bir kurala al ve `@supports not selector(:has(*))` yedeği ekle.
- `.theorem-title` ve `.remark-title`'a `display:inline-flex` verme. Boşluğu `::before` üzerinde `margin-right` ile ver.
- Kutu içindeki şekil ortalanır: `.theorem/.collapsible-body/.callout-body figure.ders-grafik { margin-left/right: auto }`.

## 3. Tasarım dilini koru

Genel ilke: sade ve animasyonsuz. Katalog yalnız hover'da renk değiştirir.

- **Callout'lar:** teorem kutularının kardeşi gibi çizilir. Bootstrap ikonu gizlidir; başlıkta glif, arka plan `--academic-bg`, sol şerit, `0 8px 8px 0` köşe kullanılır.
- **Callout glifleri:**

  | Tür | Glif ve stil |
  |---|---|
  | note | ✎, gri noktalı |
  | tip | ✦, turkuaz |
  | important | !, kiremit |
  | warning | △, amber kesikli |
  | caution | ◇, amber |

- **Kutu glifleri:** aynı görsel boyuttadır.
  - Teorem ▲. İspat şeridi de ▲'dır ve açılınca 180° döner.
  - Tanım ≡.
  - Örnek ve alıştırma ▷. Çözüm şeridi de ▷'dir ve açılınca 90° döner.
- **Bağlantılar:** içerik bağlantıları mavi ya da altı çizili değildir. Müfredat bağlantıları `--color-theory`, başlıklar `--color-base` rengindedir.
- **Müfredat sayfası:** içerik tek bir dış kutudadır, içinde küçük kutucuk olmaz. Alt ders `##` başlıkları kutunun dışında kalır. Boşluk büyük başlığın (h1) hemen altındadır.
- **Mobil:** listeler içeri kaymaz. Kutu başlığından hemen sonra gelen görüntü formülü başlığa yapışmaz.

## 4. Sayfa ızgarası

- Değişkenler:
  - `--am-page-max: 1880px`
  - `--am-edge: 1.25rem`
  - `--am-side: clamp(10.5rem,15vw,16rem)`
  - `--am-gap: 1.5em`
  - `--am-slack: clamp(1.5rem,3vw,4rem)`
  - `--am-content: 48rem`
- 1rem = 17,6px, çünkü kök yazı boyu 1.1em.
- Izgara `body.floating #quarto-content.page-layout-article` üzerinde kuruludur. 768–991 px için ayrı bir ızgara vardır.
- Portal sayfaları (`/`, `/dersler/`) Quarto'nun article ızgarasında kalır. Kitap düzeni onları etkilememeli.
- Mobil içindekiler `scripts/mobile-toc.html` ile ≤ 767.98px'te görünür.
- Kataloğa dönüş bağlantısı `_kitap-ortak.yml`'de `href="/../"` olarak kalır. Katalogdaki ders bağlantıları `ders-adi/` biçimindedir.

## 5. Lua filtreleri

- Quarto callout'ları kullanıcı filtresinden önce özel bir düğüme çevirir. Bu yüzden `Div` değil `Callout` işleyicisini kullan; `el.title` tek bir Block'tur.
- Kaynak yolu için `quarto.doc.input_file` kullan. Birleşik export render'ında bu değer `index.qmd` döner.
- Filtre listesi `_kitap-ortak.yml`'dedir. Filtre değişikliği 30 kitabı yeniden derletir.

## 6. Derleme ve export hattı

- Birimler, kökten tam iki seviye aşağıdaki tek kullanımlık `_export-src/<ders>/` kopyasından derlenir.
- Aynı dersin iki export'unu paralel çalıştırma; `.quarto` kilitlenir.
- Gereken ayarlar:
  - `book.author` zorunludur.
  - Tarih için ISO `date` ile `date-format` kullanılır.
  - PDF'in 25 MiB sınırı vardır.
- Hata ayıklama: `python scripts/export.py <ders> --keep`, ardından `cd _export-src/<ders> && quarto render --to typst`.
- Bilinen hata: `export_links.lua` kitap içi `../<altklasör>/x.qmd` bağlantılarını da siteye yönlendiriyor. Düzeltirken yalnız `dersler/<x>/_quarto.yml` olan kardeş kitapları yeniden yaz.

## 7. CI

- `CLAUDE.md`, `.claude/**`, README ve LICENCE değişiklikleri CI'ı tetiklemez (`paths-ignore`).
- Kurallar için `altyapi.md` dosyasına bak.

## 8. Doğrula

- CSS için `python scripts/build.py <ders> --no-export` yeterlidir.
- Lua ya da `_kitap-ortak.yml` değişikliğini önce tek kitapla dene.
- `check_layout.py` ile beş genişliği ölç. Açık ve koyu temaya, katalog ve portal sayfalarına da bak.
- Kök sebebi ölçümle kanıtla.

## 9. Raporla

Raporda site geneline etkiyi ve istenenin ötesinde yaptığın değişiklikleri açıkça yaz.
