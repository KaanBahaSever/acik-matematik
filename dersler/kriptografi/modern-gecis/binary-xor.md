---
title: İkili Sistem, Boolean Cebri ve XOR Mantığı
description: Kriptografide kullanılan ikili gösterim, Boolean cebri ve XOR işleminin temel kurallarını açıklar.
---

# İkili Sistem (Binary) ve XOR Mantığı

Klasik kriptografide şifreleme işlemleri harfler ve alfabenin boyutu (Mod 26) üzerinden yapılıyordu. Ancak 20. yüzyılın ortalarında bilgisayarların icadıyla kriptografi kağıt-kalemden çıkıp işlemcilere taşındı. 

Modern kriptografide şifrelenen şey "A" harfi değil, o harfi veya herhangi bir veriyi (resim, ses, video) temsil eden **0 ve 1'lerden oluşan bit dizileridir**.

## İkili Sistem (Base-2) ve Boolean Cebri

Bilgisayarların temel yapı taşı olan transistörler sadece iki durumu anlayabilir: Elektrik var (1) veya elektrik yok (0). Bu yüzden modern şifreleme sistemleri $\mathbb{Z}_{26}$ yerine $\mathbb{Z}_2 = \{0, 1\}$ cismi üzerinde çalışır.

19.yüzyılda İngiliz matematikçi George Boole tarafından geliştirilen **Boolean Cebri**, sadece *Doğru (1)* ve *Yanlış (0)* değerleriyle yapılan mantıksal işlemleri tanımlar. Kriptografide en sık kullandığımız üç temel mantık kapısı şunlardır:
* **AND (VE):** Sadece her iki girdi de 1 ise sonuç 1'dir (Çarpma işlemi gibidir).
* **OR (VEYA):** Girdilerden en az biri 1 ise sonuç 1'dir (Toplama işlemi gibidir).
* **NOT (DEĞİL):** Girdiyi tersine çevirir (1 ise 0, 0 ise 1 yapar).

Ancak modern kriptografinin asıl kahramanı bu üçü değil, özel bir mantık kapısı olan **XOR**'dur.

## XOR İşlemi (Exclusive OR)

XOR (Dışlayıcı VEYA), "Sadece biri doğruysa doğrudur, ikisi aynıysa yanlıştır" mantığıyla çalışır. Kriptografide $\oplus$ sembolü ile gösterilir. 

Matematiksel olarak XOR işlemi, aslında **Mod 2'de toplama işleminden** başka bir şey değildir:
$$A \oplus B \equiv A + B \pmod 2$$

**XOR Doğruluk Tablosu:**
Farklı bitler 1 (True), aynı bitler 0 (False) sonucunu verir.

<div style="display: flex; justify-content: center;">

| A (Açık Metin Biti) | B (Anahtar Biti) | A $\oplus$ B (Şifreli Bit) |
|:---:|:---:|:---:|
| **0** | **0** | **0** |
| **0** | **1** | **1** |
| **1** | **0** | **1** |
| **1** | **1** | **0** |

</div>

## Neden Kriptografinin Kalbinde XOR Var?

Bir bilgisayar bilimcisine veya matematikçiye "Neden AES veya OTP gibi sistemler veriyi şifrelemek için toplama, çıkarma veya AND kullanmıyor da XOR kullanıyor?" diye sorarsanız, size şu **4 kusursuz özelliği** sayacaktır:

1. **Birim Eleman Özelliği (Identity):** Bir biti 0 ile XOR'lamak o biti değiştirmez.
   $$A \oplus 0 = A$$
2. **Kendi Kendini Yok Etme (Nilpotent Özellik):** Bir biti kendisiyle XOR'larsanız sonuç daima 0 olur. *(İşte sihir buradadır!)*
   $$A \oplus A = 0$$
3. **Değişme Özelliği (Commutative):** Sıranın bir önemi yoktur.
   $$A \oplus B = B \oplus A$$
4. **Birleşme Özelliği (Associative):** İşlem önceliğinin bir önemi yoktur.
   $$A \oplus (B \oplus C) = (A \oplus B) \oplus C$$

::: tip 🔑 Mükemmel Geri Dönüşebilirlik (Şifre Çözme İspatı)
XOR'un 2. özelliği (Nilpotent), kriptografide **aynı fonksiyonun hem şifreleme hem de deşifreleme yapabilmesini** sağlar!

Diyelim ki Açık Metin ($P$) ve Anahtar ($K$) bitlerini XOR'layarak Şifreli Metin ($C$) elde ettik:
$$C = P \oplus K$$

Şimdi bu şifreli metni ($C$), tekrar aynı anahtarla ($K$) XOR'layalım. Birleşme ve yok etme özelliklerini kullanarak orijinal metne ($P$) nasıl geri döndüğümüzü izleyin:
$$C \oplus K = (P \oplus K) \oplus K$$
$$C \oplus K = P \oplus (K \oplus K)$$
$K \oplus K = 0$ olduğu için denklem şu hale gelir:
$$C \oplus K = P \oplus 0$$
$$C \oplus K = P$$

Yani şifrelerken de çözerken de **aynı matematiksel işlemi (XOR)** yaparız. Bu donanım (çip) tasarımında devasa bir maliyet ve hız tasarrufu sağlar!
:::

## 📝 Çözümlü Uygulamalar

Modern sistemlerde XOR işlemi tek bir bit yerine, uzun bit dizileri (baytlar veya bloklar) üzerinde **karşılıklı (bitwise)** olarak uygulanır.

::: details 🟢 Örnek 1: Şifreleme ve Deşifreleme (Bitwise XOR)
**Soru:** 8 bitlik (1 Bayt) $P = 10110100$ açık metnini, $K = 01101011$ anahtarını kullanarak XOR ile şifreleyiniz. Ardından bulduğunuz sonucu tekrar aynı anahtarla XOR'layarak deşifre ediniz.

**Çözüm:**
Bitleri alt alta yazarak sütun sütun (aynıysa 0, farklıysa 1) XOR'layalım.

**Aşama 1: Şifreleme ($C = P \oplus K$)**
$$P: \quad 1\ 0\ 1\ 1\ 0\ 1\ 0\ 0$$
$$K: \quad \underline{0\ 1\ 1\ 0\ 1\ 0\ 1\ 1}$$
$$C: \quad 1\ 1\ 0\ 1\ 1\ 1\ 1\ 1$$
**Şifreli Metin ($C$):** `11011111`

**Aşama 2: Deşifreleme ($P = C \oplus K$)**
$$C: \quad 1\ 1\ 0\ 1\ 1\ 1\ 1\ 1$$
$$K: \quad \underline{0\ 1\ 1\ 0\ 1\ 0\ 1\ 1}$$
$$P: \quad 1\ 0\ 1\ 1\ 0\ 1\ 0\ 0$$
**Orijinal Metin ($P$):** `10110100`

*Görüldüğü gibi, aynı anahtar ile ikinci kez XOR'landığında başlangıç noktasına kusursuz bir şekilde geri dönülmüştür.*
:::