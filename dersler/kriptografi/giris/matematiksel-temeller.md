# 🧮 Kriptografide Matematiksel Temeller ve Notasyon

Modern kriptografi, güvenliğini karmaşık metin karıştırma oyunlarından değil; **Sayılar Teorisi** ve **Soyut Cebir**'in sarsılmaz kurallarından alır. Şifreleme algoritmalarının (özellikle RSA, Diffie-Hellman ve Eliptik Eğri gibi asimetrik sistemlerin) temelinde yatan en önemli matematiksel yapılar aşağıda özetlenmiştir.

::: info 📝 EBOB ve EKOK Notasyon Anlaşması
Uluslararası literatüre sadık kalmak adına, notlarımızda Türkçe kısaltmalar (EBOB/EKOK) yerine küresel kriptografi kaynaklarında kullanılan standart matematiksel fonksiyonlar tercih edilecektir:
* **$\gcd(a, b)$ (Greatest Common Divisor):** $a$ ve $b$ sayılarının **En Büyük Ortak Bölenini** ifade eder.
* **$\operatorname{lcm}(a, b)$ (Least Common Multiple):** $a$ ve $b$ sayılarının **En Küçük Ortak Katını** ifade eder.

> **Altın Notasyon: Aralarında Asallık**
> Notlarımız boyunca karşılaşacağımız en kritik gösterim şudur:
> $$\gcd(a, b) = 1 \iff a \text{ ve } b \text{ sayıları aralarında asaldır.}$$
> Bu sade gösterim; modüler aritmetikte sadeleştirme yapılabilirliğinin, $\mathbb{Z}_n$ içinde çarpımsal tersin var olmasının ve Euler Phi ($\phi$) fonksiyonunun hesaplanmasının yegane matematiksel şartıdır.
:::

## 1. Modüler Aritmetik ve $\mathbb{Z}_n$ Kümeleri

Kriptografide sonsuz sayılarla işlem yapmak bilgisayarlar için pratik (veya güvenli) değildir. Bu nedenle işlemler, sayılar belirli bir $n$ modülüne (modülüs) ulaştığında başa saran dairesel bir sistem üzerinde, yani **modüler aritmetik** kullanılarak yapılır.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Modüler Denkliği (Kongrüans)

  </div>

  $a$, $b$ ve $n$ tam sayılar ($n > 0$) olmak üzere; eğer $n$ sayısı $(a - b)$ farkını tam bölüyorsa, "$a$ ve $b$ sayıları modülo $n$'de birbirine denktir" denir ve şu şekilde gösterilir:
  $$a \equiv b \pmod n$$

</div>

### ⚙️ Modüler Aritmetiğin Temel Özellikleri

$a, b, c, d$ birer tam sayı ve $n > 0$ bir modül olsun. Cebirsel işlemler, alt alta yazılan denkliklerin taraf tarafa işleme sokulmasıyla çok daha net görülebilir:

* **Toplama ve Çıkarma:** Aynı modüle sahip denklikler alt alta toplanabilir veya çıkarılabilir. Modül aynen korunur:
  $$\left.
  \begin{aligned}
  a &\equiv b \pmod n \\
  c &\equiv d \pmod n
  \end{aligned}
  \right\} \implies a \pm c \equiv b \pm d \pmod n$$

* **Aynı Sayıyı Ekleme ve Çıkarma (Her İki Tarafa):** Klasik cebirde olduğu gibi, modüler aritmetikte de bir denklemin her iki tarafına aynı sayıyı ekleyebilir veya çıkarabilirsiniz. Modül yine sabit kalır:
  $$a \equiv b \pmod n \iff a \pm c \equiv b \pm c \pmod n$$

* **Çarpma (Taraf Tarafa):** Aynı modüle sahip iki farklı denkliğin sol tarafları kendi arasında, sağ tarafları ise kendi arasında çarpılabilir. Modül yine sabit kalır:
  $$\left.
  \begin{aligned}
  a &\equiv b \pmod n \\
  c &\equiv d \pmod n
  \end{aligned}
  \right\} \implies a \cdot c \equiv b \cdot d \pmod n$$

* **Üs Alma:** Taraf tarafa çarpma kuralının doğal bir sonucu olarak ($c=a$ ve $d=b$ alınarak $k$ defa çarpıldığında), bir denkliğin her iki tarafının aynı $k \geq 1$ pozitif tam sayı kuvveti alınabilir:
  $$a \equiv b \pmod n \implies a^k \equiv b^k \pmod n$$

