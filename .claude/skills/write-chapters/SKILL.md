---
name: write-chapters
description: Bir kaynak PDF'ten ya da müfredat başlığından ders bölümü yazar, mevcut kitaba bölüm, alıştırma ya da soru ekler. Kaynağı okuma, plan, yazım, sayısal doğrulama, şekil, kitaba bağlama, ispat denetimi, derleme ve rapor adımlarını kapsar. Kullanıcı "şu dersi/bölümü yaz", "masaüstündeki PDF'ten notları çıkar", "müfredattaki eksik başlıkları tamamla" ya da "bu soruları kitaba ekle" dediğinde kullan. Tek cümlelik bir düzeltme, yalnız şekil ya da yalnız CSS işi için kullanma.
---

# Bölüm yazma yordamı

Bağlayıcı kurallar `CLAUDE.md` ve `.claude/rules/qmd-yazim.md` dosyalarındadır. Başlamadan ikisini de oku.

## 1. Kapsamı sabitle

- Hangi dersin tam olarak hangi kısımlarının yazılacağını netleştir. Kullanıcı "sadece 3 kısım" dediyse yalnız o kısımlar yazılır.
- `dersler/<ders>/` zaten var mı bak. 30 kitap var ve 14'ü yalnız iskelettir; yeni ders açmak yerine mevcut kitabı doldur.
- Claude belleğinde `<ders>-kaynak-ve-uretim` notu varsa önce onu oku. Notta kaynak yolu, etiket anahtarları, sessizce düzeltilmiş hatalar ve kullanıcı kararları bulunur.
- Kullanıcının oturum bütçesi kuralına uy (bellekte). Büyük işi bölümlere ayır; her bölümü bitir ve teslim et.

## 2. Kaynağı oku

- Önce `import pymupdf` ile `page.get_text()` dene.
- Metin boşsa ya da formüller bozuksa:
  - Sayfaları 110–125 DPI PNG olarak scratchpad'e render et.
  - Read ile mesaj başına en çok 4 görsel oku.
  - Her partiden hemen sonra scratchpad'deki not dosyasına özet yaz.
  - Boş dönen görseli okunmuş sayma, yeniden oku.
- Aynı klasörde md5'i eşit dosyaları bir kez oku.
- Birden çok aday dosya varsa ilk sayfalarını oku ve hangisinin kullanılacağını sor.

## 3. Planla

`scratchpad/PLAN.md` dosyasını hazırla:

- Her bölümün hangi kaynak sayfalarına karşılık geldiğini yaz.
- Bölümlemeyi `CLAUDE.md`'deki ilkeye göre yap. Boş bırakılmış ispat ve çözümleri "EKLE" diye işaretle.
- Aynı konu bu kitapta ya da kardeş kitapta (ST1/ST2, Analiz 1/2, LC1/LC2) var mı ara. Önce etiketlere bak (`grep -rn '{#def-' dersler/<ders> --include=*.qmd`), sonra konu adlarıyla ara. Konu varsa yeniden tanımlama, bağlantı ver.
- Yapı belirsizse planı kullanıcıya göster.

## 4. Yazım sözleşmesi (büyük işlerde)

`scratchpad/STYLE.md` dosyasını hazırla:

- İngilizce kaynaksa Türkçe terim tablosu.
- Kitabın `.qmd` dosyalarından taranmış mevcut gösterim.
- Kitabın kutu derinliği (bkz. qmd-yazim tablosu).
- Her bölüm için kısa ve tekil bir etiket anahtarı (`<önek>-<anahtar>-<ad>`).
- Şekil yer tutucusu: `<!-- FIGURE: ad | tarif -->` (ad `[a-z0-9-]+`).

İş birden çok oturum sürecekse sözleşmenin bir kopyasını scratchpad dışında kalıcı bir klasöre koy, çünkü scratchpad oturumla birlikte kaybolur.

## 5. Yaz

