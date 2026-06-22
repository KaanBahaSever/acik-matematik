# Kısmi Diferansiyel Denklemlere Giriş

Kısmi diferansiyel denklemlerin (KDD) tarihsel gelişimi, 18. yüzyılda fiziksel dünyadaki dinamikleri ve sürekli ortamları matematiksel olarak modelleme çabalarına dayanır. Jean le Rond d'Alembert'in titreşen bir telin hareketini açıklamak için geliştirdiği tek boyutlu dalga denklemi, Leonhard Euler'in akışkanlar mekaniğine kazandırdığı formüller ve Joseph Fourier'nin ısı yayılımı teorisi bu disiplinin temel taşlarını oluşturur. Bu fiziksel problemler, tek bir bağımsız değişken içeren adi diferansiyel denklemlerin (ADD) aksine, doğadaki olayların hem zamana hem de uzaydaki konuma bağlı olarak çok boyutlu incelenmesi gerektiğini göstererek KDD alanının doğmasını sağlamıştır.

Bu ders notlarında, kısmi diferansiyel denklemlerin temel kavramsal çerçevesini kuracağız. Önce bağımlı ve bağımsız değişkenleri ayırt etmeyi öğrenecek, ardından denklemleri analitik olarak inceleyebilmek için kritik öneme sahip olan **mertebe**, **homojenlik** ve **lineerlik** kriterlerine göre sınıflandırma yapılarını ele alacağız.

## Temel Notasyonlar ve Kavramsal Çerçeve

Matematiksel analize geçmeden önce, bir denklemin kısmi diferansiyel denklem olarak nitelendirilebilmesi için gereken temel şartı net bir şekilde ortaya koymalıyız.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Kısmi Diferansiyel Denklem (KDD)

  </div>

  Birden fazla bağımsız değişkene göre türevler içeren, bir veya daha fazla bağımlı değişkenin ve bu değişkenlerin kısmi türevlerinin arasındaki ilişkiyi gösteren denklemlere **kısmi diferansiyel denklem** denir.

</div>

Bir diferansiyel denklemle karşılaştığımızda yapmamız gereken ilk iş, hangi değişkenin fonksiyonun kendisini (bağımlı), hangi değişkenlerin ise girdileri (bağımsız) temsil ettiğini belirlemektir. Bu ayrım, türev operatörlerinin kime uygulandığını anlamamızı sağlar.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Bağımlı ve Bağımsız Değişken Analizi

  </div>

  Aşağıdaki yaygın diferansiyel modellemelerde değişkenlerin rollerini inceleyelim:

  1. $\frac{\partial z}{\partial s} + s^2 \frac{\partial z}{\partial t} = 0$ denklemi verilmiş olsun. Burada $z = z(s,t)$ formunda bir fonksiyon aranmaktadır.
     * **$z$**: Bağımlı değişken
     * **$s, t$**: Bağımsız değişkenler

  2. Fizikte dalga yayılımını modelleyen $\frac{\partial^2 u}{\partial t^2} - c^2 \frac{\partial^2 u}{\partial x^2} = 0$ denkleminde $u = u(x,t)$ yapısı mevcuttur.
     * **$u$**: Bağımlı değişken
     * **$x$** (konum), **$t$** (zaman): Bağımsız değişkenler

</div>

## 1. Mertebe (Order)

Bir denklemin yapısını ve çözümünün zorluk derecesini belirleyen en somut özelliklerinden biri mertebesidir. Diferansiyel denklemlerin çözüm uzaylarının boyutu doğrudan bu kavrama bağlı olarak şekillenir.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Denklemin Mertebesi

  </div>

  Bir kısmi diferansiyel denklemde yer alan en yüksek mertebeden kısmi türevin derecesine, o **diferansiyel denklemin mertebesi** (order) denir.

</div>

