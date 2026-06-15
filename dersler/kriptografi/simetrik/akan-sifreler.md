# Akan Şifreleme (Stream Ciphers)

One-Time Pad (OTP) sisteminin mükemmel gizlilik sunduğunu, ancak mesajla aynı boyutta rastgele bir anahtara ihtiyaç duyduğu için pratik (Anahtar Dağıtım Problemi) olmadığını gördük. Akan şifreler (Stream Ciphers), OTP'nin bu XOR tabanlı şifreleme mantığını taklit eden, ancak çok daha kısa ve yönetilebilir bir kök anahtar (seed key) kullanarak pratik hale getirilmiş modern sistemlerdir.

Temel felsefesi şudur: Gönderici ve alıcı kısa bir kök anahtarı paylaşır. Her iki taraftaki şifreleme cihazı, bu kısa anahtarı kullanarak matematiksel algoritmalarla Sözde Rastgele (Pseudo-Random) ve çok uzun bir "anahtar akışı" (keystream) üretir. Daha sonra bu akış, tıpkı One-Time Pad'de olduğu gibi açık metinle XOR'lanır.

## Sistemin Formal Tanımı

Akan şifrelemede işlemler, bit dizileri (0 ve 1) üzerinde eşzamanlı olarak gerçekleşir.

* **Açık Metin ($\mathcal{P}$):** İkili (binary) formdaki açık metin bitlerinin dizisi: $x = x_1, x_2, \dots$
* **Şifreli Metin ($\mathcal{C}$):** İkili formdaki şifreli metin bitlerinin dizisi: $y = y_1, y_2, \dots$
* **Anahtar Uzayı ($\mathcal{K}$):** Belirli ve sabit bir uzunluğa sahip kök anahtarların (seed keys) kümesi.
* **Anahtar Akışı Üreteci (Keystream Generator):** $K \in \mathcal{K}$ kök anahtarını alarak, $z_1, z_2, \dots$ şeklinde açık metin uzunluğunda bir Sözde Rastgele sayı dizisi üreten deterministik fonksiyondur.
* **Şifreleme Fonksiyonu ($\mathcal{E}$):** Açık metnin her bir $\tau$. biti, anahtar akışının ilgili $\tau$. biti ile XOR'lanır:
  $$e_{z_\tau}(x_\tau) \equiv x_\tau \oplus z_\tau \pmod 2$$
* **Deşifreleme Fonksiyonu ($\mathcal{D}$):** Şifreli metnin her bir $\tau$. biti, aynı üretilmiş anahtar akışı ile tekrar XOR'lanır:
  $$d_{z_\tau}(y_\tau) \equiv y_\tau \oplus z_\tau \pmod 2$$

## ⚙️ Anahtar Akışı (Keystream) Nasıl Üretilir?

Akan şifrelerin kalbi Anahtar Akışı Üretecidir (Keystream Generator). Üretilen dizi dışarıdan bakan bir düşman için tamamen rastgele görünmelidir ancak aslında matematiksel bir formüle dayanan deterministik bir yapıdır. Bu diziler tarihsel olarak sayı teorisi ve lineer cebir tabanlı matematiksel fonksiyonlarla üretilirler.

İki temel matematiksel üreteç modeli şöyledir:

### 1. Doğrusal Eşlenik Üreteci (Linear Congruential Generator - LCG)

Kriptografik olarak çok güçlü olmasa da, sözde rastgele sayı üretiminin temel matematiksel mantığını anlamak için en iyi örnektir. Doğrudan modüler aritmetiğe ve sayı teorisine dayanır.

Bir $S_0$ başlangıç değeri (kök anahtar) belirlenir. Her bir $\tau$ adımında yeni bir durum değeri şu doğrusal denklemle hesaplanır:
$$S_{\tau} \equiv (a \cdot S_{\tau-1} + c) \pmod m$$

