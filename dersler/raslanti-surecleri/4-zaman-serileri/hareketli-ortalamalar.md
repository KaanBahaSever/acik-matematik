# 📉 Zaman Serileri: Hareketli Ortalamalar Metodu (HOM)

Zaman serilerinde bazen veriler rastgele ve anlık dalgalanmalar (gürültü) gösterir. Bu anlık zıplamaları veya düşüşleri yumuşatıp serinin asıl gidişatını (ana eğilimi) görmek için **Hareketli Ortalamalar Metodu (Moving Averages)** kullanılır. Bu yöntemin temel mantığı, geçmişteki belirli sayıda ($n$) periyodun ortalamasını alarak geleceği tahmin etmektir. 

Zaman serisinde trend (istikrarlı büyüme/küçülme) olup olmamasına göre bu yöntem ikiye ayrılır: **Tek Katlı** ve **İki Katlı** hareketli ortalamalar.

---

## 1. Tek Katlı Hareketli Ortalamalar (Trend Yoksa)

Eğer verilerde zamanla sürekli artan veya azalan bir trend yoksa, sadece geçmiş $n$ dönemin basit aritmetik ortalaması alınarak bir sonraki periyot tahmin edilir. Zaman ilerledikçe en eski veri hesaplamadan çıkarılır ve en yeni veri dahil edilir; bu yüzden ortalama "hareket eder".

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Tek Katlı Hareketli Ortalama ($\mu_t$)

  </div>
  
  $n$ periyotluk tek katlı hareketli ortalama ($\mu_t$), $t$ zamanı dahil olmak üzere geçmiş $n$ adet gerçek değerin ortalamasıdır:
  
  $$\mu_t = \frac{Y_t + Y_{t-1} + Y_{t-2} + \dots + Y_{t-n+1}}{n}$$

  Bir sonraki periyodun tahmini değeri ($\hat{Y}_{t+1}$), hesaplanan bu ortalamaya eşittir:
  $$\hat{Y}_{t+1} = \mu_t$$

  Burada;
  * **$n$**: Hareketli ortalamanın hesaplanacağı geçmiş periyot sayısını (örneğin 3 aylık, 5 yıllık vb.) ifade eder.
</div>

::: info 📌 Formül Hatasına Dikkat! (İndis Kuralı)
Bazı ders notlarında formülün pay kısmında $Y_{t+1}$ (gelecek zaman) ifadesinin yer aldığı hatalı yazımlar görebilirsiniz. Bir model, geleceği tahmin etmek için gelecekteki veriyi kullanamaz. Doğru hesaplama, içinde bulunduğumuz $t$ anından geriye doğru giderek ($Y_t, Y_{t-1}$ vb.) tam $n$ adet terimi toplamaktır.
:::

<br>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Tek Katlı Hareketli Ortalama Çözümü

  </div>

  Aşağıdaki zaman serisi için $3$ aylık ($n=3$) tek katlı hareketli ortalamaları hesaplayarak $6.$ ay için tahmini değeri ($\hat{Y}_6$) bulunuz.

  <div style="display: flex; justify-content: center;">

  | $t$ (Ay) | $1$ | $2$ | $3$ | $4$ | $5$ |
  | :---: | :---: | :---: | :---: | :---: | :---: |
  | **$Y_t$** | $12$ | $15$ | $18$ | $14$ | $16$ |

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  Periyot sayımız $n=3$ olduğu için ortalama almaya ancak 3. aydan ($t=3$) itibaren başlayabiliriz. Hesaplamalarımızı adım adım yaparak bir tabloya yerleştirelim:

  * **$t=3$ için:** $\mu_3 = \frac{12 + 15 + 18}{3} = \mathbf{15.00}$ $\implies$ $\hat{Y}_4 = 15.00$
  * **$t=4$ için:** $\mu_4 = \frac{15 + 18 + 14}{3} \approx \mathbf{15.67}$ $\implies$ $\hat{Y}_5 = 15.67$
  * **$t=5$ için:** $\mu_5 = \frac{18 + 14 + 16}{3} = \mathbf{16.00}$ $\implies$ $\hat{Y}_6 = 16.00$

  <div style="display: flex; justify-content: center;">

  | $t$ | $Y_t$ | $\mu_t$ (Hareketli Ortalama) | $\hat{Y}_t$ (Tahmin Edilen) |
  | :---: | :---: | :---: | :---: |
  | $1$ | $12$ | - | - |
  | $2$ | $15$ | - | - |
  | $3$ | $18$ | $15.00$ | - |
  | $4$ | $14$ | $15.67$ | $15.00$ |
  | $5$ | $16$ | $16.00$ | $15.67$ |
  | $6$ | - | - | $\mathbf{16.00}$ |

  </div>

  **Sonuç:** 5. aydaki ortalama değeri kullanarak 6. ayın tahmini değerini **$\hat{Y}_6 = 16.00$** olarak buluruz.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

---

## 2. İki Katlı Hareketli Ortalamalar (Trend Varsa)

