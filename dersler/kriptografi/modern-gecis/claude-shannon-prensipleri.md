# Claude Shannon Prensipleri

Klasik şifrelerin (Sezar, Afin, Vigenère) tamamı sonunda kriptanalistlere boyun eğmiştir çünkü metnin içindeki dilden kaynaklı istatistiksel izleri (örneğin İngilizcedeki 'E' harfi sıklığını) tam olarak yok edememişlerdir. 

1949'da Bilgi Kuramı'nın (Information Theory) babası **Claude Shannon**, bir şifreleme sisteminin "kırılamaz" olması için istatistiksel analizleri tamamen işe yaramaz hale getirecek iki temel prensip tanımlamıştır: **Karışıklık (Confusion)** ve **Yayılma (Diffusion)**.

Modern sistemlerin kalbini oluşturan bu iki kavramı anlamak, dijital kriptografiyi anlamak demektir.

## 1. Karışıklık (Confusion)

Karışıklık prensibinin tek bir amacı vardır: **Şifreli metin ($\mathcal{C}$) ile Anahtar ($\mathcal{K}$) arasındaki ilişkiyi olabildiğince karmaşık ve çözülemez hale getirmek.**

Eğer düşman, şifreli metin üzerinde bir istatistiksel analiz yaparsa, kullandığımız anahtar hakkında en ufak bir ipucu bile elde edememelidir. Anahtarın bir biti bile şifreli metnin karakterini tamamen değiştirmelidir.

* **Nasıl Sağlanır?** Karışıklık genellikle **Yerine Koyma (Substitution)** algoritmalarıyla sağlanır. Klasik dönemdeki Sezar ve Afin şifreleri çok basit Karışıklık örnekleridir. Modern şifrelerde (örneğin AES algoritmasında) bu işlem karmaşık, doğrusal olmayan **S-Kutuları (Substitution Boxes)** ile gerçekleştirilir.

## 2. Yayılma (Diffusion)

Yayılma prensibinin amacı ise şudur: **Açık metnin ($\mathcal{P}$) istatistiksel yapısını, şifreli metnin ($\mathcal{C}$) tamamına yayarak yok etmek.**

Açık metindeki tek bir harf veya tek bir bit değiştiğinde, şifreli metindeki *birçok* harf veya bit değişmelidir. Böylece açık metindeki dilden kaynaklı kalıplar (tekrar eden heceler, sık kullanılan harfler) şifreli metnin içinde adeta eriyip kaybolur.

* **Nasıl Sağlanır?**
  Yayılma işlemi genellikle **Yer Değiştirme (Permutation / Transposition)** algoritmalarıyla sağlanır. Klasik dönemdeki Hill Şifrelemesi (matris çarpımı sayesinde) çok güçlü bir Yayılma örneğidir. Modern şifrelerde bu işlem **P-Kutuları (Permutation Boxes)** veya karmaşık bit kaydırmaları ile yapılır.

::: tip 🏔️ Kriptografinin Kutsal Kasesi: Çığ Etkisi (Avalanche Effect)
Yayılma (Diffusion) prensibinin ne kadar başarılı çalıştığı **Çığ Etkisi** ile ölçülür. 

Eğer açık metinde veya anahtarda **sadece 1 bitlik** ufak bir değişiklik yaptığınızda, şifreli metnin bitlerinin yaklaşık **%50'si (yarısı)** tamamen rastgele bir şekilde değişiyorsa, o sistemde muazzam bir Çığ Etkisi var demektir. 

Dağın tepesinden yuvarlanan tek bir kar topunun (1 bit), aşağı indiğinde devasa bir çığa (metnin yarısının değişmesine) dönüşmesi gibi düşünülebilir. Modern AES ve SHA-256 algoritmaları kusursuz bir Çığ Etkisine sahiptir.
:::

## 🧩 Çarpım Şifreleri (Product Ciphers) ve SPN Yapısı

Shannon, sadece Karışıklık (Substitution) veya sadece Yayılma (Permutation) kullanmanın tek başına yeterli güvenliği sağlamadığını fark etti. Çözüm olarak bu iki işlemi art arda, defalarca kez tekrar eden bir yapı önerdi.

Bu birleşik yapılara **Çarpım Şifreleri (Product Ciphers)** denir.

Modern şifreleme standartlarının temelini oluşturan **SPN (Substitution-Permutation Network)** mimarisi bu fikirden doğmuştur. Veri bloğu sisteme girer:
1. **S-Box (Karışıklık):** Veri bitleri kendi içinde başka bitlerle değiştirilir.
2. **P-Box (Yayılma):** Değişen bu bitlerin yerleri (sıralamaları) karıştırılarak tüm bloğa dağıtılır.
3. Bu döngü (Raund) aynı veri üzerinde 10, 12 veya 16 kez tekrar edilerek mesaj kırılamaz bir beton bloğa dönüştürülür.

### 📊 Klasik Şifrelerin Shannon Analizi

Bugüne kadar öğrendiğimiz klasik şifrelerin Shannon prensipleri açısından durumunu bir tabloyla özetleyelim:

| Algoritma | Karışıklık (Confusion) | Yayılma (Diffusion) | Genel Güvenlik Analizi |
| :--- | :---: | :---: | :--- |
| **Sezar Şifresi** | Var (Çok Zayıf) | Yok | İstatistiksel frekansları korur, saniyeler içinde kırılır. |
| **Afin Şifreleme** | Var (Orta) | Yok | Tek harf tek harfe dönüştüğü için frekans analiziyle kırılır. |
| **Vigenère Şifresi** | Var (Çoklu) | Yok | Çığ etkisi yoktur, Kasiski metodu ile şifre boyu bulunup kırılır. |
| **Hill Şifreleme** | Yok | **Var (Güçlü)** | Matris ile bitler yayıldığı için dönemine göre devrimseldir. |
| **Modern AES** | **Mükemmel** | **Mükemmel** | S ve P kutularını defalarca tekrarlayarak kusursuz güvenlik sağlar. |