# Kuvvet Rezidüler ve Mertebe (Eksponent) Kavramı

Sayılar Teorisi II dersi kapsamında, yüksek mertebeden kongrüansların çözüm stratejilerini geride bıraktıktan sonra, modüler yapılardaki çözülebilirliği ve döngüsel periyotları incelediğimiz bu konuya giriş yapıyoruz.

## 1. $n$. Kuvvet Rezidü Kavramı

Bir sayının belirli bir modüle göre bir tam kuvvetinin alınıp alınamayacağını ifade eden yapıya "rezidü (kalan)" denir.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: $n$. Kuvvet Rezidü

  </div>
  
  $n$ pozitif bir tam sayı ve $m \geq 2$ bir modül olsun. Eğer:
  $$x^n \equiv a \pmod m$$
  kongrüansının (denkliğinin) bir $x$ çözümü varsa, $a$ sayısına modülo $m$'ye göre bir **$n$. kuvvet rezidüsü** denir.
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Rezidü Kavramı

  </div>
  
  $x^3 \equiv 2 \pmod 5$ denklemini inceleyelim. $x \equiv 3 \pmod 5$ denediğimizde:
  $$3^3 = 27 \equiv 2 \pmod 5$$
  Denklem sağlandığı için **2 sayısı, modülo 5'e göre bir 3. kuvvet rezidüsüdür.**
</div>

Rezidüler bize temelde bir denklemin kökü olup olmadığını söyler. Ancak modüler aritmetikte asıl sihir, bir sayının kuvvetlerini almaya devam ettiğimizde ortaya çıkan döngüselliktir. Sayılar sonsuza kadar büyümez, modüle ulaştığında başa sarar. İşte bu "başa sarma" noktasını ölçmek için yeni bir kavrama ihtiyacımız var.

## 2. Mertebe (Eksponent) Nedir?

Euler-Fermat Teoreminden biliyoruz ki; $\gcd(a, m) = 1$ ise $a^{\phi(m)} \equiv 1 \pmod m$'dir. Yani $a$'nın kuvvetlerini almaya devam ettiğimizde *eninde sonunda* sonucu 1 yapan bir üs (garanti olarak $\phi(m)$) karşımıza çıkar. Peki döngüyü tamamlayıp 1 sonucunu veren **en küçük** üs hangisidir?

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Mertebe (Eksponent)

  </div>
  
  $m \geq 2$ bir tam sayı ve $\gcd(a, m) = 1$ olsun.
  $$a^x \equiv 1 \pmod m$$
  koşulunu sağlayan **en küçük pozitif $x$ tam sayısına**, $a$'nın modülo $m$'ye göre **mertebesi** (veya eksponenti) denir ve genellikle $\operatorname{ord}_m(a)$ ile gösterilir.
</div>

Mertebeyi tanımladık, peki bu sayı rastgele bir değer midir? Elbette hayır. Bir sayının modüler döngü uzunluğu (mertebesi), o modülün Euler Phi değeriyle doğrudan ve kusursuz bir bölünme ilişkisi içindedir.

## 3. Mertebe ve Euler Phi İlişkisi

Sayılar Teorisinin en temel ve zarif ispatlarından biri olan bu ilişki, mertebenin sınırlarını kesin olarak çizer.

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Mertebe $\phi(m)$'i Böler

  </div>
  
  $m \geq 2$ bir tam sayı, $\gcd(a, m) = 1$ ve $a$'nın modülo $m$'ye göre mertebesi $h$ olsun. Bu durumda $h$, $\phi(m)$'i tam böler. Notasyonla:
  $$h \mid \phi(m)$$

  ::: details İspat
  Bu teoremi ispatlamak için **Bölme Algoritmasını** kullanacağız. Elimizde iki tam sayı var: $\phi(m)$ ve $h$.

  $\phi(m)$ sayısını $h$'ye bölelim. Bu durumda, bölüm $q$ ve kalan $r$ olmak üzere şöyle bir denklem yazabiliriz:
  $$\phi(m) = q \cdot h + r \quad (0 \leq r < h)$$

  Euler-Fermat Teoremi gereği, $\gcd(a,m)=1$ olduğu için şunu kesin olarak biliyoruz:
  $$a^{\phi(m)} \equiv 1 \pmod m$$

  Şimdi $\phi(m)$ yerine bölme algoritmasından elde ettiğimiz eşitliği yazalım:
  $$a^{q \cdot h + r} \equiv 1 \pmod m$$

  Üslü sayıların özelliklerini kullanarak bu ifadeyi parçalayalım:
  $$(a^h)^q \cdot a^r \equiv 1 \pmod m$$

  Başlangıçtaki kabulümüze göre $h$, $a$'nın mertebesidir. Yani mertebe tanımı gereği **$a^h \equiv 1 \pmod m$**'dir. Bunu denklemde yerine koyalım:
  $$(1)^q \cdot a^r \equiv 1 \pmod m \implies a^r \equiv 1 \pmod m$$

  **Kritik Mantıksal Adım:** Elimizde $a^r \equiv 1 \pmod m$ şartını sağlayan bir $r$ sayısı kaldı. Üstelik bölme algoritmasının kuralı gereği bu $r$ sayısı $h$'den küçüktür ($0 \leq r < h$).

  Fakat biz $h$'yi, $a^x \equiv 1$ şartını sağlayan **en küçük pozitif tam sayı** olarak tanımlamıştık! Eğer $r > 0$ olsaydı, $h$'den daha küçük pozitif bir sayı bu şartı sağlamış olurdu ki bu durum mertebe tanımıyla çelişir.

  Çelişkiyi önlemenin tek yolu $r$'nin sıfır olmasıdır:
  $$r = 0$$

  Kalan sıfır olduğuna göre, bölme denklemine geri dönersek:
  $$\phi(m) = q \cdot h + 0 \implies \phi(m) = q \cdot h$$
  Bu da tam olarak $h$'nin $\phi(m)$'i tam böldüğü anlamına gelir.
  $$h \mid \phi(m) \quad \blacksquare$$
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Mertebenin $\phi(m)$'i Bölmesi

  </div>

  $m = 7$ ve $a = 2$ olsun. $\gcd(2, 7) = 1$ olduğu açıktır. Öncelikle $\phi(7) = 6$'dır.

  Şimdi 2'nin modülo 7'ye göre mertebesi olan $h$ değerini bulalım. Bunun için 2'nin kuvvetlerini sırasıyla alıyoruz:
  $$
  \begin{aligned}
  2^1 &\equiv 2 \pmod 7 \\
  2^2 &\equiv 4 \pmod 7 \\
  2^3 &\equiv 8 \equiv 1 \pmod 7
  \end{aligned}
  $$
  Sonucu 1 yapan en küçük pozitif üs 3 olduğu için 2'nin mertebesi $h = 3$'tür.

  Teoremin ifade ettiği üzere, mertebe olan 3 sayısı, $\phi(7) = 6$ değerini tam böler ($3 \mid 6$).