Mertebe bulunurken denklemdeki tüm türevli terimler tek tek taranır ve uygulanan en yüksek türev operatörü baz alınır. Terimlerin kendi kuvvetleri (örneğin bir türevin karesinin alınması) mertebeyi etkilemez.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Mertebe Belirleme

  </div>

  $$\frac{\partial^2 u}{\partial t^2} + \frac{\partial^3 u}{\partial x^2 \partial t} + u^2 = 0$$

  ::: details 💡 Çözümü Göster / Gizle
  * **Analiz:** Denklemde yer alan en yüksek türev, $x$'e göre iki, $t$'ye göre bir kez türev alınarak oluşturulmuş olan $\frac{\partial^3 u}{\partial x^2 \partial t}$ terimidir.
  * **Sonuç:** Denklem **3. mertebeden** bir KDD'dir.
  :::

</div>

## 2. Homojenlik (Homogeneity)

Denklemlerin süperpozisyon ilkesine uyup uymadığını anlamak ve genel çözüme ulaşırken izlenecek stratejiyi belirlemek için homojenlik kavramı incelenmelidir. Bu kavramı en basit ve pratik haliyle denklemin terimlerine bakarak ayırt edebiliriz.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Homojenlik

  </div>

  Bir kısmi diferansiyel denklemdeki tüm terimler tek tek incelendiğinde; **her bir terimin içinde** bağımlı değişkenin ($u$) kendisi veya onun kısmi türevlerinden ($u_x, u_{xx}, u_y, \dots$) en az biri çarpan olarak bulunuyorsa, bu denklem **homojen** (homogeneous) bir denklemdir.

  Eğer denklemde, içinde hiçbir şekilde bağımlı değişken veya türevi geçmeyen, sadece bağımsız değişkenlerden ($x, y, t, \dots$) veya sabit sayılardan oluşan "yalnız" bir terim varsa, bu denklem **homojen olmayan** (nonhomogeneous) bir denklemdir.

</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Homojen ve Homojen Olmayan Denklem Farkı

  </div>

  Aşağıdaki iki denklemin homojenlik durumlarını inceleyelim:

  1. $\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2} - 5u = 0$
  2. $\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2} - 5u = x^2 + \sin(y)$

  ::: details 💡 Çözümü Göster / Gizle
  * **1. Denklem:** Tüm terimlerde ($\frac{\partial^2 u}{\partial x^2}$, $\frac{\partial^2 u}{\partial y^2}$, $-5u$) bağımlı değişken veya türevi mevcuttur. Dışarıdan eklenmiş yalnız bir terim yoktur. Denklem **homojendir**.
  * **2. Denklem:** Eşitliğin sağ tarafındaki $x^2 + \sin(y)$ ifadesinde $u$ veya türevi yoktur. Sadece bağımsız değişkenlerden oluşan bu terimler denklemin homojenliğini bozar. Denklem **homojen değildir**.
  :::

</div>

## 3. Lineerlik (Linearity) ve Alt Sınıfları

Lineerlik, matematiksel analizin en güçlü sınır çizgisidir. Doğrusal yapıdaki bir denklemde en büyük kural şudur: Bağımlı değişken ($u$) ve tüm türevleri **sadece birinci dereceden** olmalıdır, asla birbirleriyle çarpılmamalıdır ve sinüs, karekök gibi fonksiyonların içine girmemelidir. Bir KDD'yi lineerlik yapısına göre dört ana sınıfta inceleriz.

### A) Lineer (Doğrusal) Denklemler

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Lineer Denklem

  </div>

  Bütün terimlerdeki bağımlı değişken ($u$) ve tüm kısmi türevlerinin birinci dereceden olduğu, kendi aralarında çarpılmadığı ve katsayılarının **yalnızca bağımsız değişkenlerden** (veya sabitlerden) oluştuğu denklemlere **lineer** denir.

</div>

