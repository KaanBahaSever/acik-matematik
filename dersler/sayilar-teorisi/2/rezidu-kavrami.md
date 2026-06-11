# Kuadratik (İkinci Dereceden) Rezidüler

Yüksek mertebeden kongrüansları ($x^n \equiv a \pmod p$) genel hatlarıyla inceledikten sonra, Sayılar Teorisinin en önemli özel durumu olan $n=2$ durumuna, yani **İkinci Dereceden (Kuadratik) Kongrüanslara** geçiş yapıyoruz. 

Modüler aritmetikte kök bulma problemlerinin temelini oluşturan bu konu, en temelde şu soruyla başlar: Genel bir ikinci dereceden modüler denklemi nasıl çözeriz?

## 1. Genel İkinci Dereceden Denklemlerin İndirgenmesi

$p$ bir asal sayı ve $a, b, c \in \mathbb{Z}$ olmak üzere, $a \not\equiv 0 \pmod p$ şartını sağlayan genel ikinci dereceden kongrüans şu şekildedir:
$$ax^2 + bx + c \equiv 0 \pmod p$$

Eğer $p = 2$ ise, bu denklem $ax^2 + bx + c \equiv 0 \pmod 2$ halini alır ve sadece $x=0$ ile $x=1$ değerleri denenerek çözümler kolayca bulunabilir. Dolayısıyla asıl problem, $p > 2$ olan **tek asal sayılar** için çözümlerin aranmasıdır.

Aşağıdaki teorem, modül $p > 2$ tek asal sayısı olduğunda, karmaşık görünen bu genel denklemin basit bir $y^2 \equiv d \pmod p$ formatına nasıl eşdeğer olduğunu gösterir.

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Kuadratik İndirgeme ve Tam Kareye Tamamlama

  </div>

  $p > 2$ bir tek asal sayı ve $\gcd(a, p) = 1$ olmak üzere;
  $$ax^2 + bx + c \equiv 0 \pmod p$$
  kongrüansını çözmek, diskriminantı $d = b^2 - 4ac$ olan 
  $$y^2 \equiv d \pmod p$$
  kongrüansını çözmeye denk (eşdeğer) bir problemdir.

  ::: details İspat
  $f(x) = ax^2 + bx + c \equiv 0 \pmod p$ diyelim.
  
  $p$ bir tek asal sayı ($p > 2$) ve $a \not\equiv 0 \pmod p$ olduğundan, $4a$ sayısı da $p$ ile aralarında asaldır, yani $\gcd(4a, p) = 1$'dir. Bu sayede kongrüansın çözüm kümesini değiştirmeden (sadeleştirme ve genişletme kuralları gereği) her iki tarafı $4a$ ile çarpabiliriz:
  $$4a \cdot f(x) \equiv 0 \pmod p$$
  $$4a(ax^2 + bx + c) \equiv 0 \pmod p$$
  $$4a^2x^2 + 4abx + 4ac \equiv 0 \pmod p$$

  Şimdi bu ifadeyi klasik cebirdeki gibi "tam kareye" tamamlayalım. İlk iki terim $(2ax + b)^2$'nin açılımına çok benzemektedir:
  $$(2ax + b)^2 = 4a^2x^2 + 4abx + b^2$$
  Eşitliği yakalamak için denklemimize $b^2$ ekleyip çıkaralım:
  $$(4a^2x^2 + 4abx + b^2) - b^2 + 4ac \equiv 0 \pmod p$$
  $$(2ax + b)^2 \equiv b^2 - 4ac \pmod p$$

  Bu aşamada değişken değişimi yapıyoruz. $2ax + b = y$ diyelim. Bu durumda denklem şu sade forma dönüşür:
  $$y^2 \equiv b^2 - 4ac \pmod p$$

  **Birebir Eşleme (1-1 Örtenlik):**
  - Eğer $f(x) \equiv 0 \pmod p$ denkleminin bir $x_0$ çözümü varsa, $y_0 \equiv 2ax_0 + b \pmod p$ değeri de $y^2 \equiv b^2 - 4ac \pmod p$ denkleminin bir çözümüdür.
  - Tersine, eğer $y^2 \equiv b^2 - 4ac \pmod p$ denkleminin bir $y_0$ çözümü varsa, $\gcd(2a, p) = 1$ olduğu için $2ax_0 \equiv y_0 - b \pmod p$ lineer kongrüansını sağlayan **tek bir $x_0$ çözümü** kesin olarak vardır ve bu $x_0$, asıl $f(x) \equiv 0 \pmod p$ denklemini sağlar.

  O halde bu iki denklemin çözümleri arasında birebir bir eşleme vardır ve problemi başarıyla $y^2 \equiv d \pmod p$ formatına indirgedik. $\blacksquare$
  :::