</div>

Bu teorem sayesinde mertebenin alabileceği değerleri sınırlandırmış olduk. Peki, bir sayının kuvvetlerini alırken iki farklı üs bize aynı sonucu veriyorsa (örneğin $a^j \equiv a^k$) bu durum üsler hakkında bize ne söyler? İşte bu nokta, mertebenin bir "periyot" olarak nasıl davrandığını gösterir.

## 4. Üslerin Denkliği ve Periyodiklik

İki farklı kuvvetin modüler sistemde aynı kalanı vermesi tesadüf değildir. Üslerin arasındaki fark, doğrudan sayının mertebesiyle bağlantılıdır.

<div class="math-block theorem">
  <div class="math-block-title">

  Önerme: Üslerin Denkliği ve Mertebe İlişkisi

  </div>
  
  $m \geq 2$ bir tam sayı, $\gcd(a, m) = 1$ ve $a$'nın modülo $m$'ye göre mertebesi $h$ olsun. $j, k \geq 0$ tam sayıları için bu ilişki mantıksal olarak şu şekilde ifade edilir:

  $$a^j \equiv a^k \pmod m \implies h \mid (j - k)$$

  ::: details İspat
  İspata başlarken genelliği bozmadan $j \geq k$ olduğunu kabul edebiliriz.

  Elimizdeki başlangıç denkliği:
  $$a^j \equiv a^k \pmod m$$

  $\gcd(a, m) = 1$ olduğu için, $a$'nın herhangi bir pozitif kuvveti de $m$ ile aralarında asaldır, yani $\gcd(a^k, m) = 1$'dir. Bu sayede her iki tarafı güvenle $a^k$'ya bölebiliriz (veya çarpımsal tersi olan $a^{-k}$ ile çarpabiliriz):
  $$a^{j-k} \equiv 1 \pmod m$$

  Şimdi, bir önceki teoremde uyguladığımız **Bölme Algoritmasını** tekrar kullanalım. $(j-k)$ tam sayısını, mertebemiz olan $h$'ye bölelim. Bölüm $q$ ve kalan $r$ olmak üzere:
  $$j - k = q \cdot h + r \quad (0 \leq r < h)$$

  Bu eşitliği modüler denklemimizde yerine yazalım:
  $$a^{q \cdot h + r} \equiv 1 \pmod m$$

  Üslü sayıların özellikleriyle parçalayalım:
  $$(a^h)^q \cdot a^r \equiv 1 \pmod m$$

  Mertebe tanımı gereği $a^h \equiv 1 \pmod m$'dir. Yerine koyduğumuzda:
  $$(1)^q \cdot a^r \equiv 1 \pmod m \implies a^r \equiv 1 \pmod m$$

  **Kritik Mantıksal Adım:** Yine aynı çelişki argümanına ulaştık. Elimizde $a^r \equiv 1 \pmod m$ var ve kalan olduğu için $0 \leq r < h$ şartını sağlıyor. Ancak $h$, bu denkliği sağlayan **en küçük pozitif** tam sayıydı! Eğer $r > 0$ olsaydı, mertebe tanımı çökerdi.

  Bu çelişkiden kaçınmanın tek yolu kalanın sıfır olmasıdır:
  $$r = 0$$

  Kalan sıfır olduğuna göre bölme algoritmamıza geri dönersek:
  $$j - k = q \cdot h + 0 \implies j - k = q \cdot h$$
  Bu da tam olarak $h$'nin $(j - k)$ farkını tam böldüğü anlamına gelir.
  $$h \mid (j - k) \quad \blacksquare$$
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Üslerin Denkliği ve Mertebe İlişkisi

  </div>

  Bir önceki örnekten devam edelim: Modülümüz $m = 7$, sayımız $a = 2$ ve bu sayının mertebesi $h = 3$'tür. Denklemdeki üsler olarak $j = 8$ ve $k = 2$ seçelim.

  Üslerin modülo 7'deki değerlerini hesaplarsak:
  $$
  \begin{aligned}
  2^8 &= 256 \equiv 4 \pmod 7 \\
  2^2 &= 4 \equiv 4 \pmod 7
  \end{aligned}
  $$
  Görüldüğü üzere $2^8 \equiv 2^2 \pmod 7$ denkliği kusursuz bir şekilde sağlanmaktadır.

  Önermenin ifade ettiği kurala göre; mertebemiz olan $h = 3$, üslerin farkı olan $(8 - 2) = 6$ sayısını tam bölmelidir. Gerçekten de $3 \mid 6$'dır.
