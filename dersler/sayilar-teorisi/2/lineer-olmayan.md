# Doğrusal Diofant Denklemleri

Sayılar teorisinde katsayıları ve aranılan çözümleri yalnızca **tam sayılar** olan denklemlere Diofant Denklemleri denir. Bu bölümde yüksek dereceli karmaşık yapılar yerine, modüler aritmetik ve Öklid Algoritması ile doğrudan bağlantılı olan birinci dereceden (lineer) denklemleri inceleyeceğiz.

## 1. Tanım ve Çözülebilirlik Şartı

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: 1. Dereceden İki Bilinmeyenli Diofant Denklemi

  </div>

  $a, b, c \in \mathbb{Z} - \{0\}$ olmak üzere;
  $$ax + by = c$$
  şeklinde ifade edilen ve yalnızca tam sayılı $x$ ve $y$ çözümleri aranan denklemlere **1. dereceden iki bilinmeyenli bir Diofant denklemi** denir.
</div>

Bu denklemleri çözmek, aslında daha önce öğrendiğimiz lineer kongrüansları çözmekle birebir aynı şeydir. Çünkü:
$$ax + by = c \iff ax \equiv c \pmod b$$
denkliği vardır. Dolayısıyla $ax + by = c$ denklemini çözme problemi, $ax \equiv c \pmod b$ kongrüansını çözme problemine denktir.

::: info 💡 Çözülebilirlik ve Sadeleştirme Kuralı
1. **Çözülebilirlik Şartı:** Bir $ax + by = c$ Diofant denkleminin tam sayılı çözümünün olabilmesi için gerek ve yeter koşul, **$\gcd(a, b) \mid c$** olmasıdır. (Yani $a$ ve $b$'nin en büyük ortak böleni, $c$'yi tam bölmelidir).
2. **Sadeleştirme:** Eğer $\gcd(a, b) \mid c$ şartı sağlanıyorsa, denklem çözülebilirdir. İşlemleri kolaylaştırmak için denklemin her iki tarafını bu en büyük ortak bölene böleriz:
   $$\frac{a}{\gcd(a,b)}x + \frac{b}{\gcd(a,b)}y = \frac{c}{\gcd(a,b)}$$
3. Bu sadeleştirme sonucunda, yeni katsayılarımız daima aralarında asal olur. Bu yüzden Diofant denklemlerini incelerken genel olarak **$\gcd(a, b) = 1$** olan sadeleştirilmiş formlar üzerinde çalışmak yeterlidir.
:::

## 2. Genel Çözüm Teoremi

Eğer elimizde denklemi sağlayan sadece bir tane başlangıç çözümü (özel çözüm) varsa, bu çözümü kullanarak sonsuz sayıdaki diğer tüm çözümleri nasıl bulacağımızı aşağıdaki teorem söyler.

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Diofant Denkleminin Genel Çözümü

  </div>

  $a, b, c \in \mathbb{Z} - \{0\}$ ve $\gcd(a, b) = 1$ olsun. 
  Bu durumda, $ax + by = c$ Diofant denkleminin bir tam sayılı özel çözümü $(x_0, y_0)$ ise, denklemin **bütün tam sayılı çözümleri** $t \in \mathbb{Z}$ olmak üzere şu şekildedir:
  $$x = x_0 + b \cdot t, \quad y = y_0 - a \cdot t$$

  ::: details İspat
  $x, y$ değerleri, $ax + by = c$ denkleminin herhangi bir tam sayılı çözümü olsun. 
  $(x_0, y_0)$ da özel bir çözüm olduğundan $ax_0 + by_0 = c$'dir. Bu iki denklemi taraf tarafa çıkaralım:
  
  $$\left. \begin{array}{l} ax + by = c \\ ax_0 + by_0 = c \end{array} \right\} \implies a(x - x_0) + b(y - y_0) = 0$$
  
  Terimlerden birini karşıya atalım:
  $$a(x - x_0) = -b(y - y_0)$$
  
  Bu eşitlikten anlıyoruz ki $b$ sayısı, sol tarafı yani $a(x - x_0)$ çarpımını tam bölmektedir:
  $$b \mid a(x - x_0)$$
  
  Teoremin başında $\gcd(a, b) = 1$ (aralarında asal) kabul etmiştik. Öklid'in lemasına göre, eğer $b$ çarpımı bölüyorsa ve çarpanlardan biriyle ($a$) aralarında asalsa, mecburen diğer çarpanı tam bölmek zorundadır:
  $$b \mid (x - x_0) \implies x - x_0 = b \cdot t \quad (t \in \mathbb{Z})$$
  $$x = x_0 + b \cdot t$$
  
  Şimdi bu bulduğumuz $(x - x_0) = b \cdot t$ ifadesini yukarıdaki asıl denklemde yerine yazalım:
  $$a(b \cdot t) + b(y - y_0) = 0$$
  Her iki tarafı $b$'ye bölersek ($b \neq 0$):
  $$a \cdot t + y - y_0 = 0 \implies y - y_0 = -a \cdot t \implies y = y_0 - a \cdot t$$
  
  Tersine, bulduğumuz $x = x_0 + bt$ ve $y = y_0 - at$ tam sayıları $ax+by=c$ denkleminde yerine konulduğunda denklemi her zaman sağlar. Dolayısıyla tüm çözümleri bulmuş oluruz. $\blacksquare$
  :::
