# Vigenère Şifreleme

**Monoalfabetik şifrelerin** (Sezar, Afin) en zayıf noktası, dildeki harf frekanslarını (örneğin İngilizcedeki 'E' harfinin diğerlerinden çok daha sık geçmesini) aynen korumasıdır. 16. yüzyılda Giovan Battista Bellaso tarafından tasarlanan ve Blaise de Vigenère'in adıyla anılan bu sistem, **Polialfabetik (Çoklu Alfabe)** yapısıyla bu istatistiksel zafiyeti çözer. 

Temelde sistem, tek bir sabit kaydırma yerine, bir **anahtar kelime** kullanarak mesajdaki her harf için farklı ve döngüsel bir Sezar kaydırması uygular.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Vigenère Şifreleme Sistemi

  </div>
  
  Vigenère şifrelemesinde işlemler, $n$ uzunluğundaki açık metin vektörleri ile $m$ uzunluğundaki anahtar vektörleri (kelimeleri) arasında gerçekleşir. Sistemi vektör uzayları üzerinden tanımlarsak:

  * **Açık Metin ($\mathcal{P}$):** Elemanları $\mathbb{Z}_{26}$'dan alınan $n$ boyutlu vektörlerin kümesi: 
    $$\mathbf{x} = (x_0, x_1, \dots, x_{n-1}) \in (\mathbb{Z}_{26})^n$$
  * **Şifreli Metin ($\mathcal{C}$):** Elemanları $\mathbb{Z}_{26}$'dan alınan $n$ boyutlu vektörlerin kümesi: 
    $$\mathbf{y} = (y_0, y_1, \dots, y_{n-1}) \in (\mathbb{Z}_{26})^n$$
  * **Anahtar Uzayı ($\mathcal{K}$):** Elemanları $\mathbb{Z}_{26}$'dan alınan $m$ uzunluğundaki vektörlerden (kelimelerden) oluşan küme: 
    $$K = (k_0, k_1, \dots, k_{m-1}) \in (\mathbb{Z}_{26})^m$$
  * **Şifreleme Fonksiyonu ($\mathcal{E}$):** $\mathbf{x} \in \mathcal{P}$ vektörünün her bir $i$. elemanı ($x_i$), anahtar vektörünün döngüsel olarak sıraya denk gelen elemanı ile toplanır:
    $$e_K(x_i) \equiv x_i + k_{i \pmod m} \pmod{26}$$
  * **Deşifreleme Fonksiyonu ($\mathcal{D}$):** $\mathbf{y} \in \mathcal{C}$ şifreli vektörünün her bir $i$. elemanından ($y_i$), anahtar vektöründeki ilgili eleman çıkarılır:
    $$d_K(y_i) \equiv y_i - k_{i \pmod m} \pmod{26}$$
</div>

::: info 📌 Anahtar Uzayı ve Kasiski İncelemesi
Vigenère şifrelemesinin anahtar uzayı, kullanılan anahtar kelimenin uzunluğuna ($m$) doğrudan bağlıdır. Anahtardaki her bir harf için 26 farklı seçenek olduğundan, toplam uzay şu formülle ifade edilir:

$$|\mathcal{K}| = 26^m$$

Örneğin, sadece 5 harfli bir anahtar kelime ($m=5$) kullanılıyorsa:

$$|\mathcal{K}| = 26^5 = 11.881.376$$

Bu devasa anahtar uzayı, o dönemki Kaba Kuvvet (**Brute Force**) saldırılarını imkansız kılmıştır. Sistem 300 yıl boyunca kırılamamış, ancak 1863'te Friedrich Kasiski'nin şifreli metindeki tekrar eden hece aralıklarını ölçerek **anahtar uzunluğunu ($m$)** tespit etmesiyle (**Kasiski İncelemesi**) sistemin zafiyeti ortaya çıkmıştır.
:::

## Çözümlü Uygulamalar

Aşağıdaki örneklerde işlemleri yaparken Harf - Sayı Dönüşüm Tablosunu kullanınız. Matematiksel hataya düşmemek için açık metnin altına anahtar kelimeyi **döngüsel olarak** harf harf yazmak en pratik yoldur.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Açık metni "MATH" olan bir mesajı, $K = \text{"KEY"}$ anahtarı kullanarak Vigenère şifrelemesi ile şifreleyiniz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **Çözüm:**
  
  Açık metnimiz 4 harfli, anahtar kelimemiz ise 3 harfli ($m=3$). 
  Öncelikle anahtar kelimeyi, açık metnin boyuna ulaşana kadar yan yana tekrar ederek genişletiriz (**Padding**):
  
  * **Açık Metin:** M A T H
  * **Anahtar:** K E Y K

  Şimdi şifreleme formülüne ($e_K(x_i) \equiv x_i + k_i \pmod{26}$) göre her harfi alt alta toplayalım:

  1. **M** (12) + **K** (10) $\implies 12 + 10 = 22 \implies$ **W**
  2. **A** (0) + **E** (4) $\implies 0 + 4 = 4 \implies$ **E**
  3. **T** (19) + **Y** (24) $\implies 19 + 24 = 43 \equiv 17 \pmod{26} \implies$ **R**
  4. **H** (7) + **K** (10) $\implies 7 + 10 = 17 \implies$ **R**

  **Sonuç:** `MATH` kelimesi Vigenère ile `WERR` olarak şifrelenir. 
  
  > **Dikkat Edin:** Açık metinde hiç tekrar eden harf olmamasına rağmen, şifreli metinde iki tane yan yana 'R' harfi oluştu. İşte frekans analizini çökerten **Polialfabetik** özellik tam olarak budur.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $K = \text{"KEY"}$ anahtarı ile şifrelenmiş olan "WERR" kapalı metnini deşifre ediniz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **Çözüm:**
  
  Deşifreleme kuralımız: $d_K(y_i) \equiv y_i - k_i \pmod{26}$
  
  Yine anahtar kelimeyi mesaj boyuna kadar tekrar ettiriyoruz.
  
  * **Şifreli Metin:** W E R R
  * **Anahtar:** K E Y K

  Alt alta çıkarma işlemlerini yapalım:

  1. **W** (22) - **K** (10) $\implies 22 - 10 = 12 \implies$ **M**
  2. **E** (4) - **E** (4) $\implies 4 - 4 = 0 \implies$ **A**
  3. **R** (17) - **Y** (24) $\implies 17 - 24 = -7$ 
     *Negatif sonucu mod 26'da pozitife çevirelim:* $-7 \equiv -7 + 26 = 19 \pmod{26} \implies$ **T**
  4. **R** (17) - **K** (10) $\implies 17 - 10 = 7 \implies$ **H**

  **Sonuç:** Çıkarma işlemi ve modüler aritmetik bizi orijinal `MATH` mesajına kusursuzca geri götürdü.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>