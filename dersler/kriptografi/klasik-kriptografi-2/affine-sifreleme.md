<script setup>
/* Klasör yolunu, md dosyasının ve .vitepress klasörünün konumuna göre ayarlayabilirsin */
import AffineCalculator from '/.vitepress/components/AffineCalculator.vue'
</script>

# Affine (Afin) Şifreleme

Sezar şifrelemesi, harfleri sadece sabit bir miktar kaydırarak (toplama işlemiyle) gizler. Affine (Afin) şifreleme ise bu mantığı bir adım ileri taşıyarak, modüler aritmetik üzerinde hem **çarpma** hem de **toplama** işlemini aynı anda kullanan doğrusal (lineer) bir yerine koyma algoritmasıdır.

Klasik cebirdeki $y = ax + b$ doğru denkleminin, alfabe (mod $26$) üzerine inşa edilmiş halidir.

## Sistemin Formal Tanımı

Afin şifrelemesinde anahtarımız ($k$) artık tek boyutlu bir skaler değil, **$k = (a, b)$** şeklinde tanımlanan sıralı bir sayı ikilisidir. Sistemi 5 bileşenli yapıya uyarlarsak:

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Afin Şifrelemesinin Matematiksel Modeli

  </div>
  
  * **Açık Metin ($\mathcal{P}$):** $\mathbb{Z}_{26} = \{0, 1, 2, \dots, 25\}$
  * **Şifreli Metin ($\mathcal{C}$):** $\mathbb{Z}_{26} = \{0, 1, 2, \dots, 25\}$
  * **Anahtar Uzayı ($\mathcal{K}$):** $k = (a, b)$ formunda olmak üzere; $a, b \in \mathbb{Z}_{26}$ ve $\gcd(a, 26) = 1$ koşulunu sağlayan tüm sıralı ikililerin kümesi.
  * **Şifreleme Fonksiyonu ($\mathcal{E}$):** Her $k = (a, b) \in \mathcal{K}$ ve $x \in \mathcal{P}$ için şifreleme işlemi:
    $$e_k(x) \equiv a \cdot x + b \pmod{26}$$
  * **Deşifreleme Fonksiyonu ($\mathcal{D}$):** Her $k = (a, b) \in \mathcal{K}$ ve $y \in \mathcal{C}$ için açma işlemi; fonksiyonun tersinin alınmasıyla bulunur. Burada $a^{-1}$, $a$'nın mod 26'ya göre çarpımsal tersidir:
    $$d_k(y) \equiv a^{-1} \cdot (y - b) \pmod{26}$$
</div>

## ⚠️ Anahtar Seçme Koşulları ve Birebirlik (Injective) Şartı

Afin şifrelemesinde $b$ (kaydırma) değeri için $\mathbb{Z}_{26}$ içindeki tüm sayılar seçilebilir. Ancak $a$ (çarpan) değeri rastgele seçilemez! 

Şifreleme fonksiyonunun çözülebilmesi için **mutlaka birebir (1-1) olması** gerekir. Eğer $a$ sayısı $26$ ile aralarında asal değilse (yani $\gcd(a, 26) \neq 1$), fonksiyon birebirliğini kaybeder.

**Örnek bir felaket senaryosu:**
Diyelim ki kuralı ihlal edip $\gcd(2, 26) \neq 1$ olmasına rağmen $k = (2, 3)$ seçtik.
Denklemimiz: $e_k(x) \equiv 2x + 3 \pmod{26}$
* **A** harfi ($0$) şifrelendiğinde: $2 \cdot 0 + 3 \equiv 3 \implies \mathbf{D}$
* **N** harfi ($13$) şifrelendiğinde: $2 \cdot 13 + 3 = 29 \equiv 3 \pmod{26} \implies \mathbf{D}$

Gördüğünüz gibi hem A hem de N harfi aynı şifreli harfe (D) dönüştü. Mesajı alan kişi D harfini deşifre etmek istediğinde orijinal harfin A mı yoksa N mi olduğunu asla bilemez. Sistem çöker.

::: info 📌 Toplam Anahtar Uzayı ve Euler'in Phi (Totient) Fonksiyonu
Afin şifrelemesinde $a$ değerleri için $m$ ile aralarında asal olan sayıların adedini bulmamız gerekir. Kriptografide bu değer **Euler'in Phi Fonksiyonu ($\phi$)** ile hesaplanır. $b$ değeri için ise modül ($m$) kadar seçenek vardır. 

Bu nedenle Afin kriptosisteminin toplam anahtar uzayı şu formülle ifade edilir:
$$|\mathcal{K}| = \phi(m) \cdot m$$

İngilizce alfabe ($m=26$) için hesaplarsak, $26$ ile aralarında asal olan sayıların adedi:
$$\phi(26) = \phi(2) \cdot \phi(13) = (2-1) \cdot (13-1) = 12$$

Geçerli olan bu 12 çarpan şunlardır: $\{1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25\}$. 
$a$ için $12$, $b$ için $26$ seçenek olduğundan toplam anahtar uzayı:
$$|\mathcal{K}| = 12 \cdot 26 = 312$$

*Sezar'ın 25'lik anahtar uzayına göre daha geniş görünse de, $|\mathcal{K}| = 312$ modern bilgisayarlar için kaba kuvvet (brute force) saldırılarıyla saniyeler içinde kırılabilir.*
:::

