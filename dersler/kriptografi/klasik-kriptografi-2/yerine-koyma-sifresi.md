---
title: Yerine Koyma Şifrelemesi
description: Alfabe permütasyonlarına dayalı yerine koyma şifrelemesinin matematiksel tanımını ve kullanım mantığını açıklar.
---

# Alfabe Permütasyonu (Yerine Koyma) Şifrelemesi

Soyut cebirsel perspektiften bakıldığında, klasik şifreleme yöntemlerinin büyük bir kısmı alfabe kümesinin kendi üzerindeki birebir ve örten dönüşümleriyle, yani permütasyonlarıyla ifade edilir. Kriptografi literatüründe **Monoalfabetik Yerine Koyma Şifresi** olarak da bilinen bu yapı, matematiksel olarak tamamen bir **simetrik grup ($S_n$)** işlemidir.

Bu sistemde harflerin metin içindeki konumları (indeksleri olan $\tau$) sabit kalır; ancak her bir karakterin alfabedeki sayısal değeri ($x_\tau$), bir $\pi$ permütasyon fonksiyonuna sokularak karakterin kimliği değiştirilir.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Simetrik Grup ($S_n$)

  </div>

  Boş olmayan bir $A$ kümesinin kendi üzerine tanımlı tüm **birebir ve örten** fonksiyonlarının (permütasyonlarının) bileşke işlemi ($\circ$) altında oluşturduğu gruba **simetrik grup** denir ve $\text{Sym}(A)$ ile gösterilir. 
  
  Eğer $A$ kümesi $n$ elemanlı sonlu bir küme ise (örneğin $A = \{0, 1, 2, \dots, n-1\}$), bu grup **$S_n$** sembolü ile ifade edilir. Bu grubun eleman sayısı (grubun mertebesi), elemanların tüm olası dizilimlerinin sayısına eşit olup faktöriyel işlemiyle hesaplanır:

  $$|S_n| = n!$$
</div>

Simetrik gruplar, sonlu bir kümenin elemanlarının tüm olası yeniden dizilimlerini tek bir cebirsel çatı altında toplar. Kriptografik açıdan bakıldığında bu grup, bir alfabedeki harflerin yerini değiştirmek veya karıştırmak amacıyla kullanılabilecek tüm **geçerli ve kapalı** eşleme kurallarının kümesini oluşturur. Kümenin eleman sayısı arttıkça, bu olası dizilimlerin sayısı da faktöriyel hızında büyüyerek devasa bir kombinatoryal uzay meydana getirir. 
Şimdi ufak bir örnekle simetrik grubun soyut yapısını somutlaştırıp, iki satırlı matris gösterimiyle permütasyon fonksiyonlarını inceleyelim.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Simetrik Grup ($S_6$) ve İki Satırlı Matris Gösterimi

  </div>

  Kümemiz $A = \{0, 1, 2, 3, 4, 5\}$ olsun. Bu küme üzerindeki tüm permütasyonlar **$S_6$** grubunu oluşturur ve grubun toplam eleman sayısı $|S_6| = 6! = 720$'dir. Bu gruptan rastgele bir $\pi$ permütasyon elemanını ayrık döngü (cycle) formunda şu şekilde tanımlayalım:
  
  $$\pi = (0\ 3\ 5)(1\ 4)(2)$$
  
  Bu permütasyon fonksiyonunun elemanları hangi sıra ile eşlediğini daha sistematik görmek için **iki satırlı matris gösterimi ($2 \times 6$ matris)** kullanılabilir. Bu gösterimde üst satıra kümenin orijinal elemanları sıralı yazılırken, alt satıra bu elemanların $\pi$ altındaki görüntüleri (hedefleri) yerleştirilir:

  $$\pi = \begin{pmatrix} 0 & 1 & 2 & 3 & 4 & 5 \\ 3 & 4 & 2 & 5 & 1 & 0 \end{pmatrix}$$

  Hem matris gösterimi hem de döngü tanımı üzerinden fonksiyonun değerleri şu şekilde elde edilir:
  * $\pi(0) = 3$ *(0 sayısı matriste altındaki 3'e, döngüde ise kendisinden hemen sonra gelen 3'e gider)*
  * $\pi(1) = 4$ *(1 sayısı matriste altındaki 4'e, döngüde ise kendisinden hemen sonra gelen 4'e gider)*
  * $\pi(2) = 2$ *(2 sayısı matriste kendisine eşlenir; tek elemanlı bir döngü olduğu için fonksiyon altında sabittir)*
  * $\pi(3) = 5$ *(3 sayısı matriste altındaki 5'e, döngüde ise kendisinden hemen sonra gelen 5'e gider)*
  * $\pi(4) = 1$ *(4 sayısı matriste altındaki 1'e, döngüde ise döngünün başına dönerek 1'e gider)*
  * $\pi(5) = 0$ *(5 sayısı matriste altındaki 0'a, döngüde ise döngünün başına dönerek 0'a gider)*
