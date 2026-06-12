<script setup>
import LegendreCalculator from '/.vitepress/components/LegendreCalculator.vue'
</script>

# Legendre Sembolü ve Euler Kriteri

Bir önceki bölümde bir sayının kuadratik rezidü (KR) veya kuadratik non-rezidü (KNR) olma durumunu denklemler üzerinden tanımlamıştık. Ancak sayılar büyüdükçe her defasında "Acaba modülo $p$'de karesi $a$'yı veren bir sayı var mıdır?" diye tek tek kare alarak kontrol etmek imkansızlaşır. 

Bu durumu matematiksel olarak çok daha kompakt ve işlevsel bir forma sokan gösterim **Legendre Sembolü**'dür.

## 1. Legendre Sembolü Tanımı

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Legendre Sembolü

  </div>

  $p$ bir tek asal sayı ve $a$ herhangi bir tam sayı olsun. 
  $a$'nın modülo $p$'ye göre kuadratik karakterini belirten **Legendre Sembolü**, $\left( \frac{a}{p} \right)$ ile gösterilir ve şu şekilde tanımlanır:

  $$
  \left( \frac{a}{p} \right) = \begin{cases} 
  \hfill 1, & a \text{ mod } p \text{'de Kuadratik Rezidü ise} \\ 
  -1, & a \text{ mod } p \text{'de Kuadratik Non-Rezidü ise} \\
  \hfill 0, & p \mid a \text{ ise}
  \end{cases}
  $$
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Legendre Sembolü Değerleri

  </div>

  **1. Kuadratik Rezidü Örneği:** &nbsp;
  $x^2 \equiv 1 \pmod 7$ kongrüansının çözülebilir olduğu barizdir (Örn: $x=1$). 
  Bu durumda $1$, modülo 7'ye göre bir Kuadratik Rezidü (KR) olduğundan sembolün değeri $1$'dir:
  $$\left( \frac{1}{7} \right) = 1$$

  **2. Kuadratik Non-Rezidü Örneği:** &nbsp;
  $x^2 \equiv 3 \pmod 5$ kongrüansını inceleyelim. Çözüm kümesinin olmadığını (3'ün KNR olduğunu) test ederek görebiliriz. 
  Dolayısıyla sembolün değeri $-1$'dir:
  $$\left( \frac{3}{5} \right) = -1$$
</div>

Tanımı oldukça basit görünse de, Legendre sembolünün asıl gücü sahip olduğu çarpımsal özelliklerden ve **Euler Kriterinden** gelir. 

## 2. Euler Kriteri ve Sembolün Özellikleri

Aşağıdaki teorem, Legendre sembolü ile modüler üs alma işlemi arasında kusursuz bir köprü kurar. Kriptografide büyük asal sayılarla çalışırken, bir sayının KR olup olmadığını tespit etmek için çözülebilirlik testleri yapmak yerine yalnızca Euler Kriteri kullanılır.

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Euler Kriteri ve Legendre Sembolünün Özellikleri

  </div>

  $p$ bir tek asal sayı; $a$ ve $b$ tam sayılar ve $\gcd(a, p) = \gcd(b, p) = 1$ olsun. Bu durumda aşağıdaki dört özellik geçerlidir:

  1. **Euler Kriteri:** $\left( \frac{a}{p} \right) \equiv a^{(p-1)/2} \pmod p$
  2. **Çarpımsallık Kuralı:** $\left( \frac{a}{p} \right) \cdot \left( \frac{b}{p} \right) = \left( \frac{a \cdot b}{p} \right)$
  3. **Periyodiklik (Modüler Denklik):** Eğer $a \equiv b \pmod p$ $\implies$ $\left( \frac{a}{p} \right) = \left( \frac{b}{p} \right)$
  4. **Özel Değerler:** $\left( \frac{a^2}{p} \right) = 1, \quad \left( \frac{1}{p} \right) = 1, \quad \left( \frac{-1}{p} \right) = (-1)^{(p-1)/2}$

  ::: details İspat
  **1) Euler Kriterinin İspatı:**
  Bu ispatı, daha önce işlediğimiz "$n$. Kuvvetten Kongrüanslar (Euler Kriteri Genellemesi)" teoreminin $n=2$ olan özel durumu üzerinden yapacağız.
  
  * **KR Durumu:** $a$ modülo $p$'ye göre bir KR olsun. Bu durumda kongrüansın çözümü vardır. Önceki teoremimiz gereği çözüm olması için $a^{(p-1)/2} \equiv 1 \pmod p$ olmalıdır. Legendre tanımı gereği $\left( \frac{a}{p} \right) = 1$'dir. Dolayısıyla:
    $$\left( \frac{a}{p} \right) \equiv a^{(p-1)/2} \pmod p$$
    
  * **KNR Durumu:** $a$ modülo $p$'ye göre bir KNR olsun. Çözüm yoktur ve önceki teorem gereği $a^{(p-1)/2} \not\equiv 1 \pmod p$'dir.
    Öte yandan Fermat'nın Küçük Teoreminden dolayı $a^{p-1} \equiv 1 \pmod p$'dir. İki kare farkı ile açarsak:
    $$(a^{(p-1)/2} - 1)(a^{(p-1)/2} + 1) \equiv 0 \pmod p$$
    $p$ asal olduğu için bu çarpanlardan birini tam bölmek zorundadır. $a^{(p-1)/2} \not\equiv 1 \pmod p$ olduğunu bildiğimizden birinci çarpanı bölemez. O halde mecburen ikinci çarpanı böler:
    $$a^{(p-1)/2} \equiv -1 \pmod p$$
    Legendre tanımı gereği KNR için $\left( \frac{a}{p} \right) = -1$'dir. Sonuç olarak yine eşitlik sağlanır:
    $$\left( \frac{a}{p} \right) \equiv a^{(p-1)/2} \pmod p$$

  **2) Çarpımsallık Kuralının İspatı:**
  Euler kriterini (1. kuralı) $a$ yerine $ab$ alarak yazalım:
  $$\left( \frac{ab}{p} \right) \equiv (ab)^{(p-1)/2} \equiv a^{(p-1)/2} \cdot b^{(p-1)/2} \pmod p$$
  Yine Euler kriterinden $a^{(p-1)/2} \equiv \left( \frac{a}{p} \right)$ ve $b^{(p-1)/2} \equiv \left( \frac{b}{p} \right)$ olduğunu biliyoruz. Yerlerine yazarsak:
  $$\left( \frac{ab}{p} \right) \equiv \left( \frac{a}{p} \right) \cdot \left( \frac{b}{p} \right) \pmod p$$
  Sembollerin alabileceği değerler yalnızca $1$ ve $-1$'dir. $p$ tek asal sayı ($p > 2$) olduğu için modülo $p$'de $1 \not\equiv -1 \pmod p$'dir. Modüler denklikteki değerler ancak tam olarak birbirine eşitlerse denk olabilirler. Dolayısıyla:
  $$\left( \frac{ab}{p} \right) = \left( \frac{a}{p} \right) \cdot \left( \frac{b}{p} \right)$$

  **3) Periyodikliğin İspatı:**
  Kabul edelim ki $a \equiv b \pmod p$ olsun. Her iki tarafın $(p-1)/2$'inci kuvvetini alırsak:
  $$a^{(p-1)/2} \equiv b^{(p-1)/2} \pmod p$$
  Euler kriteri gereği bu kuvvetler Legendre sembollerine denktir:
  $$\left( \frac{a}{p} \right) \equiv \left( \frac{b}{p} \right) \pmod p$$
  İkinci ispatta vurguladığımız mantıkla, sadece $\pm 1$ olabilen bu sembollerin modülo $p > 2$'de denk olması, birbirlerine birebir eşit olduklarını kanıtlar.

  **4) Özel Değerlerin İspatı:**
  * $a=1$ için Euler Kriterini uygularsak:
    $$\left( \frac{1}{p} \right) \equiv 1^{(p-1)/2} = 1 \pmod p \implies \left( \frac{1}{p} \right) = 1$$
  * Çarpımsallık özelliğini kullanarak (Teorem 2):
    $$\left( \frac{a^2}{p} \right) = \left( \frac{a}{p} \right) \cdot \left( \frac{a}{p} \right) = (\pm 1)^2 = 1$$
  * $a = -1$ için Euler Kriterini uygularsak, Sayılar Teorisinde ve Soyut Cebirde çok sık karşılaşacağımız o meşhur özdeşliği elde ederiz:
    $$\left( \frac{-1}{p} \right) \equiv (-1)^{(p-1)/2} \pmod p$$
    Değerler $\pm 1$ aralığında olduğu için eşitlik kesindir: $\left( \frac{-1}{p} \right) = (-1)^{(p-1)/2} \quad \blacksquare$
  :::
</div>

## 3. İnteraktif Legendre Hesaplayıcısı
Legendre sembolünün tanımını ve özelliklerini öğrendikten sonra, farklı $a$ ve $p$ değerleri için sembolün nasıl davrandığını gözlemlemek faydalı olacaktır. Aşağıdaki interaktif hesaplayıcı, herhangi bir $a$ ve tek asal $p$ değeri için $\left( \frac{a}{p} \right)$'nın değerini hızlıca hesaplamanıza olanak tanır.

<LegendreCalculator />