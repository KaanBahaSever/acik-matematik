# 📉 Zaman Serileri: Otokorelasyon ve Tahmin Hataları

Zaman serisi analizlerinde, elimizdeki verinin geçmiş değerlerden ne kadar etkilendiğini anlamak ve kurduğumuz tahmin modellerinin (regresyon, hareketli ortalamalar vb.) ne kadar başarılı olduğunu ölçmek zorundayız. Bu bölümde, verinin kendi geçmişiyle olan ilişkisini ölçen **otokorelasyon** kavramını ve modellerimizin performansını test ettiğimiz **hata ölçütlerini** inceleyeceğiz.

---

## 1. Otokorelasyon Kavramı

Bir değişkenin farklı iki değişkene göre değil, **kendi geçmiş (gecikmeli) değerlerine göre** gösterdiği ilişkiye **otokorelasyon** denir. Örneğin, "Dünkü hava sıcaklığı bugünkü sıcaklığı etkiliyor mu?" veya "Geçen ayki satışlar, bu ayki satışların bir göstergesi mi?" sorularının matematiksel cevabını bu yöntemle ararız.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: $k$. Dereceden Otokorelasyon Katsayısı ($r_k$)

  </div>
  
  $Y_0, Y_1, \dots, Y_n$ şeklinde $0$'dan başlayan bir zaman serisinde, $t$ zamanındaki değer ($Y_t$) ile $k$ periyot önceki gecikmeli değer ($Y_{t-k}$) arasındaki doğrusal ilişkinin yönünü ve gücünü ölçen katsayıdır. $-1$ ile $+1$ arasında değerler alır.
  
  $$r_k = \frac{\sum_{t=k}^{n} (Y_t - \bar{Y})(Y_{t-k} - \bar{Y})}{\sum_{t=0}^{n} (Y_t - \bar{Y})^2}$$

  Burada;
  * $n$: Serideki son zaman indeksini (Toplam veri sayısı $n+1$'dir),
  * $k$: Gecikme periyodunu (1. dereceden ise $k=1$, 2. dereceden ise $k=2$),
  * $\bar{Y}$: Serinin aritmetik ortalamasını ifade eder.
</div>

::: info 📌 İndis Kuralı ve Başlangıç Noktası
Zaman serisi $t=0$'dan başladığı için, gecikmeli terim $Y_{t-k}$'nın hesaplanabilmesi adına pay kısmındaki toplam işlemi kesinlikle **$t=k$**'dan başlamalıdır (Çünkü $t-k \ge 0 \implies t \ge k$).
:::

---

## 2. Tahmin Hatalarının Ölçülmesi

Bir tahmin modeli kurduğumuzda, modelin ürettiği beklenen değerler ($\hat{Y}_t$) ile ölçülen gerçek değerler ($Y_t$) arasındaki farka **tahmin hatası ($e_t$)** denir:

$$e_t = Y_t - \hat{Y}_t$$

Modelimizin performansını değerlendirmek için pozitif ve negatif hataların birbirini sıfırlamasını engelleyen dört temel hata ölçütü kullanılır. Serimiz $t=0$'dan $t=n$'e kadar olduğu için toplam veri sayısı **$n+1$**'dir:

### 2.1. Ortalama Mutlak Sapma (MAD)

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: MAD (Mean Absolute Deviation)

  </div>
  
  Hataların mutlak değerlerinin ortalamasıdır. Hataların yönünü göz ardı ederek, hedeften ortalama ne kadar saptığımızı gösterir.
  $$MAD = \frac{\sum_{t=0}^{n} |e_t|}{n+1}$$
</div>

### 2.2. Ortalama Kareli Hata (MSE)

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: MSE (Mean Squared Error)

  </div>
  
  Hataların karelerinin ortalamasıdır. Büyük hataların karesini alarak onları cezalandırdığı için, modeldeki aşırı sapmaları (aykırı değerleri) tespit etmede çok etkilidir.
  $$MSE = \frac{\sum_{t=0}^{n} e_t^2}{n+1}$$
</div>

### 2.3. Ortalama Yüzde Hata (MPE)

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: MPE (Mean Percentage Error)

  </div>
  
  Hataların, gerçek değere oranlarının ortalamasıdır. Mutlak değer kullanılmadığı için modelin sürekli fazla mı yoksa eksik mi tahmin yaptığını (taraf tutma durumunu) gösterir.
  $$MPE = \frac{\sum_{t=0}^{n} \left(\frac{e_t}{Y_t}\right)}{n+1}$$
</div>

### 2.4. Ortalama Mutlak Yüzde Hata (MAPE)

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: MAPE (Mean Absolute Percentage Error)

  </div>
  
  Mutlak hataların gerçek değerlere oranının ortalamasıdır. Sonucu yüzde (%) olarak verdiği için anlaşılması ve yorumlanması en kolay ölçüttür.
  $$MAPE = \frac{\sum_{t=0}^{n} \left| \frac{e_t}{Y_t} \right|}{n+1}$$
</div>

---

## ⚙️ Adım Adım Çözüm Algoritması

Hem otokorelasyon hem de hata ölçümleri tablolar yardımıyla adım adım çözülmelidir:

1. **Ortalamayı Bulun:** Otokorelasyon için tüm $Y_t$ gerçek değerlerinin aritmetik ortalamasını ($\bar{Y}$) hesaplayın.
2. **Sütunları Hazırlayın:** Hatalar için $e_t$, $|e_t|$, $e_t^2$, $\frac{e_t}{Y_t}$ ve $\left|\frac{e_t}{Y_t}\right|$ sütunlarını hesaplayıp tabloya yazın.
3. **Gecikmeli Seriyi Kaydırın:** Otokorelasyon hesabı için $Y_t$ değerlerini istenen $k$ periyodu kadar aşağı kaydırarak $Y_{t-k}$ sütununu oluşturun.
4. **Formülleri Uygulayın:** Tablodaki sütunların toplamlarını ($\sum$) alarak ilgili hata ve otokorelasyon formüllerinde yerine koyun.

<br>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Bir zaman serisine ait gerçekleşen değerler ($Y_t$) ve bir tahmin modeli kullanılarak elde edilen beklenen değerler ($\hat{Y}_t$) aşağıda verilmiştir. İndisin $t=0$'dan başladığını kabul ederek; bu veri seti için birinci dereceden otokorelasyon katsayısını ($r_1$) ve dört temel hata ölçütünü (MAD, MSE, MPE, MAPE) hesaplayınız.

  <div style="display: flex; justify-content: center;">

  | $t$ | $0$ | $1$ | $2$ | $3$ | $4$ |
  | :---: | :---: | :---: | :---: | :---: | :---: |
  | **$Y_t$** | $10$ | $12$ | $15$ | $14$ | $17$ |
  | **$\hat{Y}_t$** | $11$ | $11$ | $14$ | $16$ | $16$ |

  </div>

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **1. Hata Değerlerinin Tablolaştırılması:**
  Veriler $t=0, 1, 2, 3, 4$ aralığındadır. Yani $n=4$ ve toplam veri sayısı $n+1=5$'tir. $e_t = Y_t - \hat{Y}_t$ ile hataları hesaplıyoruz. *(Virgülden sonra 4 basamak alınmıştır).* sad

<div style="display: flex; justify-content: center;">

| $t$ | $Y_t$ | $\hat{Y}_t$ | $e_t$ | $\vert e_t \vert$ | $e_t^2$ | $e_t / Y_t$ | $\vert e_t \vert / Y_t$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $0$ | $10$ | $11$ | $-1$ | $1$ | $1$ | $-0.1000$ | $0.1000$ |
| $1$ | $12$ | $11$ | $1$ | $1$ | $1$ | $0.0833$ | $0.0833$ |
| $2$ | $15$ | $14$ | $1$ | $1$ | $1$ | $0.0667$ | $0.0667$ |
| $3$ | $14$ | $16$ | $-2$ | $2$ | $4$ | $-0.1429$ | $0.1429$ |
| $4$ | $17$ | $16$ | $1$ | $1$ | $1$ | $0.0588$ | $0.0588$ |
| **$\sum$** | - | - | **$0$** | **$6$** | **$8$** | **$-0.0341$** | **$0.4517$** |

</div>

  **2. Hata Ölçütlerinin Hesaplanması:**
  Veri sayımız $n+1 = 5$'tir. Tablodaki toplamları formüllere yerleştirelim:
  
  * **MAD** $= \frac{\sum |e_t|}{5} = \frac{6}{5} = \mathbf{1.2}$
  * **MSE** $= \frac{\sum e_t^2}{5} = \frac{8}{5} = \mathbf{1.6}$
  * **MPE** $= \frac{\sum (e_t/Y_t)}{5} = \frac{-0.0341}{5} = \mathbf{-0.0068} \quad (\text{Yani } -\%0.68)$
  * **MAPE** $= \frac{\sum (|e_t|/Y_t)}{5} = \frac{0.4517}{5} = \mathbf{0.0903} \quad (\text{Yani } \%9.03)$

  <br>

  **3. Birinci Dereceden Otokorelasyon ($r_1$) Hesabı:**
  İlk olarak gerçek değerlerin ortalamasını bulalım:
  $$\bar{Y} = \frac{10+12+15+14+17}{5} = \frac{68}{5} = 13.6$$

  $r_1$ formülündeki pay ve payda kısımları için hesaplamaları yapalım. Birinci dereceden olduğu için ($k=1$) gecikmeli çarpım işlemine $t=1$'den başlıyoruz.

  <div style="display: flex; justify-content: center;">

  | $t$ | $Y_t$ | $Y_t - \bar{Y}$ | $(Y_t - \bar{Y})^2$ | $(Y_t - \bar{Y})(Y_{t-1} - \bar{Y})$ |
  | :---: | :---: | :---: | :---: | :---: |
  | $0$ | $10$ | $-3.6$ | $12.96$ | - |
  | $1$ | $12$ | $-1.6$ | $2.56$ | $(-1.6) \cdot (-3.6) = 5.76$ |
  | $2$ | $15$ | $1.4$ | $1.96$ | $1.4 \cdot (-1.6) = -2.24$ |
  | $3$ | $14$ | $0.4$ | $0.16$ | $0.4 \cdot 1.4 = 0.56$ |
  | $4$ | $17$ | $3.4$ | $11.56$ | $3.4 \cdot 0.4 = 1.36$ |
  | **$\sum$** | **$68$** | **$0$** | **$29.2$** | **$5.44$** |

  </div>

  Bulduğumuz toplam değerleri $r_1$ formülünde yerine koyarsak:
  $$r_1 = \frac{\sum_{t=1}^{4} (Y_t - 13.6)(Y_{t-1} - 13.6)}{\sum_{t=0}^{4} (Y_t - 13.6)^2} = \frac{5.44}{29.2} \approx \mathbf{0.1863}$$

  **Yorum:** Zaman serisinde çok zayıf düzeyde pozitif bir otokorelasyon vardır. Geçmişteki bir periyodun gelecek üzerindeki etkisi istatistiksel olarak oldukça düşüktür.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>