</div>

Şimdiye kadar hep saf bir $a$ tabanının mertebesiyle ilgilendik. Pratik problemlerde ise çoğu zaman, mertebesini zaten bildiğimiz bir sayının **belli bir kuvvetinin** (örneğin $a^k$) mertebesini hesaplamamız istenir. Her defasında tek tek kuvvet alarak döngüyü baştan hesaplamak yerine, aşağıdaki teorem sayesinde tek bir formülle sonuca ulaşabiliriz.

## 5. Bir Kuvvetin Mertebesini Hesaplama

Eğer bir tabanın mertebesini biliyorsanız, o tabandan türetilmiş herhangi bir kuvvetin mertebesini de zahmetsizce bulabilirsiniz.

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Bir Kuvvetin Mertebesi

  </div>
  
  $m \geq 2$ bir tam sayı, $\gcd(a, m) = 1$ ve $k \in \mathbb{Z}^+$ olmak üzere, $a$'nın modülo $m$'ye göre mertebesi $h$ olsun. Bu durumda, $a^k$ tam sayısının modülo $m$'ye göre mertebesi şu formülle hesaplanır:
  $$\frac{h}{\gcd(h, k)}$$

  ::: details İspat
  $\gcd(a, m) = 1$ olduğundan, $\gcd(a^k, m) = 1$'dir.

  $a^k$ tam sayısının modülo $m$'ye göre mertebesi $t$ olsun ($t \in \mathbb{Z}^+$). Mertebe tanımı gereği:
  $$(a^k)^t = a^{k \cdot t} \equiv 1 \pmod m$$

  Bir önceki önermeden biliyoruz ki, eğer bir kuvvet 1'e denkse, tabanın mertebesi o kuvveti tam böler. $a$'nın mertebesi $h$ olduğuna göre:
  $$h \mid (k \cdot t)$$

  Bölünebilme özelliğini kullanarak her iki tarafı $\gcd(h, k)$ değerine bölelim:
  $$\frac{h}{\gcd(h, k)} \mid \left( \frac{k}{\gcd(h, k)} \cdot t \right)$$

  Biliyoruz ki, bir sayıyı en büyük ortak bölenine böldüğümüzde elde edilen bölümler her zaman aralarında asaldır:
  $$\gcd\left( \frac{h}{\gcd(h, k)}, \frac{k}{\gcd(h, k)} \right) = 1$$

  **Aritmetiğin Esas Yardımcı Teoremi (Öklid Lemması)** gereği; eğer bir tam sayı bir çarpımı tam bölüyorsa ve çarpanlardan biriyle aralarında asalsa, diğer çarpanı tam bölmek zorundadır. Bu nedenle:
  $$\frac{h}{\gcd(h, k)} \mid t \quad \dots (*)$$

  Öte yandan, $a^k$'nın $\frac{h}{\gcd(h, k)}$'nci kuvvetini alalım:
  $$(a^k)^{\frac{h}{\gcd(h, k)}} = a^{\frac{k \cdot h}{\gcd(h, k)}} = (a^h)^{\frac{k}{\gcd(h, k)}}$$

  $a$'nın mertebesi $h$ olduğundan $a^h \equiv 1 \pmod m$'dir. Yerine yazarsak:
  $$(a^h)^{\frac{k}{\gcd(h, k)}} \equiv 1^{\frac{k}{\gcd(h, k)}} \equiv 1 \pmod m$$

  Yani, $a^k$'nın $\frac{h}{\gcd(h, k)}$'nci kuvveti 1'e denktir. Mertebenin tanımı ve bir önceki önerme gereği, $a^k$'nın mertebesi olan $t$, 1 sonucunu veren her kuvveti tam bölmek zorundadır:
  $$t \mid \frac{h}{\gcd(h, k)} \quad \dots (**)$$

  Hem $t$ hem de $\frac{h}{\gcd(h, k)}$ pozitif tam sayılar olduğundan, $(*)$ ve $(**)$ durumlarının aynı anda sağlanabilmesi için bu iki ifadenin birbirine eşit olması zorunludur:
  $$t = \frac{h}{\gcd(h, k)} \quad \blacksquare$$
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Bir Kuvvetin Mertebesini Bulma

  </div>

  $m = 11$ ve $a = 2$ olsun. $\gcd(2, 11) = 1$'dir.

  Hesaplamalar yapıldığında $2^{10} \equiv 1 \pmod{11}$ olduğu ve daha küçük bir kuvvette 1 sonucuna ulaşılamadığı görülür. Yani 2'nin modülo 11'e göre mertebesi $h = 10$'dur.

  Şimdi, tabanımızın $k = 4$. kuvveti olan $2^4 \equiv 16 \equiv 5 \pmod{11}$ sayısının mertebesini arayalım. Teoreme göre bu yeni sayının mertebesi şu formülle bulunur:
  $$\frac{h}{\gcd(h, k)} = \frac{10}{\gcd(10, 4)} = \frac{10}{2} = 5$$

  Sağlamasını yapmak için elde ettiğimiz sayının (yani 5'in) modülo 11'deki kuvvetlerine bakalım:
  $$
  \begin{aligned}
  5^1 &\equiv 5 \pmod{11} \\
  5^2 &= 25 \equiv 3 \pmod{11} \\
  5^3 &= 125 \equiv 4 \pmod{11} \\
  5^4 &= 625 \equiv 9 \pmod{11} \\
  5^5 &= 3125 \equiv 1 \pmod{11}
  \end{aligned}
  $$
  Görüldüğü üzere, $2^4$'ün (yani 5'in) mertebesi gerçekten de formülün verdiği gibi tam olarak 5'tir.
