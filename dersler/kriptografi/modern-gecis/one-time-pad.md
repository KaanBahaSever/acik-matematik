---
title: One-Time Pad ve Vernam Şifresi
description: Tam gizlilik sağlayan One-Time Pad yaklaşımını, Vernam şifresi ve tek kullanımlık anahtar mantığıyla ele alır.
---

# One-Time Pad (OTP) ve Vernam Şifresi

Kriptografi tarihindeki tüm algoritmalar (Sezar, Vigenère, Enigma, hatta günümüzdeki RSA ve AES) yeterli zaman ve işlem gücü verildiğinde teorik olarak kırılabilir. Kırılamayacağı matematiksel olarak ispatlanmış, evrendeki **tek** şifreleme sistemi **One-Time Pad (Tek Kullanımlık Şerit)** algoritmasıdır.

Temeli 1917'de Gilbert Vernam'ın icat ettiği ikili (binary) toplama işlemine (**XOR**) dayanır. 

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: One-Time Pad (Vernam Şifresi) Kriptosistemi

  </div>

  Modern One-Time Pad, alfabe harfleri yerine doğrudan bit dizileri ($0$ ve $1$'ler) üzerinde işlem yapar. Mesaj uzunluğunun $n$ bit olduğunu varsayarsak, 5 bileşenli kriptosistem anatomisi şu şekilde tanımlanır:

  * **Açık Metin ($\mathcal{P}$):** Uzunluğu $n$ olan tüm olası bit dizilerinin kümesi: $\{0, 1\}^n$
  * **Şifreli Metin ($\mathcal{C}$):** Uzunluğu $n$ olan tüm olası bit dizilerinin kümesi: $\{0, 1\}^n$
  * **Anahtar Uzayı ($\mathcal{K}$):** Uzunluğu $n$ olan tüm olası bit dizilerinin kümesi: $\{0, 1\}^n$
  * **Şifreleme Fonksiyonu ($\mathcal{E}$):** Açık metin vektörü ($x$) ile anahtar vektörünün ($K$) karşılıklı olarak XOR'lanmasıdır:
    $$e_K(x) \equiv x \oplus K \pmod 2$$
  * **Deşifreleme Fonksiyonu ($\mathcal{D}$):** Şifreli metnin ($y$), aynı anahtar ($K$) ile tekrar XOR'lanmasıdır (XOR işleminin nilpotent, yani kendisinin tersi olma özelliği gereği):
    $$d_K(y) \equiv y \oplus K \pmod 2$$
</div>

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Shannon'un Kusursuz Gizlilik (Perfect Secrecy) İlkesi

  </div>
  
  Claude Shannon, 1949 yılında bir sistemin "Kusursuz Gizliliğe" sahip olabilmesi için şu şartı sağlaması gerektiğini matematiksel olarak ispatlamıştır:
  
  $$P(x \mid y) = P(x)$$
  
  Yani; şifreli metni ($y$) ele geçiren bir düşmanın, orijinal mesajın ($x$) ne olduğuna dair yapacağı olasılık hesabı, şifreli metni hiç görmeden yapacağı tahminle **birebir aynı olmalıdır**. Şifreli metin, orijinal metin hakkında **sıfır** bilgi verir.

  ::: details İspat (One-Time Pad İçin)
  One-Time Pad bu şartı sağlar çünkü her $x$ açık metni ve her $y$ şifreli metni için, $x \oplus K = y$ eşitliğini sağlayan **benzersiz ve tek bir $K$ anahtarı** mutlaka vardır. Anahtar tamamen rastgele seçildiği için, şifreli metnin altından "SALDIR" kelimesinin çıkma ihtimali ile "BEKLE" kelimesinin çıkma ihtimali matematiksel olarak tamamen eşittir. Düşman sonsuz işlem gücüne sahip olsa bile doğru mesajı bulamaz, çünkü ortada analiz edilecek istatistiksel bir iz yoktur.
  
  <span style="float: right;">$\blacksquare$</span>
  <div style="clear: both;"></div>
  :::
</div>

## One-Time Pad'in 3 Altın Kuralı

Bu sistemin kusursuz olabilmesi için aşağıdaki 3 kuralın **istisnasız** uygulanması gerekir. Biri bile ihlal edilirse sistem çöker:

1. **Tam Rastgelelik (True Randomness):** Anahtar ($K$), hiçbir algoritmik kurala bağlı olmayan, evrendeki fiziksel olaylardan (örneğin radyoaktif bozunma veya atmosferik gürültü) elde edilmiş tam rastgele bitlerden oluşmalıdır. Bilgisayarların ürettiği Sözde Rastgele (Pseudo-Random) sayılar kesinlikle kullanılamaz.
2. **Uzunluk Şartı:** Anahtarın uzunluğu, şifrelenecek açık metnin uzunluğuna **eşit veya ondan daha büyük** olmalıdır ($|K| \ge |x|$).
3. **Tek Kullanımlık (Never Reuse):** Bir anahtar şeridi, sadece bir mesaj için kullanılmalı ve ardından fiziksel/dijital olarak **imha edilmelidir**.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: İki Kez Kullanılan Şerit (Two-Time Pad) Zafiyeti

  </div>

  Eğer 3. kural ihlal edilip aynı $K$ anahtarı ile iki farklı mesaj ($x_1$ ve $x_2$) şifrelenirse, düşman bu durumu matematiksel olarak nasıl istismar eder?

  ::: details 💡 Çözümü Göster / Gizle
  Aynı $K$ anahtarı kullanıldığında üretilen şifreli metinler şunlardır:
  
  $$ 
  \begin{aligned}
  y_1 &= x_1 \oplus K \\
  y_2 &= x_2 \oplus K
  \end{aligned}
  $$

  Düşman hattı dinleyip bu iki şifreli metni ele geçirir ve bunları birbiriyle XOR'larsa ($y_1 \oplus y_2$), XOR işleminin özellikleri gereği (değişme ve birleşme özellikleri ile $K \oplus K = 0$ kuralı) aradaki anahtarlar birbirini yok eder:

  $$ 
  \begin{aligned}
  y_1 \oplus y_2 &= (x_1 \oplus K) \oplus (x_2 \oplus K) \\
  &= x_1 \oplus x_2 \oplus (K \oplus K) \\
  &= x_1 \oplus x_2 \oplus 0 \\
  &= x_1 \oplus x_2
  \end{aligned}
  $$

  **Sonuç:** Düşmanın elinde artık anahtardan tamamen arındırılmış, doğrudan orijinal iki mesajın birbirine XOR'lanmış hali vardır! Doğal dil analizleriyle bu iki metin dakikalar içinde birbirinden ayrıştırılıp okunabilir. (Tarihteki ünlü **Venona Projesi**'nde Sovyet şifrelerinin kırılma sebebi tam olarak bu tembelliktir).
  
  <span style="float: right;">$\blacksquare$</span>
  <div style="clear: both;"></div>
  :::