* **Denkliği Genişletme (Modülü Çarpmak):** Tüm denkliği bir $k > 0$ tam sayısıyla çarparak genişletiyorsanız, çözüm kümesinin bozulmaması için **modülü de aynı $k$ sayısıyla çarpmak zorundasınız.** Sadece tarafları çarpıp modülü sabit bırakmak denklemi tamamen değiştirir ve yanlış sonuçlara götürür:
  $$a \equiv b \pmod n \iff a \cdot k \equiv b \cdot k \pmod{n \cdot k}$$

::: warning ⚠️ Tehlikeli Sular: Bölme ve Sadeleştirme Kuralı!
Modüler aritmetikte doğrudan "bölme" işlemi yoktur ve klasik cebirdeki gibi her iki tarafı aynı sayıya bölerek sadeleştirme yapmak çok sık yapılan ölümcül bir hatadır. 

Çarpım durumundaki bir $c$ tam sayısını her iki taraftan sadeleştirmek istiyorsak, modülün de $c$ ile olan en büyük ortak bölenine ($\gcd$) bölünmesi zorunludur:

$$a \cdot c \equiv b \cdot c \pmod n \iff a \equiv b \pmod{\frac{n}{\gcd(c,n)}}$$

**Özel ve Kriptografide En Sık Kullanılan Durum:** Eğer sadeleştireceğimiz $c$ sayısı ile modülümüz $n$ **aralarında asal** ise ($\gcd(c, n) = 1$), o halde $\frac{n}{1} = n$ olacağından, modül değişmeden doğrudan sadeleştirme yapılabilir:
$$a \cdot c \equiv b \cdot c \pmod n \implies a \equiv b \pmod n$$
:::

::: danger 🚫 Dikkat: Üslerde Sadeleştirme Yapılamaz!
Tabanlardaki sayılar aralarında asallık kuralına göre sadeleşebilse de, **üsler doğrudan sadeleştirilemez**. Yani:
$$x^a \equiv x^b \pmod n \centernot\implies a \equiv b \pmod n$$
Modüler aritmetikte üsleri birbirine eşitlemek, indirgemek veya sadeleştirmek için modül $n$'ye göre değil; her zaman Euler-Fermat Teoremi gereği **$\phi(n)$'e göre** işlem yapılması matematiksel olarak zorunludur.
:::

### $\mathbb{Z}_n$ Kümeleri ve Çarpımsal Ters

İşte tüm bu modüler işlemlerin yapıldığı kalanlar kümesine $\mathbb{Z}_n$ denir.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: $\mathbb{Z}_n$ Kümesi

  </div>
  
  $n$ pozitif bir tam sayı olmak üzere, modülo $n$'de kalanların oluşturduğu tam sayılar kümesi:
  $$\mathbb{Z}_n = \{0, 1, 2, \dots, n-1\}$$
  şeklinde gösterilir.

</div>

Modüler aritmetikte doğrudan "bölme" işlemi olmadığı için, denklemleri çözmek adına **Çarpımsal Ters** (Multiplicative Inverse) kavramı devreye girer. Bir sayıya bölmek yerine, o sayının çarpımsal tersi ile çarparız.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Çarpımsal Ters (Multiplicative Inverse)

  </div>
  
  $a \in \mathbb{Z}_n$ olmak üzere, eğer:
  $$a \cdot x \equiv 1 \pmod n$$
  denkliğini sağlayan bir $x$ tam sayısı varsa, bu $x$ sayısına $a$'nın modülo $n$'deki çarpımsal tersi denir ve $a^{-1} \pmod n$ şeklinde gösterilir.

</div>

Kriptografik açıdan bu terslerin bulunabilmesi çok kritiktir. $\mathbb{Z}_n$ içinde bir $a$ elemanının çarpımsal tersinin olabilmesi için **gerek ve yeter şart $\gcd(a, n) = 1$ (aralarında asal) olmasıdır**. (Bu ters elemanlar pratikte Genişletilmiş Öklid Algoritması kullanılarak çok hızlı bir şekilde hesaplanır).

::: tip 💡 Neden Asal Sayılar?
Eğer $n$ sayısı bir $p$ **asal sayısı** olarak seçilirse ($\mathbb{Z}_p$), sıfır hariç *her elemanın* $p$ ile aralarında asal olacağı garanti edilir. Yani sıfır hariç her elemanın bir çarpımsal tersi olur! Bu durum $\mathbb{Z}_p$'yi sadece bir halka olmaktan çıkarıp kusursuz bir **Cisim (Field)** yapar. Bu yapı, AES (Gelişmiş Şifreleme Standardı) gibi modern algoritmaların bel kemiğidir.
:::