</div>

## 6. Primitif (İlkel) Kök Kavramı

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Primitif Kök

  </div>

  $m \geq 2$ bir tam sayı ve $\gcd(a, m) = 1$ olsun. Eğer $a$'nın modülo $m$'ye göre mertebesi tam olarak $\phi(m)$ ise, $a$'ya modülo $m$'ye göre bir **primitif kök (ilkel kök)** denir.
</div>


Her modül değerinin bir primitif kökü olmak zorunda değildir. Hangi modüllerin primitif kök barındırdığı, Sayılar Teorisinin ünlü ve kapsamlı teoremlerinden biriyle kesin olarak sınıflandırılmıştır.

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Primitif Köklerin Varlığı

  </div>

  $m \geq 2$ bir tam sayı olsun. Modülo $m$'ye göre bir primitif kökün var olabilmesi için gerek ve yeter şart $m$'nin aşağıdaki formlardan birinde olmasıdır:
  $$m \in \{2, 4, p^n, 2p^n\}$$
  Burada $p$ herhangi bir tek asal sayı ve $n$ herhangi bir pozitif tam sayıdır. $m$'nin başka hiçbir değeri için modülo $m$'ye göre primitif kök yoktur.
</div>
<div class="math-block example">
  <div class="math-block-title">

  Örnek: Primitif Kökün Varlığı ve Yokluğu

  </div>

  **1. Primitif Kökü Olan Bir Modül ($m = 7$):** &nbsp;
  $m = 7$ asaldır ($p^1$ formuna uyar). $\phi(7) = 6$'dır. Acaba $a = 3$ bir primitif kök müdür? 3'ün modülo 7'ye göre kuvvetlerine bakalım:
  $$
  \begin{aligned}
  3^1 &\equiv 3 \pmod 7 \\
  3^2 &\equiv 2 \pmod 7 \\
  3^3 &\equiv 6 \pmod 7 \\
  3^4 &\equiv 4 \pmod 7 \\
  3^5 &\equiv 5 \pmod 7 \\
  3^6 &\equiv 1 \pmod 7
  \end{aligned}
  $$
  Görüldüğü üzere, 1 sonucunu veren en küçük pozitif üs 6'dır. Yani 3'ün mertebesi tam olarak $\phi(7) = 6$'ya eşittir. Bu nedenle **3, modülo 7'ye göre bir primitif köktür.**

  **2. Primitif Kökü Olmayan Bir Modül ($m = 8$):** &nbsp;
  $m = 8$ sayısını inceleyelim. $8 = 2^3$ olduğundan, varlık teoreminin izin verdiği $\{2, 4, p^n, 2p^n\}$ kümelerinden hiçbirine uymaz. $\phi(8) = 4$'tür ve 8 ile aralarında asal sayılar $\{1, 3, 5, 7\}$'dir.
  Bu sayıların kuvvetlerini alırsak:
  $$
  \begin{aligned}
  1^1 &\equiv 1 \pmod 8 \\
  3^2 &\equiv 9 \equiv 1 \pmod 8 \\
  5^2 &\equiv 25 \equiv 1 \pmod 8 \\
  7^2 &\equiv 49 \equiv 1 \pmod 8
  \end{aligned}
  $$
  Görüldüğü üzere hiçbir elemanın mertebesi $\phi(8) = 4$'e ulaşamaz (maksimum mertebe 2'de kalır). Bu nedenle **modülo 8'in hiçbir primitif kökü yoktur.**
</div>

