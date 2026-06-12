# Kuadratik Resiprosite (Karesel Karşılıklılık) Teoremi

Şu ana kadar Legendre Sembolünün özelliklerini, Euler Kriterini ve Gauss Lemmasını kullanarak sayıların karesel karakterlerini belirledik. Ancak asal sayılar büyüdükçe (örneğin $\left(\frac{7}{61}\right)$ gibi ifadelerde) üs alma işlemleri veya Gauss saymaları bile yetersiz kalır.

Tarihin en büyük matematikçilerinden Gauss'un "Altın Teorem" adını verdiği **Kuadratik Resiprosite Teoremi**, iki farklı tek asal sayının birbirine göre karesel durumlarının birbiriyle doğrudan bağlantılı olduğunu kanıtlar. Bu teorem, büyük modüller altındaki denklemlerin çözülebilirliğini saniyeler içinde tespit etmemizi sağlar.

## 1. Kuadratik Resiprosite Teoremi ve Kafes (Lattice) İspatı

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Kuadratik Resiprosite (Karşılıklılık) Teoremi

  </div>

  $p$ ve $q$ birbirinden farklı iki tek asal sayı olsun. Bu durumda:
  $$\left( \frac{p}{q} \right) \cdot \left( \frac{q}{p} \right) = (-1)^{\frac{p-1}{2} \cdot \frac{q-1}{2}}$$
  eşitliği sağlanır.

  ::: details İspat
  Bu ispat, kartezyen koordinat sistemindeki tam sayı koordinatlı noktaların (kafes noktalarının) sayılması mantığına dayanır.

  İlk olarak, birinci bölgede yer alan ve sınırları belirli olan bir $K$ dikdörtgensel tam sayı kümesi tanımlayalım:
  $$K = \left\{ (x, y) : 1 \leq x \leq \frac{p-1}{2}, \quad 1 \leq y \leq \frac{q-1}{2}, \quad x, y \in \mathbb{Z} \right\}$$
  Bu $K$ kümesinin toplam eleman sayısı, x ve y'nin alabileceği değerler çarpımı kadardır:
  $$s(K) = \frac{p-1}{2} \cdot \frac{q-1}{2}$$

  Şimdi bu $K$ kümesini, $y = \frac{q}{p}x$ doğrusu (veya $qx = py$ denklemi) yardımıyla iki alt kümeye ayıralım:
  * Doğrunun üstünde kalanlar: $K_1 = \{ (x, y) \in K : qx > py \}$
  * Doğrunun altında kalanlar: $K_2 = \{ (x, y) \in K : qx < py \}$

  **Kritik Detay:** $K$ kümesi içindeki hiçbir nokta tam olarak $qx = py$ doğrusunun üzerinde olamaz. Çünkü $\gcd(p, q) = 1$ olduğu için $qx = py$ eşitliğinin sağlanması için $p \mid x$ ve $q \mid y$ olmalıdır. Halbuki kümemizin sınırlarında $x \leq \frac{p-1}{2} < p$ ve $y \leq \frac{q-1}{2} < q$'dur.
  Dolayısıyla $K_1 \cap K_2 = \emptyset$ (kümeler ayrıktır) ve $K_1 \cup K_2 = K$'dır. Eleman sayıları toplamı şu şekildedir:
  $$s(K_1) + s(K_2) = s(K) = \frac{p-1}{2} \cdot \frac{q-1}{2}$$

  Şimdi $K_1$ kümesinin eleman sayısını satır satır bulalım:
  $$K_1 = \left\{ (x, y) : 1 \leq x \leq \frac{p-1}{2}, \quad 1 \leq y < \frac{qx}{p}, \quad x,y \in \mathbb{Z} \right\}$$
  Bu kümeyi, $x$'in aldığı her bir tam sayı değeri için ayrı ayrı birleşimler şeklinde yazabiliriz:
  $$K_1 = \bigcup_{x=1}^{(p-1)/2} \left\{ (x, y) : 1 \leq y < \frac{qx}{p}, \quad y \in \mathbb{Z} \right\}$$
  Bu birleşime giren kümeler ikişer ikişer ayrıktır. Belli bir $x$ değeri için $1 \leq y < \frac{qx}{p}$ şartını sağlayan y tam sayılarının adedi, $\frac{qx}{p}$ kesrinin tam değerine (bölümüne) yani $\lfloor \frac{qx}{p} \rfloor$ sayısına eşittir. O halde:
  $$s(K_1) = \sum_{x=1}^{(p-1)/2} \lfloor \frac{qx}{p} \rfloor$$

  Tamamen simetrik bir düşünceyle $K_2$ kümesinin eleman sayısı da $y$ ekseni üzerinden toplanarak bulunur:
  $$s(K_2) = \sum_{y=1}^{(q-1)/2} \lfloor \frac{py}{q} \rfloor$$

  Bulduğumuz bu $s(K_1)$ ve $s(K_2)$ değerlerini toplam denkleminde yerine yazalım:
  $$\sum_{x=1}^{(p-1)/2} \lfloor \frac{qx}{p} \rfloor + \sum_{y=1}^{(q-1)/2} \lfloor \frac{py}{q} \rfloor = \frac{p-1}{2} \cdot \frac{q-1}{2}$$
  
  Eşitliğin her iki tarafını $(-1)$'in üssü olarak yazalım (üssün toplamı, tabanların çarpımıdır):
  $$(-1)^{\sum \lfloor \frac{qx}{p} \rfloor} \cdot (-1)^{\sum \lfloor \frac{py}{q} \rfloor} = (-1)^{\frac{p-1}{2} \cdot \frac{q-1}{2}}$$

  Bir önceki bölümde Gauss Lemması üzerinden kanıtladığımız genel formül (Teorem 3) gereği biliyoruz ki; 
  $\left( \frac{q}{p} \right) = (-1)^{\sum \lfloor \frac{qx}{p} \rfloor}$ ve simetrik olarak $\left( \frac{p}{q} \right) = (-1)^{\sum \lfloor \frac{py}{q} \rfloor}$'dir. 
  
  Bu değerleri yerine yazdığımızda ispat kusursuz bir şekilde tamamlanır:
  $$\left( \frac{q}{p} \right) \cdot \left( \frac{p}{q} \right) = (-1)^{\frac{p-1}{2} \cdot \frac{q-1}{2}} \quad \blacksquare$$
  :::
