---
name: run-checks
description: Bir .qmd, şekil, CSS ya da altyapı değişikliğinden sonra, teslimden ve commit'ten önce çalıştırılan denetim zinciri. Kapsamı yapısal kontroller, kutu ve formül denetimleri, derleme, derlenmiş HTML ve PDF taraması ve düzen ölçümüdür. Kullanıcı "kontrol et", "derle", "commit öncesi bak" dediğinde, bir hata düzeltmesini doğrularken ya da write-chapters, make-figures ve site-infra becerilerinin son adımında kullan.
---

# Teslim öncesi denetim

Hedef şudur: yeni ya da değişen içerikte her denetim 0 sorun vermeli. Eski kitaplardaki bilinen pürüzler (aşağıda) bu işin kapsamı dışındadır; onları toplu düzeltme.

## 1. Değişen dosyalarda yapısal kontrol

Depoda yapısal denetçi yok. Değişen `.qmd` dosyalarında şunları kontrol et; gerekiyorsa scratchpad'de küçük bir betik yaz:

- **Fence dengesi:** Açılış ve kapanış kolon sayıları eşleşmeli. Açılış regex'i greedy olmalı: `^(:{3,})\s*\{(.*)\}\s*$`. `[^}]*` kalıbı `name="$5^{2n}$"` gibi adları kaçırır. ``` blokları atlanır.
- **Etiketler:**
  - Kitap genelinde yinelenen etiket olmamalı.
  - `[a-z0-9-]` dışında karakter içeren etiket olmamalı.
  - Çözümlenmeyen `@etiket` olmamalı.
- **İspat ve çözüm blokları:**
  - `.ispat`/`.cozum` bloğu bir kutunun içinde olmalı.
  - Her blok bir `]{.qed}` işaretiyle bitmeli. konveks-analiz çözümleri bundan muaftır.
- **Frontmatter:** `pagetitle:` eksik olmamalı.
- **Şekiller:**
  - Kalmış `FIGURE:` yer tutucusu olmamalı.
  - `<!--FIG:ad-->` yorumu kalıcı bir çapadır. Yalnız arkasından bir ```` ```{=html} ```` `<figure>` bloğu gelmiyorsa hatadır.
  - Tanım kutusunun içinde `<figure` olmamalı.
  - `##` başlığın hemen altında şekil olmamalı.
- **Dosya:** CRLF, BOM ve `$` dengesizliği olmamalı.

Bilinen eski etiket ihlalleri, `@` atıfları da güncellenmeden yeniden adlandırılmaz:

- `sec-nEx`, `def-nEx` (finans-matematigi)
- `thm-koprü`, `thm-uA`, `thm-P-us-n` (raslanti-surecleri)
- `cor-a-uzeri-N` (soyut-cebir)

## 2. Kutu başına tek soru

`python scripts/check_box_questions.py <dosyalar.qmd>` çıkış kodu 0 olmalı.

Betiğin gerçek kör noktaları, bu yüzden şüpheli kutuları elle de oku:

- Numaralı `1.` maddelerini saymaz.
- `.cozum baslik=…` ve `.ispat baslik=…` bloklarını bölmez.
- Eski `callout collapse="true"` çözümlerini bölmez.
- Adında `}` geçen kutuyu atlar.
- Tek satırda yazılmış `**a)** … **b)**` şıklarını tek parça sayar.

## 3. Formül genişliği

`python scripts/check_math_width.py <ders> [--limit N]`

- Yeni ya da değişen formüller bütçe içinde olmalı: satır içi 16,5em, kutu içinde 14,5em, görüntü formülü 34em.
- Betik her zaman 0 döner, bu yüzden çıktıyı oku.
- Aşan formülleri `$$…$$` ve `aligned` ile böl.

## 4. Hızlı grep'ler

Hepsini `--include=*.qmd` ile, yalnız değişen dosyalarda çalıştır:

- `grep -nE 'name="[0-9]+\.'` boş dönmeli.
- `grep -niE 'sınav|vize|final|hoca|ödev|kaynakta|cevap anahtar'` boş dönmeli. Masum kullanımları elle ayıkla.
- Yazım: yeni metinde `\emptyset`, `rasgele`, `keyfî` geçmemeli.

## 5. Derle

`python scripts/build.py <ders>` çalıştır. Uzun sürerse arka planda başlat ve bildirimi bekle. Yalnız HTML gerekiyorsa `--no-export` ekle.

- Çıkış 1 render hatası, 2 export hatası ya da 25 MiB aşımı demektir.
- PDF de gerekiyorsa ve kitap daha önce `--no-export` ile derlendiyse, ya da `scripts/export.py` veya `export-assets` değiştiyse, `--force` ekle. Yoksa değişmemiş kitap atlanır ve PDF hiç üretilmez.
- `WinError 32` görürsen `_site`'ı tutan `http.server`'ı kapat ve yeniden çalıştır.
- Portal adımındaki ara sıra görülen "failed to render" hatası çoğu zaman yeniden çalıştırınca geçer.

## 6. Derlenmiş HTML'i tara

Tarama `_site/dersler/<ders>/` altında yapılır, `_book` altında değil. Beklenen sayılar:

| Kontrol | Beklenen |
|---|---|
| Çözülmemiş `?@` ya da `?sec-` atıf | 0 |
| `<ol start=` ve tek `<li>`'li `<ol>` (kazara liste) | 0 |
| Ham `:::` kalıntısı | 0 |
| Kırık göreli bağlantı | 0 |

Sekme başlıkları numarasız olmalı.

## 7. PDF ve EPUB

- `_export/<ders>/*.pdf` var olmalı ve 25 MiB'ın altında kalmalı.
- Çok birimli derslerde her birim `dersler/<ders>/_downloads.json` içinde yer almalı.
- İlgili sayfaları `pymupdf` ile PNG'ye render edip bak.
- İki arama tuzağı:
  - PDF'te şekil etiketi bölünmez boşlukludur (`Şekil\xa0N.M`).
  - Typst'in "fi" bağlacı metin aramasını yanıltabilir.

## 8. Düzen (CSS, şekil ya da yerleşim değiştiyse)

`python scripts/check_layout.py dersler/<ders>/<sayfa>.html --widths 390,768,1280,1920,2560` çalıştır ve `SONUC` satırını oku. Betik taşmada da 0 döner.

Kendi ölçümün için:

- Probe ya da kopya HTML'i sayfanın kendi klasörüne yaz, yoksa göreli CSS yüklenmez ve taşma yanlışlıkla 0 çıkar. Dosyayı `finally` içinde sil.
- `<details>` içini görmek için kopyada `<details open` kullan.
- Başsız Chrome pencereyi ~485 px'in altına indirmez; dar genişlikleri iframe içinde ölç.

## 9. Raporla

- Her denetimin sayısını ver: dosya, kutu, etiket, atıf, sorun, taşma, PDF sayfa sayısı.
- Ölçmeden "temiz" deme. Yanlış yere yazılan probe ve sessizce başarısız olan sed/regex daha önce sahte 0 sonucu üretti.