::: info 📌 Yaygın Yanılgı: Bağımsız Değişkenle Çarpmak
Türevleri $x$ veya $y$ gibi bağımsız değişkenlerle çarpmak lineerliği **bozmaz**. Örneğin $x u_{xx} + y^2 u_{yy} = 0$ denklemi tamamen lineerdir. Bir denklemin lineerlikten çıkması için $u^2$, $(u_x)^2$ gibi doğrusallığı bozan bir terim barındırması şarttır.
:::

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Lineer Denklem Analizi

  </div>

  $\frac{\partial u}{\partial t} - 3 \frac{\partial^2 u}{\partial x^2} = x^2$

  ::: details 💡 Çözümü Göster / Gizle
  * **Mertebe:** 2 (En yüksek türev $\frac{\partial^2 u}{\partial x^2}$)
  * **Homojenlik:** Homojen değil (Sağ tarafta $u$ içermeyen $x^2$ terimi var)
  * **Lineerlik:** Lineer ($u$ ve türevlerinin derecesi 1, birbirleriyle çarpılmamışlar, katsayıları sabit).
  :::

</div>

### B) Yarı-Lineer (Semilinear) Denklemler

Eğer bir denklemde nonlineer (doğrusal olmayan) bir terim varsa, o denklemin sınıfını belirlemek için **en yüksek mertebeli türevlerin katsayılarına** bakarız.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Yarı-Lineer Denklem

  </div>

  Denklemde doğrusallığı bozan bir terim bulunmasına rağmen, **en yüksek mertebeli türevlerin** kendileri birinci derecedense ve başlarındaki katsayılar **yalnızca bağımsız değişkenlerden** (veya sabitlerden) oluşuyorsa, bu denkleme **yarı-lineer** (semilinear) denir. 

</div>