- Write aracıyla yaz (UTF-8, LF, heredoc yok).
- Bölüm sırası:
  1. Frontmatter
  2. 1–3 motivasyon paragrafı
  3. `##` başlıklar
  4. Tanım kutusu ve ardından "Yani …"
  5. Teorem kutusu ve içinde `.ispat`
  6. Her örnek ya da alıştırma kutusunda tek soru ve `.cozum`
  7. `## Alıştırmalar`: hepsi çözümlü
  8. Sonraki bölüme bağlantı veren kapanış
- Kullanıcının kendi yazdığı kısımları yeniden yazma; yalnız matematiğini doğrula.
- Düzenlemeden önce dosyayı yeniden oku, çünkü kullanıcı turlar arasında kendisi değişiklik yapıyor.

## 6. Sayısal doğrula

- Kaynaktaki ve senin yazdığın her sayıyı, gösterilen her ara adımı scratchpad'de bağımsız Python ile yeniden hesapla. Bunlara Gauss-Jordan adımları, tersler, ara çarpanlar ve olasılıklar dahildir.
- Araçlar: `fractions.Fraction`, sympy, numpy (`np.trapezoid`).
- Tutmayan yeri düzelt. Kaynak hatasını metne değil, ders bellek notuna yaz.

## 7. Şekiller

Yer tutucuları `make-figures` becerisiyle üret ve yerleştir. İş bitince hiç yer tutucu kalmamalı.

## 8. Kitaba bağla

- Bölümü `dersler/<ders>/_quarto.yml` içindeki `chapters`/`part:` listesine ekle.
- `index.qmd`'de doğru `##` başlığının altına bağlantısını koy.
- Müfredat sayfasının `description`'ını gerekiyorsa güncelle.

## 9. Tutarlılık taraması (yalnız yeni ya da değişen metinde)

- `\emptyset` → `\varnothing`, "rasgele" → "rastgele", "keyfî" → "keyfi".
- `grep -rniE 'sınav|vize|final|hoca|ödev|kaynakta|cevap anahtar' <dosyalar>` boş dönmeli. Konuya ait masum kullanımları elle ayıkla.
- Taşımadan ya da bölmeden sonra "bir sonraki bölümde" gibi göreli geçişleri ve silinen kutulara yapılan atıfları düzelt.

## 10. İspat denetimi (bölüm başına bir kez)

- Bitmiş bölümü `proof-checker` alt ajanına ver. Dosya yollarını ve kitabın gösterimine dair kısa bir notu ekle.
- Dönen bulguları kendin değerlendir: doğru olanları düzelt, yanlış alarmları gerekçesiyle geç.
- İkinci tur denetim yapma.

## 11. Denetle ve derle

`run-checks` becerisini uygula.

## 12. Belleği güncelle

`<ders>-kaynak-ve-uretim` bellek notuna şunları yaz:

- kaynak yolu ve türü (metin katmanı var mı)
- bölüm yapısı ve etiket anahtarları
- şekil betiği ve öneki
- sessizce düzeltilen kaynak hataları
- bilerek yazılmayan konular
- kullanıcının derse özel kararları

MEMORY.md'ye tek satırlık bir işaretçi ekle.

## 13. Rapor (Türkçe)

- Kullanıcının maddelerine madde madde karşılık ver.
- İstenenin ötesinde verdiğin kararları, veto edebilsin diye açıkça yaz.
- Sessiz düzeltmeleri; bölüm, kutu ve şekil sayılarını; denetim ve derleme sonuçlarını listele.
- Commit edilmemiş dosyaları listele. İstenirse commit mesajı öner. Push yok.

## Çok ajanlı çalışma

Yalnız oturum modu (ör. ultracode) ya da kullanıcının açık isteği varsa kullanılır:

- Bölüm başına tek yazar olur; yazarlar ayrık dosyalarda çalışır.
- `_quarto.yml`'e ve derlemeye yalnız birleştirici dokunur.
- Tek hakem turu yapılır.
- Düşen ajanları yalnız başarısız olanlar için yeniden başlat.
- Ajanlar şekil hatalarını bulamaz; şekilleri PNG'ye bakarak kendin denetle.