</div>

## Madem Kusursuz, Neden Her Yerde Kullanmıyoruz? (Anahtar Dağıtım Problemi)

Öğrencilerin aklına gelen ilk soru şudur: *"Eğer One-Time Pad kırılamıyorsa, neden WhatsApp, bankalar veya ordular sürekli AES veya RSA gibi kırılabilecek algoritmalar kullanıyor?"*

Cevap, kriptografinin en büyük açmazı olan **Anahtar Dağıtım Probleminde (Key Distribution Problem)** gizlidir.

One-Time Pad'in 2. kuralı, anahtarın en az mesaj kadar uzun olmasını emreder. Eğer arkadaşınıza 10 GB'lık bir video dosyasını OTP ile şifreleyerek göndermek isterseniz, ona öncesinde **tamamen rastgele oluşturulmuş 10 GB'lık bir anahtar dosyasını** fiziksel ve mutlak güvenli yollarla (örneğin içi dolu bir flash belleği kuryeyle vererek) ulaştırmanız gerekir.

**Paradoks şudur:** Eğer 10 GB'lık bir veriyi düşmanların eline geçmeden arkadaşınıza ulaştırabilecek kadar güvenli bir kurye/kanal ağınız varsa, neden o kanaldan 10 GB'lık anahtarı göndermek yerine *doğrudan şifrelemek istediğiniz 10 GB'lık videoyu göndermiyorsunuz?*

İşte bu pratik imkansızlık yüzünden One-Time Pad gündelik hayatta kullanılamaz; sadece "Kırmızı Telefon" (Soğuk Savaş dönemindeki Moskova-Washington hattı) gibi çok yüksek güvenlikli, düşük veri boyutlu askeri ve diplomatik haberleşmelerde kullanılabilmiştir.