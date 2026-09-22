# Açık Matematik: çalışma kuralları

Lisans matematik derslerinin açık kaynaklı, reklamsız Türkçe not arşivi. Quarto ile üretilir ve https://acik-matematik.com adresinde yayındadır. Depo herkese açıktır: bu dosyaya ve `.claude/` altına kişisel yol, kaynak dosya adı ya da gizli bilgi yazma.

## Nerede ne var

- `dersler/<ders>/`: her ders bağımsız bir Quarto kitabıdır. Bir `_quarto.yml`, müfredat sayfası olarak `index.qmd` ve bölüm `.qmd` dosyalarından oluşur. Ortak ayarlar `_kitap-ortak.yml`'den gelir. Kitap kökten tam iki seviye aşağıda olmalı; aksi hâlde Lua filtreleri ve Türkçe etiketler sessizce kaybolur.
- Analiz dört ayrı kitaptır (`dersler/analiz-1` … `analiz-4`); `dersler/analiz/` yalnız hub sayfasıdır. Diğer çok dönemli dersler (Lineer Cebir 1–2, Sayılar Teorisi 1–2, …) tek kitapta `part:` ile bölünür ve bölüm numaraları kitap boyunca kesintisiz akar.
- Kök `_quarto.yml` yalnız portalı (ana sayfa, katalog) basar. Bütün stil `styles/global.css`'tedir.
- `scripts/`: derleme, dışa aktarma, denetim ve şekil betikleri.

## Ayrıntılı kurallar ve yordamlar

- `.qmd` yazım kuralları `.claude/rules/qmd-yazim.md` dosyasındadır. Ders dosyalarıyla çalışırken bu dosyayı oku.
- CSS, betik ve CI kuralları `.claude/rules/altyapi.md` dosyasındadır.
- Beceriler (skills):
  - `write-chapters`: kaynaktan bölüm yazma
  - `run-checks`: teslim öncesi denetim
  - `make-figures`: şekiller
  - `site-infra`: tasarım ve derleme altyapısı
- `proof-checker` alt ajanı ispat ve hesap denetimi yapar. Her bölüm bitince bir kez çağrılır, ikinci tur yapılmaz.

## Dil

- Görünen her şey Türkçedir: ders metni, başlıklar, şekil etiketleri, arayüz metni.
- Kod İngilizcedir: Python, Lua, Typst, CSS sınıf ve değişken adları, gömülü JS, CI adımları, yeni yorumlar, yeni betiklerin konsol çıktıları, commit mesajları. Eski Türkçe yorumları çevirmekle uğraşma.
- `.qmd` yazım sözlüğü Türkçe kalır ve yeniden adlandırılmaz (`.ispat`, `.cozum`, `baslik=`, `acik=`, `ders-grafik*`), çünkü `scripts/collapsible.lua` bu adları okur.
- Yeni metinde emoji kullanılmaz. İstisnalar: site markası "🌿 Açık Matematik", katalog grup başlıkları ve README.

## İçerik ilkeleri

1. **Yeniden anlatım, çeviri değil.** Kaynak bizzat okunur, metin elle yazılır; kaynak içerik betikle çevrilmez ya da dönüştürülmez. Mevcut metinde toplu terim değişimi ya da atıf dönüşümü betikle yapılabilir, ama üretilen her biçim tek tek gözden geçirilir (ünlü uyumu, alt dize eşleşmesi).
2. **Sade, açık, samimi Türkçe.** Akış şöyledir: motivasyon, tanım, "Yani …" açıklaması, bol örnek. Kaynakta örnek azsa çoğaltılır. Her ispat adımı gerekçelidir ve yalnız temiz son hâl yazılır.
3. **Eksiksizlik.** Kaynaktaki tanım, teorem, ispat ve örnekler atlanmaz, özetlenmez. Boş bırakılmış ispat ve çözümler de yazılır; metinde eklendikleri söylenmez.
4. **Bağımsız ders metni.** Not; hocaya, kaynak dosyaya, sınava ya da ödeve atıf yapmaz. Kaynaktaki hata sessizce düzeltilir.
5. **Kitabın sesine uy.** Yazmadan önce kitabın mevcut `.qmd` dosyalarını tara. Gösterim, terimler, etiket düzeni, kutu derinliği ve zorluk düzeyi kitaptan alınır. Ders o noktaya kadar tanımlamadığı bir aracı kullanmaz.
6. **Tekrar yok.** Aynı kavram kitapta ya da kardeş kitapta ikinci kez tanımlanmaz; mevcut tanıma bağlantı verilir. İleri derslerde temel ön bilgi yeniden anlatılmaz.
7. **Her sayıyı doğrula.** Gösterilen her sayısal sonuç ve ara adım scratchpad'de bağımsız Python ile (`fractions.Fraction`, sympy) yeniden hesaplanır. Doğrulama betikleri depoya girmez.
8. **Bölümleme.**
   - Kaynağın açık bir haftalık programı ya da alıştırma blokları varsa bölümler onu izler; fazladan dosyaya bölünmez.
   - Kaynak dağınıksa konular akademik akışa göre sıralanır.
   - Emin değilsen önce planı göster.