</div>

Simetrik grupların bu soyut matematiksel yapısı, klasik kriptolojide **yerine koyma (substitution)** şifrelerinin temel direğidir. Alfabedeki her bir harfi matematiksel birer sayısal indeks ile eşleştirdiğimizde, bir metni şifrelemek aslında o alfabenin küme elemanlarını rastgele seçilmiş bir $\pi$ permütasyon fonksiyonuyla karıştırmaktan ibarettir. 

Şifreleme adımlarının güvenli, benzersiz ve tamamen geri döndürülebilir (deşifre edilebilir) olabilmesi için seçilen fonksiyonun dönüştürülebilir bir yapıya, yani simetrik grubun bir elemanına karşılık gelmesi şarttır. Eğer fonksiyon birebir ve örten olmazsa, birden fazla harf aynı şifreli karaktere eşleneceği için geriye dönük benzersiz bir deşifre anahtarı ($\pi^{-1}$) üretilemez. Şimdi bu soyut cebirsel modeli formel bir kriptosistem anatomisine dökelim.

## Yerine Koyma (Substitution) Şifrelemesinin Formal Tanımı

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Alfabe Permütasyonu Kriptosistemi

  </div>
  
  İngiliz alfabesi üzerinde ($\mathbb{Z}_{26}$) çalıştığımızı varsayarsak, 5 bileşenli kriptosistem anatomisi şu şekilde tanımlanır:

  * **Açık Metin ($\mathcal{P}$):** Elemanları $\mathbb{Z}_{26} = \{0, 1, 2, \dots, 25\}$ kümesinden seçilen karakter dizileridir.
  * **Şifreli Metin ($\mathcal{C}$):** Elemanları $\mathbb{Z}_{26}$ kümesinden seçilen karakter dizileridir.
  * **Anahtar Uzayı ($\mathcal{K}$):** $\mathbb{Z}_{26}$ kümesi üzerindeki tüm olası permütasyonların oluşturduğu **Simetrik Grup ($S_{26}$)** yapısıdır. 
  * **Şifreleme Fonksiyonu ($\mathcal{E}$):** Açık metindeki her bir $\tau$. karakterin sayısal değeri $x_\tau$, seçilen $\pi$ permütasyon fonksiyonuna girdi olarak verilir:
    $$e_{\pi}(x_\tau) = \pi(x_\tau)$$
  * **Deşifreleme Fonksiyonu ($\mathcal{D}$):** Şifreli metindeki değeri çözmek için permütasyon fonksiyonunun tersi ($\pi^{-1}$) kullanılır:
    $$d_{\pi}(y_\tau) = \pi^{-1}(y_\tau)$$
</div>

## Anahtar Uzayı ve Güvenlik Analizi

Permütasyon tabanlı bu yerine koyma şifresinin anahtar uzayı, $\mathbb{Z}_{26}$ simetrik grubunun mertebesine eşittir. Toplam olası anahtar sayısı $26!$ işlemi ile hesaplanır:

$$|S_{26}| = 26! \approx 4.03 \times 10^{26}$$

Bu değer, modern AES-128 şifrelemesindeki anahtar sayısına ($2^{128} \approx 3.4 \times 10^{38}$) kıyasla küçük kalsa da, kaba kuvvet (**brute-force**) saldırıları için klasik dönemde aşılamaz bir büyüklükteydi. Ancak bu sistem, harflerin kimliğini statik bir şekilde değiştirdiği için doğal dilin istatistiksel yapısını gizleyemez. Bir metindeki 'E' harfinin frekansı neyse, onun şifreli karşılığının frekansı da aynı kalır. Bu yüzden **Frekans Analizi** yöntemiyle saniyeler içinde kırılabilir.

## Döngü Gösterimi (Cycle Notation) ve Sabit Elemanlar Kuralı

Soyut cebir derslerinde permütasyonlar genellikle hantal matris gösterimleri yerine **ayrık döngülerin çarpımı (product of disjoint cycles)** şeklinde yazılır. Bu notasyonda işlem yaparken unutulmaması gereken en hayati matematiksel kural şudur:

