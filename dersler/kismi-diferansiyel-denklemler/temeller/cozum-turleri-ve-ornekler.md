---
title: Kısmi Diferansiyel Denklemlerde Çözüm Türleri ve Örnekler
description: Kısmi diferansiyel denklemlerde (KDD) genel, özel ve tekil çözüm kavramlarının pedagojik açıklaması; çözüm doğrulama ve ardışık integral yöntemleriyle analitik örnekler.
---
# Kısmi Diferansiyel Denklemler: Çözüm Türleri ve Örnekler


## Kısmi Diferansiyel Denklemlerde Çözüm Kavramı

Bir diferansiyel denklemin yapısını ve çözüm kümelerini anlamak, ileri matematiksel analizin temelidir. Kısmi diferansiyel denklemlerde (KDD) "çözüm" tanımı, denklemin sağlandığı bölge ve fonksiyonun süreklilik şartlarıyla doğrudan ilişkilidir.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: KDD Çözümü

  </div>
  
  Bir kısmi diferansiyel denklemde bağımlı değişken $u$'nun bağımsız değişkenlerinin $D \subseteq \mathbb{R}^n$ bölgesinde sınırlandığını varsayalım. $m$. mertebeden bir KDD'nin $D$ bölgesindeki çözümü; $D$ bölgesinin tüm iç noktalarında denklemi sağlayan ve $C^m$ (en az $m$ kez sürekli türevlenebilir) sınıfından olan bir fonksiyondur.
</div>

::: info 📌 Sabitler Yerine Keyfi Fonksiyonlar
Adi diferansiyel denklemlerin (ADD) genel çözümleri keyfi **sabitler** ($c_1, c_2$ vb.) içerirken; kısmi diferansiyel denklemlerin genel çözümleri, kısmi türev alma işlemlerinin doğası gereği keyfi **fonksiyonlar** içerir.
:::

## Çözüm Türleri

Diferansiyel denklemleri çözerken karşımıza çıkan fonksiyonlar, içerdikleri keyfi ifadelere ve denklemi sağlama biçimlerine göre **üç ana kategoriye** ayrılır. Bunu bir hiyerarşi gibi düşünebilirsiniz:

<div class="math-block definition">
  <div class="math-block-title">

  1. Genel Çözüm (General Solution)

  </div>
  
  Diferansiyel denklemin mertebesine uygun sayıda **keyfi fonksiyon** (veya nadiren keyfi sabit) içeren, denklemin sağlandığı en geniş çözüm ailesidir. Çözümlerin "ana şablonu" olarak da düşünülebilir.
</div>

<div class="math-block definition">
  <div class="math-block-title">

  2. Özel Çözüm (Particular Solution)

  </div>
  
  Genel çözümün (ana şablonun) içindeki keyfi fonksiyonlara belirli bir kural seçilerek elde edilen **nokta atışı** çözümdür. Genellikle sorularda verilen başlangıç veya sınır koşulları uygulandığında genel çözümden **özel çözüme** geçiş yapılır.
</div>

<div class="math-block definition">
  <div class="math-block-title">

  3. Tekil Çözüm (Singular Solution)

  </div>
  
  Diferansiyel denklemi kusursuz bir şekilde sağlamasına rağmen, **genel çözüm şablonundan hiçbir şekilde türetilemeyen** istisnai ve kural dışı çözümlerdir. Yani genel çözümdeki keyfi fonksiyonlara ne değer verirsek verelim tekil çözümü elde edemeyiz; o kendi başına denklemi sağlayan bağımsız bir fonksiyondur.
</div>

## Analitik Örnekler