Eğer elimizde bir primitif kök varsa, bu kök o modüldeki bütün çarpımsal yapıyı tek başına üretebilme gücüne sahiptir. Aşağıdaki teorem, primitif köklerin bu "üretici" gücünü ve üslerle olan kusursuz ilişkisini gösterir.

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Primitif Köklerin Özellikleri

  </div>

  $a$, modülo $m$'ye göre bir primitif kök olsun. Bu durumda aşağıdaki özellikler sağlanır:

  1. Herhangi $j, k \geq 0$ tam sayıları için:
     $$a^j \equiv a^k \pmod m \iff j \equiv k \pmod{\phi(m)}$$
  2. Herhangi $j \geq 0$ tam sayısı için:
     $$a^j \equiv 1 \pmod m \iff \phi(m) \mid j$$
  3. $a, a^2, a^3, \dots, a^{\phi(m)}$ tam sayıları, modülo $m$'ye göre bir **asal kalanlar sistemi** oluşturur.

  ::: details İspat
  **1) Birinci Özelliğin İspatı:**

  *Gereklilik ($\implies$):* Kabul edelim ki $a^j \equiv a^k \pmod m$ olsun.
  $a$, modülo $m$'ye göre primitif kök olduğundan $\gcd(a, m) = 1$'dir ve mertebesi tanım gereği $\phi(m)$'dir.
  Önceki önermemizden (Üslerin Denkliği ve Mertebe İlişkisi) biliyoruz ki, eğer iki kuvvet birbirine denkse, tabanın mertebesi bu üslerin farkını tam böler. Mertebe $\phi(m)$ olduğuna göre:
  $$\phi(m) \mid (j - k) \implies j \equiv k \pmod{\phi(m)}$$

  *Yeterlilik ($\impliedby$):* Kabul edelim ki $j \equiv k \pmod{\phi(m)}$ olsun.
  Bu durumda bölünebilme tanımı gereği, $j = k + r \cdot \phi(m)$ olacak şekilde bir $r \geq 0$ tam sayısı vardır.
  Eşitliği üslü ifadeye taşırsak:
  $$a^j = a^{k + r \cdot \phi(m)} = a^k \cdot (a^{\phi(m)})^r$$
  Euler-Fermat Teoremi gereği $\gcd(a, m) = 1$ olduğundan $a^{\phi(m)} \equiv 1 \pmod m$'dir. Yerine yazarsak:
  $$a^j \equiv a^k \cdot (1)^r \equiv a^k \pmod m$$
  Böylece birinci kısmın ispatı tamamlanır.

  **2) İkinci Özelliğin İspatı:**
  Birinci ispatta $k = 0$ alırsak:
  $$a^j \equiv a^0 \pmod m \iff j \equiv 0 \pmod{\phi(m)}$$
  $a^0 = 1$ ve $j \equiv 0 \pmod{\phi(m)}$ demek $\phi(m) \mid j$ demektir. Dolayısıyla:
  $$a^j \equiv 1 \pmod m \iff \phi(m) \mid j$$

  **3) Üçüncü Özelliğin İspatı:**
  $a$, modülo $m$'ye göre primitif kök olduğundan $\gcd(a, m) = 1$'dir. Dolayısıyla $a$'nın tüm pozitif kuvvetleri de $m$ ile aralarında asaldır:
  $$\gcd(a, m) = \gcd(a^2, m) = \dots = \gcd(a^{\phi(m)}, m) = 1$$
  Bu durum, $a, a^2, \dots, a^{\phi(m)}$ dizisindeki her bir elemanın $m$ ile aralarında asal olduğunu gösterir. Ayrıca bu kümenin eleman sayısı tam olarak $\phi(m)$ kadardır.

  İspatı tamamlamak için geriye sadece bu $\phi(m)$ tane elemandan hiçbir ikisinin modülo $m$'ye göre birbirine denk olmadığını göstermek kalıyor. Aksini varsayalım ve $1 \leq j, k \leq \phi(m)$ olmak üzere iki kuvvet denk olsun:
  $$a^j \equiv a^k \pmod m$$
  Birinci özellik gereği bu denkliğin sağlanması için:
  $$j \equiv k \pmod{\phi(m)} \iff \phi(m) \mid (j - k)$$
  olması zorunludur. Ancak $j$ ve $k$'nın her ikisi de $1$ ile $\phi(m)$ arasında olduğundan, aralarındaki farkın mutlak değeri $\phi(m)$'den küçüktür ($|j - k| < \phi(m)$).
  $\phi(m)$'den küçük olup da $\phi(m)$'e tam bölünebilen tek sayı $0$'dır.
  Bu nedenle $j - k = 0 \implies j = k$ olmak zorundadır.

  Sonuç olarak, eğer $j \neq k$ ise $a^j \not\equiv a^k \pmod m$'dir. Bu kümedeki tüm elemanlar birbirinden farklıdır ve hepsi $m$ ile aralarında asal olduğu için bir **asal kalanlar sistemi** oluştururlar. $\blacksquare$
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Asal Kalanlar Sisteminin Üretilmesi

  </div>

  Bir önceki örnekte bulduğumuz, $m = 7$ modülünün primitif kökü olan $a = 3$ sayısını kullanalım. Teoremin 3. maddesine göre, 3'ün $\phi(7) = 6$'ya kadar olan kuvvetlerinin tüm asal kalanlar sistemini oluşturması gerekir. 

  Değerleri sırasıyla tekrar yazarsak:
  $$
  \begin{aligned}
  3^1 &\equiv 3 \pmod 7 \\
  3^2 &\equiv 2 \pmod 7 \\
  3^3 &\equiv 6 \pmod 7 \\
  3^4 &\equiv 4 \pmod 7 \\
  3^5 &\equiv 5 \pmod 7 \\
  3^6 &\equiv 1 \pmod 7
  \end{aligned}
  $$
  Elde ettiğimiz sonuçların kümesi $\{3, 2, 6, 4, 5, 1\}$'dir. Gördüğünüz gibi, bir primitif kök olan 3, kendisiyle çarpılmaya devam edildikçe modülo 7'de sıfır hariç tüm sayıları (asal kalanlar sistemini) **tamamen ve eksiksiz bir şekilde üretmiştir.** Hiçbir değer kendini tekrar etmeden tüm kümeyi taramıştır.
</div>


Primitif köklerin bu $\phi(m)$ elemanlık asal kalanlar sistemini tamamen taraması özelliği, bizi modüler aritmetiğin logaritması olarak adlandırabileceğimiz muazzam bir hesaplama aracına götürür: İndeks.

