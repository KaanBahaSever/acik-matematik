---
title: Sezar Şifreleme
description: Alfabe kaydırmasına dayalı klasik Sezar şifresinin matematiksel modelini, anahtar uzayını ve kırılma nedenlerini anlatır.
---

<script setup>
/* Klasör yolunu, md dosyasının ve .vitepress klasörünün konumuna göre ayarlayabilirsin */
import CeaserCalculator from '/.vitepress/components/CeaserCalculator.vue'
</script>

# Sezar Şifreleme (Caesar Cipher)

Klasik kriptografinin en bilinen ve tarihsel olarak en eski algoritmalarından biri olan Sezar Şifrelemesi, adını onu generalleriyle gizli mesajlaşmak için kullanan Roma İmparatoru Julius Sezar'dan alır. Orijinal kullanımında Sezar, alfabedeki her harfi daima **$3$ harf ileri** kaydırarak mesajlarını gizlemiştir. 

[Image of Caesar cipher wheel]

Günümüzde "Sezar Şifresi" terimi, sadece $3$ birimlik kaydırmayı değil, harflerin alfabe üzerinde belirli ve sabit bir sayı kadar ileri veya geri kaydırıldığı **Genelleştirilmiş Kaydırma Şifrelerini (Shift Ciphers)** ifade etmek için kullanılır.

## Sistemin Formal Tanımı

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Sezar Şifrelemesinin Matematiksel Modeli

  </div>

  Bir önceki bölümde tanımladığımız 5 bileşenli kriptosistem anatomisini $(\mathcal{P}, \mathcal{C}, \mathcal{K}, \mathcal{E}, \mathcal{D})$, İngilizce alfabe kullanarak mod 26 üzerinde Sezar algoritmasına uyarlarsak şu matematiksel yapıyı elde ederiz:

  * **Açık Metin ($\mathcal{P}$):** $\mathbb{Z}_{26} = \{0, 1, 2, \dots, 25\}$
  * **Şifreli Metin ($\mathcal{C}$):** $\mathbb{Z}_{26} = \{0, 1, 2, \dots, 25\}$
  * **Anahtar Uzayı ($\mathcal{K}$):** $\mathbb{Z}_{26}$ (Kullanılabilecek kaydırma miktarları)
  * **Şifreleme Fonksiyonu ($\mathcal{E}$):** $\forall k \in \mathcal{K}$ ve $\forall x \in \mathcal{P}$ için şifreleme; açık metin karakterine anahtar değerinin eklenmesiyle yapılır:
    $$e_k(x) \equiv x + k \pmod{26}$$
  * **Deşifreleme Fonksiyonu ($\mathcal{D}$):** $\forall y \in \mathcal{C}$ için açma işlemi; şifreli karakterden anahtar değerinin çıkarılmasıyla yapılır:
    $$d_k(y) \equiv y - k \pmod{26}$$
</div>

## 🔑 Anahtar Uzayının Boyutu ve Güvenlik Zaafiyeti

Sezar şifrelemesinde anahtar uzayının büyüklüğü, **doğrudan seçilen alfabenin boyutuna (Mod 26) bağlıdır**. Şifreleme uzayımız 26 harfli İngilizce alfabe ile sınırlandırıldığı için, harfleri kaydırabileceğimiz maksimum miktar da $26$'dır.

::: info 📌 Toplam Anahtar Uzayı
İngilizce alfabe ($m=26$) için Sezar şifrelemesinin anahtar uzayı:
$$|\mathcal{K}| = 26$$

