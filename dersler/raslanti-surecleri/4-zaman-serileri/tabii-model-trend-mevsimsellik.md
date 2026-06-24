# 📉 Zaman Serileri: Tabii Model, Trend ve Mevsimsellik

Zaman serisi, belirli zaman aralıklarında (gün, ay, yıl vb.) gözlemlenen ve kronolojik olarak sıralanmış veriler dizisidir. Geleceği tahmin etmek için karmaşık istatistiksel modellere geçmeden önce başvurulan en temel yaklaşım **Tabii Model (Naive Model)** yaklaşımıdır.

Tabii model, "gelecekteki değerin, doğrudan geçmişteki en son duruma veya belirli bir örüntüye eşit olacağını" varsayar. Bu modeli kurarken zaman serisinin içinde **Trend (Sürekli Eğilim)** veya **Mevsimsellik (Periyodik Dalgalanma)** olup olmadığı kesinlikle analiz edilmelidir.

---

## 1. Trend ve Mevsimsellik Yoksa (Sabit Model)

Zaman serisinde belirgin ve sürekli bir artış/azalış (trend) veya periyodik bir dalgalanma (mevsimsellik) yoksa, bir sonraki periyodun tahmini değeri, gerçekleşen son periyodun değerine eşittir.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Sabit Tabii Model

  </div>
  
  Zaman serisinde trend ve mevsimsellik gözlenmediğinde tahmini değer ($\hat{Y}$), bir önceki gerçek değere ($Y$) eşittir.
  
  $$\hat{Y}_{t+1} = Y_t$$
</div>

<br>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Aşağıda verilen zaman serisinde trend ve mevsimsellik bulunmamaktadır. Tabii model kullanarak tahmini değerleri ($\hat{Y}_t$) hesaplayınız.

  <div style="display: flex; justify-content: center;">

  | $t$ | $1$ | $2$ | $3$ | $4$ | $5$ |
  | :---: | :---: | :---: | :---: | :---: | :---: |
  | **$Y_t$** | $10$ | $15$ | $14$ | $13$ | $14$ |

  </div>

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  Modelimiz $\hat{Y}_{t+1} = Y_t$ olduğundan, her tahmini değer, kendisinden bir önceki gerçek değere eşit olacaktır. İlk periyot için geçmiş veri olmadığından tahmin yapılamaz.

  * $\hat{Y}_2 = Y_1 = 10$
  * $\hat{Y}_3 = Y_2 = 15$
  * $\hat{Y}_4 = Y_3 = 14$
  * $\hat{Y}_5 = Y_4 = 13$
  * $\hat{Y}_6 = Y_5 = 14 \quad$ *(Gelecek periyot tahmini)*

  <div style="display: flex; justify-content: center;">

  | $t$ | $Y_t$ | $\hat{Y}_t$ |
  | :---: | :---: | :---: |
  | $1$ | $10$ | - |
  | $2$ | $15$ | $10$ |
  | $3$ | $14$ | $15$ |
  | $4$ | $13$ | $14$ |
  | $5$ | $14$ | $13$ |
  | $6$ | - | $14$ |

  </div>
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

---

## 2. Sadece Trend Varsa

Eğer zaman serisinde zamanla istikrarlı bir şekilde büyüme ya da küçülme varsa, bu duruma **Trend** denir. Sabit model bu durumda yetersiz kalır çünkü sürekli artan bir seride, gelecekteki değerin dünkü değere eşit olmasını beklemek bizi daima eksik tahmine götürür.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Trend İçeren Tabii Model

  </div>
  
  Trend içeren bir seride tahmini değer; son gerçekleşen değere, son iki periyot arasındaki **değişim miktarının (trend payının)** eklenmesiyle bulunur.
  
  $$\hat{Y}_{t+1} = Y_t + (Y_t - Y_{t-1})$$
</div>