## 7. İndeks Kavramı (Ayrık Logaritma)

Klasik cebirde logaritma nasıl ki bir üssü bulmamızı sağlıyorsa, modüler aritmetikte de "İndeks" aynı görevi üstlenir.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: İndeks (Ayrık Logaritma)

  </div>

  $a$, modülo $m$'ye göre bir primitif kök ve $b$, $\gcd(b, m) = 1$ koşulunu sağlayan herhangi bir tam sayı olsun.
  $$a^j \equiv b \pmod m$$
  koşulunu sağlayan ve $1 \leq j \leq \phi(m)$ aralığında bulunan yegane $j$ doğal sayısına, **$b$'nin $a$ primitif köküne göre (ve modülo $m$'ye göre) indeksi** denir.
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: İndeks (Ayrık Logaritma) Hesaplama

  </div>

  Modülümüz $m = 7$ ve primitif kökümüz $a = 3$ olsun. $b = 4$ sayısının 3 tabanına göre indeksini arıyoruz. $\gcd(4, 7) = 1$'dir.

  Matematiksel olarak şu soruyu soruyoruz: 
  **"3'ün modülo 7'de kaçıncı kuvveti 4'e denktir?"**
  $$3^j \equiv 4 \pmod 7$$

  Yukarıda ürettiğimiz asal kalanlar tablosuna geri dönüp bakarsak:
  $$3^4 \equiv 4 \pmod 7$$
  olduğunu görürüz. 

  Bu durumda, denklemi sağlayan yegane $j$ değeri 4'tür. Notasyon ile ifade edersek:
  $$\operatorname{ind}_3(4) \equiv 4 \pmod{\phi(7)}$$
  Yani 4 sayısının 3 primitif köküne göre modülo 7'deki indeksi (ayrık logaritması) 4'tür. 
</div>

## 8. $n$. Kuvvetten Kongrüansların Çözülebilirliği

Bir $x^n \equiv a \pmod m$ denkleminin çözümünün olup olmadığını deneme yanılma yoluyla bulmak, modül büyüdükçe imkansız hale gelir. Ancak eğer modülümüz bir asal sayı ise, primitif köklerin ve indekslerin özellikleri sayesinde bu çözülebilirliği tek bir hesaplamayla test edebiliriz.

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: $n$. Kuvvetten Kongrüanslar (Euler Kriteri Genellemesi)

  </div>

  $p$ bir asal sayı, $n$ pozitif bir tam sayı ve $\gcd(a, p) = 1$ olsun. Bu durumda $x^n \equiv a \pmod p$ kongrüansı için şu iki durum geçerlidir:

  1. Eğer $a^{ (p-1)/ \gcd(n, p-1)}\not\equiv 1 \pmod p$ ise, kongrüansın **hiçbir çözümü yoktur.**
  2. Eğer $a^{ (p-1)/ \gcd(n, p-1)} \equiv 1 \pmod p$ ise, kongrüansın **çözümü vardır** ve modülo $p$'deki **çözüm sayısı tam olarak $\gcd(n, p-1)$ tanedir.**

  ::: details İspat
  **1. Kısmın İspatı (Çözümsüzlük):**
  Aksini varsayalım ve denklemin bir $u$ çözümü olduğunu kabul edelim. Bu durumda $u^n \equiv a \pmod p$ sağlanır.
  Denkliğin her iki tarafının $\frac{p-1}{\gcd(n, p-1)}$'inci kuvvetini alalım:
  $$a^{\frac{p-1}{\gcd(n, p-1)}} \equiv (u^n)^{\frac{p-1}{\gcd(n, p-1)}} \equiv u^{\frac{n}{\gcd(n, p-1)} \cdot (p-1)} \pmod p$$
  
  $\gcd(a, p) = 1$ olduğundan çözüm olan $u$ da $p$ ile aralarında asaldır ($\gcd(u, p) = 1$). Euler-Fermat (veya Fermat'nın Küçük) Teoremi gereği $u^{p-1} \equiv 1 \pmod p$'dir. İfadeyi düzenlersek:
  $$(u^{p-1})^{\frac{n}{\gcd(n, p-1)}} \equiv 1^{\frac{n}{\gcd(n, p-1)}} \equiv 1 \pmod p$$
  O halde, $a^{\frac{p-1}{\gcd(n, p-1)}} \equiv 1 \pmod p$ olması zorunludur. Eğer ifade $1$'e denk değilse, başlangıçtaki "bir $u$ çözümü vardır" varsayımımız çöker. Yani **çözüm yoktur.**

  **2. Kısmın İspatı (Çözüm Varlığı ve Sayısı):**
  $a^{\frac{p-1}{\gcd(n, p-1)}} \equiv 1 \pmod p$ olduğunu kabul edelim. 
  $g$, modülo $p$'ye göre bir primitif kök ve $a$'nın bu primitif köke göre indeksi $j$ olsun. İndeks tanımı gereği:
  $$g^j \equiv a \pmod p$$
  Bunu kabulümüze yerleştirirsek:
  $$a^{\frac{p-1}{\gcd(n, p-1)}} \equiv (g^j)^{\frac{p-1}{\gcd(n, p-1)}} \equiv g^{\frac{j \cdot (p-1)}{\gcd(n, p-1)}} \equiv 1 \pmod p$$
  
  $g$ bir primitif kök olduğundan mertebesi $\phi(p) = p-1$'dir. Daha önce ispatladığımız "Bir kuvvet $1$'e denkse, tabanın mertebesi o üssü tam böler" kuralı gereği:
  $$(p-1) \mid \frac{j \cdot (p-1)}{\gcd(n, p-1)}$$
  Sadeleştirmeleri yaparsak $\frac{j}{\gcd(n, p-1)}$ ifadesinin bir tam sayı olması gerektiği ortaya çıkar. Bu da demek oluyor ki:
  $$\gcd(n, p-1) \mid j \quad \dots (*)$$

  Öte yandan, aradığımız $x$ çözümü de $p$ ile aralarında asal olacağından, bu çözümü $x \equiv g^y \pmod p$ formatında ($y$ bir bilinmeyen üs olmak üzere) yazabiliriz.
  Denklemimize dönersek:
  $$x^n \equiv a \pmod p \implies (g^y)^n \equiv g^j \pmod p \implies g^{y \cdot n} \equiv g^j \pmod p$$
  Primitif köklerin "Üslerin Denkliği" özelliğinden dolayı, bu tabanları modülo $\phi(p)$'de (yani $p-1$'de) eşitleriz:
  $$y \cdot n \equiv j \pmod{p-1}$$
  
  Bu, bilinmeyeni $y$ olan "Bir Bilinmeyenli Lineer Kongrüans" denklemidir. 
  Linear kongrüanslar teorisinden biliyoruz ki; $A y \equiv B \pmod M$ denkleminin çözümü olması için gerek ve yeter şart $\gcd(A, M) \mid B$ olmasıdır ve çözüm sayısı $\gcd(A, M)$ kadardır.
  Bizim denklemimizde $A = n$, $M = p-1$ ve $B = j$'dir. 
  $(*)$ adımında $\gcd(n, p-1) \mid j$ olduğunu kesin olarak kanıtlamıştık!
  Bu nedenle modülo $p-1$'de $y$ için tam olarak $\gcd(n, p-1)$ tane çözüm vardır. Bu $y_1, y_2, \dots$ çözümleri de doğrudan $x \equiv g^{y_1}, g^{y_2}, \dots \pmod p$ şeklinde ana denklemin çözümlerini üretir. $\blacksquare$
  :::