## 2. Euler'in Phi ($\phi$) Fonksiyonu

Kriptografinin, özellikle de RSA algoritmasının en büyük kahramanlarından biri **Euler'in Totient (Phi) Fonksiyonudur**.

<div class="math-block definition">
  <div class="math-block-title">
  
  Tanım: Euler Phi Fonksiyonu $\phi(n)$

  </div>

  Bir $n$ pozitif tam sayısı için, $1 \leq a \leq n$ aralığında bulunan ve $n$ ile **aralarında asal** olan tamsayıların sayısını veren fonksiyondur.

</div>

### $\phi(n)$ Fonksiyonunun Özellikleri

Hesaplama yaparken bu fonksiyonun sahip olduğu şu çarpımsal özellikler hayat kurtarır:

1. **Asal Sayı Kuralı:** Eğer $p$ bir asal sayı ise, kendisinden küçük tüm pozitif tam sayılarla aralarında asal olacağından:
   $$\phi(p) = p - 1$$
2. **Asal Kuvvet Kuralı:** Eğer $p$ asal ve $k \geq 1$ tam sayı ise:
   $$\phi(p^k) = p^k - p^{k-1}$$
3. **Çarpımsallık Kuralı:** Eğer $m$ ve $n$ aralarında asal ise ($\gcd(m,n) = 1$):
   $$\phi(m \cdot n) = \phi(m) \cdot \phi(n)$$
4. **Genel Formül:** Herhangi bir $n$ sayısının asal çarpanlarına ayrılmış hali $n = p_1^{k_1} p_2^{k_2} \dots p_r^{k_r}$ ise:
   $$\phi(n) = n \left(1 - \frac{1}{p_1}\right) \left(1 - \frac{1}{p_2}\right) \dots \left(1 - \frac{1}{p_r}\right)$$

## 3. Euler ve Fermat Teoremleri

Şifreleme sırasında veriyi çok büyük üslere çıkardığımızda, modüler aritmetikte bu üsleri küçültmek ve işlemi bilgisayarlar için çözülebilir kılmak adına bu iki teorem kullanılır.

<div class="math-block theorem">
  <div class="math-block-title">
  
  Fermat'nın Küçük Teoremi
  
  </div>

  Eğer $p$ bir asal sayı ve $a$, $p$ ile bölünemeyen bir tam sayı ise ($\gcd(a, p) = 1$):
  $$a^{p-1} \equiv 1 \pmod p$$

</div>

Fermat'nın Küçük Teoremi sadece asallar için geçerlidir. İsveçli matematikçi Leonhard Euler, bu teoremi **asal olmayan sayılar** ($n$) için genişletmiş ve literatüre RSA algoritmasının anahtar üretim iskeletini hediye etmiştir:

<div class="math-block theorem">
  <div class="math-block-title">
  
  Euler-Fermat Teoremi
  
  </div>

  Eğer $a$ ve $n$ **aralarında asal** iki tam sayı ise ($\gcd(a, n) = 1$):
  $$a^{\phi(n)} \equiv 1 \pmod n$$

</div>

::: warning ⚠️ Şifre Kırmanın Zorluğu
RSA sisteminde $n = p \cdot q$ şeklinde devasa iki asal sayının çarpımı halka açık olarak verilir. Sistemin güvenli olmasının sebebi, $n$ bilinmesine rağmen **$p$ ve $q$ çarpanları bilinmeden $\phi(n)$ değerinin hesaplanamamasıdır**. Eğer bir gün çok hızlı çalışan bir asal çarpanlara ayırma algoritması (örneğin kuantum bilgisayarlarda Shor Algoritması) bulunursa, tüm bu teoremlerin pratik zorluğu çöker ve RSA kırılır!
:::

## 4. Wilson Teoremi

Asal sayıları tespit etmek (Primality Test) veya teorik analizler yapmak için kullanılan çarpımsal bir başka güçlü teorem şudur:

<div class="math-block theorem">
  <div class="math-block-title">
  
  Wilson Teoremi
  
  </div>

  Bir $p \geq 2$ tam sayısının **asal sayı** olması için gerek ve yeter şart:
  $$(p-1)! \equiv -1 \pmod p$$

</div>

Faktöriyel hesaplaması sayılar büyüdükçe logaritmik olmayan (çok hızlı) bir şekilde büyüdüğü için, pratikte devasa kriptografik asal sayıların testinde **Wilson Teoremi** kullanılamayacak kadar yavaştır. Bunun yerine genellikle *Miller-Rabin* gibi olasılıksal (probabilistic) asallık testleri tercih edilir.