## Derleme ve denetim

- Daima `python scripts/build.py <ders>` ile derle ve yalnız üzerinde çalıştığın dersi derle (`--no-export` yalnız HTML üretir). Kökte çıplak `quarto render` çalıştırma: `_site`'ı ve içindeki 30 kitabı siler.
- Seçenekler: `python scripts/build.py [ders...] [--no-export] [--force] [--jobs N] [--serial]`. `--help` yoktur, bilinmeyen bayrak hata verir.
- Çıkış kodları:
  - 1: render hatası
  - 2: export hatası ya da 25 MiB'ı aşan dosya
- Önbellek `.build-cache.json` dosyasındadır.
  - `styles/`, `assets/` ve şekil betikleri parmak izine girmez; bunlar değişince derleme yalnız dosyaları kopyalar.
  - `scripts/export.py` ya da `scripts/export-assets/` değiştiyse, ya da kitap daha önce `--no-export` ile derlendiyse, PDF için `--force` ekle.
- Görsel kontrol `_site/`'ta yapılır, `_book/`'ta değil.
- Teslimden önce `run-checks` becerisini uygula. CI hiçbir denetim çalıştırmaz. `check_math_width.py` ve `check_layout.py` sorun bulsalar da 0 döner, bu yüzden çıktılarını oku.
- README'deki `BOOKS` ve `METRICS` bölgelerini her derlemede `scripts/stats.py` yazar; elle düzenleme. Diff'te kitap sayısı beklenenden farklıysa commit etme.

## Git

- `git push` asla çalıştırılmaz; yayını kullanıcı yapar. Commit yalnız kullanıcı isteyince atılır. İş bitince commit edilmemiş dosyaları raporla.
- Commit mesajı İngilizce ve emir kipindedir. Ders işlerinde Türkçe ders adı öneki alır, ör. `Diferansiyel Geometri: add the Frame Fields part (6 chapters)`. Gövdede nedeni ve ölçülen sayıları yaz.
- Yayındaki bir sayfanın adresi değişecekse `git mv` kullan ve bölüme `aliases:` ya da kitap düzeyinde `_redirects` ekle. Mevcut yönlendirmeleri silme.
- Yeni worktree boş başlar (`_site`, `.build-cache.json` ve `scripts/_figures` yoktur). Yalnız ilgili dersi derle; şekil düzenlemeden önce ilgili `*_figures.py` betiğini çalıştır.

## Windows ortamı

- Ters bölü içeren içeriği (LaTeX, `.qmd`, CSS) Bash heredoc ile yazma, çünkü `\b`, `\v`, `\r` gibi diziler bozulur. Write/Edit aracını, Python'da da ham dizge (`r"…"`) kullan.
- Türkçe basan Python betiklerinde `sys.stdout.reconfigure(encoding="utf-8")` çağır. Dosyaları UTF-8 (BOM'suz) ve LF (`newline="\n"`) olarak yaz.
- `dersler/` üzerinde grep'i `--include=*.qmd` ile sınırla. Ana klasörden çalışırken `.claude/` klasörünü dışarıda bırak, çünkü içinde worktree kopyaları var.