*(Ancak $k=0$ durumu metni değiştirmeyeceği için, etkili şifreleme yapan anahtar sayısı **$25$**'tir.)*
:::

**Bu neden kritik bir sorundur?**
Kerckhoffs Prensibi'ni hatırlayalım: Düşman şifreleme algoritmasını (her harfe $x + k \pmod{26}$ yapıldığını) biliyor kabul edilir. Sistemin güvenliği sadece $k$ anahtarının gizliliğine dayanmalıdır. Ancak olası sadece $25$ anahtar olduğu için, düşman şifreli bir metni ele geçirdiğinde hiçbir zekice matematiğe başvurmadan **Kaba Kuvvet Saldırısı (Brute Force Attack)** yaparak tüm ihtimalleri deneyebilir. Bir insan bile kağıt kalemle birkaç dakikada tüm $25$ kaydırmayı test edip anlamlı kelimeyi bulabilir. 

*Modern kriptografide güvenli kabul edilen sistemlerin anahtar uzayı (örn: AES-256) $2^{256}$ gibi astronomik seviyelerdedir. Sezar'ın alfabeye bağımlı 25'lik anahtar uzayı ise modern standartlarda "yok" hükmündedir.*

## 📝 Çözümlü Uygulamalar

Aşağıdaki örneklerde, bir önceki bölümün sonundaki **Harf - Sayı Dönüşüm Tablosunu** referans alacağız. Lütfen çözümlere bakmadan önce tabloyu kullanarak denklemleri kendiniz kurunuz.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Açık metni "MATH" olan bir mesajı, $k = 7$ anahtarını kullanarak Sezar şifrelemesi ile şifreleyiniz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **Çözüm:**
  Algoritmamız: $e_7(x) \equiv x + 7 \pmod{26}$

  Her bir harfi sırayla tablodan sayısal karşılığına çevirip denklemde yerine koyalım:
  1. **M** $\to 12 \implies 12 + 7 = 19 \implies \mathbf{T}$
  2. **A** $\to 0 \implies 0 + 7 = 7 \implies \mathbf{H}$
  3. **T** $\to 19 \implies 19 + 7 = 26 \equiv 0 \pmod{26} \implies \mathbf{A}$ *(Modüler döngü burada devreye girdi)*
  4. **H** $\to 7 \implies 7 + 7 = 14 \implies \mathbf{O}$

  **Sonuç:** `MATH` kelimesi, $k=7$ anahtarıyla `THAO` olarak şifrelenir.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $k = 5$ anahtarı ile şifrelenmiş olan "GTD" kapalı metnini deşifre ediniz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **Çözüm:**
  Algoritmamız: $d_5(y) \equiv y - 5 \pmod{26}$

  1. **G** $\to 6 \implies 6 - 5 = 1 \implies \mathbf{B}$
  2. **T** $\to 19 \implies 19 - 5 = 14 \implies \mathbf{O}$
  3. **D** $\to 3 \implies 3 - 5 = -2$ 
     *Eksi bir sonuç bulduğumuzda, pozitif denklik bulana kadar modül (26) ekleriz:*
     $-2 \equiv -2 + 26 \equiv 24 \pmod{26} \implies \mathbf{Y}$

  **Sonuç:** Şifreli `GTD` metninin açık hali `BOY` kelimesidir.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Düşman haberleşme hattından "WKLV" şifreli metnini ele geçirdiniz. Bunun aslında İngilizce "THIS" kelimesi olduğu bilindiğine göre, kullanılan Sezar anahtarını ($k$) cebirsel olarak bulunuz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **Çözüm:**
  Şifreleme kuralının $e_k(x) \equiv y \pmod{26}$ olduğunu biliyoruz.
  İlk harf olan **T** (Açık metin) ile **W** (Şifreli metin) arasındaki denklemi kurarak doğrudan çözüme ulaşabiliriz.

  Tabloya göre:
  * **T** $\to 19$ (Açık metin, $x$)
  * **W** $\to 22$ (Şifreli metin, $y$)

  Denklemi kuralım:
  $$19 + k \equiv 22 \pmod{26}$$
  $$k \equiv 22 - 19 \pmod{26}$$
  $$k \equiv 3 \pmod{26}$$

  **Doğrulama:**
  Bulduğumuz $k=3$ anahtarının diğer harfler için de çalışıp çalışmadığını test edelim:
  * **H** ($7$) + $3$ = $10$ (**K**) $\checkmark$
  * **I** ($8$) + $3$ = $11$ (**L**) $\checkmark$
  * **S** ($18$) + $3$ = $21$ (**V**) $\checkmark$

  **Sonuç:** Düşmanın kullandığı anahtar $k = 3$'tür (Orijinal Julius Sezar anahtarı).
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

## 🕹️ İnteraktif Sezar Hesaplayıcı

Yukarıda öğrendiğimiz matematiksel şifreleme ve deşifreleme fonksiyonlarının ($x \pm k \pmod{26}$) gerçek zamanlı olarak nasıl çalıştığını görmek için aşağıdaki aracı kullanabilirsiniz. 

Farklı mesajlar yazıp anahtar ($k$) değerini kaydırarak, metnin şifreli uzayda nasıl evrildiğini bizzat test edin!

<CeaserCalculator />