</div>

::: info 📌 Hatırlatma: Lineer Kongrüans Çözümleri
Birinci dereceden $a \cdot x \equiv b \pmod m$ şeklindeki lineer denklemlerin çözülebilir olması için **$\gcd(a, m) \mid b$** şartı sağlanmalıdır. Eğer bu şart sağlanıyorsa, denklemin modülo $m$'de tam olarak **$\gcd(a, m)$ adet** farklı çözümü vardır.
:::

## ⚙️ Adım Adım Çözüm Algoritması: $x^n \equiv a \pmod p$

Yüksek mertebeden bir modüler denklemi çözmek için, problemi karmaşık kuvvetlerden kurtarıp birinci dereceden (lineer) kongrüansa indirgeyen şu 6 adımlı algoritma uygulanır:

1. **Çözülebilirlik Kontrolü (Euler Kriteri)**
Denklemin üssü olan $n$ ile modülün bir eksiği olan $p-1$ arasındaki en büyük ortak böleni ($d$) hesaplayın: $d = \gcd(n, p-1)$. Ardından $a^{(p-1)/d} \equiv 1 \pmod p$ Euler şartının sağlanıp sağlanmadığını test edin. Eğer sonuç $1$'e denk değilse, denklem çözümsüzdür ve işlem burada biter. Sonuç $1$ ise, modülo $p$'de tam olarak $d$ adet farklı çözüm olduğu garanti edilir.

2. **Primitif Kök ($g$) Seçimi**
Sistemi asıl yönetecek olan tabanı, yani modülo $p$'ye göre mertebesi tam olarak $\phi(p) = p-1$ olan bir $g$ primitif kökünü tespit edin.

3. **İndeks Değerini Bulma (Ayrık Logaritma)**
Denklemin sağ tarafındaki $a$ sayısının, bulduğunuz $g$ primitif köküne göre indeksini ($j$) hesaplayın. Matematiksel olarak, $g^j \equiv a \pmod p$ eşitliğini sağlayan $j$ üssünü bulun. Aynı mantıkla, aradığımız asıl $x$ kökünü de $x \equiv g^y \pmod p$ şeklinde tanımlayın.

4. **Denklemi Lineer Kongrüansa Çevirme**
Orijinal $x^n \equiv a \pmod p$ denklemini primitif kök cinsinden yeniden yazın: $(g^y)^n \equiv g^j \pmod p$. Primitif köklerin özelliklerini kullanarak tabanları atın ve üsleri modülo $p-1$'de eşitleyerek birinci dereceden (lineer) denklemi elde edin:
$$n \cdot y \equiv j \pmod{p-1}$$

5. **Modüler Çözüm Kümesini Üretme**
Elde ettiğiniz lineer denklemi sadeleştirmek için, denklemin sağını, solunu ve modülünü 1. adımda bulduğumuz $d$ değerine bölün:
$$\frac{n}{d} \cdot y \equiv \frac{j}{d} \pmod{\frac{p-1}{d}}$$
Bu sadeleştirilmiş denklemi sağlayan temel $y_0$ çözümünü bulun. Diğer $d$ adet kökü elde etmek için, modülün yeni periyodu olan $(p-1)/d$ değerini ilk köke ardışık olarak ekleyin:
$$y_k = y_0 + k \cdot \frac{p-1}{d} \quad \text{, ($k = 0, 1, 2, \dots, d-1$)}$$ 

