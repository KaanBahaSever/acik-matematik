# 📈 Basit Regresyon

Gerçek hayatta birçok olay birbiriyle bağlantılıdır. Bir değişkenin değerinin, başka bir değişkenin veya değişkenlerin durumuna göre nasıl değiştiğini incelemek istatistiğin temel konularından biridir. İki değişken arasındaki ilişkileri genel olarak ikiye ayırırız:

1. **Fonksiyonel İlişki:** İki değişken arasındaki mutlak ve kesin matematiksel ilişkidir. Örneğin, bir karenin kenar uzunluğu ($x$) ile alanı ($Y$) arasındaki ilişki $Y = x^2$ şeklindedir ve istisnasız her zaman geçerlidir.
2. **İstatistiksel İlişki:** Kesin bir formülle ifade edilemeyen, aralarında bir eğilim (trend) bulunan ilişkidir. Örneğin, öğrencilerin çalışma süreleri ile sınav notları arasında bir ilişki vardır ama bu herkes için %100 aynı sonucu vermez. İşte regresyon analizi bu istatistiksel ilişkileri modellemek için kullanılır.

## Serpilme Diyagramları ve Korelasyon

İki değişken arasındaki istatistiksel ilişkinin görsel olarak incelenmesi için verilerin koordinat sistemine yerleştirilmesiyle elde edilen grafiğe **serpilme diyagramı (scatter plot)** denir. Noktaların dağılımına bakılarak ilişkinin varlığı, yönü ve kuvveti hakkında fikir sahibi olunur.

Bu görsel ilişkinin yönünü ve kuvvetini matematiksel olarak ölçen analize ise **Korelasyon** denir.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Pearson Korelasyon Katsayısı ($r$)

  </div>
  
  İki değişken arasındaki doğrusal ilişkinin şiddetini ve yönünü gösteren katsayıdır. $-1$ ile $+1$ arasında değerler alır ($-1 \le r \le 1$). 
  
  $$r = \frac{\sum_{i=1}^{n} (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{n} (x_i - \bar{x})^2 \sum_{i=1}^{n} (y_i - \bar{y})^2}}$$

  * **$r = 1$:** Mükemmel pozitif doğrusal ilişki (Biri artarken diğeri de aynı oranda artar).
  * **$r = -1$:** Mükemmel negatif doğrusal ilişki (Biri artarken diğeri aynı oranda azalır).
  * **$r = 0$:** İki değişken arasında hiçbir doğrusal ilişki yoktur.
</div>

Korelasyon bize *"Burada bir ilişki var mı ve ne kadar güçlü?"* sorusunun cevabını verirken; regresyon, *"Bu ilişkiyi matematiksel olarak hangi doğru denklemiyle modelleyebilirim?"* sorusuna yanıt verir.

## Basit Lineer Regresyon Modeli

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Regresyon Modeli

  </div>
  
  Bir bağımlı değişken ($Y$) ile tek bir bağımsız değişken ($X$) arasındaki doğrusal ilişkiyi modelleyen istatistiksel yaklaşımdır. Matematiksel ifadesi şu şekildedir:
  $$Y_i = \beta_0 + \beta_1 X_i + \epsilon_i$$
  
  Burada;
  * $Y_i$: Bağımlı değişken (Gözlem değeri)
  * $X_i$: Bağımsız değişken (Açıklayıcı değişken)
  * $\epsilon_i$: Hata terimi (Gerçek değer ile tahmin edilen değer arasındaki fark)
</div>

## En Küçük Kareler Yöntemi (EKK)

Gözlemlediğimiz veri noktalarından geçen sonsuz sayıda doğru çizebiliriz. Amacımız, noktaların içinden geçen ve eğilimi en iyi yansıtan "ideal" doğruyu bulmaktır. 

Bunun için tahminlerimiz ($\hat{Y}_i$) ile gerçek değerler ($Y_i$) arasındaki farkı (yani hatayı) minimize etmemiz gerekir:
$$e_i = Y_i - \hat{Y}_i = Y_i - (\beta_0 + \beta_1 x_i)$$