</div>

::: info 💡 Teoremin Pratik Anlamı (Ters Çevirme Kuralı)
Kuadratik Resiprosite Teoremi aslında bize şunu söyler: $\left( \frac{p}{q} \right)$ sembolünü hesaplamak zorsa, bunu ters çevirip $\left( \frac{q}{p} \right)$ sembolünü hesaplayabilirsiniz.
* Eğer p ve q asallarından **en az biri** $4k+1$ formundaysa (yani mod 4'te 1 kalanını veriyorsa), sembol hiçbir işaret değiştirmeden aynen ters çevrilir: $\left( \frac{p}{q} \right) = \left( \frac{q}{p} \right)$
* Eğer p ve q asallarının **her ikisi de** $4k+3$ formundaysa (mod 4'te 3 kalanı), sembol ters çevrildiğinde eksi işareti alır: $\left( \frac{p}{q} \right) = -\left( \frac{q}{p} \right)$
:::

::: info 🧠 Mantık Köprüsü: Çarpımdan Asıl Değere Nasıl Geçiyoruz?
Kuadratik Resiprosite teoreminde hesapladığımız şey aslında iki sembolün **çarpımıdır**. Peki bu çarpım sonucundan yola çıkarak asıl aradığımız sembolün değerini nasıl tek başına çekiyoruz?

Legendre sembolleri yalnızca $1$ veya $-1$ değerini alabilir. Dolayısıyla elimizde sadece iki senaryo vardır:

**1. Senaryo (Çarpım 1 ise):** Eğer $\left( \frac{p}{q} \right) \cdot \left( \frac{q}{p} \right) = 1$ bulduysak, bu iki sayı ya $(1 \cdot 1)$ ya da $(-1 \cdot -1)$ olmak zorundadır. Her iki durumda da semboller **birbirine eşittir**. 
O halde aradığımız sembolü doğrudan tersine eşitleyebiliriz:
$$\left( \frac{p}{q} \right) = \left( \frac{q}{p} \right)$$

**2. Senaryo (Çarpım -1 ise):**
Eğer $\left( \frac{p}{q} \right) \cdot \left( \frac{q}{p} \right) = -1$ bulduysak, bu sayılardan biri $1$ iken diğeri mecburen $-1$ olmak zorundadır. Yani semboller birbirinin **zıt işaretlisidir**.
O halde aradığımız sembol, tersinin eksi ile çarpılmış haline eşittir:
$$\left( \frac{p}{q} \right) = -\left( \frac{q}{p} \right)$$

İşte bu basit işaret mantığı sayesinde, büyük olan üstteki sayıyı (örneğin 61'i) aşağıya atıp, modüler aritmetik kullanarak küçültme (indirgeme) işlemine devam edebiliriz!
:::

## 2. Kuadratik Resiprosite Uygulamaları

Resiprosite Teoreminin gücü, çok büyük sayılar içeren kongrüansları, basit modüler indirgemeler ve sembolü sürekli ters çevirerek ("takla attırarak") çok küçük sayılara düşürmesinde yatar.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $x^2 \equiv -42 \pmod{61}$ kongrüansının çözülebilir olup olmadığını araştırınız.

  </div>

::: details 💡 Çözümü Göster / Gizle
  **Çözüm:** Problemi çözmek için Legendre Sembolü olan $\left( \frac{-42}{61} \right)$ değerini hesaplamalıyız. 61 bir asal sayıdır. 
  İlk adım olarak $-42$ sayısını asal çarpanlarına ayıralım ve Legendre'nin çarpımsallık kuralını uygulayalım:
  $$\left( \frac{-42}{61} \right) = \left( \frac{-1 \cdot 2 \cdot 3 \cdot 7}{61} \right) = \left( \frac{-1}{61} \right) \cdot \left( \frac{2}{61} \right) \cdot \left( \frac{3}{61} \right) \cdot \left( \frac{7}{61} \right)$$

  Şimdi bu 4 parçayı sırasıyla hesaplayalım:

  **1. Parça:** $\left( \frac{-1}{61} \right)$ hesabı (Özel Değer Kuralı)
  $$\left( \frac{-1}{61} \right) = (-1)^{\frac{61-1}{2}} = (-1)^{30} = 1$$

  **2. Parça:** $\left( \frac{2}{61} \right)$ hesabı (2'nin Karesel Karakteri)
  $$\left( \frac{2}{61} \right) = (-1)^{\frac{61^2-1}{8}} = -1$$

  **3. Parça:** $\left( \frac{3}{61} \right)$ hesabı (Kuadratik Resiprosite)
  Her iki sayı da tek asaldır. Formülü uygularsak:
  $$\left( \frac{3}{61} \right) \cdot \left( \frac{61}{3} \right) = (-1)^{\frac{3-1}{2} \cdot \frac{61-1}{2}} = (-1)^{1 \cdot 30} = (-1)^{30} = 1$$
  Çarpımları 1 olduğu için semboller birbirine eşittir: $\left( \frac{3}{61} \right) = \left( \frac{61}{3} \right)$
  Şimdi $61$'i modülo $3$'te indirgeyelim. $61 \equiv 1 \pmod 3$'tür.
  $$\left( \frac{61}{3} \right) = \left( \frac{1}{3} \right) = 1$$
  Dolayısıyla $\left( \frac{3}{61} \right) = 1$ bulunur.

  **4. Parça:** $\left( \frac{7}{61} \right)$ hesabı (Kuadratik Resiprosite)
  $$\left( \frac{7}{61} \right) \cdot \left( \frac{61}{7} \right) = (-1)^{\frac{7-1}{2} \cdot \frac{61-1}{2}} = (-1)^{3 \cdot 30} = (-1)^{90} = 1$$
  Yine çarpımları 1 çıktığından sembol işaretsiz çevrilir: $\left( \frac{7}{61} \right) = \left( \frac{61}{7} \right)$
  Modülo 7'ye göre indirgeyelim: $61 \equiv 5 \pmod 7$'dir. O halde $\left( \frac{61}{7} \right) = \left( \frac{5}{7} \right)$ olur.
  
  Karşımıza yine iki asal sayı çıktı ($5$ ve $7$). Teoremi bir kez daha peş peşe uygulayıp "takla" attıralım:
  $$\left( \frac{5}{7} \right) \cdot \left( \frac{7}{5} \right) = (-1)^{\frac{5-1}{2} \cdot \frac{7-1}{2}} = (-1)^{2 \cdot 3} = 1 \implies \left( \frac{5}{7} \right) = \left( \frac{7}{5} \right)$$
  Şimdi $7$'yi modülo $5$'e göre indirgeyelim: $7 \equiv 2 \pmod 5$.
  $$\left( \frac{7}{5} \right) = \left( \frac{2}{5} \right)$$
  Burada karşımıza 2'nin karesel karakteri çıktı. Formülden:
  $$\left( \frac{2}{5} \right) = (-1)^{\frac{5^2-1}{8}} = (-1)^3 = -1$$
  Zincirleme olarak geriye dönersek: $\left( \frac{7}{61} \right) = \left( \frac{61}{7} \right) = \left( \frac{5}{7} \right) = \left( \frac{7}{5} \right) = \left( \frac{2}{5} \right) = -1$ buluruz.

  **Sonuçların Birleştirilmesi:**
  Bulduğumuz 4 ayrı değeri başlangıçtaki denklemde yerlerine koyalım:
  $$\left( \frac{-42}{61} \right) = 1 \cdot (-1) \cdot 1 \cdot (-1) = 1$$

  Genel sonuç $1$ çıktığı için, $-42$ sayısı modülo $61$'e göre bir **Kuadratik Rezidü (KR)**'dür. 
  Yani $x^2 \equiv -42 \pmod{61}$ kongrüansı **kesin olarak çözülebilirdir.**
:::

</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Hangi $p$ tek asal sayıları için 3, modülo $p$'ye göre bir Kuadratik Rezidü'dür? (Yani hangi $p$ tek asal sayıları için $x^2 \equiv 3 \pmod p$ kongrüansı çözülebilirdir?)

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  Soru bizden $\left( \frac{3}{p} \right) = 1$ koşulunu sağlayan tüm $p$ tek asal sayılarını bulmamızı istiyor. Kuadratik Resiprosite Teoreminden faydalanalım:
  $$\left( \frac{3}{p} \right) \cdot \left( \frac{p}{3} \right) = (-1)^{\frac{3-1}{2} \cdot \frac{p-1}{2}} = (-1)^{\frac{p-1}{2}}$$
  Denklemi düzenlersek:
  $$\left( \frac{3}{p} \right) = \left( \frac{p}{3} \right) \cdot (-1)^{\frac{p-1}{2}}$$
  
  Bizden sonucun $1$ çıkması isteniyor. İki sayının çarpımının $1$ olması için ya ikisi de $1$ olmalı ya da ikisi de $-1$ olmalıdır. O halde iki ayrı durum (sistem) ortaya çıkar:

  **Durum 1:** $\left( \frac{p}{3} \right) = 1 \quad \text{ve} \quad (-1)^{\frac{p-1}{2}} = 1$
  * $(-1)^{\frac{p-1}{2}} = 1 \implies \frac{p-1}{2}$ çift sayı olmalıdır $\implies p \equiv 1 \pmod 4$
  * $\left( \frac{p}{3} \right) = 1 \implies p$, mod 3'e göre bir KR'dir $\implies x^2 \equiv p \pmod 3$ çözülebilirdir. $1^2 \equiv 1$ ve $2^2 \equiv 1$ olduğundan $\implies p \equiv 1 \pmod 3$

  **Durum 2:** $\left( \frac{p}{3} \right) = -1 \quad \text{ve} \quad (-1)^{\frac{p-1}{2}} = -1$
  * $(-1)^{\frac{p-1}{2}} = -1 \implies \frac{p-1}{2}$ tek sayı olmalıdır $\implies p \equiv -1 \equiv 3 \pmod 4$
  * $\left( \frac{p}{3} \right) = -1 \implies p$, mod 3'e göre bir KNR'dir $\implies x^2 \equiv p \pmod 3$ çözülemez. $\implies p \equiv 2 \pmod 3$

  Sonuç olarak aradığımız $p$ asalları şu iki kongrüans sisteminden birini sağlamalıdır:
  1) $p \equiv 1 \pmod 3$ ve $p \equiv 1 \pmod 4$
  2) $p \equiv 2 \pmod 3$ ve $p \equiv 3 \pmod 4$

  Şimdi **Çinlilerin Kalan Teoreminden (CRT)** yararlanarak bu iki sistemi ayrı ayrı çözelim:

  **1. Sistemin Çözümü:**
  $p \equiv 1 \pmod 3 \implies p = 1 + 3y \quad (y \in \mathbb{Z})$
  Bunu ikinci denklemde yerine koyalım:
  $$1 + 3y \equiv 1 \pmod 4 \implies 3y \equiv 0 \pmod 4 \implies y \equiv 0 \pmod 4 \implies y = 4z \quad (z \in \mathbb{Z})$$
  Başa dönersek: $p = 1 + 3(4z) = 1 + 12z \implies \mathbf{p \equiv 1 \pmod{12}}$

  **2. Sistemin Çözümü:**
  $p \equiv 2 \pmod 3 \implies p = 2 + 3y \quad (y \in \mathbb{Z})$
  Bunu ikinci denklemde yerine koyalım:
  $$2 + 3y \equiv 3 \pmod 4 \implies 3y \equiv 1 \pmod 4$$
  Modüler bölme için 1'e 8 ekleyelim (9, 3'e tam bölünür):
  $$3y \equiv 9 \pmod 4 \implies y \equiv 3 \pmod 4 \implies y = 3 + 4z \quad (z \in \mathbb{Z})$$
  Başa dönersek: $p = 2 + 3(3 + 4z) = 2 + 9 + 12z = 11 + 12z \implies \mathbf{p \equiv 11 \pmod{12}}$

  **Genel Sonuç:**
  $\left( \frac{3}{p} \right) = 1$ olması için, $p$ tek asal sayısının modülo 12'ye göre **1** veya **11** kalanını vermesi gerekir. 
  :::
</div>