6. **Orijinal $x$ Köklerine Dönüş**
5. adımda bulduğunuz tüm $y_k$ üslerini, $x \equiv g^{y_k} \pmod p$ denkleminde yerine koyun. Çıkan sonuçların modülo $p$'deki karşılıkları, orijinal yüksek mertebeli denkleminizin aranan $x$ kökleridir.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $x^{20} \equiv 13 \pmod{17}$ Denkleminin Çözümü

  </div>

  Bu yüksek mertebeli kongrüansın çözümü olup olmadığını ve varsa çözüm kümesini teorem yardımıyla bulalım.
  Verilenler: $p = 17$, $a = 13$, $n = 20$. Açıkça $\gcd(13, 17) = 1$'dir.

  **1. Adım: Çözülebilirlik Testi (Euler Kriteri Genellemesi)**
  $\gcd(n, p-1) = \gcd(20, 16) = 4$'tür. Test kuvvetimizi hesaplayalım:
  $$a^{\frac{p-1}{\gcd(n, p-1)}} = 13^{\frac{16}{4}} = 13^4 \pmod{17}$$
  Modüler indirgeme yapalım:
  $$13 \equiv -4 \pmod{17} \implies 13^2 \equiv 16 \equiv -1 \pmod{17} \implies 13^4 \equiv (-1)^2 \equiv 1 \pmod{17}$$
  Sonuç 1 çıktığı için teoremin 2. koşulu sağlanır: **Çözüm vardır ve çözüm sayısı $\gcd(20, 16) = 4$ tanedir.**

  **2. Adım: Primitif Kök Bulma**
  Çözümleri bulmak için modülo 17'ye göre bir primitif kök ($g$) bulmalıyız. $\phi(17) = 16$'dır. Mertebesi 16 olan sayıyı arıyoruz. 
  $g=3$ değerini deneyelim. Mertebesi $\phi(17)$'yi bölmek zorunda olduğundan sadece 1, 2, 4, 8 ve 16 kuvvetlerini kontrol etmek yeterlidir:
  $$
  \begin{aligned}
  3^1 &= 3 \\
  3^2 &= 9 \\
  3^4 &= 81 \equiv 13 \equiv -4 \pmod{17} \\
  3^8 &= (-4)^2 = 16 \equiv -1 \pmod{17} \\
  3^{16} &= (-1)^2 = 1 \pmod{17}
  \end{aligned}
  $$
  Sonucu 1 yapan en küçük üs 16 olduğu için **$g = 3$, modülo 17'nin bir primitif köküdür.**

  **3. Adım: İndeks Hesaplama ve Lineer Denkleme Geçiş**
  Ana denklemdeki 13'ün, 3 primitif köküne göre indeksini ($j$) arıyoruz:
  $$3^j \equiv 13 \pmod{17}$$
  Yukarıdaki hesaplamalarımızda $3^4 \equiv 13 \pmod{17}$ olduğunu bulmuştuk. Yani indeks **$j = 4$'tür.**
  
  Bilinmeyen $x$'i de $x \equiv 3^y \pmod{17}$ olarak ifade edersek denklem şuna dönüşür:
  $$x^{20} \equiv 13 \implies (3^y)^{20} \equiv 3^4 \implies 3^{20y} \equiv 3^4 \pmod{17}$$
  Primitif kök kuralı gereği üsleri modülo $p-1$'de ($16$'da) eşitleriz:
  $$20y \equiv 4 \pmod{16}$$

  **4. Adım: Çözümleri Elde Etme**
  Lineer kongrüansı sadeleştirelim ($20 \equiv 4 \pmod{16}$):
  $$4y \equiv 4 \pmod{16}$$
  Her iki tarafı $\gcd(4, 16) = 4$'e bölersek, modülü de 4'e bölmemiz gerekir (Modüler sadeleştirme kuralı):
  $$y \equiv 1 \pmod 4 \iff y = 1 + 4t \quad (t \in \mathbb{Z})$$
  Modülo $16$'da kalan y değerlerini (4 adet çözümümüz olacağını biliyorduk) $t$'ye $0, 1, 2, 3$ vererek bulalım:
  $y \in \{1, 5, 9, 13\}$

  Bulduğumuz bu üsleri $x \equiv 3^y \pmod{17}$ formatına yerleştirip asıl çözümleri elde edelim:
  $$
  \begin{aligned}
  x_1 &\equiv 3^1 \equiv \mathbf{3} \pmod{17} \\
  x_2 &\equiv 3^5 = 3^4 \cdot 3 \equiv 13 \cdot 3 = 39 \equiv \mathbf{5} \pmod{17} \\
  x_3 &\equiv 3^9 = 3^8 \cdot 3 \equiv 16 \cdot 3 \equiv -1 \cdot 3 = -3 \equiv \mathbf{14} \pmod{17} \\
  x_4 &\equiv 3^{13} = 3^{12} \cdot 3 \equiv (3^4)^3 \cdot 3 \equiv 13^3 \cdot 3 \equiv (-4)^3 \cdot 3 = -64 \cdot 3 \equiv 4 \cdot 3 = \mathbf{12} \pmod{17}
  \end{aligned}
  $$

  Sonuç olarak, $x^{20} \equiv 13 \pmod{17}$ denkleminin dört farklı çözümü vardır: **$x \in \{3, 5, 14, 12\}$**.
</div>