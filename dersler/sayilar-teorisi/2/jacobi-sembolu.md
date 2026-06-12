# Jacobi Sembolü

Legendre Sembolü yalnızca tek asal modüller için tanımlıydı. Ancak pratikte ve ileri düzey kriptografik algoritmalarda, asal çarpanlarına ayrılmamış büyük kompozit (asal olmayan) sayılarla çalışmamız gerekir. Carl Gustav Jacob Jacobi, Legendre sembolünün özelliklerini kullanarak bu kavramı tüm tek tam sayılara genelleştirmiştir.

## 1. Jacobi Sembolünün Tanımı

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Jacobi Sembolü

  </div>

  $P$ bir tam sayı ve $Q > 1$ bir **tek tam sayı** olsun. $\gcd(P, Q) = 1$ kabul edelim.
  
  Eğer $Q$ sayısının asal çarpanlarına ayrılmış hali $Q = q_1 \cdot q_2 \dots q_s$ ($q_i$'ler tek asal sayılar) ise, $P$'nin $Q$'ya göre **Jacobi Sembolü** şu şekilde tanımlanır:

  $$
  \left( \frac{P}{Q} \right) = \left( \frac{P}{q_1} \right) \cdot \left( \frac{P}{q_2} \right) \dots \left( \frac{P}{q_s} \right)
  $$

  *(Not: Buradaki $q_i$ asal sayılarının birbirinden farklı olması gerekmez. Aynı asal çarpandan birden fazla varsa, çarpımda o kadar kez tekrar edilir.)*
</div>

Bu tanımdan yola çıkarak Jacobi sembolünün doğası hakkında üç temel çıkarım (not) elde ederiz:

1. Eğer tanımdaki $Q$ sayısı zaten bir tek asal sayı ise, Jacobi Sembolü doğrudan **Legendre Sembolü ile çakışır** (ikisi aynı şey olur).
2. Sağ taraftaki Legendre sembollerinin her biri yalnızca $\pm 1$ değerlerini alabildiğinden, **Jacobi Sembolünün de alabileceği değerler yalnızca $1$ veya $-1$'dir.**

::: warning ⚠️ DİKKAT: Jacobi Sembolünün Tuzağı
Jacobi sembolü, Legendre sembolünün görünümünü taklit etse de "çözülebilirlik" konusunda aynı garantiyi vermez!

* Eğer $\left( \frac{P}{Q} \right) = -1$ ise, $x^2 \equiv P \pmod Q$ kongrüansının **çözümü kesinlikle yoktur**. ($P$, modülo $Q$'ya göre bir KNR'dir.)
* Ancak $\left( \frac{P}{Q} \right) = 1$ olması, denklemin **çözülebilir olduğunu GARANTİ ETMEZ.** **Örnek:** $\left( \frac{2}{9} \right)$ Jacobi sembolünü inceleyelim. $9 = 3 \cdot 3$ olduğundan:
$$\left( \frac{2}{9} \right) = \left( \frac{2}{3} \right) \cdot \left( \frac{2}{3} \right) = (-1) \cdot (-1) = 1$$
Sembolün değeri $1$ çıkmasına rağmen, $x^2 \equiv 2 \pmod 9$ kongrüansının hiçbir tam sayı çözümü yoktur! Çözümün olması için sağ taraftaki *tüm* Legendre sembollerinin ayrı ayrı $1$ olması gerekir.
:::

## 2. Jacobi Sembolünün Temel Özellikleri

Jacobi sembolü, Legendre sembolünün sahip olduğu tüm o muazzam çarpımsal özellikleri aynen korur.

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Jacobi Sembolünün Cebirsel Özellikleri

  </div>

  $Q > 1$ ve $Q' > 1$ tek tam sayılar; $P$ ve $P'$ tam sayılar olsun. $\gcd(PP', QQ') = 1$ koşulu altında aşağıdaki özellikler geçerlidir:

  1. $\left( \frac{P}{Q} \right) \cdot \left( \frac{P}{Q'} \right) = \left( \frac{P}{Q \cdot Q'} \right)$
  2. $\left( \frac{P}{Q} \right) \cdot \left( \frac{P'}{Q} \right) = \left( \frac{P \cdot P'}{Q} \right)$
  3. $\left( \frac{P^2}{Q} \right) = \left( \frac{P}{Q^2} \right) = 1$
  4. $\left( \frac{P' \cdot P^2}{Q' \cdot Q^2} \right) = \left( \frac{P'}{Q'} \right)$
  5. Eğer $P \equiv P' \pmod Q$ ise, $\left( \frac{P}{Q} \right) = \left( \frac{P'}{Q} \right)$

  ::: details İspat
  $Q$ ve $Q'$ sayılarını tek asal çarpanlarına ayıralım: 
  $Q = q_1 \dots q_s$ ve $Q' = q'_1 \dots q'_t$ olsun.

  **1) Birinci Özelliğin İspatı:**
  Sol tarafı Jacobi tanımına göre açalım:
  $$\left( \frac{P}{Q} \right) \cdot \left( \frac{P}{Q'} \right) = \left( \frac{P}{q_1} \dots \frac{P}{q_s} \right) \cdot \left( \frac{P}{q'_1} \dots \frac{P}{q'_t} \right)$$
  Bu çarpım, $Q \cdot Q'$ sayısının tüm asal çarpanlarının Legendre sembollerinin yan yana çarpımıdır. Dolayısıyla sağ tarafa, yani $\left( \frac{P}{Q \cdot Q'} \right)$ ifadesine eşittir.

  **2) İkinci Özelliğin İspatı:**
  $$\left( \frac{P}{Q} \right) \cdot \left( \frac{P'}{Q} \right) = \left( \frac{P}{q_1} \dots \frac{P}{q_s} \right) \cdot \left( \frac{P'}{q_1} \dots \frac{P'}{q_s} \right)$$
  Terimleri aynı tabanlara (aynı $q_i$'lere) göre gruplayalım:
  $$= \left( \frac{P}{q_1} \cdot \frac{P'}{q_1} \right) \dots \left( \frac{P}{q_s} \cdot \frac{P'}{q_s} \right)$$
  Legendre sembolünün çarpımsallık özelliğinden (Teorem 2):
  $$= \left( \frac{P \cdot P'}{q_1} \right) \dots \left( \frac{P \cdot P'}{q_s} \right) = \left( \frac{P \cdot P'}{Q} \right)$$

  **3) Üçüncü Özelliğin İspatı:**
  İkinci özelliği kullanarak: $\left( \frac{P^2}{Q} \right) = \left( \frac{P}{Q} \right) \cdot \left( \frac{P}{Q} \right) = (\pm 1)^2 = 1$
  Birinci özelliği kullanarak: $\left( \frac{P}{Q^2} \right) = \left( \frac{P}{Q} \right) \cdot \left( \frac{P}{Q} \right) = (\pm 1)^2 = 1$

  **4) Dördüncü Özelliğin İspatı:**
  İlk 3 özelliğin doğrudan birleştirilmesidir:
  $$\left( \frac{P' \cdot P^2}{Q' \cdot Q^2} \right) = \left( \frac{P'}{Q'} \right) \cdot \underbrace{\left( \frac{P'}{Q^2} \right)}_{1} \cdot \underbrace{\left( \frac{P^2}{Q'} \right)}_{1} \cdot \underbrace{\left( \frac{P^2}{Q^2} \right)}_{1} = \left( \frac{P'}{Q'} \right)$$

  **5) Beşinci Özelliğin İspatı:**
  Eğer $P \equiv P' \pmod Q$ ise, modüler aritmetik kuralı gereği $Q$'nun her bir $q_i$ asal çarpanı için de $P \equiv P' \pmod{q_i}$ geçerlidir. Legendre sembolü modüler denkliği koruduğundan:
  $$\left( \frac{P}{q_i} \right) = \left( \frac{P'}{q_i} \right)$$
  Tüm $q_i$'ler için bu eşitlik sağlandığından çarpımları da birbirine eşit olur: $\left( \frac{P}{Q} \right) = \left( \frac{P'}{Q} \right) \quad \blacksquare$
  :::
</div>

## 3. Jacobi Sembolü İçin Özel Değerler

Jacobi sembolü, daha önce Euler Kriteri ve Gauss Lemması ile asal modüller için bulduğumuz $-1$ ve $2$'nin karesel karakteri formüllerini **birebir aynı şekilde** korur. Ancak ispatı, asal çarpanlar üzerinde çok zarif bir modüler tümevarım (indüksiyon) gerektirir.

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Jacobi Sembolünde Özel Değerler ($-1$ ve $2$)

  </div>

  $Q > 1$ bir tek tam sayı olsun. Bu durumda:

  1. $\left( \frac{-1}{Q} \right) = (-1)^{\frac{Q-1}{2}}$
  2. $\left( \frac{2}{Q} \right) = (-1)^{\frac{Q^2-1}{8}}$

  ::: details İspat
  $Q = q_1 \cdot q_2 \dots q_s$ şeklinde tek asal çarpanlarına ayrılmış olsun.

  **1) Birinci Formülün İspatı:**
  Jacobi tanımını kullanarak sol tarafı açalım:
  $$\left( \frac{-1}{Q} \right) = \left( \frac{-1}{q_1} \right) \dots \left( \frac{-1}{q_s} \right)$$
  $q_i$'ler asal olduğu için Legendre'nin özel formülünü kullanabiliriz:
  $$= (-1)^{\frac{q_1-1}{2}} \dots (-1)^{\frac{q_s-1}{2}} = (-1)^{\frac{q_1-1}{2} + \dots + \frac{q_s-1}{2}} \quad \dots (*)$$

  **Yardımcı Cebirsel Gerçek:** $a$ ve $b$ iki tek tam sayı olsun. 
  $$\frac{ab-1}{2} - \left( \frac{a-1}{2} + \frac{b-1}{2} \right) = \frac{(a-1)(b-1)}{2}$$
  $a$ ve $b$ tek sayı oldukları için $(a-1)$ ve $(b-1)$ çift sayıdır. İki çift sayının çarpımı 4'ün katıdır. Bu ifadeyi 2'ye böldüğümüzde sonuç kesinlikle 2'nin bir katı (çift sayı) olur. O halde modülo 2'de bu fark $0$'a denktir:
  $$\frac{ab-1}{2} \equiv \frac{a-1}{2} + \frac{b-1}{2} \pmod 2$$
  
  Bu mantığı indüksiyon yöntemiyle tüm $q_i$'lere genellersek:
  $$\frac{q_1-1}{2} + \frac{q_2-1}{2} + \dots + \frac{q_s-1}{2} \equiv \frac{q_1 \cdot q_2 \dots q_s - 1}{2} \pmod 2$$
  $$ \equiv \frac{Q-1}{2} \pmod 2$$

  Modülo 2'deki denklik, $(-1)$'in üssündeki çiftlik/teklik durumunu (işareti) değiştirmeyeceğinden, $(*)$ denklemindeki toplamı doğrudan bu sonuca eşitleyebiliriz:
  $$\left( \frac{-1}{Q} \right) = (-1)^{\frac{Q-1}{2}}$$

  ---

  **2) İkinci Formülün İspatı:**
  Yine Jacobi tanımını kullanarak sol tarafı açalım:
  $$\left( \frac{2}{Q} \right) = \left( \frac{2}{q_1} \right) \dots \left( \frac{2}{q_s} \right) = (-1)^{\frac{q_1^2-1}{8}} \dots (-1)^{\frac{q_s^2-1}{8}} = (-1)^{\frac{q_1^2-1}{8} + \dots + \frac{q_s^2-1}{8}} \quad \dots (+)$$

  **Yardımcı Cebirsel Gerçek:** $a$ ve $b$ iki tek tam sayı olsun.
  $$\frac{a^2b^2-1}{8} - \left( \frac{a^2-1}{8} + \frac{b^2-1}{8} \right) = \frac{(a^2-1)(b^2-1)}{8}$$
  Her tek sayının karesi modülo 8'de 1'e denktir. Yani $a^2-1$ ve $b^2-1$ sayıları 8'in katlarıdır ($8 \mid a^2-1$ ve $8 \mid b^2-1$). Dolayısıyla bu çarpım 64'ün katı olur, 8'e böldüğümüzde ise sonuç hala çift sayı olur ($\equiv 0 \pmod 2$).
  O halde:
  $$\frac{a^2b^2-1}{8} \equiv \frac{a^2-1}{8} + \frac{b^2-1}{8} \pmod 2$$

  Bu mantığı yine indüksiyonla tüm $q_i$'lere uygularsak:
  $$\frac{q_1^2-1}{8} + \dots + \frac{q_s^2-1}{8} \equiv \frac{(q_1 \dots q_s)^2 - 1}{8} \pmod 2$$
  $$\equiv \frac{Q^2-1}{8} \pmod 2$$

  Bu sonucu $(+)$ denklemindeki üsse yazdığımızda ispat tamamlanır:
  $$\left( \frac{2}{Q} \right) = (-1)^{\frac{Q^2-1}{8}} \quad \blacksquare$$
  :::