Hataların direkt toplamını almak yanıltıcıdır çünkü pozitif ve negatif sapmalar birbirini sıfırlayabilir. Bu sorunu aşmak için hataların **karelerinin toplamını** minimize eden optimum $\beta_0$ ve $\beta_1$ değerlerini ararız. 

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Gauss Normal Denklemleri ve EKK Katsayıları

  </div>
  
  Aradığımız en iyi doğru denklemi olan $\hat{Y} = \beta_0 + \beta_1 X$ modelini kurabilmek için, hata kareleri toplamı fonksiyonunu ($E$) minimum yapan katsayıları aşağıdaki formüllerle hesaplarız:
  
  $$\beta_1 = \frac{\sum_{i=1}^{n} (x_i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^{n} (x_i - \bar{x})^2} = \frac{n \sum_{i=1}^{n} x_i y_i - (\sum_{i=1}^{n} x_i)(\sum_{i=1}^{n} y_i)}{n \sum_{i=1}^{n} x_i^2 - (\sum_{i=1}^{n} x_i)^2}$$
  
  $$\beta_0 = \bar{y} - \beta_1 \bar{x}$$

  Burada;
  * **$n$**: Toplam gözlem (veri) sayısını,
  * **$\bar{x}$**: Bağımsız değişkenin ($X$) veri setindeki aritmetik ortalamasını,
  * **$\bar{y}$**: Bağımlı değişkenin ($Y$) veri setindeki aritmetik ortalamasını ifade eder.

  ::: details İspat: Bu Formüller Nereden Geliyor?
  Hata kareleri toplamı fonksiyonu, $\beta_0$ ve $\beta_1$'e bağlı iki değişkenli bir fonksiyondur:
  $$E(\beta_0, \beta_1) = \sum_{i=1}^{n} e_i^2 = \sum_{i=1}^{n} (y_i - \beta_0 - \beta_1 x_i)^2$$
  
  Çok değişkenli analizden (Calculus) biliyoruz ki; bir fonksiyonun minimum noktasını bulmak için, o fonksiyonun her bir değişkene göre kısmi türevini alıp sıfıra eşitlemeliyiz.
  
  **1. $\beta_0$'a (Sabit Terime) göre kısmi türev:**
  $$\frac{\partial E}{\partial \beta_0} = -2 \sum_{i=1}^{n} (y_i - \beta_0 - \beta_1 x_i) = 0$$
  Her iki tarafı $-2$'ye bölüp toplam sembolünü terimlere dağıttığımızda birinci normal denklemi elde ederiz:
  $$\sum y_i - n\beta_0 - \beta_1 \sum x_i = 0 \implies \sum y_i = n\beta_0 + \beta_1 \sum x_i \quad \text{(1. Normal Denklem)}$$
  
  **2. $\beta_1$'e (Eğime) göre kısmi türev:**
  Zincir kuralı gereği, içinin türevinden fazladan bir $-x_i$ çarpanı gelir:
  $$\frac{\partial E}{\partial \beta_1} = -2 \sum_{i=1}^{n} (y_i - \beta_0 - \beta_1 x_i)x_i = 0$$
  Yine $-2$'leri sadeleştirip $x_i$'yi içeri dağıtırsak ikinci normal denklemi elde ederiz:
  $$\sum x_i y_i - \beta_0 \sum x_i - \beta_1 \sum x_i^2 = 0 \implies \sum x_i y_i = \beta_0 \sum x_i + \beta_1 \sum x_i^2 \quad \text{(2. Normal Denklem)}$$
  
  Elde ettiğimiz bu iki bilinmeyenli ($\beta_0$ ve $\beta_1$) denklem sistemine **Gauss Normal Denklemleri** denir. Bu sistem yok etme veya yerine koyma metoduyla çözüldüğünde yukarıdaki $\beta_1$ ve $\beta_0$ formülleri ortaya çıkar.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

::: warning ⚠️ Kritik Uyarı: Farklı Modeller İçin Hazır Formüller Kullanılamaz!
Yukarıda ispatlayarak çıkardığımız $\beta_0$ ve $\beta_1$ hazır formülleri **sadece ve sadece** $Y = \beta_0 + \beta_1 X$ (yani $y = ax + b$) şeklindeki **basit doğrusal (lineer)** denklemler için geçerlidir. 

Eğer veriye $y = a x^2 + b$ (kuadratik) veya $y = c \cdot e^{ax}$ (üstel) gibi farklı formatta bir eğri uydurmamız istenirse, bu hazır formüller **kesinlikle kullanılamaz**. Böyle bir durumda, hata kareleri toplamı ($E$) fonksiyonunu istenen modele göre yeniden yazmalı, ilgili parametrelere göre kısmi türev alıp sıfıra eşitleyerek **kendi Gauss denklemlerimizi sıfırdan çıkarmalıyız**.
:::

---

## ⚙️ Adım Adım Çözüm Algoritması: Regresyon Doğrusunu Bulmak

Sınavlarda veya el hesaplamalarında en güvenilir yol bir tablo oluşturmaktır.

1. **Tabloyu Hazırlayın:** $X_i$ ve $Y_i$ değerlerini alt alta yazın.
2. **Ortalamaları Bulun:** $X$'lerin ortalamasını ($\bar{x}$) ve $Y$'lerin ortalamasını ($\bar{y}$) hesaplayın.
3. **Sapmaları Hesaplayın:** Her bir satır için $(x_i - \bar{x})$ ve $(y_i - \bar{y})$ değerlerini bulun.
4. **Çarpım ve Kareleri Alın:** Her satır için sapmaların çarpımını $(x_i - \bar{x})(y_i - \bar{y})$ ve $X$'in sapma karelerini $(x_i - \bar{x})^2$ hesaplayıp sütunları toplayın.
*(Dikkat ederseniz bu değerlerin aynısı yukarıdaki korelasyon formülünde de lazımdır!)*
5. **Katsayıları Yerine Koyun:** Önce $\beta_1$ formülünü, bulduğunuz $\beta_1$ değerini kullanarak da $\beta_0$ formülünü uygulayın.

<br>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Aşağıda verilen $X$ ve $Y$ değerleri için en küçük kareler yöntemini kullanarak tahmini regresyon doğrusunu ($\hat{Y}$) bulunuz.
  
  <div style="display: flex; justify-content: center;">

  | $X$ | $1$ | $2$ | $3$ | $4$ | $5$ |
  | :---: | :---: | :---: | :---: | :---: | :---: |
  | **$Y$** | $2$ | $4$ | $5$ | $4$ | $5$ |

  </div>

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  Öncelikle ortalamaları bulalım ($n=5$ veri noktası var):
  $\bar{x} = \frac{1+2+3+4+5}{5} = \frac{15}{5} = 3$
  $\bar{y} = \frac{2+4+5+4+5}{5} = \frac{20}{5} = 4$

  Tablomuzu oluşturalım:

  <div style="display: flex; justify-content: center;">

  | $X_i$ | $Y_i$ | $(x_i - \bar{x})$ | $(y_i - \bar{y})$ | $(x_i - \bar{x})(y_i - \bar{y})$ | $(x_i - \bar{x})^2$ |
  | :---: | :---: | :---: | :---: | :---: | :---: |
  | $1$ | $2$ | $-2$ | $-2$ | $4$ | $4$ |
  | $2$ | $4$ | $-1$ | $0$ | $0$ | $1$ |
  | $3$ | $5$ | $0$ | $1$ | $0$ | $0$ |
  | $4$ | $4$ | $1$ | $0$ | $0$ | $1$ |
  | $5$ | $5$ | $2$ | $1$ | $2$ | $4$ |
  | **Toplam**| | - | - | **$\sum = 6$** | **$\sum = 10$** |

  </div>

  Formülleri uygulayalım:
  $$\beta_1 = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2} = \frac{6}{10} = 0.6$$
  
  $$\beta_0 = \bar{y} - \beta_1 \bar{x} = 4 - (0.6 \times 3) = 4 - 1.8 = 2.2$$
  
  Tahmini regresyon doğrusu denklemimiz:
  $$\hat{Y} = 2.2 + 0.6X$$
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