Aşağıdaki örneklerde KDD çözümlerinin doğrulanması ve genel çözümler üzerinden diferansiyel denklemlerin nasıl inşa edileceği incelenmiştir.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Aşağıdaki denklemin çözümünü inceleyiniz.

  $$u_x^4 + u_y^4 = 0$$

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  Reel sayılar kümesinde çalıştığımız için, iki çift kuvvetin toplamının sıfır olabilmesi ancak her iki terimin de tabanlarının ayrı ayrı sıfır olmasıyla mümkündür. Dolayısıyla şu şartlar sağlanmalıdır:
  
  $$u_x = 0 \quad \text{ve} \quad u_y = 0$$
  
  İlk olarak $u_x = 0$ denklemini ele alırsak, $u$ fonksiyonunun $x$'e göre değişmediğini anlarız. Bu durumda $u$, sadece $y$'ye bağlı bir fonksiyon olmalıdır:
  
  $$u = A(y)$$
  
  Şimdi bu ifadeyi $u_y = 0$ denkleminde yerine koyalım:
  
  $$u_y = A'(y) = 0$$
  
  Bir fonksiyonun türevi sıfırsa, o fonksiyon bir sabite eşittir. Öyleyse $A(y) = c$ olmak zorundadır.
  
  $$u(x,y) = c$$
  
  Sonuç olarak, genel çözüm $u(x,y) = c$ şeklindedir. Yani bu özel ve istisnai durumda KDD'nin genel çözümü, beklendiği gibi **keyfi fonksiyonlar içermez**, sadece keyfi bir sabit içerir.
  
  <span style="float: right;">$\blacksquare$</span>
  <div style="clear: both;"></div>
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $f \in C^1$ keyfi bir fonksiyon olmak üzere, $u(x,y) = \sqrt{y} f(2x+y)$ fonksiyonunun

  $$y u_x - 2y u_y + u = 0$$

  kısmi diferansiyel denkleminin bir çözümü olduğunu gösteriniz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  $u(x,y) = \sqrt{y} f(2x+y)$ fonksiyonunun $x$ ve $y$'ye göre kısmi türevlerini alalım. $f$ fonksiyonu için zincir kuralını, $u_y$ türevi içinse çarpım kuralını uygulayacağız:
  
  $$u_x = \frac{\partial u}{\partial x} = \sqrt{y} \cdot 2 f'(2x+y)$$
  
  $$u_y = \frac{\partial u}{\partial y} = \frac{1}{2\sqrt{y}} f(2x+y) + \sqrt{y} \cdot f'(2x+y)$$
  
  Şimdi bu türevleri $y u_x - 2y u_y + u = 0$ denkleminde yerine yazalım:
  
  $$\begin{aligned} y \Big(2\sqrt{y} f'\Big) - 2y \left( \frac{1}{2\sqrt{y}} f + \sqrt{y} f' \right) + \sqrt{y} f &= 0 \\ 2y\sqrt{y} f' - \frac{2y}{2\sqrt{y}} f - 2y\sqrt{y} f' + \sqrt{y} f &= 0 \end{aligned}$$
  
  $\frac{y}{\sqrt{y}} = \sqrt{y}$ sadeleştirmesini yaparak denklemi tekrar düzenlersek:
  
  $$2y\sqrt{y} f' - \sqrt{y} f - 2y\sqrt{y} f' + \sqrt{y} f = 0$$
  
  Zıt işaretli terimler birbirini götürür ve $0 = 0$ eşitliği sağlanır. Çözüm matematiksel olarak doğrulanmıştır.
  
  <span style="float: right;">$\blacksquare$</span>
  <div style="clear: both;"></div>
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $f$, tek değişkenli keyfi sürekli bir fonksiyon olmak üzere;

  $$u(x,y) = x f(x \cdot y) + y^2$$
  
  ifadesi hangi kısmi diferansiyel denklemin genel çözümüdür?

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  Denklem bir adet keyfi fonksiyon ($f$) içerdiğinden, aradığımız kısmi diferansiyel denklemin **1. mertebeden** olmasını bekleriz. Temel hedefimiz, türev işlemleri yardımıyla denklemin içindeki $f$ ve $f'$ ifadelerinden kurtulmaktır. 
  
  İlk olarak $u$'nun $x$ ve $y$'ye göre kısmi türevlerini (çarpım ve zincir kurallarını kullanarak) alalım:
  
  $$u_x = 1 \cdot f(xy) + x \cdot \big(y f'(xy)\big) = f(xy) + xy f'(xy)$$
  
  $$u_y = x \cdot \big(x f'(xy)\big) + 2y = x^2 f'(xy) + 2y$$
  
  Bu iki denklemdeki $f'$ terimlerini eşitleyip yok etmek için, ilk denklemi $x$ ile, ikinci denklemi ise $y$ ile çarpalım:
  
  $$x u_x = x f(xy) + x^2 y f'(xy)$$
  $$y u_y = x^2 y f'(xy) + 2y^2$$
  
  Şimdi $f'$ terimlerini yok etmek için ilk denklemden ikinci denklemi çıkaralım:
  
  $$x u_x - y u_y = x f(xy) + x^2 y f'(xy) - \big(x^2 y f'(xy) + 2y^2\big)$$
  $$x u_x - y u_y = x f(xy) - 2y^2$$
  
  Elde ettiğimiz KDD'nin içinde hala keyfi $f$ fonksiyonu barınmaktadır. Bundan tamamen kurtulmak için, sorunun en başında verilen $u = x f(xy) + y^2$ eşitliğini kullanarak $x f(xy)$ ifadesini yalnız bırakalım:
  
  $$x f(xy) = u - y^2$$
  
  Bunu bulduğumuz denklemde yerine yazdığımızda:
  
  $$x u_x - y u_y = (u - y^2) - 2y^2$$
  $$x u_x - y u_y = u - 3y^2$$
  
  Böylece keyfi fonksiyondan tamamen arındırılmış, istenen kısmi diferansiyel denklemi elde etmiş oluruz.
  
  <span style="float: right;">$\blacksquare$</span>
  <div style="clear: both;"></div>
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $u = u(x,y,z)$ olmak üzere,

  $$u_{xy} = 0$$
  
  kısmi diferansiyel denkleminin genel çözümünü bulunuz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  Öncelikle $u_{xy} = \frac{\partial}{\partial x} \left( \frac{\partial u}{\partial y} \right)$ olduğunu hatırlayalım. Denklemi çözmek için her iki tarafa sırasıyla kısmi integral uygulayacağız.
  
  İlk olarak, denklemin her iki tarafının $x$'e göre integralini alalım. Kısmi integral aldığımız için, oluşacak entegrasyon sabiti sıradan bir sayı değil, $x$'ten bağımsız olan ancak $y$ ve $z$'ye bağlı olan keyfi bir fonksiyon olmalıdır:
  
  $$\int u_{xy} \, \partial x = \int 0 \, \partial x$$
  $$u_y = f(y,z)$$
  
  Şimdi elde ettiğimiz $u_y = f(y,z)$ denkleminin her iki tarafının $y$'ye göre kısmi integralini alalım. Bu kez entegrasyon "sabiti", $y$'den bağımsız olan $x$ ve $z$'ye bağlı keyfi bir fonksiyon ($G(x,z)$) olacaktır:
  
  $$\int u_y \, \partial y = \int f(y,z) \, \partial y$$
  
  $f(y,z)$ fonksiyonunun $y$'ye göre integrali de yine $y$ ve $z$'ye bağlı başka bir keyfi fonksiyon üretecektir; buna da $F(y,z)$ diyelim. Sonuç olarak genel çözüm:
  
  $$u(x,y,z) = F(y,z) + G(x,z)$$
  
  şeklinde bulunur. Görüldüğü üzere çözüm, birbirinden bağımsız iki keyfi fonksiyondan oluşmaktadır.
  
  <span style="float: right;">$\blacksquare$</span>
  <div style="clear: both;"></div>
  :::
</div>

::: info 📌 Mertebe ve Fonksiyon Sayısı İlişkisi
Genel bir kural olarak; $n$ tane bağımsız değişken içeren $m$. mertebeden bir KDD'nin genel çözümü, $n-1$ değişkene bağlı $m$ adet keyfi fonksiyon ile ifade edilebilir. Ancak yukarıdaki ilk örnekte ($u_x^4 + u_y^4 = 0$) gördüğümüz üzere, denklemin yapısına bağlı olarak **bu kural her zaman geçerli olmak zorunda değildir.**
:::