</div>

## 4. Jacobi Sembolü İçin Kuadratik Resiprosite Teoremi

Legendre sembolü için ispatladığımız "Altın Teorem" (Karşılıklılık), Jacobi sembolü için de birebir aynı formda geçerlidir. Bu teorem, devasa kompozit sayılarla çalışırken asal çarpanlara ayırma zahmetinden kurtulup doğrudan "takla attırma" (ters çevirme) işlemi yapmamıza olanak tanır.

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Jacobi Sembolü İçin Karşılıklılık Teoremi

  </div>

  $P > 1$ ve $Q > 1$ iki **tek tam sayı** ve $\gcd(P, Q) = 1$ olsun. Bu durumda:
  $$\left( \frac{P}{Q} \right) \cdot \left( \frac{Q}{P} \right) = (-1)^{\frac{P-1}{2} \cdot \frac{Q-1}{2}}$$
  eşitliği sağlanır.

  ::: details İspat
  $P$ ve $Q$ tek tam sayılarını asal çarpanlarına ayıralım:
  $P = p_1 \dots p_r$ ve $Q = q_1 \dots q_s$ ($p_i$ ve $q_j$'ler tek asal sayılar).

  Jacobi sembolünün tanımı ve çarpımsallık özelliğinden (Teorem 2):
  $$\left( \frac{P}{Q} \right) = \left( \frac{P}{q_1} \right) \dots \left( \frac{P}{q_s} \right) = \prod_{j=1}^{s} \left( \frac{P}{q_j} \right) = \prod_{j=1}^{s} \left( \prod_{i=1}^{r} \left( \frac{p_i}{q_j} \right) \right)$$

  Buradaki $\left( \frac{p_i}{q_j} \right)$ sembolleri, tabanlar asal olduğu için doğrudan **Legendre sembolleridir.** Bu yüzden onlara klasik Kuadratik Resiprosite Teoremini uygulayabiliriz:
  $$\left( \frac{p_i}{q_j} \right) = \left( \frac{q_j}{p_i} \right) (-1)^{\frac{p_i-1}{2} \cdot \frac{q_j-1}{2}}$$

  Bu eşitliği çarpım sembolünün içine yerleştirirsek:
  $$\left( \frac{P}{Q} \right) = \prod_{j=1}^{s} \prod_{i=1}^{r} \left[ \left( \frac{q_j}{p_i} \right) (-1)^{\frac{p_i-1}{2} \cdot \frac{q_j-1}{2}} \right]$$
  
  Çarpımı iki parçaya (semboller ve işaretler) ayıralım:
  $$\left( \frac{P}{Q} \right) = \left[ \prod_{i=1}^{r} \prod_{j=1}^{s} \left( \frac{q_j}{p_i} \right) \right] \cdot (-1)^{\sum_{i=1}^{r} \sum_{j=1}^{s} \frac{p_i-1}{2} \cdot \frac{q_j-1}{2}}$$
  
  Birinci köşeli parantezin içi tam olarak $\left( \frac{Q}{P} \right)$ Jacobi sembolünün açılımıdır. İkinci kısımdaki üs toplamını ise çarpanlarına ayırabiliriz:
  $$\left( \frac{P}{Q} \right) = \left( \frac{Q}{P} \right) \cdot (-1)^{\left( \sum_{i=1}^{r} \frac{p_i-1}{2} \right) \cdot \left( \sum_{j=1}^{s} \frac{q_j-1}{2} \right)}$$

  Bir önceki teoremin özel değerler ispatında kullandığımız o "Yardımcı Cebirsel Gerçek" (mod 2'deki denklik) gereği biliyoruz ki:
  $$\sum_{i=1}^{r} \frac{p_i-1}{2} \equiv \frac{P-1}{2} \pmod 2 \quad \text{ve} \quad \sum_{j=1}^{s} \frac{q_j-1}{2} \equiv \frac{Q-1}{2} \pmod 2$$

  Bu denklikleri üsse yazdığımızda ve her iki tarafı $\left( \frac{Q}{P} \right)$ ile çarptığımızda ispat tamamlanır:
  $$\left( \frac{P}{Q} \right) \cdot \left( \frac{Q}{P} \right) = (-1)^{\frac{P-1}{2} \cdot \frac{Q-1}{2}} \quad \blacksquare$$
  :::
</div>

## 5. Çözümlü Örnekler

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $x^2 \equiv 105 \pmod{317}$ kongrüansının çözümü var mıdır? (Başka bir deyişle, $105$, modülo $317$'ye göre bir KR midir?)

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **Hatırlatma (Asallık Testi):** Asal olmayan bir $t > 1$ doğal sayısının, $p \leq \sqrt{t}$ koşuluna uyan en az bir $p$ asal böleni vardır. Dolayısıyla, bu koşula uyan hiçbir asal sayıya bölünemeyen bir sayı kesinlikle asaldır.

  Sorumuzdaki modül olan $317$'nin durumunu inceleyelim:
  $17 < \sqrt{317} < 18$ olup; kontrol etmemiz gereken asallar $2, 3, 5, 7, 11, 13, 17$'dir. Bu asal sayıların hiçbiri $317$'yi tam bölmediğinden, **$317$ bir asal sayıdır.**

  O halde $105$ bir tek tam sayı, $317$ bir tek asal sayı ve $\gcd(105, 317) = 1$'dir. 
  Şimdi $\left( \frac{105}{317} \right)$ Jacobi sembolünü hesaplayalım. ($317$ asal olduğu için, burada Jacobi sembolü ile Legendre sembolü birbiriyle çakışır ve bulacağımız sonuç bize %100 kesin bir çözülebilirlik yanıtı verir).

  Jacobi Resiprosite Teoremini uygulayarak "takla" attıralım:
  $$\left( \frac{105}{317} \right) = \left( \frac{317}{105} \right) \cdot (-1)^{\frac{105-1}{2} \cdot \frac{317-1}{2}} = \left( \frac{317}{105} \right) \cdot (-1)^{52 \cdot 158}$$
  Üs ($52 \cdot 158$) bir çift sayı olduğu için $(-1)^{\text{çift}} = +1$'dir. İşaret değişmez:
  $$\left( \frac{105}{317} \right) = \left( \frac{317}{105} \right)$$

  Şimdi $317$'yi modülo $105$'e göre indirgeyelim ($317 \equiv 2 \pmod{105}$):
  $$\left( \frac{317}{105} \right) = \left( \frac{2}{105} \right)$$

  Karşımıza 2'nin karesel karakteri çıktı. Özel değer formülünü uygularsak:
  $$\left( \frac{2}{105} \right) = (-1)^{\frac{105^2-1}{8}}$$
  Üssü hesaplayalım: $105^2 = 11025$. $\frac{11024}{8} = 1378$. Bu sayı bir **çift sayıdır.**
  $$\left( \frac{2}{105} \right) = (-1)^{\text{çift}} = 1$$

  **Sonuç:** Zincirleme eşitliklerden $\left( \frac{105}{317} \right) = 1$ elde edilir. 
  Buna "Legendre sembolü gözüyle" baktığımızda ($317$ asal olduğundan); $105$, modülo $317$'ye göre kesin bir **Kuadratik Rezidü'dür (KR)**. 
  Dolayısıyla $x^2 \equiv 105 \pmod{317}$ kongrüansı **çözülebilirdir.**
  :::
</div>

## 6. Çalışma Problemleri (Kendini Dene)

Konuyu pekiştirmek için aşağıdaki problemleri öğrendiğin Legendre/Jacobi sembolü kuralları, Euler Kriteri ve Kuadratik Resiprosite teoremlerini kullanarak çözebilirsin.

**Soru 1:** Aşağıdaki sembollerin değerlerini hesaplayınız.
* $\left( \frac{-23}{83} \right)$
* $\left( \frac{51}{71} \right)$
* $\left( \frac{71}{73} \right)$
* $\left( \frac{-35}{97} \right)$

**Soru 2:** Aşağıdaki kongrüansların hangileri çözülebilirdir?
* **a)** $x^2 \equiv 10 \pmod{127}$
* **b)** $x^2 \equiv 234 \pmod{401}$
* **c)** $x^2 \equiv -73 \pmod{143}$
* **d)** $x^2 \equiv 45 \pmod{101}$