---

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Bir laboratuvar deneyinde elde edilen $X$ ve $Y$ verileri aşağıda verilmiştir. Gauss Normal Denklemlerini kullanarak regresyon doğrusunu bulunuz.

  <div style="display: flex; justify-content: center;">

  | $X$ | $-1$ | $0$ | $1$ | $2$ | $3$ | $4$ | $5$ | $6$ |
  | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
  | **$Y$** | $10$ | $9$ | $7$ | $5$ | $4$ | $3$ | $0$ | $-1$ |

  </div>

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  Burada formülün diğer versiyonunu (Gauss Denklemlerini doğrudan çözmeyi) kullanalım. $n=8$ adet verimiz var. Gerekli toplamları bulalım:
  
  * $\sum X_i = (-1) + 0 + 1 + 2 + 3 + 4 + 5 + 6 = 20$
  * $\sum Y_i = 10 + 9 + 7 + 5 + 4 + 3 + 0 + (-1) = 37$
  * $\sum X_i^2 = 1 + 0 + 1 + 4 + 9 + 16 + 25 + 36 = 92$
  * $\sum X_i Y_i = (-10) + 0 + 7 + 10 + 12 + 12 + 0 + (-6) = 25$

  Normal denklemleri yazalım:
  1) $\sum y_i = n\beta_0 + \beta_1 \sum x_i \implies 37 = 8\beta_0 + 20\beta_1$
  2) $\sum x_i y_i = \beta_0 \sum x_i + \beta_1 \sum x_i^2 \implies 25 = 20\beta_0 + 92\beta_1$

  Bu iki denklemli sistemi çözelim. Birinci denklemi $-2.5$ ile çarparsak:
  $-92.5 = -20\beta_0 - 50\beta_1$
  
  İkinci denklem ile taraf tarafa toplayalım:
  $$(-92.5 + 25) = (-20\beta_0 + 20\beta_0) + (-50\beta_1 + 92\beta_1)$$
  $$-67.5 = 42\beta_1 \implies \beta_1 = -\frac{67.5}{42} \approx -1.607$$

  Bulduğumuz eğimi ilk denklemde yerine koyalım:
  $$37 = 8\beta_0 + 20(-1.607)$$
  $$37 = 8\beta_0 - 32.14 \implies 8\beta_0 = 69.14 \implies \beta_0 \approx 8.643$$

  **Sonuç:** Regresyon doğrumuz:
  $$\hat{Y} = 8.643 - 1.607X$$
  
  *(Not: $X$ değerleri artarken $Y$ değerlerinin sürekli düştüğüne dikkat edin. Bu yüzden eğim ($\beta_1$) negatif çıkmalıdır, pozitif çıkması matematiksel olarak imkansızdır.)*
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>