</div>

## 3. Öklid Algoritması ile Çözümlü Örnekler

Eğer katsayılar küçükse deneme-yanılma ile bir $x_0, y_0$ bulabiliriz. Ancak katsayılar büyükse, "Genişletilmiş Öklid Algoritması" kullanarak en büyük ortak böleni geriye doğru açarız ve o sihirli ilk çözümü algoritmik olarak buluruz.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $30x + 66y = 41$ Diofant denkleminin çözümünü araştırınız.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  Çözülebilirlik şartını kontrol etmeliyiz: $\gcd(a, b) \mid c$ olmalıdır.
  $\gcd(30, 66) = 6$'dır.
  Ancak $6$ sayısı $41$'i tam bölmez ($6 \nmid 41$). 
  
  Bu nedenle verilen Diofant denklemi **çözümsüzdür** (Hiçbir tam sayı çözümü yoktur).
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $291x + 549y = 54$ Diofant denkleminin tüm tam sayı çözümlerini bulunuz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **1. Çözülebilirlik ve Sadeleştirme:**
  $\gcd(291, 549) = 3$ ve $3 \mid 54$ olduğundan denklemin sonsuz çözümü vardır.
  Denklemin her iki tarafını 3'e bölerek sadeleştirelim:
  $$97x + 183y = 18$$
  Artık aralarında asal olan 97 ve 183 sayılarıyla çalışacağız.

  **2. Öklid Algoritması:**
  183 ve 97 için bölme algoritmasını uygulayalım. Bu aşamada hedefimiz sağ taraftaki 18'i elde etmek olduğu için, kalanları dikkatle izleyelim:
  $$
  \begin{aligned}
  183 &= 1 \cdot 97 + 86 &\implies 86 &= 183 - 97 \\
  97 &= 1 \cdot 86 + 11 &\implies 11 &= 97 - 86 \\
  86 &= 7 \cdot 11 + 9 &\implies 9 &= 86 - 7 \cdot 11
  \end{aligned}
  $$
  *(Not: Algoritmayı 1 kalanına kadar indirmeye gerek yoktur. Çünkü 9 sayısı, aradığımız 18'in tam yarısıdır! İşlemi burada kesip 9'u yalnız bırakıyoruz.)*

  **3. Geriye Doğru Yerine Koyma (Kısayol):**
  Şimdi sondan başa doğru giderek 9'u, 97 ve 183 cinsinden ifade edelim:
  $$
  \begin{aligned}
  9 &= 86 - 7 \cdot 11 \\
    &= 86 - 7 \cdot (97 - 86) \\
    &= 86 - 7 \cdot 97 + 7 \cdot 86 \\
    &= 8 \cdot 86 - 7 \cdot 97 \\
    &= 8 \cdot (183 - 97) - 7 \cdot 97 \\
    &= 8 \cdot 183 - 8 \cdot 97 - 7 \cdot 97 \\
  9 &= 183 \cdot (8) + 97 \cdot (-15)
  \end{aligned}
  $$
  Doğrusal birleşimimizi bulduk: $97 \cdot (-15) + 183 \cdot (8) = 9$.

  **4. Hedef Denkleme Ulaşma:**
  Sadeleşmiş denklemimizin sağ tarafı 9 değil, 18'di ($97x + 183y = 18$).
  Bulduğumuz eşitliğin her iki tarafını 2 ile çarparak asıl denkleme ulaşıyoruz:
  $$
  \begin{aligned}
  2 \cdot [97 \cdot (-15) + 183 \cdot (8)] &= 2 \cdot 9 \\
  97 \cdot (-30) + 183 \cdot (16) &= 18
  \end{aligned}
  $$
  O halde ilk özel çözümümüz: 
  $$x_0 = -30, \quad y_0 = 16$$

  **5. Genel Çözüm Formülü:**
  Özel çözümümüzü genel çözüm formülüne ($x = x_0 + bt$, $y = y_0 - at$) yerleştirelim. Sadeleşmiş denklemimizde $a=97$ ve $b=183$'tür:
  $$
  \begin{aligned}
  x &= -30 + 183t \\
  y &= 16 - 97t
  \end{aligned}
  $$
  Denklemin bütün tam sayı çözümleri $(t \in \mathbb{Z})$ bu şekildedir.
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $312x + 51y = 9$ Diofant denklemini çözünüz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **1. Sadeleştirme:**
  $\gcd(312, 51) = 3$ ve $3 \mid 9$ olduğundan çözüm vardır. 3 ile bölelim:
  $$104x + 17y = 3$$

  **2. Öklid Algoritması (104 ve 17 için):**
  $$
  \begin{aligned}
  104 &= 6 \cdot 17 + 2 \\
  17 &= 8 \cdot 2 + 1 \\
  2 &= 2 \cdot 1 + 0
  \end{aligned}
  $$

  **3. Geriye Dönüş:**
  $1 = 17 - 8 \cdot 2$
  (Üstten $2 = 104 - 6 \cdot 17$ koyalım)
  $1 = 17 - 8(104 - 6 \cdot 17) = 17 - 8 \cdot 104 + 48 \cdot 17$
  $1 = 104 \cdot (-8) + 17 \cdot (49)$

  **4. Hedef Denkleme Genişletme:**
  Denklemimizin sağ tarafı 3 olduğu için, eşitliğin iki tarafını 3 ile çarpalım:
  $$3 \cdot 1 = 3 \cdot [104 \cdot (-8) + 17 \cdot (49)]$$
  $$3 = 104 \cdot (-24) + 17 \cdot (147)$$
  Buradan özel çözümümüz: $x_0 = -24$ ve $y_0 = 147$ olarak bulunur.

  **5. Genel Çözüm:**
  $a=104$ ve $b=17$ kullanılarak:
  $$x = -24 + 17t$$
  $$y = 147 - 104t \quad (t \in \mathbb{Z})$$
  :::
</div>

## 4. Çalışma Problemleri (Kendini Dene)

Konuyu pekiştirmek için aşağıdaki Diofant denklemlerinin bütün tam sayılı çözümlerini bulunuz (Önce çözülebilirlik şartı olan $\gcd(a,b) \mid c$ kuralını kontrol etmeyi unutmayın).

* **a)** $3x + 5y = 1$
* **b)** $5x + 3y = 52$
* **c)** $40x + 63y = 521$
* **d)** $330x + 175y = 50$
* **e)** $15x - 7y = 111$
* **f)** $12x + 501y = 1$
* **g)** $10x - 7y = 17$
* **h)** $15x + 11y = 1$