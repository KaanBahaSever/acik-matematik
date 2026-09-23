---
name: make-figures
description: Ders şekillerini (ders-grafik SVG) ekler, düzeltir, siler ya da yeniden üretir. Adımlar üretici betik, center_figures, PNG ile gözle kontrol ve .qmd kutusuna yerleştirmedir; diferansiyel geometri için etkileşimli 3B sahneleri de kapsar. Kullanıcı "grafik/şema ekle", "şu şekil yanlış/ortalı değil/çok büyük", "diyagram az" dediğinde ya da bir taslakta `<!-- FIGURE: … -->` yer tutucusu kaldığında kullan.
---

# Şekil yordamı

## 1. Hazırlık

- `scripts/_figures/` gitignore'dadır ve yeni bir worktree'de bulunmaz; önce ilgili üretici betiği çalıştır.
- `center_figures.py` için `rsvg-convert` PATH'te, Pillow da kurulu olmalı.

## 2. Betiği seç

Önekler:

| Betik | Önek |
|---|---|
| `analysis_figures.py` | `analysis-` |
| `analysis2_figures.py` | `analysis2-` |
| `complex_figures.py` | `complex-` |
| `convex_figures.py` | `convex-` |
| `crypto_figures.py` | `crypto-` |
| `diffgeo_figures.py` | `diffgeo-` |
| `finance_figures.py` | `finance-` |
| `probability_figures.py` | `probability-` |
| `topology_figures.py` | `topology-` |
| `stochastic_figures.py` | `figA`…`figG` (ortalanmaz) |
| `real_analysis_figures.py` | `real-` |
| `analytic_figures/<anahtar>.py` | `analytic-<anahtar>-` |
| `statistics_figures/<anahtar>.py` | `statistics-<anahtar>-` |

Yeni bir ders için `scripts/<konu>_figures.py` dosyasını İngilizce yaz:

- 2B için `svg_plot.py`, 3B için `svg_plot3.py` üzerine kur (Camera/Space; azimut 35°, yükseklik 22°).
- Docstring doğru `dersler/<ders>` yolunu ve "figures go INSIDE the box they explain" kuralını söylemeli.
- `complex_figures.py` ve `crypto_figures.py` docstring'lerindeki "always OUTSIDE boxes" cümlesi eskidir; uyma.

## 3. Şekli yaz

- Her şekil kendi `"# " + "="*60` bantlı bölümünde durur: `figure(W, H, panels, caption, css_class="ders-grafik" | WIDE, aria="...")`.
- Renkler için `THEORY`, `BASE`, `PRACTICE`, `REMARK`, `TEXT`, `BG` sabitlerini kullan; sabit hex yazma.
- `Plot.label(x, y, s, dx, dy, …)`: dx/dy pikseldir ve pozitif dy aşağı demektir.
- `aria` metni yalnız ASCII olur ve `<`/`>` içermez (rsvg XML hatası verir). Altyazı Türkçedir.
- Fonksiyon ve dağılım grafiklerinde eksenler etiketlidir; ızgara için `Plot.grid()` var.

## 4. Tuzaklar

- **Kırpma:** `Plot` kırpma yapmaz. Sınırsız nesneleri (hiperdüzlem, yarı düzlem, koni, asimptot) panele kırp. Hazır yardımcılar: `analysis2_figures.py`'de `clipped()`, `convex_figures.py`'de `clip_seg`/`clip_poly`.
- **Oran:** Gerçek daire ve Venn için x ve y ölçeği eşit olmalı (`YR = XR*PH/PW`).
- **Yazı tipi glifleri:** rsvg yazı tipinde ∪ ∖ ∈ ⊂ ⊆ ⋯ ∅ ∧ ∨ ¬ ⇒ ∥ kutucuk çıkar; sözcük, ASCII ya da HTML varlığı kullan. ∩ ≤ ≥ ≠ − ∞ → ℝ ℕ √ π sorunsuzdur.
- **Yazı tipi ailesi:** Üretilen SVG'ye asla `font-family` (özellikle Georgia) yazma; Typst derlemesi kilitlenmişti. Birleşik üst çizgiyi `export_figures.lua` zaten işler.
- **Dolgu:** Opak dolgulu daire içeriği örter; yarı saydam dolgu kullan.
- **Etiket yeri:** Eğik bir doğrunun yanına yatay etiket koyma; etiketi karşı tarafa ya da boş banda taşı.

