# 🌿 Açık Matematik

Lisans matematik derslerinden derlenmiş; karmaşık el yazılarından arındırılmış, pürüzsüz dizgiye sahip (LaTeX/MathJax), tamamen açık kaynaklı ve reklamsız Türkçe not arşivi.

Bu proje, Türkçe matematik literatüründeki dağınık ve okunması zor kaynak problemini çözmek ve öğrenciler için erişilebilir bir dijital kütüphane yaratmak amacıyla oluşturulmuştur.

🌐 Canlı site: **[acik-matematik.com](https://acik-matematik.com)**

## 🏗️ Proje Mimarisi

Proje, standart bir web sitesi yerine **çoklu kütüphane (multi-project)** mimarisiyle inşa edilmiştir. Kök dizin bir portal (katalog) görevi görürken, her ders kendi içinde bağımsız ve otomatik numaralandırmalı birer **Quarto kitabı** olarak çalışır.

Bu sayede devasa müfredat birbirine karışmaz ve her ders kendi izolasyonunda saniyeler içinde derlenebilir.

```text
📂 acik-matematik/
├── 📄 _quarto.yml               # Portal ayarları (type: website)
├── 📄 _kitap-ortak.yml          # Tüm kitapların paylaştığı ortak ayarlar
├── 📄 index.qmd                 # Giriş ve karşılama sayfası
│
├── 📂 styles/
│   └── 📄 global.css            # Global tasarım (teorem kutuları, hesaplayıcılar…)
│
├── 📂 assets/                   # Favicon ve statik dosyalar
│
├── 📂 scripts/
│   ├── 📄 build.py              # Portalı + tüm kitapları derleyip _site'a toplar
│   ├── 📄 export.py             # Her dersi (alt dersleri) PDF/EPUB/DOCX olarak üretir
│   ├── 📄 collapsible.lua       # Pandoc filtresi: çözüm/ispat blokları, emoji temizliği, müfredat kutusu
│   ├── 📄 export_figures.lua    # Pandoc filtresi: gömülü SVG çizimleri PDF/EPUB/DOCX için şekle çevirir
│   ├── 📄 export_math.lua       # Pandoc filtresi: \tag, vmatrix, array gibi yapıları Typst'e uyarlar
│   ├── 📄 downloads.lua         # Pandoc filtresi: müfredat sayfasına indirme panelini ekler
│   ├── 📂 export-assets/        # Dışa aktarma şablonları: Typst altbilgi/kapak-lisans/gövde ayarları + EPUB meta verisi
│   ├── 📄 svg_plot.py           # Tema uyumlu, bağımlılıksız SVG çizim yardımcısı
│   ├── 📄 stochastic_figures.py # Raslantı Süreçleri grafiklerini üretir (çıktı .qmd'ye elle gömülür)
│   ├── 📄 complex_figures.py    # Kompleks Analiz grafiklerini üretir
│   ├── 📄 crypto_figures.py     # Kriptografi grafiklerini üretir
│   ├── 📄 analysis_figures.py   # Analiz grafiklerini üretir
│   └── 📄 finance_figures.py    # Finans Matematiği grafiklerini üretir
│
├── 📂 .github/workflows/
│   └── 📄 deploy.yml            # CI/CD: derle → Cloudflare Pages'e yayınla
│
└── 📂 dersler/                  # Müfredat arşivi
    ├── 📄 index.qmd             # Ders kataloğu (yönlendirme paneli)
    │
    ├── 📂 kriptografi/          # BAĞIMSIZ KİTAP
    │   ├── 📄 _quarto.yml       # Kitap ayarları (type: book)
    │   ├── 📄 index.qmd         # Müfredat ve giriş sayfası
    │   ├── 📂 kriptografiye-giris/
    │   ├── 📂 klasik-kriptografi-2/
    │   └── …
    │
    ├── 📂 sayilar-teorisi/      # BAĞIMSIZ KİTAP
    ├── 📂 raslanti-surecleri/   # BAĞIMSIZ KİTAP
    └── …                        # (toplam 27 ders)
```

### Ortak ayarlar nasıl yönetiliyor?

Her ders kitabının `_quarto.yml` dosyası, kök dizindeki ortak yapılandırmayı içeri alır:

```yaml
metadata-files:
  - ../../_kitap-ortak.yml
```

Böylece tema, tipografi, Türkçe teorem/tanım etiketleri (`Teorem`, `Tanım`, `Örnek`…) ve global CSS **tek bir yerden** yönetilir; 27 dosyada tekrar edilmez.

## 🚀 Yerel Geliştirme

Derlemek için sisteminizde [Quarto CLI](https://quarto.org/docs/get-started/) (1.9.17+; CI 1.9.38 kullanır — PDF dışa aktarmanın dayandığı Typst kitap şablonu bu sürümle gelir) ve Python 3.8+ kurulu olmalıdır.

**1. Projeyi klonlayın:**

```bash
git clone https://github.com/KaanBahaSever/acik-matematik.git
cd acik-matematik
```

**2. Tüm siteyi derleyin:**

```bash
python scripts/build.py
```

Bu komut önce portalı, ardından `dersler/` altındaki tüm kitapları derler ve hepsini `_site/` dizininde birleştirir.

**3. Tek bir dersi derleyin:**

Sadece üzerinde çalıştığınız dersi derleyerek çok daha hızlı ilerleyebilirsiniz:

```bash
python scripts/build.py kriptografi
```

**4. Canlı önizleme:**

Bir ders üzerinde çalışırken, o dersin klasöründe canlı önizleme başlatabilirsiniz:

```bash
cd dersler/kriptografi
quarto preview
```

**5. Yalnızca HTML (hızlı derleme):**

`build.py` her dersin PDF/EPUB/DOCX dosyalarını da üretir (aşağıya bakınız). Yalnızca web sürümüyle ilgileniyorsanız bu adımı atlayabilirsiniz:

```bash
python scripts/build.py kriptografi --no-export
```

## 📥 İndirilebilir Dosyalar (PDF / EPUB / DOCX)

Her ders — dönemlere bölünmüş derslerde her **alt ders** (Cebir 1, Cebir 2, Lineer Cebir 1/2 …) — ayrı bir PDF, EPUB ve DOCX dosyası olarak indirilebilir. Bağlantılar dersin müfredat sayfasındaki "Notları indirin" panelinde yer alır.

- **Üretim:** `scripts/export.py`, `build.py` tarafından her kitabın HTML derlemesinden önce çağrılır; elle de çalıştırılabilir:

  ```bash
  python scripts/export.py                    # tüm dersler
  python scripts/export.py soyut-cebir        # tek ders
  python scripts/export.py analiz --formats pdf
  ```

- **Alt dersler nereden bilinir?** Kitabın `index.qmd` sayfasındaki ikinci düzey başlıklardan (`## Cebir 1 — Grup Teorisi` gibi). Bir başlığın altında bağlantısı bulunan bölümler o alt dersin dosyasına girer; henüz hiç bölümü yazılmamış alt dersler ve yalnızca müfredat sayfasından ibaret kitaplar atlanır. Alt ders başlığı olmayan kitaplar (`## Ders İçeriği`) tek dosya olarak üretilir. Ayrıca — birden çok alt ders varsa ya da hiçbir alt ders başlığına bağlanmamış bölümler kaldıysa — kitabın tamamı da tek dosya olarak sunulur.
- **PDF nasıl üretiliyor?** LaTeX değil, Quarto ile birlikte gelen **Typst** kullanılır: ek kurulum gerektirmez, saniyeler içinde derlenir ve satır içi SVG çizimleri doğrudan vektör olarak basar. Kapak dışındaki her sayfanın altında site adresi ve lisans (CC BY-NC-SA 4.0), kapağın arkasındaki sayfada ise lisans açıklaması yer alır (`scripts/export-assets/`).
- **Üretim mekanizması:** Quarto profilleri `book.chapters` listesini değiştirmek yerine ona eklediğinden, her birim `_export-src/<ders>/` altındaki geçici bir kopyadan, üretilmiş bir `_quarto.yml` ile derlenir. Çıktılar `_export/<ders>/` altına yazılır, kitapla birlikte `_site/dersler/<ders>/` altına kopyalanır; `dersler/<ders>/_downloads.json` manifesti panelin kaynağıdır. Bu dizinlerin hepsi `.gitignore`'dadır.
- **Bilinmesi gerekenler:**
  - Alt ders dosyalarında bölüm numaraları 1'den başlar (site kitap boyunca kesintisiz numaralar); dosyanın kendi içindeki çapraz referanslar tutarlıdır. Kitabın ilk alt dersinde ve tek dosyalık kitaplarda numaralar siteyle birebir aynıdır (giriş sayfası numarasızdır).
  - Bir dışa aktarma başarısız olursa `build.py` her şeyi bitirdikten sonra hata koduyla çıkar; CI bunu ve "manifesti olup PDF'i olmayan ders" durumunu yakalar.
  - `\tag{…}` etiketleri, `vmatrix` ve `\begin{array}` (dikey/yatay çizgileriyle) Typst'e `export_math.lua` ile uyarlanır. Pandoc'un tanımadığı yeni bir LaTeX makrosu PDF derlemesini durdurur; `export.py` hangi dosyanın hangi yapıda takıldığını yazdırır, karşılığı `export_math.lua` içindeki `MACROS` tablosuna eklenir.
  - Etkileşimli hesaplayıcılar (yalnızca web) PDF'te tek satırlık bir notla belirtilir.
  - Typst etiketli PDF üretir; yapı ağacı sayfa başına yüzlerce küçük nesneden oluştuğu için uzun kitaplarda dosya şişer (Analiz 1: 420 sayfa, 21 MB). Makinede **PyMuPDF** kuruluysa (`pip install pymupdf`) `export.py` PDF'i nesne akışlarıyla yeniden yazar ve dosya üçte birine iner (6,6 MB); kurulu değilse bu adım sessizce atlanır. Cloudflare Pages tek dosyada 25 MiB sınırı koyduğundan CI'da da kurulması önerilir.
  - Tarih ("Bu sürüm") son commit'in tarihidir; aynı commit yeniden derlendiğinde dosyalar değişmez.

## 🌍 Yayınlama (CI/CD)

`main` dalına yapılan her push, GitHub Actions üzerinden şu adımları tetikler:

1. Quarto ve Python kurulur.
2. `scripts/build.py` ile tüm site derlenir (her dersin PDF/EPUB/DOCX dosyaları dâhil).
3. Çıktı doğrulanır (ana sayfa ve katalog üretilmiş mi, en az bir PDF var mı?).
4. `_site/` dizini **Cloudflare Pages**'e yayınlanır; üretim dağıtımı [acik-matematik.com](https://acik-matematik.com) özel alan adından yayınlanır (alan adı Cloudflare panelinde Pages projesine bağlıdır).

Pull request'ler için ayrıca birer önizleme dağıtımı oluşturulur.

### Gerekli GitHub ayarları

Depo ayarlarından şu değerlerin tanımlanması gerekir:

| Tür | Ad | Açıklama |
| :--- | :--- | :--- |
| Secret | `CLOUDFLARE_API_TOKEN` | Cloudflare Pages düzenleme yetkisine sahip API token |
| Secret | `CLOUDFLARE_ACCOUNT_ID` | Cloudflare hesap kimliği |
| Variable | `CLOUDFLARE_PROJECT_NAME` | (İsteğe bağlı) Pages proje adı — varsayılan: `acik-matematik` |

## 📚 Birden Fazla Alt Derse Bölünen Kurslar

Bazı dersler dönemlere ayrılır (Cebir 1 / 2 / 3, Analiz 1–4, Sayılar Teorisi 1–2 gibi). Bunlar **ayrı kitaplar değil, tek kitabın parçaları** olarak kurgulanır:

```yaml
book:
  chapters:
    - file: index.qmd            # Müfredat ve giriş

    - part: "Cebir 1 — Grup Teorisi"
      chapters:
        - 1/gruplar.qmd
        - 1/alt-devresel-gruplar.qmd

    - part: "Cebir 2 — Halkalar ve İdealler"
      chapters:
        - 2/halka-alt-halka.qmd
```

**Numaralandırma nasıl çalışır?** Quarto bölümleri kitap boyunca kesintisiz numaralandırır (1, 2, 3, …); numaralandırma her `part` başında sıfırlanmaz ve Quarto bunu değiştirmeye izin vermez. Bu davranış bilinçli olarak korunmuştur, çünkü:

- Çapraz referanslar (`Tanım 3.1`, `@thm-euler-fermat`) bölüm numarasını kullanır; numaralandırma sıfırlanırsa aynı numara kitapta birden fazla kez görünür ve bağlantılar belirsizleşir.
- Basılı ders kitaplarında da "kısım" başlıkları bölüm sayacını sıfırlamaz.

Alt dersler arasındaki ayrım numarayla değil, **sol menüdeki grup başlıklarıyla** yapılır: her `part`, üstünde ince bir ayraç çizgisi olan kalın bir başlık olarak görünür ve kendi bölümlerini içine alır.

**İçindekiler tarafında** ise alt dersler, kitabın `index.qmd` sayfasında ikinci düzey başlıklarla (`##`) ayrılır — böylece müfredat sayfası da sol menüyle aynı gruplamayı yansıtır. Örnek için [dersler/sayilar-teorisi/index.qmd](dersler/sayilar-teorisi/index.qmd) dosyasına bakabilirsiniz.

## ✍️ İçerik Yazım Standartları

Notlar yazılırken Quarto'nun yerleşik akademik ortamları kullanılır:

```markdown
::: {#def-ornek-tanim name="Tanımın Adı"}
Tanım metni burada.
:::

:::: {#exm-ornek-soru}
Soru metni burada.

::: {.cozum}
Çözüm adımları…

[$\blacksquare$]{.qed}
:::
::::
```

Dikkat edilecek noktalar:

- **Kimlik önekleri:** `#def-` (tanım), `#thm-` (teorem), `#lem-` (lemma), `#cor-` (sonuç), `#prp-` (önerme), `#exm-` (örnek), `#exr-` (alıştırma).
- **Çözüm ve ispat blokları:** `::: {.cozum}` ve `::: {.ispat}` kullanılır. [scripts/collapsible.lua](scripts/collapsible.lua) bunları tarayıcının kendi `<details>` öğesine çevirir; okuyucu başlığa tıklayınca açılır. Özel başlık için `::: {.cozum baslik="Alternatif çözüm"}`, varsayılan açık gelmesi için `acik="true"` yazılabilir.
- **İç içe bloklar:** Dış blok, iç bloktan bir fazla iki nokta üst üste alır (`::::` dışta, `:::` içte).
- **İspat sonu işareti:** `[$\blacksquare$]{.qed}` veya `[$\boxtimes$]{.qed}`.
- **Matematik:** Satır içi `$…$`, blok `$$…$$`. MathJax'te bulunmayan komutlardan (`\centernot` gibi) kaçının.
- **Ondalık ayırıcı:** Türkçe metinde virgül — matematik modunda `$0{,}6$` biçiminde yazılır.
- **Callout başlıkları:** Emoji yazabilirsiniz; filtre çıktıda otomatik temizler. Bölüm başlıklarındaki emojilere dokunulmaz.
- **Grafikler:** Çizimler derleme sırasında üretilmez. `scripts/svg_plot.py` yardımcısıyla yazılmış üretici betikler (`scripts/complex_figures.py`, `scripts/crypto_figures.py`, `scripts/stochastic_figures.py`, `scripts/analysis_figures.py`, `scripts/finance_figures.py`) çalıştırılır, ardından `scripts/center_figures.py` her çizimin görünür içeriğini ölçüp viewBox'ı ortalar (varsayılan desen `complex-*.md`'dir; başka bir ders için desen verilir: `python scripts/center_figures.py "analysis-*.md"`); çıktı `scripts/_figures/*.md` dosyalarına yazılır ve ilgili `.qmd` dosyasına elle yapıştırılır. Bir teoremi, ispatı, örneği ya da çözümü açıklayan grafik **o kutunun içine**, anlattığı adımın hemen yanına konur; kutudan çıkarılırsa bağlam kopar. Yalnızca **tanım kutularının** (`def-…`) içine grafik konmaz — tanım kısa kalır, grafik kutunun altına gelir. SVG'ler tema renklerini CSS değişkenlerinden (`--color-theory` vb.) aldığı için açık ve koyu temada doğru görünür.

## 🤝 Katkıda Bulunma

Eksik bir ispat, hatalı bir işlem veya eklenmesini istediğiniz yeni bir teorem mi gördünüz? Bu arşiv hepimizin.

**Dil kuralı:** İçerik (notlar, başlıklar, arayüz metinleri, grafik etiketleri) Türkçe; **kod İngilizce** yazılır — `scripts/` altındaki betikler ve Lua filtreleri, `styles/global.css` (yorumlar ve sınıf adları), YAML yapılandırma yorumları, CI iş akışı ve `.qmd` içine gömülü JavaScript dâhil. Yalnızca notların yazım sözlüğü (`::: {.cozum}`, `.ispat`, `baslik=`, `acik=`, `ders-grafik`) Türkçe kalır.

1. Bu depoyu **fork**'layın.
2. Yeni bir dal oluşturun: `git checkout -b ozellik/yeni-teorem`
3. Değişikliklerinizi yapın ve yukarıdaki yazım standartlarına uyun.
4. Yerelde derleyip kontrol edin: `python scripts/build.py <ders-adi>`
5. Commit edin: `git commit -m "Analiz 1 — Bolzano-Weierstrass ispatı eklendi"`
6. Dalınızı push'layın ve bir **pull request** açın.

## 📜 Lisans

Bu proje **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** ile lisanslanmıştır. Eseri ticari olmayan amaçlarla paylaşabilir ve uyarlayabilirsiniz; ancak uygun atıf yapmalı ve aynı lisansla dağıtmalısınız. Detaylar için `LICENCE` dosyasına bakınız.