<br>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Aşağıda verilen ve istikrarlı bir artış (trend) sergileyen veri kümesi için tahmini değerleri bulunuz.

  <div style="display: flex; justify-content: center;">

  | $t$ | $1$ | $2$ | $3$ | $4$ | $5$ |
  | :---: | :---: | :---: | :---: | :---: | :---: |
  | **$Y_t$** | $6$ | $8$ | $11$ | $13$ | $15$ |

  </div>

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  Trend modeli $\hat{Y}_{t+1} = Y_t + (Y_t - Y_{t-1})$ formülünü kullanır. Tahmin yapabilmek için geriye dönük en az iki gerçek değere ihtiyacımız olduğundan, $t=1$ ve $t=2$ için tahmin yapılamaz. Hesaplamalar $t=3$'ten başlar:

  * $\hat{Y}_3 = Y_2 + (Y_2 - Y_1) = 8 + (8 - 6) = 10$
  * $\hat{Y}_4 = Y_3 + (Y_3 - Y_2) = 11 + (11 - 8) = 14$
  * $\hat{Y}_5 = Y_4 + (Y_4 - Y_3) = 13 + (13 - 11) = 15$
  * $\hat{Y}_6 = Y_5 + (Y_5 - Y_4) = 15 + (15 - 13) = 17 \quad$ *(Gelecek periyot tahmini)*

  <div style="display: flex; justify-content: center;">

  | $t$ | $Y_t$ | $\hat{Y}_t$ |
  | :---: | :---: | :---: |
  | $1$ | $6$ | - |
  | $2$ | $8$ | - |
  | $3$ | $11$ | $10$ |
  | $4$ | $13$ | $14$ |
  | $5$ | $15$ | $15$ |
  | $6$ | - | $17$ |

  </div>
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

---

## 3. Sadece Mevsimsellik Varsa

Eğer zaman serisinde belirli periyotlarla (örneğin her yılın aynı aylarında veya çeyreklerinde) bir düzenli dalgalanma varsa buna **Mevsimsellik** denir. Mevsimselliği tespit etmek için verilerin en az birkaç yıl arka arkaya karşılaştırılması gerekir.

Mevsimsel serilerde tahmini değer; bir önceki mevsime veya periyoda ait değil, **tam bir devir (yıl) önceki aynı mevsimin/periyodun** değerine eşit alınır. Örneğin, veriler $4$ çeyreklik ($s=4$) dönemler halinde veriliyorsa formülümüz:

$$\hat{Y}_{t+1} = Y_{t-3}$$