Burada $a$ çarpan, $c$ artış miktarı, $m$ ise modüldür. Elde edilen bu $S_{\tau}$ sayısının doğrudan kendisi kullanılabileceği gibi, ikili sisteme (binary) indirgemek için sayının tek mi çift mi olduğuna bakılarak (yani mod 2'si alınarak) $z_{\tau}$ anahtar biti elde edilir:
$$z_{\tau} \equiv S_{\tau} \pmod 2$$

Bu yöntem çok basittir ancak periyodu (döngüye girme süresi) $m$ değerine ve seçilen katsayıların aralarında asal olma durumlarına sıkı sıkıya bağlıdır.

### 2. Doğrusal Geri Beslemeli Kaydırmalı Yazmaç (LFSR)

LCG'nin donanım üzerinde $\mathbb{Z}_2$ (Galois Field 2) cismine uyarlanmış, çok daha hızlı çalışan lineer cebirsel versiyonudur. Belirli $L$ uzunluğunda bir bit dizisi (başlangıç durumu) sisteme verilir. 

[Image of Linear Feedback Shift Register mathematics and shift mechanism]

Her bir $\tau$ zaman adımında, mevcut bitler bir sağa kaydırılır. En sağdan düşen bit, bizim **anahtar akışı bitimiz ($z_\tau$)** olur. Boşalan en sol haneye ise, içerideki belirli bitlerin XOR'lanmasıyla elde edilen yeni bir bit yazılır. 

$\tau > L$ adımları için üretilen bitin genel doğrusal tekrar bağıntısı (recurrence relation) şu şekildedir:
$$z_{\tau} \equiv c_1 z_{\tau-1} + c_2 z_{\tau-2} + \dots + c_L z_{\tau-L} \pmod 2$$

Burada $c_i \in \{0, 1\}$ katsayıları, hangi indekslerdeki bitlerin geri beslemeye (XOR işlemine) dahil edileceğini belirler. Uygun bir polinom (primitive polynomial) seçildiğinde, $L$ boyutlu bir LFSR, kendini tekrar etmeden önce tam $2^L - 1$ adet rastgele görünümlü bit üretebilir. Ancak sistem tamamen lineer olduğu için Berlekamp-Massey algoritması ile kolayca çözülür. Bu yüzden modern sistemlerde birden fazla LFSR doğrusal olmayan (non-linear) fonksiyonlarla harmanlanarak kullanılır.

## 🔄 Anahtar Periyodu (Period) ve Döngü Tehlikesi

Akan şifreler, ürettikleri anahtar akışının (keystream) kalitesine göre güvendedir. Ancak hiçbir matematiksel formül (PRNG) sonsuza kadar birbirinden farklı sayılar üretemez. Üretilen dizi belli bir adımdan sonra mutlaka başa döner ve **kendini tekrar etmeye** başlar. 

Anahtar dizisinin kendini tekrar edene kadar ürettiği benzersiz sayı adedine **Periyot (Period)** denir.

::: warning ⚠️ Periyot Kısalığı Zafiyeti
Eğer şifreleyeceğiniz mesajın uzunluğu, üretecinizin periyodundan daha uzunsa, aynı anahtar akışı mesajın ilerleyen kısımlarında **ikinci kez** kullanılmış olur. Bu durum, One-Time Pad'de gördüğümüz ölümcül **İki Kez Kullanılan Şerit (Two-Time Pad)** zafiyetini tetikler. Şifre saniyeler içinde kırılır!

* **LCG Üreteçleri** için ulaşılabilecek maksimum periyot modül değeri kadardır ($m$).
* **LFSR Üreteçleri** için ulaşılabilecek maksimum periyot $2^L - 1$'dir (Burada $L$ yazmaçtaki bit sayısıdır).

Modern akan şifreler (örn: ChaCha20), mesaj ne kadar uzun olursa olsun asla döngüye girmeyecek kadar devasa periyotlara (örn: $2^{64}$ byte) sahip olacak şekilde tasarlanır.
:::

## ⚡ Akan Şifrelerin Özellikleri ve Kriptanalizi

1. **Hız ve Donanım Verimliliği:** Akan şifreler, veriyi bit bit veya bayt bayt işledikleri için (verinin tamamının belleğe yüklenmesini beklemezler) donanım üzerinde inanılmaz hızlı çalışırlar. Bu özellikleri onları canlı video yayınları (streaming), Bluetooth ve Wi-Fi iletişimleri için vazgeçilmez kılar.
2. **Hata Yayılımı Yoktur (No Error Propagation):** İletişim hattındaki bir gürültü nedeniyle şifreli metindeki ($y$) tek bir bit bozulursa, alıcı tarafında deşifre edilen açık metinde ($x$) sadece o ilgili tek bit bozuk

## 📝 Çözümlü Uygulamalar

Aşağıdaki örnekte, açık metnimiz doğrudan işlemcilerin anladığı **ikili sistem (binary)** blokları (8-bit baytlar) halinde verilmiştir. Anahtar akışını üretmek için $m=256$ (1 baytlık sınırı korumak için) olan bir LCG üreteci kullanılmıştır.

::: details 🟢 Örnek 1: x = [10101010, 11110000] ikili açık metnini, LCG (S₀ = 10, a = 5, c = 7, m = 256) üreteci ve XOR işlemi ile şifreleyiniz.
**Çözüm:**
Şifreleme fonksiyonumuz: $e(x_\tau) \equiv x_\tau \oplus S_\tau$
Anahtar akışı üretim fonksiyonumuz: $S_\tau \equiv (a \cdot S_{\tau-1} + c) \pmod{256}$

Bize verilen 8-bitlik (1 Bayt) iki adet açık metin bloğumuz şunlardır:
* $x_1 = 10101010_2$
* $x_2 = 11110000_2$

**1. Adım: İlk bloğun ($x_1$) şifrelenmesi**
Önce bu bloğu şifreleyecek olan 1. anahtar akışımızı ($S_1$) onluk tabanda hesaplayalım:
$$S_1 \equiv (5 \cdot S_0 + 7) \pmod{256}$$
$$S_1 \equiv (5 \cdot 10 + 7) \pmod{256} = 57_{10}$$

Şimdi bulduğumuz 57 sayısını ikili (binary) sisteme çevirelim: 
$S_1 = 00111001_2$

Açık metin ile anahtar akışını karşılıklı (bitwise) **XOR** işlemine sokalım (Farklıysa 1, aynıysa 0):
$$
\begin{array}{r l}
           x_1: & 10101010_2 \\
  \oplus \ S_1: & 00111001_2 \\
  \hline
           y_1: & 10010011_2
\end{array}
$$
İlk şifreli bloğumuz: $y_1 = 10010011_2$

**2. Adım: İkinci bloğun ($x_2$) şifrelenmesi**
Sistemin kalbi burasıdır! Yeni anahtar bir önceki duruma ($S_1 = 57$) bağlı olarak güncellenir.
$$S_2 \equiv (5 \cdot S_1 + 7) \pmod{256}$$
$$S_2 \equiv (5 \cdot 57 + 7) \pmod{256}$$
$$S_2 \equiv (285 + 7) \pmod{256}$$
$$S_2 \equiv 292 \pmod{256} = 36_{10}$$

Bulduğumuz 36 sayısını ikili (binary) sisteme çevirelim: 
$S_2 = 00100100_2$

Şimdi ikinci bloğumuzu yeni anahtarla XOR'layalım:
$$
\begin{array}{r l}
           x_2: & 11110000_2 \\
  \oplus \ S_2: & 00100100_2 \\
  \hline
           y_2: & 11010100_2
\end{array}
$$
İkinci şifreli bloğumuz: $y_2 = 11010100_2$

**Sonuç:** Verilen açık metin blokları, bu LCG tabanlı akan şifreleme sistemi ile kusursuz bir şekilde şifrelenerek $\mathbf{[10010011,\ 11010100]}$ ikili (binary) şifreli metin dizisine dönüştürülmüştür.
:::