Verilerde sürekli bir artış veya azalış (trend) varken tek katlı ortalama kullanırsak, tahminlerimiz her zaman gerçek değerlerin gerisinde (altında) kalacaktır. Trendi yakalamak için **hareketli ortalamanın da hareketli ortalamasını** alır ve bunu doğrusal bir doğru denklemine çeviririz.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: İki Katlı Hareketli Ortalama Formülleri

  </div>
  
  İki katlı metot uygulanırken sırasıyla 4 aşamalı bir matematiksel model kurulur:

  **1. Birinci Ortalama ($\mu_t$):** Standart tek katlı ortalamadır.
  $$\mu_t = \frac{Y_t + Y_{t-1} + \dots + Y_{t-n+1}}{n}$$

  **2. İkinci Ortalama ($\mu'_t$):** Bulunan birinci ortalamaların kendi içindeki ortalamasıdır.
  $$\mu'_t = \frac{\mu_t + \mu_{t-1} + \dots + \mu_{t-n+1}}{n}$$

  **3. Düzeltme Katsayıları ($a_t$ ve $b_t$):** Gecikmeyi telafi eden doğru denklemi bileşenleridir.
  * Sabit Terim (Kesim): $a_t = 2\mu_t - \mu'_t$
  * Eğim (Trend Hızı): $b_t = \frac{2}{n-1}(\mu_t - \mu'_t)$

  **4. Tahmin Denklemi:** $t$ anında dururken, $p$ periyot sonrası için yapılacak tahmin formülüdür.
  $$\hat{Y}_{t+p} = a_t + p \cdot b_t$$

  Burada;
  * **$n$**: Hareketli ortalamanın hesaplanacağı periyot sayısını (örneğin 3 aylık, 5 yıllık),
  * **$p$**: Bulunduğumuz $t$ anından kaç periyot sonrasını tahmin etmek istediğimizi ifade eder.
</div>

<br>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: İki Katlı Hareketli Ortalama Çözümü

  </div>

  Aşağıda belirgin bir yükseliş trendi gösteren veriler için $3$ aylık ($n=3$) hareketli ortalama periyodu kullanarak; $6.$ ve $7.$ aylar için tahmini değerleri ($\hat{Y}_6$ ve $\hat{Y}_7$) hesaplayınız.

  <div style="display: flex; justify-content: center;">

  | $t$ | $1$ | $2$ | $3$ | $4$ | $5$ |
  | :---: | :---: | :---: | :---: | :---: | :---: |
  | **$Y_t$** | $10$ | $14$ | $21$ | $29$ | $34$ |

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  Tahmin yapabilmek için en son an olan $t=5$ periyodu için düzeltme katsayılarını ($a_5$ ve $b_5$) bulmamız gerekir. Tüm adımları tablo üzerinde gösterebiliriz:

  1. **Birinci Ortalamalar ($\mu_t$):** $n=3$ ile $t=3$'ten itibaren hesaplanır. 
  2. **İkinci Ortalamalar ($\mu'_t$):** Elimizde $3$ adet $\mu_t$ biriktiğinde (yani $t=5$ anında) $\mu'_5 = \frac{15 + 21.33 + 28}{3} \approx 21.44$ olarak bulunur.

  <div style="display: flex; justify-content: center;">

  | $t$ | $Y_t$ | $\mu_t$ (1. Ortalama) | $\mu'_t$ (2. Ortalama) | $a_t$ | $b_t$ |
  | :---: | :---: | :---: | :---: | :---: | :---: |
  | $1$ | $10$ | - | - | - | - |
  | $2$ | $14$ | - | - | - | - |
  | $3$ | $21$ | $15.00$ | - | - | - |
  | $4$ | $29$ | $21.33$ | - | - | - |
  | $5$ | $34$ | $28.00$ | $21.44$ | **$34.56$** | **$6.56$** |

  </div>

  **3. Düzeltme Katsayılarının ($a_5$ ve $b_5$) Hesaplanması:**
  Formülleri doğrudan tabloda bulduğumuz $t=5$ değerleriyle uyguluyoruz:
  * $a_5 = 2\mu_5 - \mu'_5 = 2(28) - 21.44 = 56 - 21.44 = \mathbf{34.56}$
  * $b_5 = \frac{2}{n-1}(\mu_5 - \mu'_5) = \frac{2}{3-1}(28 - 21.44) = \frac{2}{2}(6.56) = \mathbf{6.56}$

  **4. Gelecek Periyotların Tahmini:**
  Tahmin denklemimiz $\hat{Y}_{5+p} = a_5 + p \cdot b_5$ olarak şekillendi.

  * **6. ayın tahmini ($p=1$):**
    $\hat{Y}_{5+1} = \hat{Y}_6 = 34.56 + 1 \cdot (6.56) = \mathbf{41.12}$

  * **7. ayın tahmini ($p=2$):**
    $\hat{Y}_{5+2} = \hat{Y}_7 = 34.56 + 2 \cdot (6.56) = \mathbf{47.68}$

  *(Dikkat ederseniz trend eğilimi korundu ve gelecek aylardaki tahminler de düzenli bir şekilde artmaya devam etti.)*
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>