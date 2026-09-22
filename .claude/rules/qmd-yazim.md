---
paths:
  - "dersler/**/*.qmd"
  - "dersler/**/_quarto.yml"
---

# .qmd yazım kuralları

## Dosya ve frontmatter

- Dosya adı küçük harfli, tireli ve Türkçe karaktersiz bir slug'dır (`cekirdek-ve-goruntu.qmd`). Taşımada `git mv` kullan.
- Frontmatter sırası `title` → `pagetitle` → `description`.
  - `pagetitle` numarasızdır ve kitap adı içermez; sekme başlığı olarak görünür.
  - `description` içeriği özetleyen, özgün ve SEO'ya uygun tek bir cümledir.
- Yeni bölümü hem `_quarto.yml`'deki `chapters`/`part:` listesine hem de `index.qmd` müfredat listesine ekle; bağlantısız bölüm PDF ve EPUB'a girmez. Hiçbir bölüm "Giriş" adını taşımaz.

## Kutular

- Önekler: `def`, `thm`, `lem`, `cor`, `prp`, `exm`, `exr`. Aksiyomlar `def-` kutusunda verilir. `rem`, `cnj` ve `alg` kullanılmaz.
- Etiketler:
  - Yalnız `[a-z0-9-]` içerir, sayıyla başlamaz ve kitap genelinde tekildir. Sayılar Teorisi 1 ile 2 aynı ad alanını paylaşır.
  - Yeni kitaplarda biçim `<önek>-<bölüm-anahtarı>-<ad>` olur. Yeni etiket vermeden önce kitapta ara.
  - `{#sec-…}` kimlikleri tamamen küçük harflidir.
- Kutu adı (`name="…"`) rakam ve noktayla başlamaz; "24. …" öneki sessizce yutulur.
- Başlıklara ve kutu adlarına elle numara yazma, Quarto numaralar. İstisna: müfredat sayfasındaki `## 1. Bölüm — …` alt ders başlıkları, çünkü export birim adları bunlardan üretilir.
- İspat ve çözüm, ait olduğu kutunun İÇİNDE `::: {.ispat}` ya da `::: {.cozum}` olarak durur.
  - Bu bloklar varsayılan olarak kapalıdır. `baslik="…"` özel başlık verir, `acik="true"` bloğu açık başlatır.
  - Eski `callout collapse="true"` kalıbını yeni yazımda kullanma.
- İki nokta derinliği kitaba göre değişir. Mevcut kitabı asla yeniden girintileme:

  | Derinlik (dış / iç) | Kitaplar |
  |---|---|
  | 4 / 3 | analiz-1, analiz-2, diferansiyel-geometri, olasilik-teorisi, sayilar-teorisi, topoloji, diferansiyel-denklemler, finans-matematigi |
  | 3 / 3 | kompleks-analiz, lineer-cebir, soyut-cebir-1, matematigin-temelleri, kismi-diferansiyel-denklemler |
  | tanım 4; ispatlı kutu 5 / 4 | konveks-analiz |
  | içinde ispat ya da çözüm olmayan kutu 3; olan kutu 4 / 3 | yeni kitaplar |

- Her ispat ve çözüm bir `{.qed}` işaretiyle biter. Yeni yazımda `[$\blacksquare$]{.qed}` kullan. Mevcut `\boxtimes` işaretlerine ve konveks-analiz'in işaretsiz çözümlerine dokunma.
- **Her `exm-` ya da `exr-` kutusu tek soru içerir.**
  - (a)(b)(c) şıkları ayrı kutulara bölünür. Etiketler `-a`, `-b` gibi sonek alır, `name` değerleri farklı ve açıklayıcı olur, ortak kurulum her kutuda kısaca yinelenir.
  - Her alıştırmanın adım adım bir `.cozum` bloğu vardır; tek satırlık "Yanıt:" yazılmaz.
  - Kontrol: `python scripts/check_box_questions.py <dosyalar>`.
- Bir tanım kutusu tek kavram içerir; birbirini tamamlayan ikilikler istisnadır.
  - Atıf yapılan ya da alıştırmalarda kullanılan bir kavram düz metinde kalmaz, bir `def-` kutusuna alınır.
  - Bir sınıflandırmada her tür kendi kutusunda olur.
  - Tanımdan sonra "Yani …" diye başlayan sade bir açıklama gelir.
- Callout'ları seyrek kullan (note, tip, warning, important).
  - `.cozum`/`.ispat` bloklarının ve örnek kutularının içine callout koyma.
  - Bir yöntem öğretilirken önce "X adımda …" başlıklı kısa bir `callout-tip` reçetesi, hemen ardından onu uygulayan çözümlü örnek gelir.

## Metin ve gösterim