*(Sonraki tahmin, mevcut $t$'den 3 periyot geriye gidildiğinde, yani tam 4 periyot önceki aynı döneme ait gerçek değere eşitlenir.)*

<br>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Aşağıda bir işletmenin iki yıllık çeyreklik ($s=4$) veri seti verilmiştir. Verilerde yıllar geçtikçe belirgin bir büyüme (trend) yoktur, ancak her yılın aynı çeyreklerinde benzer satış dalgalanmaları (mevsimsellik) yaşanmaktadır. Tabii model kullanarak 3. yılın tüm çeyrekleri ($t=9, 10, 11, 12$) için tahmini değerleri bulunuz.

  <div style="display: flex; justify-content: center;">

  | Yıl | 1. Çeyrek | 2. Çeyrek | 3. Çeyrek | 4. Çeyrek |
  | :--- | :---: | :---: | :---: | :---: |
  | **1. Yıl** | $10 \; (Y_1)$ | $50 \; (Y_2)$ | $40 \; (Y_3)$ | $15 \; (Y_4)$ |
  | **2. Yıl** | $10 \; (Y_5)$ | $50 \; (Y_6)$ | $40 \; (Y_7)$ | $15 \; (Y_8)$ |

  </div>

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  Sadece mevsimsellik olduğu için, her çeyreğin tahmini değeri tam bir yıl (4 periyot) önceki aynı çeyreğin değerine eşit olacaktır ($\hat{Y}_{t+1} = Y_{t-3}$).

  Hesaplamalarımızı 3. yıl için yapalım:
  * 3. Yıl 1. Çeyrek ($t=9$): $\hat{Y}_9 = Y_5 = 10$
  * 3. Yıl 2. Çeyrek ($t=10$): $\hat{Y}_{10} = Y_6 = 50$
  * 3. Yıl 3. Çeyrek ($t=11$): $\hat{Y}_{11} = Y_7 = 40$
  * 3. Yıl 4. Çeyrek ($t=12$): $\hat{Y}_{12} = Y_8 = 15$

  Bunu bir tahmin tablosunda özetlersek:

  <div style="display: flex; justify-content: center;">

  | $t$ (3. Yıl) | Gerçekleşen ($Y_t$) | Tahmin Edilen ($\hat{Y}_t$) |
  | :---: | :---: | :---: |
  | $9$ (1. Çeyrek) | - | $10$ |
  | $10$ (2. Çeyrek) | - | $50$ |
  | $11$ (3. Çeyrek) | - | $40$ |
  | $12$ (4. Çeyrek) | - | $15$ |

  </div>
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

---

## 4. Hem Trend Hem Mevsimsellik Varsa

Zaman serisi hem periyodik dalgalanmalar gösteriyor hem de genel bir artış/azalış eğiliminde ilerliyorsa her iki etkiyi de formüle aynı anda dahil etmemiz gerekir.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Trend ve Mevsimsellik İçeren Tabii Model

  </div>
  
  Bu modelde tahmini değer; **tam bir devir önceki aynı dönemin** değerine, son devir (örneğin son 4 çeyrek) boyunca gerçekleşen **ortalama periyot trendinin** eklenmesiyle bulunur. Dönem sayısının 4 ($s=4$) olduğu varsayımıyla uzun formül:
  
  $$\hat{Y}_{t+1} = Y_{t-3} + \frac{(Y_t - Y_{t-1}) + (Y_{t-1} - Y_{t-2}) + (Y_{t-2} - Y_{t-3}) + (Y_{t-3} - Y_{t-4})}{4}$$

  Dikkat edilirse pay kısmındaki ara terimler matematiksel olarak birbirini götürür (teleskopik toplam) ve formül işlem kolaylığı sağlayan şu **en sade haline** dönüşür:

  $$\hat{Y}_{t+1} = Y_{t-3} + \frac{Y_t - Y_{t-4}}{4}$$
</div>

::: info 📌 Formülün Mantığı ve Sadeleşmesi
Pay kısmındaki uzun toplam işlemi aslında sondan başa doğru ardışık periyotlar arasındaki değişim (trend) miktarlarının toplanmasıdır. Matematiksel olarak ara değerler birbirini sıfırladığı için, geriye sadece **son gerçekleşen değer ($Y_t$) ile tam bir devir önceki değer ($Y_{t-4}$) arasındaki net fark** kalır. Bu net fark, periyot sayısına (4'e) bölünerek ortalama büyüme/küçülme adımı bulunur ve geçmişteki mevsimsel ana değere ($Y_{t-3}$) eklenerek tahmin yapılır.
:::

<br>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Aşağıdaki tabloda 3 yıla ait çeyreklik ($s=4$) veriler ($Y_t$) sırasıyla verilmiştir. Veriler incelendiğinde her yılın kendi içinde periyodik bir dalgalanma (mevsimsellik) ve yıllar geçtikçe sürekli bir artış (trend) olduğu görülmektedir. Buna göre 2003 yılının ilk periyodu ($t=13$) için tahmini değeri ($\hat{Y}_{13}$) bulunuz.

  <div style="display: flex; justify-content: center;">

  | Yıl \ Çeyrek | 1. Çeyrek | 2. Çeyrek | 3. Çeyrek | 4. Çeyrek |
  | :--- | :---: | :---: | :---: | :---: |
  | **2000** | $10 \; (Y_1)$ | $20 \; (Y_2)$ | $15 \; (Y_3)$ | $17 \; (Y_4)$ |
  | **2001** | $18 \; (Y_5)$ | $29 \; (Y_6)$ | $21 \; (Y_7)$ | $22 \; (Y_8)$ |
  | **2002** | $25 \; (Y_9)$ | $30 \; (Y_{10})$ | $33 \; (Y_{11})$ | $34 \; (Y_{12})$ |

  </div>

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  Bizden istenen değer $t=13$ (2003'ün ilk çeyreği) tahminidir. Formülümüzde $\hat{Y}_{t+1}$ ifadesi bulunduğundan, $t+1=13$ için formülü $t=12$ referansına göre kurmalıyız.

  Hem mevsimsellik hem trend içeren **sadeleştirilmiş** formülümüzü (4 dönemli) kullanalım:
  $$\hat{Y}_{13} = Y_9 + \frac{Y_{12} - Y_8}{4}$$

  *(Buradaki $Y_9$ değeri tam bir yıl yani 4 periyot önceki 2002 yılının 1. çeyrek değeridir.)*
  
  Tablodan gerekli gerçek değerleri ($Y_t$) yerine koyalım:
  * $Y_{12} = 34$
  * $Y_9 = 25$
  * $Y_8 = 22$

  Hesaplamayı yapalım:
  
  $$ 
  \begin{aligned}
  \hat{Y}_{13} &= 25 + \frac{34 - 22}{4} \\[10pt]
  \hat{Y}_{13} &= 25 + \frac{12}{4} \\[10pt]
  \hat{Y}_{13} &= 25 + 3 = \mathbf{28}
  \end{aligned} 
  $$

  **Sonuç:** Uzun uzun ara farkları bulmaya gerek kalmadan, doğrudan sadeleşmiş formül üzerinden 2003 yılının ilk çeyreği için tabii model tahmini $\hat{Y}_{13} = 28$ olarak bulunmuştur.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>