Bu denklem türünde nonlineerlik yaratan unsurlar her zaman en yüksek mertebeden daha düşük seviyedeki terimlerde bulunur.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Yarı-Lineer Denklem Analizi

  </div>

  $x u_{xx} + y u_{yy} - (u_x)^2 = 0$

  ::: details 💡 Çözümü Göster / Gizle
  * **Mertebe:** 2
  * **Homojenlik:** Homojen
  * **Lineerlik:** Yarı-lineer (Denklemdeki $(u_x)^2$ doğrusallığı bozar. Fakat en yüksek mertebeli türevler olan $u_{xx}$ ve $u_{yy}$'nin katsayıları olan $x$ ve $y$, sadece bağımsız değişkendir.)
  :::

</div>

### C) Kuazi-Lineer (Quasilinear) Denklemler

Doğrusallıktan bir adım daha uzaklaştığımızda, en yüksek mertebeli türevlerin katsayılarına bağımlı değişkenin kendisi veya türevleri sızmaya başlar.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Kuazi-Lineer Denklem

  </div>

  En yüksek mertebeli türevlerin kendileri hala birinci dereceden (doğrusal) olmasına rağmen, bu yüksek mertebeli terimlerin katsayılarında bağımlı değişken ($u$) veya onun **daha düşük mertebeli türevleri** çarpım durumunda bulunuyorsa, denklem **kuazi-lineer**dir.

</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Kuazi-Lineer Denklem Analizi

  </div>

  $u \cdot u_{xx} + u_{yy} = 0$

  ::: details 💡 Çözümü Göster / Gizle
  * **Mertebe:** 2
  * **Homojenlik:** Homojen
  * **Lineerlik:** Kuazi-lineer (En yüksek mertebeli $u_{xx}$ teriminin baş katsayısında bağımlı değişken olan $u$ çarpanı vardır.)
  :::

</div>

### D) Nonlineer (Tam Doğrusal Olmayan) Denklemler

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Nonlineer Denklem

  </div>

  En yüksek mertebeden türevlerin kendi aralarında çarpıldığı, kuvvetlerinin alındığı (örneğin $u_{xx}^2$) veya doğrusal olmayan aşkın fonksiyonların (örneğin $\sin(u_{xx})$) içinde yer aldığı denklemlere bütünüyle **nonlineer** denir.

</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Nonlineer Denklem Analizi

  </div>

  $u_{xxx}^2 + u_{xy} = 0$

  ::: details 💡 Çözümü Göster / Gizle
  * **Mertebe:** 3
  * **Homojenlik:** Homojen
  * **Lineerlik:** Nonlineer (En yüksek mertebeli $u_{xxx}$ türevinin doğrudan karesi alındığı için doğrusal form tamamen kaybedilmiştir.)
  :::

</div>

## 🔄 Denklemler Arası Kapsama (Alt Küme) İlişkisi

Bu dört sınıflandırma birbirinden tamamen bağımsız kutular değildir; aksine tıpkı bir matruşka bebeği gibi birbirlerini kapsayan matematiksel alt kümelerdir. Her dar tanım, bir geniş tanımın özel bir halidir.

### Hiyerarşik Kapsama Sıralaması:
**Lineer $\subset$ Yarı-Lineer $\subset$ Kuazi-Lineer $\subset$ Nonlineer (Genel)**



Bunu kafamızda canlandırmak için şu mantıkla düşünebiliriz:
1. **Lineer Denklemler**, aslında *yarı-lineer* denklemlerin doğrusallığı bozan alt terimlerinin sıfır olduğu çok özel bir halidir.
2. **Yarı-Lineer Denklemler**, *kuazi-lineer* denklemlerin en yüksek mertebeli teriminin katsayısındaki $u$ çarpanının yok olup yerine sadece bağımsız değişkenlerin geldiği özel bir halidir.
3. **Kuazi-Lineer Denklemler** de, evrendeki tüm *genel nonlineer* KDD'lerin, en azından yüksek mertebeli türevlerinin doğrusal kalmayı başardığı düzenli alt kümesidir.

---

## 📝 Karışık Sınıflandırma Örnekleri

<div class="math-block example">
  <div class="math-block-title">

  Örnek 1: Burgers Denklemi

  </div>

  $u_t + u \cdot u_x = 0$

  ::: details 💡 Çözümü Göster / Gizle
  * **Mertebe:** 1 (En yüksek türevler $u_t$ ve $u_x$)
  * **Homojenlik:** Homojen (Her terimde $u$ veya türevi var)
  * **Lineerlik:** Kuazi-lineer (En yüksek türev olan $u_x$'in başında $u$ çarpanı var)
  :::

</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek 2: Dalga Denklemi Varyasyonu

  </div>

  $u_{tt} - c^2 u_{xx} = \sin(x)$

  ::: details 💡 Çözümü Göster / Gizle
  * **Mertebe:** 2 (En yüksek türevler $u_{tt}$ ve $u_{xx}$)
  * **Homojenlik:** Homojen Değil (Sağ taraftaki $\sin(x)$ terimi $u$ içermez)
  * **Lineerlik:** Lineer ($u$ ve tüm türevleri 1. dereceden, katsayıları sabittir)
  :::

</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek 3: Eikonal Denklem

  </div>

  $(u_x)^2 + (u_y)^2 = 1$

  ::: details 💡 Çözümü Göster / Gizle
  * **Mertebe:** 1 (En yüksek türevler $u_x$ ve $u_y$)
  * **Homojenlik:** Homojen Değil (Sağ tarafta bağımsız bir sabit var)
  * **Lineerlik:** Nonlineer (En yüksek türevlerin karesi alınmış, doğrusal yapı bozulmuş)
  :::

</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek 4: Karmaşık Katsayılı Denklem

  </div>

  $y u_{xx} + x^2 u_{yy} - u^2 = e^x$

  ::: details 💡 Çözümü Göster / Gizle
  * **Mertebe:** 2 (En yüksek türevler $u_{xx}$ ve $u_{yy}$)
  * **Homojenlik:** Homojen Değil (Sağ tarafta $e^x$ terimi var)
  * **Lineerlik:** Yarı-lineer ($u^2$ terimi doğrusallığı bozar ancak en yüksek mertebeli türevlerin katsayıları olan $y$ ve $x^2$ sadece bağımsız değişkenlerden oluşur)
  :::

</div>