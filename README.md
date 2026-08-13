# 📐 Açık Matematik

Lisans matematik derslerinden derlenmiş; karmaşık el yazılarından arındırılmış, pürüzsüz dizgiye sahip (LaTeX/MathJax), tamamen açık kaynaklı ve reklamsız Türkçe not arşivi.

Bu proje, Türkçe matematik literatüründeki dağınık ve okunması zor kaynak problemini çözmek ve öğrenciler için erişilebilir bir dijital kütüphane yaratmak amacıyla oluşturulmuştur.

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
│   └── 📄 build.py              # Portalı + tüm kitapları derleyip _site'a toplar
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

Derlemek için sisteminizde [Quarto CLI](https://quarto.org/docs/get-started/) (1.9+) ve Python 3.8+ kurulu olmalıdır.

**1. Projeyi klonlayın:**

```bash
git clone https://github.com/KaanBahaSever/math-notebook.git
cd math-notebook
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

## 🌍 Yayınlama (CI/CD)

`main` dalına yapılan her push, GitHub Actions üzerinden şu adımları tetikler:

1. Quarto ve Python kurulur.
2. `scripts/build.py` ile tüm site derlenir.
3. Çıktı doğrulanır (ana sayfa ve katalog üretilmiş mi?).
4. `_site/` dizini **Cloudflare Pages**'e yayınlanır.

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
- **Çözüm ve ispat blokları:** `::: {.cozum}` ve `::: {.ispat}` kullanılır. [scripts/katlanir.lua](scripts/katlanir.lua) bunları tarayıcının kendi `<details>` öğesine çevirir; okuyucu başlığa tıklayınca açılır. Özel başlık için `::: {.cozum baslik="Alternatif çözüm"}`, varsayılan açık gelmesi için `acik="true"` yazılabilir.
- **İç içe bloklar:** Dış blok, iç bloktan bir fazla iki nokta üst üste alır (`::::` dışta, `:::` içte).
- **İspat sonu işareti:** `[$\blacksquare$]{.qed}` veya `[$\boxtimes$]{.qed}`.
- **Matematik:** Satır içi `$…$`, blok `$$…$$`. MathJax'te bulunmayan komutlardan (`\centernot` gibi) kaçının.
- **Ondalık ayırıcı:** Türkçe metinde virgül — matematik modunda `$0{,}6$` biçiminde yazılır.
- **Callout başlıkları:** Emoji yazabilirsiniz; filtre çıktıda otomatik temizler. Bölüm başlıklarındaki emojilere dokunulmaz.

## 🤝 Katkıda Bulunma

Eksik bir ispat, hatalı bir işlem veya eklenmesini istediğiniz yeni bir teorem mi gördünüz? Bu arşiv hepimizin.

1. Bu depoyu **fork**'layın.
2. Yeni bir dal oluşturun: `git checkout -b ozellik/yeni-teorem`
3. Değişikliklerinizi yapın ve yukarıdaki yazım standartlarına uyun.
4. Yerelde derleyip kontrol edin: `python scripts/build.py <ders-adi>`
5. Commit edin: `git commit -m "Analiz 1 — Bolzano-Weierstrass ispatı eklendi"`
6. Dalınızı push'layın ve bir **pull request** açın.

## 📜 Lisans

Bu proje **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** ile lisanslanmıştır. Eseri ticari olmayan amaçlarla paylaşabilir ve uyarlayabilirsiniz; ancak uygun atıf yapmalı ve aynı lisansla dağıtmalısınız. Detaylar için `LICENCE` dosyasına bakınız.
