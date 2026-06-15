# One-Time Pad (OTP) ve Vernam Şifresi

Kriptografi tarihindeki tüm algoritmalar (Sezar, Vigenère, Enigma, hatta günümüzdeki RSA ve AES) yeterli zaman ve işlem gücü verildiğinde teorik olarak kırılabilir. Kırılamayacağı matematiksel olarak ispatlanmış, evrendeki **tek** şifreleme sistemi **One-Time Pad (Tek Kullanımlık Şerit)** algoritmasıdır.

Temeli 1917'de Gilbert Vernam'ın icat ettiği ikili (binary) toplama işlemine (XOR) dayanır. 

## Sistemin Formal Tanımı

Modern One-Time Pad (Vernam Şifresi), alfabe harfleri yerine doğrudan bit dizileri ($0$ ve $1$'ler) üzerinde işlem yapar. Mesaj uzunluğunun $n$ bit olduğunu varsayarsak, 5 bileşenli kriptosistem anatomisi şu şekilde tanımlanır:

* **Açık Metin ($\mathcal{P}$):** Uzunluğu $n$ olan tüm olası bit dizilerinin kümesi: $\{0, 1\}^n$
* **Şifreli Metin ($\mathcal{C}$):** Uzunluğu $n$ olan tüm olası bit dizilerinin kümesi: $\{0, 1\}^n$
* **Anahtar Uzayı ($\mathcal{K}$):** Uzunluğu $n$ olan tüm olası bit dizilerinin kümesi: $\{0, 1\}^n$
* **Şifreleme Fonksiyonu ($\mathcal{E}$):** Açık metin vektörü ($x$) ile anahtar vektörünün ($K$) karşılıklı olarak XOR'lanmasıdır:
  $$e_K(x) \equiv x \oplus K \pmod 2$$
* **Deşifreleme Fonksiyonu ($\mathcal{D}$):** Şifreli metnin ($y$), aynı anahtar ($K$) ile tekrar XOR'lanmasıdır (XOR'un nilpotent özelliği gereği):
  $$d_K(y) \equiv y \oplus K \pmod 2$$



## 🌟 Shannon'un Kusursuz Gizlilik (Perfect Secrecy) İspatı

Claude Shannon, 1949 yılında bir sistemin "Kusursuz Gizliliğe" sahip olabilmesi için şu şartı sağlaması gerektiğini matematiksel olarak ispatlamıştır:
$$P(x \mid y) = P(x)$$
Yani; şifreli metni ($y$) ele geçiren bir düşmanın, orijinal mesajın ($x$) ne olduğuna dair yapacağı olasılık hesabı, şifreli metni hiç görmeden yapacağı tahminle **birebir aynı olmalıdır**. Şifreli metin, orijinal metin hakkında **sıfır** bilgi verir.

One-Time Pad bu şartı sağlar çünkü her $x$ açık metni ve her $y$ şifreli metni için, $x \oplus K = y$ eşitliğini sağlayan **benzersiz ve tek bir $K$ anahtarı** mutlaka vardır. Anahtar tamamen rastgele seçildiği için, şifreli metnin altından "SALDIR" kelimesinin çıkma ihtimali ile "BEKLE" kelimesinin çıkma ihtimali matematiksel olarak tamamen eşittir. Düşman sonsuz işlem gücüne sahip olsa bile doğru mesajı bulamaz, çünkü ortada "kırılacak" istatistiksel bir iz yoktur.

---

## ⚠️ One-Time Pad'in 3 Altın Kuralı

Bu sistemin kusursuz olabilmesi için aşağıdaki 3 kuralın **istisnasız** uygulanması gerekir. Biri bile ihlal edilirse sistem çöker:

1. **Tam Rastgelelik (True Randomness):** Anahtar ($K$), hiçbir algoritmik kurala bağlı olmayan, evrendeki fiziksel olaylardan (örneğin radyoaktif bozunma veya atmosferik gürültü) elde edilmiş tam rastgele bitlerden oluşmalıdır. (Sözde rastgele / Pseudo-Random sayılar kullanılamaz).
2. **Uzunluk Şartı:** Anahtarın uzunluğu, şifrelenecek açık metnin uzunluğuna **eşit veya ondan daha büyük** olmalıdır ($|K| \ge |x|$).
3. **Tek Kullanımlık (Never Reuse):** Bir anahtar şeridi, sadece bir mesaj için kullanılmalı ve ardından fiziksel/dijital olarak **imha edilmelidir**.

::: danger Felaket Senaryosu: İki Kez Kullanılan Şerit (Two-Time Pad)
Eğer 3. kuralı ihlal edip aynı $K$ anahtarı ile iki farklı mesajı ($x_1$ ve $x_2$) şifrelerseniz ne olur?
$$y_1 = x_1 \oplus K$$
$$y_2 = x_2 \oplus K$$

Düşman hattı dinleyip bu iki şifreli metni ele geçirirse ve bunları birbiriyle XOR'larsa ($y_1 \oplus y_2$), aradaki anahtarlar kendilerini yok eder ($K \oplus K = 0$):
$$y_1 \oplus y_2 = (x_1 \oplus K) \oplus (x_2 \oplus K)$$
$$y_1 \oplus y_2 = x_1 \oplus x_2$$

**Sonuç:** Düşmanın elinde artık anahtardan tamamen arındırılmış, doğrudan orijinal iki mesajın birbirine XOR'lanmış hali vardır! Doğal dil analizleriyle bu iki metin dakikalar içinde birbirinden ayrıştırılıp okunabilir. Sovyetlerin ünlü "Venona Projesi"ndeki şifrelerinin kırılma sebebi, tembellik edip bazı şeritleri iki kez kullanmalarıdır.
:::

## 💡 Madem Kusursuz, Neden Her Yerde Kullanmıyoruz? (Anahtar Dağıtım Problemi)

Öğrencilerin aklına gelen ilk soru şudur: *"Eğer One-Time Pad kırılamıyorsa, neden WhatsApp, bankalar veya ordular sürekli AES veya RSA gibi kırılabilecek algoritmalar kullanıyor?"*

Cevap, kriptografinin en büyük açmazı olan **Anahtar Dağıtım Probleminde** gizlidir (Key Distribution Problem).

One-Time Pad'in 2. kuralı, anahtarın en az mesaj kadar uzun olmasını emreder. Eğer arkadaşınıza 10 GB'lık bir video dosyasını OTP ile şifreleyerek göndermek isterseniz, ona öncesinde **tamamen rastgele oluşturulmuş 10 GB'lık bir anahtar dosyasını** fiziksel ve güvenli yollarla (örneğin içi dolu bir flash bellekle) ulaştırmanız gerekir.

**Paradoks şudur:** Eğer 10 GB'lık bir veriyi düşmanların eline geçmeden arkadaşınıza ulaştırabilecek kadar güvenli bir kurye/kanal ağınız varsa, neden o kanaldan 10 GB'lık anahtarı göndermek yerine *doğrudan şifrelemek istediğiniz 10 GB'lık videoyu göndermiyorsunuz?*

İşte bu pratik imkansızlık yüzünden One-Time Pad, sadece "Kırmızı Telefon" (Moskova-Washington hattı) gibi çok yüksek güvenlikli, düşük veri boyutlu askeri/diplomatik haberleşmelerde kullanılabilmiştir.