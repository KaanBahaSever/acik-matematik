# Gauss Lemması ve 2'nin Karesel Karakteri

Legendre Sembolünün değerini hesaplamak için her zaman Euler Kriterine başvurmak zorunda değiliz. Carl Friedrich Gauss, modüler sistemin sadece yarısını ($1$'den $\frac{p-1}{2}$'ye kadar olan kısmı) inceleyerek sembolün değerini veren inanılmaz zarif bir sayma yöntemi ispatlamıştır.

## 1. Gauss Lemması

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Gauss Lemması

  </div>

  $p$ bir tek asal sayı, $a$ bir tam sayı ve $\gcd(a, p) = 1$ olsun. 
  
  $a, 2a, 3a, \dots, \left(\frac{p-1}{2}\right)a$ tam sayılarını $p$ ile bölüp kalanları bulalım. Eğer $p/2$'den büyük olan kalanların sayısı $n$ ise:
  $$\left( \frac{a}{p} \right) = (-1)^n$$
  olur.

  ::: details İspatı
  $a, 2a, 3a, \dots, \frac{p-1}{2}a$ tam sayılarını $p$ ile bölüp kalanları bulalım. Bu kalanlar kümesini büyüklüklerine göre ikiye ayıralım:
  
  * $p/2$'den **büyük** olan kalanların sayısı $n$ olsun ve bunları $r_1, r_2, \dots, r_n$ ile gösterelim.
  * $p/2$'den **küçük** olan kalanların sayısı $k$ olsun ve bunları $s_1, s_2, \dots, s_k$ ile gösterelim.

  Başlangıçtaki sayılar $\gcd(a, p)=1$ olduğu için modülo $p$'de birbirine denk olamazlar, dolayısıyla elde edilen tüm kalanlar birbirinden farklıdır. Kümenin eleman sayıları toplamı eşittir:
  $$n + k = \frac{p-1}{2}$$

  Kalanların sınırlarını yazarsak:
  $$0 < s_1, \dots, s_k \leq \frac{p-1}{2} < \frac{p}{2}$$
  $$\frac{p}{2} < \frac{p+1}{2} \leq r_1, \dots, r_n < p$$

  Şimdi büyük kalanları modül değerinden çıkararak yeni bir küme oluşturalım: $p-r_1, p-r_2, \dots, p-r_n$. Bu sayılar da birbirinden farklıdır ve $0 < p-r_i < p/2$ aralığına düşerler. 

  **Kritik Soru:** Acaba herhangi bir $p-r_i$ değeri, küçük kalanlardan bir $s_j$ değerine eşit olabilir mi? 
  Aksini varsayalım ve $p-r_i = s_j$ olsun. Modüler aritmetiğe geçersek:
  $$p - r_i \equiv s_j \pmod p \implies r_i + s_j \equiv 0 \pmod p$$
  Başlangıçtaki tanımımız gereği $r_i \equiv t_1 a \pmod p$ ve $s_j \equiv t_2 a \pmod p$ ($1 \leq t_1, t_2 \leq \frac{p-1}{2}$ olacak şekilde $t_1, t_2$ tam sayıları vardır).
  $$(t_1 a) + (t_2 a) \equiv 0 \pmod p \implies (t_1 + t_2)a \equiv 0 \pmod p$$
  $\gcd(a, p) = 1$ olduğundan sadeleştirme yapabiliriz:
  $$t_1 + t_2 \equiv 0 \pmod p$$
  Ancak $1 \leq t_1, t_2 \leq \frac{p-1}{2}$ olduğundan, toplamları en fazla $p-1$ olabilir. $0 < t_1 + t_2 < p$ iken bu toplam modülo $p$'de $0$'a denk olamaz. **Çelişki!**

  Demek ki $\{p-r_1, \dots, p-r_n\}$ kümesi ile $\{s_1, \dots, s_k\}$ kümesinin hiçbir ortak elemanı yoktur. Her iki kümenin elemanları toplamı $(n + k = \frac{p-1}{2})$ adettir ve hepsi $1$ ile $\frac{p-1}{2}$ arasındadır. O halde bu iki kümenin birleşimi bize tam olarak şu diziyi verir:
  $$\{p-r_1, \dots, p-r_n, s_1, \dots, s_k\} = \left\{1, 2, \dots, \frac{p-1}{2}\right\}$$

  Bu iki kümenin tüm elemanlarını kendi aralarında çarpalım:
  $$(p-r_1)\dots(p-r_n) \cdot s_1\dots s_k = 1 \cdot 2 \dots \frac{p-1}{2} = \left(\frac{p-1}{2}\right)!$$

  Şimdi bu eşitliğin modülo $p$'deki durumuna bakalım ($p \equiv 0$ olduğundan $p-r_i \equiv -r_i$ olur):
  $$(-r_1)\dots(-r_n) \cdot s_1\dots s_k \equiv \left(\frac{p-1}{2}\right)! \pmod p$$
  $$(-1)^n (r_1\dots r_n \cdot s_1\dots s_k) \equiv \left(\frac{p-1}{2}\right)! \pmod p$$

  $r_i$ ve $s_j$'lerin orijinal halleri $1a, 2a, \dots, \frac{p-1}{2}a$'nın kalanlarıydı. Yerlerine koyarsak:
  $$(-1)^n \cdot (a \cdot 2a \cdot 3a \dots \frac{p-1}{2}a) \equiv \left(\frac{p-1}{2}\right)! \pmod p$$
  $$(-1)^n \cdot a^{(p-1)/2} \cdot \left(1 \cdot 2 \dots \frac{p-1}{2}\right) \equiv \left(\frac{p-1}{2}\right)! \pmod p$$
  $$(-1)^n \cdot a^{(p-1)/2} \cdot \left(\frac{p-1}{2}\right)! \equiv \left(\frac{p-1}{2}\right)! \pmod p$$

  Faktöriyelli ifade $p$ ile aralarında asal olduğu için her iki tarafı bölebiliriz:
  $$(-1)^n \cdot a^{(p-1)/2} \equiv 1 \pmod p$$
  Her iki tarafı $(-1)^n$ ile çarparsak (çünkü $(-1)^n \cdot (-1)^n = 1$'dir):
  $$a^{(p-1)/2} \equiv (-1)^n \pmod p$$

  **Euler Kriterinden** biliyoruz ki $\left( \frac{a}{p} \right) \equiv a^{(p-1)/2} \pmod p$'dir. Öyleyse:
  $$\left( \frac{a}{p} \right) \equiv (-1)^n \pmod p$$
  Her iki taraf da yalnızca $\pm 1$ olabileceği ve $p > 2$ olduğu için denklik doğrudan eşitliğe dönüşür:
  $$\left( \frac{a}{p} \right) = (-1)^n \quad \blacksquare$$
  :::
</div>

Gauss Lemması, tek başına bir sayısal hesaplama yönteminden ziyade, arkasından gelecek olan devasa teoremleri kanıtlamak için bir köprüdür. Aşağıdaki teorem, Gauss Lemmasını kullanarak $a$'nın ve özel olarak $2$'nin karesel durumunu çok daha pratik bir formüle bağlar.

## 2. Legendre Sembolü İçin Genel Formül ve 2'nin Karesel Karakteri

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Karesel Karakterlerin Hesabı

  </div>

  $p$ bir tek asal sayı ve $\gcd(a, 2p) = 1$ (Yani $a$ tek tam sayı ve $p$ ile aralarında asal) olsun. Bu durumda:

  1. Eğer $t = \sum_{j=1}^{(p-1)/2} \lfloor \frac{ja}{p} \rfloor$ ise, $\left( \frac{a}{p} \right) = (-1)^t$ dir.
  2. $\left( \frac{2}{p} \right) = (-1)^{(p^2-1)/8}$ dir.

  *(Not: $\lfloor x \rfloor$ sembolü, x'in tam değerini (bölümünü) ifade eder.)*

  ::: details İspat
  **1) Birinci Kısmın İspatı:**
  $j \in \{1, 2, \dots, \frac{p-1}{2}\}$ olmak üzere $j \cdot a$ sayılarına $p$ modülünde Bölme Algoritması uygulayalım:
  $$j \cdot a = q_j \cdot p + \ell_j \quad (0 < \ell_j < p)$$
  Burada bölüm $q_j$, tam değer fonksiyonu kullanılarak $q_j = \lfloor \frac{ja}{p} \rfloor$ şeklinde ifade edilebilir. Denklemi yeniden yazalım:
  $$j \cdot a = \lfloor \frac{ja}{p} \rfloor \cdot p + \ell_j$$

  Bu eşitliği $j=1$'den $\frac{p-1}{2}$'ye kadar toplayalım:
  $$\sum_{j=1}^{(p-1)/2} (j \cdot a) = \sum_{j=1}^{(p-1)/2} \left( \lfloor \frac{ja}{p} \rfloor \cdot p \right) + \sum_{j=1}^{(p-1)/2} \ell_j$$

  Kalanlar olan $\ell_j$ dizisi, Gauss Lemması ispatındaki $r_i$ (büyük kalanlar) ve $s_i$ (küçük kalanlar) dizilerinin ta kendisidir. Kalanlar toplamını ayırırsak:
  $$a \sum j = p \sum \lfloor \frac{ja}{p} \rfloor + \sum r_j + \sum s_j \quad \dots (*)$$

  Öte yandan Gauss Lemması ispatında, $1$'den $\frac{p-1}{2}$'ye kadar olan sayıların toplamını iki parçaya ayırmıştık:
  $$\sum_{j=1}^{(p-1)/2} j = \sum_{j=1}^n (p - r_j) + \sum_{j=1}^k s_j$$
  $$\sum j = n \cdot p - \sum r_j + \sum s_j \quad \dots (**)$$

  Şimdi $(*)$ denkleminden $(**)$ denklemini taraf tarafa çıkaralım ($\sum s_j$'ler birbirini götürür):
  $$(a - 1) \sum j = p \sum \lfloor \frac{ja}{p} \rfloor - n \cdot p + 2 \sum r_j$$

  Sol taraftaki ardişık sayıların toplam formülü $\sum j = \frac{\frac{p-1}{2} \cdot (\frac{p-1}{2} + 1)}{2} = \frac{p^2-1}{8}$'dir. Yerine yazarsak:
  $$(a - 1) \frac{p^2-1}{8} = p \left( \sum \lfloor \frac{ja}{p} \rfloor - n \right) + 2 \sum r_j \quad \dots (***)$$

  Bu denklemi **modülo 2'de (çiftlik-teklik)** inceleyelim. $p$ tek asal sayı olduğundan $p \equiv 1 \pmod 2$'dir. $a$ tek tam sayı kabul edildiği için $(a-1)$ çifttir, yani $(a-1) \equiv 0 \pmod 2$'dir. Denklem şu hale gelir:
  $$0 \equiv 1 \cdot \left( \sum \lfloor \frac{ja}{p} \rfloor - n \right) + 0 \pmod 2$$
  $$n \equiv \sum \lfloor \frac{ja}{p} \rfloor \pmod 2$$
  
  Eğer $\sum \lfloor \frac{ja}{p} \rfloor = t$ dersek, $n \equiv t \pmod 2$ bulunur.
  Sonuç olarak Gauss Lemması gereği $\left( \frac{a}{p} \right) = (-1)^n$ olduğundan, üslerin mod 2'deki denkliği işareti değiştirmeyeceği için:
  $$\left( \frac{a}{p} \right) = (-1)^t \quad \blacksquare$$

  ---

  **2) İkinci Kısmın İspatı (2'nin Karesel Karakteri):**
  Bu ispat için $(***)$ etiketli ana denklemimizde $a=2$ alıp irdeleyeceğiz. Eğer $a=2$ ise toplam formülündeki terimlere bakalım:
  $$t = \sum_{j=1}^{(p-1)/2} \lfloor \frac{2j}{p} \rfloor$$
  $j$'nin alabileceği en büyük değer $\frac{p-1}{2}$'dir. O halde $2j$'nin alabileceği en büyük değer $p-1$'dir. 
  $2j < p$ olduğu için $\frac{2j}{p}$ kesri daima 1'den küçüktür. Dolayısıyla tam kısmı sıfırdır:
  $$\lfloor \frac{2j}{p} \rfloor = 0 \implies \sum \lfloor \frac{2j}{p} \rfloor = 0 \implies t = 0$$

  Şimdi $(***)$ denkleminde $a=2$ ve toplam yerine $0$ yazalım:
  $$(2 - 1) \frac{p^2-1}{8} = p (0 - n) + 2 \sum r_j$$
  $$\frac{p^2-1}{8} = -pn + 2 \sum r_j$$

  Yine bu denklemi **modülo 2'de** okuyalım. $p$ tek asal olduğundan $-p \equiv -1 \equiv 1 \pmod 2$'dir:
  $$\frac{p^2-1}{8} \equiv 1 \cdot n + 0 \pmod 2$$
  $$n \equiv \frac{p^2-1}{8} \pmod 2$$

  Gauss Lemmasına geri dönersek $\left( \frac{2}{p} \right) = (-1)^n$ olduğunu biliyoruz. Mod 2'deki denklik üslerde işareti etkilemediğinden:
  $$\left( \frac{2}{p} \right) = (-1)^{(p^2-1)/8} \quad \blacksquare$$
  :::
</div>

## 3. Teoremlerin Uygulamaları ve Çözümlü Örnekler

İspatladığımız bu soyut teoremlerin, modüler aritmetikteki karmaşık sayıların karesel karakterini bulmak için nasıl güçlü bir araca dönüştüğünü aşağıdaki örneklerle inceleyelim.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $x^2 \equiv 22 \pmod{41}$ kongrüansının çözümünün olup olmadığını Gauss Lemması ve Euler Kriteri olmak üzere iki farklı yolla inceleyiniz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle

  **Çözüm:** Burada $p=41$ (tek asal) ve $a=22$'dir. $\gcd(22, 41) = 1$.

  **1. Yol (Gauss Lemması ile):**
  Öncelikle $\frac{p-1}{2} = 20$'dir. 22'nin 1'den 20'ye kadar olan ardışık katlarını alıp, modülo 41'deki karşılıklarına bakalım:
  $$
  \begin{aligned}
  1 \cdot 22 &\equiv 22 \pmod{41} \\
  2 \cdot 22 &= 44 \equiv 3 \pmod{41} \\
  3 \cdot 22 &= 66 \equiv 25 \pmod{41} \\
  4 \cdot 22 &= 88 \equiv 6 \pmod{41} \\
  &\dots \text{ (bu şekilde } 20 \cdot 22 \text{'ye kadar devam edilir)}
  \end{aligned}
  $$
  Bu 20 adet kalanın içinden $p/2 = 20.5$'ten büyük olanları saydığımızda (örneğin 22, 25, 28, 31, 34, 37, 40, 21, 24, 27, 30), toplam sayının $n = 11$ adet olduğunu görürüz.
  Gauss Lemmasına göre:
  $$\left( \frac{22}{41} \right) = (-1)^{11} = -1$$
  Sonuç $-1$ çıktığı için 22 bir KNR'dir ve denklemin çözümü yoktur.

  ---

  **2. Yol (Euler Kriteri ile):**
  Aynı soruyu Euler kriteri ile çözelim. $\left( \frac{22}{41} \right) \equiv 22^{20} \pmod{41}$ olmalıdır.
  $$
  \begin{aligned}
  22^2 &= 484 = 41 \cdot 11 + 33 \equiv -8 \pmod{41} \\
  22^4 &\equiv (-8)^2 = 64 \equiv -18 \pmod{41} \\
  22^8 &\equiv (-18)^2 = 324 \equiv 37 \equiv -4 \pmod{41} \\
  22^{16} &\equiv (-4)^2 = 16 \pmod{41}
  \end{aligned}
  $$
  Üsleri toplayarak sonuca gidelim:
  $$22^{20} = 22^{16} \cdot 22^4 \equiv 16 \cdot (-18) = -288 \pmod{41}$$
  $$-288 = 41 \cdot (-8) + 40 \equiv -1 \pmod{41}$$
  Yani $22^{20} \equiv -1 \pmod{41}$. Sonuç yine $-1$ (KNR) olarak bulunur.

  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Euler Kriteri ile bulduğumuz $\left( \frac{-1}{p} \right) = (-1)^{(p-1)/2}$ özel değer formülünün doğruluğunu Gauss Lemmasını kullanarak ispatlayınız.

  </div>

  ::: details 💡 Çözümü Göster / Gizle

 **Çözüm:**

  $a = -1$ alalım. Gauss Lemması gereği $-1$'in katlarını yazarsak:
  $$-1, \quad 2(-1), \quad \dots, \quad \frac{p-1}{2}(-1)$$
  Bu negatif sayıların modülo $p$'deki asıl kalanlarını (modül ekleyerek) bulalım:
  $$p-1, \quad p-2, \quad \dots, \quad p - \frac{p-1}{2} = \frac{p+1}{2}$$
  Bu dizideki en küçük eleman olan $\frac{p+1}{2}$ sayısı bile $\frac{p}{2}$ değerinden büyüktür. Yani bu kalanların **hepsi** $\frac{p}{2}$'den büyüktür.
  Dolayısıyla büyük kalanların sayısı ($n$), doğrudan dizinin eleman sayısına eşittir:
  $$n = \frac{p-1}{2}$$
  Gauss Lemmasına göre $\left( \frac{a}{p} \right) = (-1)^n$ olduğundan ispat tamamlanır:
  $$\left( \frac{-1}{p} \right) = (-1)^{(p-1)/2}$$

  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $x^2 \equiv 3 \pmod{17}$ kongrüansının çözülebilirliğini $t$-toplam formülü ve Gauss Lemması olmak üzere iki yolla analiz ediniz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle

  **Çözüm:** Verilenler: $p=17$, $a=3$.

  **1. Yol ($t$-Toplam Formülü ile):**
  Önceki teoremde tanımladığımız $t = \sum_{j=1}^{(p-1)/2} \lfloor \frac{ja}{p} \rfloor$ formülünü uygulayalım. $\frac{p-1}{2} = 8$.
  $$t = \sum_{j=1}^8 \lfloor \frac{3j}{17} \rfloor = \lfloor \frac{3}{17} \rfloor + \lfloor \frac{6}{17} \rfloor + \dots + \lfloor \frac{24}{17} \rfloor$$
  Tam değerleri hesaplarsak: $0+0+0+0+0+1+1+1 = 3$.
  Yani $t = 3$. Buradan $\left( \frac{3}{17} \right) = (-1)^3 = -1$. **(Çözüm yok)**.

  ---

  **2. Yol (Gauss Lemması ile):**
  3'ün ilk 8 katının modülo 17'deki değerleri:
  $$3, 6, 9, 12, 15, 1, 4, 7$$
  Bu sayılardan $p/2 = 8.5$'ten büyük olanlar yalnızca: $9, 12, 15$'tir.
  Toplam $n=3$ adet olduğu için yine $\left( \frac{3}{17} \right) = (-1)^3 = -1$ bulunur.

  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Legendre sembolünün özelliklerini kullanarak $x^2 \equiv -2 \pmod{61}$ kongrüansının çözümünün olup olmadığını bulunuz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle

  **Çözüm:** $p=61$ ve $a=-2$'dir. Legendre sembolünün çarpımsallık özelliğini kullanarak sayıyı parçalayalım

  
  $$\left( \frac{-2}{61} \right) = \left( \frac{-1}{61} \right) \cdot \left( \frac{2}{61} \right)$$
  
  Özel değer formüllerinden her iki parçayı ayrı ayrı hesaplayalım:
  1. $\left( \frac{-1}{61} \right) = (-1)^{(61-1)/2} = (-1)^{30} = 1$
  2. $\left( \frac{2}{61} \right) = (-1)^{(61^2-1)/8}$. Üssü hesaplayalım: $\frac{3721 - 1}{8} = 465$. Bu tek bir sayı olduğu için $(-1)^{465} = -1$'dir.
  
  Bu iki sonucu çarptığımızda:
  $$\left( \frac{-2}{61} \right) = 1 \cdot (-1) = -1$$
  Sonuç $-1$ (KNR) olduğundan denklemin çözümü yoktur.

  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $p$ tek asal sayı olmak üzere, $x^2 \equiv 2 \pmod p$ denkleminin çözülebilir olması için gerek ve yeter koşul nedir?

  </div>

  ::: details 💡 Çözümü Göster / Gizle

  **Çözüm:** Denklemin çözülebilmesi için 2'nin KR olması, yani $\left( \frac{2}{p} \right) = 1$ olması zorunludur.
  2'nin karesel karakter formülünü hatırlayalım
  $$\left( \frac{2}{p} \right) = (-1)^{(p^2-1)/8} = 1$$
  Bu eşitliğin $1$ çıkabilmesi için, üs olan $\frac{p^2-1}{8}$ ifadesinin **çift tam sayı** ($2k$) olması zorunludur:
  $$\frac{p^2-1}{8} = 2k \implies p^2 - 1 = 16k \implies p^2 \equiv 1 \pmod{16}$$
  Asal sayılar analiz edildiğinde bu durumun sadece $p \equiv 1 \pmod 8$ veya $p \equiv -1 \pmod 8$ (yani $p \equiv 7 \pmod 8$) formatındaki asallarda sağlandığı kesin olarak görülür.

  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $m \geq 2$ bir tam sayı ve $\gcd(r, m) = 1$ olsun. Eğer $r$, modülo $m$'ye göre bir Kuadratik Rezidü ise, $r^{\phi(m)/2} \equiv 1 \pmod m$ olduğunu gösteriniz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle

  **Çözüm:** $r$, bir KR olduğundan $x^2 \equiv r \pmod m$ denklemini sağlayan en az bir $a$ tam sayısı vardır.

  
  $$a^2 \equiv r \pmod m$$
  $\gcd(r, m) = 1$ olduğundan, $\gcd(a^2, m) = 1$ ve dolayısıyla $a$ da modül ile aralarında asaldır ($\gcd(a, m) = 1$).
  
  Kongrüansın her iki tarafının $\frac{\phi(m)}{2}$'nci kuvvetini alalım:
  $$r^{\phi(m)/2} \equiv (a^2)^{\phi(m)/2} \equiv a^{\phi(m)} \pmod m$$
  
  $a$ ve $m$ aralarında asal olduğu için **Euler Teoremi** devreye girer ve $\gcd(a,m)=1$ iken $a^{\phi(m)} \equiv 1 \pmod m$'dir. Yerine yazdığımızda ispat tamamlanır:
  $$r^{\phi(m)/2} \equiv 1 \pmod m \quad \blacksquare$$

  :::
</div>