::: info 📌 Sabit Eleman Kuralı
Eğer alfabedeki bir sayı ($\mathbb{Z}_{26}$'nın bir elemanı) tanımlanan permütasyon döngüleri (cycles) içinde hiç yer almıyorsa, o eleman permütasyon altında sabit kalır ve **kendisine eşlenir** ($\pi(x) = x$).
:::

Aşağıdaki örneklerde, 26 harflik alfabenin tamamını kapsayan büyük bir permütasyon anahtarı tanımlanmış, ancak bazı sayılar döngüye bilerek dahil edilmeyerek bu kuralın nasıl çalıştığı gösterilmiştir.

## Çözümlü Uygulamalar

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $\mathbb{Z}_{26}$ alfabesi üzerinde tanımlı $\pi \in S_{26}$ permütasyon anahtarı ayrık döngüler formunda aşağıda verilmiştir. Bu anahtarı kullanarak "MATHS" açık metnini şifreleyiniz.
  
  $$\pi = (0\ 12\ 2\ 19)(1\ 5\ 8\ 20\ 24)(3\ 14\ 17)(4\ 7\ 11\ 22)$$

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **Çözüm:**
  
  Öncelikle "MATHS" açık metnindeki harflerin sayısal karşılıklarını ($x_\tau$) bulalım:
  * **M** $\rightarrow x_1 = 12$
  * **A** $\rightarrow x_2 = 0$
  * **T** $\rightarrow x_3 = 19$
  * **H** $\rightarrow x_4 = 7$
  * **S** $\rightarrow x_5 = 18$
  
  Şimdi şifreleme fonksiyonumuzu ($y_\tau = \pi(x_\tau)$) her bir değer için uygulayalım ve döngüdeki haritasını takip edelim:
  
  1. $\pi(12)$'yi bulalım: $(0\ 12\ 2\ 19)$ döngüsünde 12'den sonra 2 gelir.
     $$\pi(12) = 2 \implies \mathbf{C}$$
  
  2. $\pi(0)$'ı bulalım: Aynı döngüde 0'dan sonra 12 gelir.
     $$\pi(0) = 12 \implies \mathbf{M}$$
  
  3. $\pi(19)$'u bulalım: Döngünün son elemanı her zaman ilk elemana döner.
     $$\pi(19) = 0 \implies \mathbf{A}$$
  
  4. $\pi(7)$'yi bulalım: $(4\ 7\ 11\ 22)$ döngüsünde 7'den sonra 11 gelir.
     $$\pi(7) = 11 \implies \mathbf{L}$$
  
  5. $\pi(18)$'i bulalım: 18 sayısı tanımlanan hiçbir döngünün içinde yer **almamaktadır**. **Sabit eleman kuralı** gereği kendisine eşlenir.
     $$\pi(18) = 18 \implies \mathbf{S}$$
  
  **Sonuç:** `MATHS` açık metni, $\pi$ fonksiyonu altında `CMALS` olarak şifrelenir.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Aynı $\pi = (0\ 12\ 2\ 19)(1\ 5\ 8\ 20\ 24)(3\ 14\ 17)(4\ 7\ 11\ 22)$ permütasyon anahtarı kullanılarak şifrelenmiş olan "CMALS" kapalı metnini deşifre ediniz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **Çözüm:**
  
  Deşifreleme yapabilmek için permütasyonun tersini ($\pi^{-1}$) almalıyız. Döngü (cycle) notasyonunda bir permütasyonun tersini almak, döngünün içindeki elemanları **sondan başa doğru** tersten yazmaktır:
  
  $$\pi^{-1} = (19\ 2\ 12\ 0)(24\ 20\ 8\ 5\ 1)(17\ 14\ 3)(22\ 11\ 7\ 4)$$
  
  > **Not:** Döngü içinde yer almayan elemanlar ters permütasyonda da yine sabit kalır, yani kendilerine eşlenirler.
  
  Şifreli metnimiz "CMALS" harflerinin sayısal değerlerini ($y_\tau$) ters fonksiyona ($x_\tau = \pi^{-1}(y_\tau)$) sokalım:
  * **C** $\rightarrow y_1 = 2$
  * **M** $\rightarrow y_2 = 12$
  * **A** $\rightarrow y_3 = 0$
  * **L** $\rightarrow y_4 = 11$
  * **S** $\rightarrow y_5 = 18$
  
  Ters haritayı takip edelim:
  
  1. $\pi^{-1}(2)$'yi bulalım: $(19\ 2\ 12\ 0)$ döngüsünde 2'den sonra 12 gelir.
     $$\pi^{-1}(2) = 12 \implies \mathbf{M}$$
  
  2. $\pi^{-1}(12)$'yi bulalım: Aynı döngüde 12'den sonra 0 gelir.
     $$\pi^{-1}(12) = 0 \implies \mathbf{A}$$
  
  3. $\pi^{-1}(0)$'ı bulalım: Döngünün sonundan başına döneriz.
     $$\pi^{-1}(0) = 19 \implies \mathbf{T}$$
  
  4. $\pi^{-1}(11)$'i bulalım: $(22\ 11\ 7\ 4)$ döngüsünde 11'den sonra 7 gelir.
     $$\pi^{-1}(11) = 7 \implies \mathbf{H}$$
  
  5. $\pi^{-1}(18)$'i bulalım: 18 sayısı ters döngülerde de yoktur, dolayısıyla kendine eşlenir.
     $$\pi^{-1}(18) = 18 \implies \mathbf{S}$$
  
  **Sonuç:** Deşifreleme işlemi matematiksel olarak kusursuz çalışmış ve orijinal `MATHS` kelimesine ulaşılmıştır.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>