- Yeni yazımda bir `##` başlığın hemen altına önce bağlayıcı bir cümle gelir. Hiçbir kitapta başlığın hemen altına şekil konmaz. Mevcut bölümleri bu kural için yeniden yazma.
- Bölüm, sonraki bölüme `[Ad](dosya.qmd)` bağlantısı veren kısa bir kapanışla biter.
- Satır başındaki `19.`, `II.`, `(f)` gibi diziler kazara liste açar. Kapanış ayracını kaçır: `19\.`, `II\.`, `(f\)`. Açılış ayracını asla kaçırma, çünkü `\(` LaTeX'tir.
- Atıf:
  - Kitap içinde `@etiket` kullanılır.
  - lineer-cebir ve soyut-cebir-1 `@` kullanmaz, yalnız dosya bağlantısı kullanır. Topoloji bölüm içinde `@`, bölümler arasında dosya bağlantısı kullanır.
  - Kitaplar arasında `@` çalışmaz; biçim `bkz. [Analiz 1](../analiz-1/<bölüm>.html#etiket)` olur.
  - Yeni yazımda `@sec-…'ndeki` gibi atfa bitişik ek yazma. Mevcut olanları toplu düzeltme.
- Gösterim:
  - Ondalık ayırıcı virgüldür: `$0{,}6$`.
  - Boş küme `\varnothing`.
  - Parçalı fonksiyonda `\text{diğer durumlarda}`.
  - Yazımlar "rastgele" ve "keyfi".
  - `\tag{n}` numaraları bölüm içinde 1'den sırayla artar.
- Teknik tuzaklar:
  - MathJax'ta olmayanlar: `\centernot`, `psmallmatrix`.
  - Alt ve üst integral `\underline{I}(f)`, `\overline{I}(f)` diye yazılır; `\underline{\int}` Typst'i bozar.
  - Pandoc'un tanımadığı yeni bir makro PDF'i durdurur. Karşılığını `scripts/export_math.lua` içindeki `MACROS` tablosuna ekle.
- İngilizce kaynaklı kitaplarda terimin İngilizcesi ilk geçişte parantez içinde verilir. Türkçe kaynaklı kitaplarda kitabın mevcut alışkanlığına uy.
- Mobil genişlik bütçesi:
  - Satır içi formül en çok 16,5em, kutu içinde 14,5em.
  - Görüntü formülü en çok 34em.
  - Uzun hesabı `$$ … $$` ve `aligned` ile böl: satır sonu `\\[1mm]`, devam satırı `&\quad`. Bölerken adımları silme.
  - Kontrol: `python scripts/check_math_width.py <ders>`.
- Çözümler dersin o noktada öğrettiği yöntemle yapılır; daha ileri bir yöntem ancak ek yol olarak verilir. Σ içeren karmaşık ifadeler terim terim açılır. Zor bir problemden önce gerekirse kolaydan zora 2–3 ısınma sorusu çözülür.

## Şekiller

- Şekil, açıkladığı teorem, ispat, örnek, çözüm ya da callout kutusunun İÇİNDE durur: ilgili paragrafın hemen altında ve ortalı. Tanım kutusunun içine değil, hemen altına konur. Bir çözümün farklı adımları ayrı şekillerdir.
- Derleme sırasında yürütülen kod hücresi (python, r, Jupyter) yoktur. Şekiller `scripts/*_figures.py` ile üretilip `.qmd`'ye gömülür; ayrıntılar `make-figures` becerisinde. Tek istisna diferansiyel-geometri'deki, tarayıcıda çalışan OJS 3B sahneleridir.
- Gömülü SVG elle düzeltilmez: üretici betik düzeltilir ve şekil yeniden üretilir.

## Müfredat sayfası (`index.qmd`)

- YAML:
  - `title: "# Müfredat ve Giriş {.unnumbered}"`
  - `pagetitle: "Müfredat ve Giriş"`
  - `description`
  - `number-sections: false`
- Sayfada kısa bir giriş ve yalnız bağlantılardan oluşan bir liste bulunur.
- `scripts/export.py` her `##` başlığını bir alt ders (ayrı PDF/EPUB) sayar.
  - "Ders İçeriği", "İçindekiler", "Müfredat" ve "Konular" genel başlıklardır ve tek birim demektir.
  - Alt ders olmayan içerik için `##` açma, callout kullan.
- Sayfa başındaki tek satırlık `callout-note appearance="simple"` durum notu bir gelenektir, zorunlu değildir.
- Şunlar eklenmez: "Notların kullanımı", sınav ya da notlandırma bilgisi, "yazım aşamasındaki başlıklar" grubu.
- Kaynağın kapsamadığı müfredat başlıkları bazı derslerde bağlantısız kaldı, bazılarında silindi. Mevcutlara dokunma; yeni bir derste kullanıcıya sor.
- İndirme panelini `downloads.lua` sayfanın sonuna kendisi ekler. Panele açıklama cümlesi ekleme.