## 📝 Çözümlü Uygulamalar

Aşağıdaki örneklerde işlemleri **Harf - Sayı Dönüşüm Tablosunu** kullanarak yapınız.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Açık metni "MATH" olan bir mesajı, $k = (5, 8)$ anahtarını kullanarak Afin şifrelemesi ile şifreleyiniz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **Çözüm:**
  Şifreleme kuralımız: $e_k(x) \equiv 5x + 8 \pmod{26}$

  Harfleri tablodan sayıya çevirip denklemde yerine koyalım:
  1. **M** $\to 12 \implies 5 \cdot 12 + 8 = 68 \equiv 16 \pmod{26} \implies \mathbf{Q}$
  2. **A** $\to 0 \implies 5 \cdot 0 + 8 = 8 \implies \mathbf{I}$
  3. **T** $\to 19 \implies 5 \cdot 19 + 8 = 103 \equiv 25 \pmod{26} \implies \mathbf{Z}$
  4. **H** $\to 7 \implies 5 \cdot 7 + 8 = 43 \equiv 17 \pmod{26} \implies \mathbf{R}$

  **Sonuç:** `MATH` kelimesi `QIZR` olarak şifrelenir.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $k = (7, 2)$ anahtarı ile şifrelenmiş olan "QCF" kapalı metnini deşifre ediniz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **Çözüm:**
  Deşifreleme formülümüz: $d_k(y) \equiv a^{-1} \cdot (y - b) \pmod{26}$
  
  Öncelikle $a = 7$ sayısının mod 26'daki çarpımsal tersini ($7^{-1}$) bulmalıyız. 
  Yani öyle bir sayı bulmalıyız ki $7 \cdot x \equiv 1 \pmod{26}$ olsun.
  $7 \cdot 15 = 105 = 4 \cdot 26 + 1$ olduğundan, $7^{-1} \equiv 15 \pmod{26}$ bulunur.

  Yeni deşifreleme denklemimiz: $d_k(y) \equiv 15 \cdot (y - 2) \pmod{26}$

  1. **Q** $\to 16 \implies 15 \cdot (16 - 2) = 15 \cdot 14 = 210 \equiv 2 \pmod{26} \implies \mathbf{C}$
  2. **C** $\to 2 \implies 15 \cdot (2 - 2) = 0 \implies \mathbf{A}$
  3. **F** $\to 5 \implies 15 \cdot (5 - 2) = 15 \cdot 3 = 45 \equiv 19 \pmod{26} \implies \mathbf{T}$

  **Sonuç:** Şifreli `QCF` metninin açık hali `CAT` kelimesidir.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Düşmandan ele geçirilen "AGIY" şifreli metninin, orijinalinde "OKAY" kelimesi olduğu bilinmektedir. Kullanılan $(a, b)$ Afin anahtarını bulunuz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **Çözüm:**
  $e_k(x) \equiv a \cdot x + b \pmod{26}$ olduğunu biliyoruz. İlk iki harf üzerinden iki bilinmeyenli bir denklem sistemi kurarak sistemi çözebiliriz.

  **O** ($14$) $\to$ **A** ($0$):
  $$14a + b \equiv 0 \pmod{26} \quad \text{--- (Denklem 1)}$$

  **K** ($10$) $\to$ **G** ($6$):
  $$10a + b \equiv 6 \pmod{26} \quad \text{--- (Denklem 2)}$$

  Denklem 1'den Denklem 2'yi taraf tarafa çıkaralım ($b$'leri yok etmek için):
  $$(14a + b) - (10a + b) \equiv 0 - 6 \pmod{26}$$
  $$4a \equiv -6 \equiv 20 \pmod{26}$$

  **Kritik Aşama:** Mod 26'da $4a \equiv 20$ denklemini çözerken direkt 4'e bölemeyiz. $\gcd(4, 26) = 2$ olduğu için bu denklemin iki farklı kökü vardır:
  1. $a \equiv 5 \pmod{26}$
  2. $a \equiv 5 + 13 = 18 \pmod{26}$

  Ancak Afin kuralları gereği $\gcd(a, 26) = 1$ olmak zorundadır. $\gcd(18, 26) \neq 1$ olduğu için $a = 18$ değeri **geçersizdir.** Demek ki **$a = 5$** olmalıdır.

  Bulduğumuz $a = 5$ değerini Denklem 1'de yerine koyalım:
  $$14 \cdot 5 + b \equiv 0 \pmod{26}$$
  $$70 + b \equiv 0 \pmod{26}$$
  $$18 + b \equiv 0 \pmod{26}$$
  $$b \equiv -18 \equiv 8 \pmod{26}$$

  **Sonuç:** Düşmanın kullandığı anahtar $k = (5, 8)$ ikilisidir. *(Örnek 1'deki anahtarı bulmuş olduk!)*
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

## 🕹️ İnteraktif Afin Hesaplayıcı

$e_k(x) \equiv a \cdot x + b \pmod{26}$ denkleminin pratikte nasıl çalıştığını aşağıdaki araçla test edebilirsiniz. 

Dikkat ederseniz, fonksiyonun 1-1 (birebir) olma şartını korumak için **"Çarpan (a)"** menüsünde yalnızca 26 ile aralarında asal olan o 12 geçerli anahtar yer almaktadır. Yanlarında modüler terslerinin de ($a^{-1}$) hesaplandığını görebilirsiniz.

<AffineCalculator />