</div>

Bu indirgeme ispatı bize gösteriyor ki; ikinci dereceden karmaşık bir denklemi çözmenin bütün sırrı, aslında basit bir sayının **karekökünün** modüler aritmetikte var olup olmadığını bulmaktan geçmektedir. Bu da bizi Sayılar Teorisinin temel kavramlarından biriyle tanıştırır.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: İkinci Dereceden Denklemi İndirgeme ve Çözme

  </div>

  $3x^2 + 2x + 6 \equiv 0 \pmod{11}$ kongrüansını ele alalım. 
  Burada $p = 11$ (tek asal), $a = 3$, $b = 2$ ve $c = 6$'dır. $\gcd(3, 11) = 1$ koşulu sağlanmaktadır.

  **1. Adım: Diskriminantı ($d$) Hesaplama**
  Teoreme göre denklemin diskriminantı:
  $$d = b^2 - 4ac = 2^2 - 4(3)(6) = 4 - 72 = -68$$
  Bu değeri modülo 11'de indirgersek:
  $$-68 = -77 + 9 \equiv 9 \pmod{11}$$

  **2. Adım: İndirgenmiş Denklemi Kurma ve Çözme ($y^2 \equiv d$)**
  Karmaşık denklemimiz artık $y^2 \equiv 9 \pmod{11}$ gibi çok daha basit bir forma dönüşmüştür. Hangi sayıların karesi modülo 11'de 9'u verir?
  $$y \equiv 3 \pmod{11} \quad \text{veya} \quad y \equiv -3 \equiv 8 \pmod{11}$$

  **3. Adım: Orijinal $x$ Değişkenine Dönüş**
  Teoremdeki değişken dönüşümümüz $y = 2ax + b$ şeklindeydi. Değerleri yerine koyarsak $y = 2(3)x + 2 = 6x + 2$ olur. Bulduğumuz $y$ değerlerini tek tek lineer denklemlere eşitleyelim:

  *Durum 1:* $y \equiv 3$ için
  $$6x + 2 \equiv 3 \pmod{11}$$
  $$6x \equiv 1 \pmod{11}$$
  (Modüler bölme için sağ tarafa 11 ekleyip sayıyı 6'nın katı yapalım: $1 + 11 = 12$)
  $$6x \equiv 12 \pmod{11} \implies x \equiv 2 \pmod{11}$$

  *Durum 2:* $y \equiv 8$ için
  $$6x + 2 \equiv 8 \pmod{11}$$
  $$6x \equiv 6 \pmod{11}$$
  $$x \equiv 1 \pmod{11}$$

  Sonuç olarak, başlangıçtaki $3x^2 + 2x + 6 \equiv 0 \pmod{11}$ kongrüansının çözüm kümesi eksiksiz bir şekilde **$x \in \{1, 2\}$** olarak elde edilmiştir.
  
  *(Sağlama: $x=2$ için $3(4) + 2(2) + 6 = 12 + 4 + 6 = 22 \equiv 0 \pmod{11}$.)*
</div>

## 2. Kuadratik Rezidü (Kalan) Kavramı

Bir sayının modüler aritmetikte karekökü alınabiliyorsa, o sayıya kuadratik rezidü denir.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Kuadratik Rezidü ve Non-Rezidü

  </div>

  $m \geq 2$ bir tam sayı ve $\gcd(a, m) = 1$ olsun. 
  
  Eğer $x^2 \equiv a \pmod m$ kongrüansının en az bir çözümü varsa, $a$ tam sayısına modülo $m$'ye göre bir **Kuadratik Rezidü (Karesel Kalan)** denir.
  
  Eğer $x^2 \equiv a \pmod m$ kongrüansının hiçbir çözümü yoksa, $a$ tam sayısına modülo $m$'ye göre bir **Kuadratik Non-Rezidü (Karesel Olmayan Kalan)** denir.
</div>

::: info 📝 Notasyon Anlaşması (Kısaltmalar)
Notlarımızın devamında ve ilerleyen teorik ispatlarda, terim tekrarlarını önlemek adına şu standart kısaltmaları kullanacağız:
* Kuadratik Rezidü yerine $\implies$ **KR**
* Kuadratik Non-Rezidü yerine $\implies$ **KNR**
:::

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Kuadratik Rezidü Tespiti

  </div>

  $x^2 \equiv 3 \pmod{13}$ kongrüansını inceleyelim. $a = 3$ sayısı modülo 13'e göre bir KR midir yoksa KNR midir?

  Modülo 13'teki sayıların karelerini test ettiğimizde:
  $$x = 4 \implies 4^2 = 16 \equiv 3 \pmod{13}$$
  olduğunu görürüz. 
  
  Denklemi sağlayan bir $x$ değeri (çözümü) bulunduğu için; **3 sayısı, modülo 13'e göre bir kuadratik rezidüdür (KR).**
</div>

::: info 📝 Not: Denklik Sınıfları Üzerinde Çalışmak
Eğer $a$, modülo $m$'ye göre bir kuadratik rezidü ise ve $a \equiv b \pmod m$ denkliği sağlanıyorsa, $b$ tam sayısı da modülo $m$'ye göre bir kuadratik rezidüdür. 

Dolayısıyla, modülo $m$'ye göre kuadratik rezidüleri ararken sonsuz tam sayı kümesini değil, yalnızca modülo $m$'ye göre **birbirine denk olmayan (farklı kalan sınıfındaki)** sayıları inceleriz. Birbirine denk olan sayıların kuadratik durumlarına aynı gözle bakarız.
:::

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Modülo 7 İçin KR ve KNR Kümeleri

  </div>

  Modülo 7 sistemini ele alalım. Tüm denklik sınıflarını taramak için $1 \leq x < 7$ aralığındaki sayıların karelerini incelediğimizde:
  $$
  \begin{aligned}
  1^2 &= 1 \equiv 1 \pmod 7 \\
  2^2 &= 4 \equiv 4 \pmod 7 \\
  3^2 &= 9 \equiv 2 \pmod 7 \\
  4^2 &= 16 \equiv 2 \pmod 7 \\
  5^2 &= 25 \equiv 4 \pmod 7 \\
  6^2 &= 36 \equiv 1 \pmod 7
  \end{aligned}
  $$
  
  Kare alma işlemi sonucunda elde ettiğimiz birbirinden farklı kalanlar yalnızca 1, 2 ve 4'tür. 7'den küçük diğer pozitif tam sayılar (3, 5 ve 6) ise hiçbir sayının karesi olarak elde edilememiştir. Bu durumda modülo 7 için kümelerimiz kesin olarak şöyledir:

  * **Kuadratik Rezidüler (KR):** $\{1, 2, 4\}$
  * **Kuadratik Non-Rezidüler (KNR):** $\{3, 5, 6\}$
</div>