## 5. Üret ve ortala

1. `python scripts/<x>_figures.py`
2. Ardından HER seferinde `python scripts/center_figures.py "<önek>-*.md"`. Desen verilmezse yalnız `complex-*.md` işlenir. Kare şekillerin dar sütuna (24rem) düşmemesi gereken kitaplarda (ör. analitik-geometri) `--keep-width` ekle.
3. `python scripts/check_figure_labels.py "scripts/_figures/<önek>-*.md"` sonucu `problems: 0` olmalı: çakışan etiketleri, noktayı örten etiketi, tuvalden taşan ve 10 px'ten küçük yazıyı bulur. Çizgi–etiket çakışmasını görmez; onu gözle kontrol et.

center_figures viewBox'ı içeriğe 14 birim pay bırakarak kırpar. Oran ≥ 0,72 olan geniş olmayan şekle `ders-grafik-dar` ekler.

## 6. Gözle kontrol et

- Yeni ya da değişen her şekli açık ve koyu temada `rsvg-convert` ile PNG'ye çevir ve Read ile incele.
- Aranacaklar: etiket çakışması, kırpma, yanlış tarafı boyanmış yarı düzlem, viewBox şişmesi.
- Şekildeki sayılar, aralıklar ve parametreler ait olduğu kutunun metniyle birebir aynı olmalı.
- Kullanıcı yanlış bir şema bildirirse aynı türdeki bütün şekilleri kendi çözümleriyle karşılaştır.

## 7. Yerleştir

- `scripts/_figures/<önek>-<ad>.md` içeriğini (```` ```{=html} ```` bloğu) .qmd'de açıkladığı kutunun İÇİNE, ilgili paragrafın hemen altına yapıştır.
- Tanım kutusuna koyma, hemen altına koy. `##` başlığın hemen altına da koyma.
- Güncellemede eski bloğu `aria-label` ile bul ve bloğun tamamını değiştir.
- Gömülü SVG'yi elle düzeltme.
- Karşılaştırma yaparken satır sonlarını normalleştir: üretici betikler Windows'ta CRLF yazar, .qmd dosyaları LF'tir.
- Silme: .qmd bloğunu, betikteki bantlı bölümü ve `scripts/_figures` dosyasını birlikte kaldır.

## 8. Seçim ve boyut

- Kavramı görselleştiren ya da ispat fikrini taşıyan şekil konur; teoremi yalnız resimle tekrar eden şekil konmaz.
- Boyutlar:
  - `.ders-grafik`: 30rem
  - `.ders-grafik-genis` (WIDE, çok panelli): 39rem
  - `.ders-grafik-dar`: 24rem
- Bu CSS değerleri bütün dersleri etkiler; değiştirirsen kullanıcıya söyle.

## 9. Etkileşimli 3B (yalnız diferansiyel-geometri)

- ```` ```{ojs} ```` hücresinde `//| echo: false` ve `import {…} from "../ojs/scene3d.js"` kullanılır. Plotly `plotly.js-dist-min@2.35.2` ile yüklenir.
- Sahne `:::: {.content-visible when-format="html:js"}` içinde durur, `.cozum` içinde değil.
- OJS değişkenleri sayfa genelidir; her sahne kendi önekini kullanır.
- PDF ve EPUB için aynı yere durağan bir SVG de konur.

## 10. Doğrula

`python scripts/build.py <ders>` çalıştır. Ardından şekle `_site`'ta (kutu içinde ve ortalı mı) ve PDF'te bak.
