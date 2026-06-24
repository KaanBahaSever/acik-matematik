# 📈 Lineer Hale Dönüştürülebilir Modeller

Regresyon analizinde, bağımlı ($Y$) ve bağımsız ($X$) değişkenler arasındaki ilişki her zaman $Y = \beta_0 + \beta_1 X$ gibi dümdüz bir doğru (lineer) şeklinde olmak zorunda değildir. Bazen veriler bir eğri çizerek üstel, logaritmik veya üslü bir şekilde artış/azalış gösterebilir.

Eğrisel bir ilişkiyi modellemek için En Küçük Kareler (EKK) yöntemini doğrudan uygulamaya kalkarsak, çözümü çok zor olan karmaşık denklem sistemleriyle karşılaşırız. Bunun yerine harika bir matematiksel hile yaparız: **Orijinal denklemi logaritma veya ters alma gibi işlemlerle doğrusal (lineer) bir formata dönüştürürüz.**

::: info 📌 Dönüşümün Temel Mantığı
Eğrisel bir modeli çözebilmek için değişkenleri ($Y$ veya $X$) yeni bir isme (örneğin $Y^*$ ve $X^*$) atayarak modeli $Y^* = A + B X^*$ formatına getiririz. Artık denklem lineer olduğu için bildiğimiz standart regresyon işlemlerini (Gauss Denklemlerini) bu **yeni yıldızlı değişkenler** üzerinden rahatça çözebiliriz. İşlem bitince de ters dönüşüm yaparak orijinal katsayılarımıza geri döneriz.
:::

---

## Sık Kullanılan Matematiksel Dönüşümler

Aşağıdaki dönüşüm modelleri, istatistiksel analizlerde en sık karşılaştığımız lineer olmayan (non-lineer) yapılardır.

### 1. Üstel (Exponential) Model

Verilerin başlangıçta yavaş, sonra aniden hızlanarak arttığı durumlarda kullanılır. Modelin doğrusallaştırılabilmesi için her iki tarafın doğal logaritması ($\ln$) alınır.

::: tip 🟢 Modelin Doğrusallaştırılması
**Genel Denklem:**
$$\Large Y = c \cdot e^{aX}$$

**Dönüşüm Adımları:**
$$\ln(Y) = \ln(c \cdot e^{aX})$$
$$\ln(Y) = \ln(c) + \ln(e^{aX})$$
$$\ln(Y) = \ln(c) + aX$$

**Lineer Format:** $Y^* = \ln(Y)$ ve $c^* = \ln(c)$ dersek, denklemimiz bildiğimiz doğrusal formata dönüşür:
$$Y^* = c^* + aX$$
:::

### 2. Üslü (Power) Model

Bağımsız değişkenin de bir üs olarak değil, taban olarak yer aldığı modeldir. Bu modeli doğrusallaştırmak için her iki tarafın 10 tabanında logaritması ($\log$) alınır.

::: tip 🟢 Modelin Doğrusallaştırılması
**Genel Denklem:**
$$\Large Y = a_1 \cdot X^{a_2}$$

**Dönüşüm Adımları:**
$$\log(Y) = \log(a_1 \cdot X^{a_2})$$
$$\log(Y) = \log(a_1) + a_2 \log(X)$$

**Lineer Format:** $Y^* = \log(Y)$, $a_1^* = \log(a_1)$ ve $X^* = \log(X)$ dersek modelimiz lineerleşir:
$$Y^* = a_1^* + a_2 X^*$$
:::

### 3. Rasyonel (Ters) Model

Bağımlı ve bağımsız değişkenlerin bir kesir (oran) ilişkisi içinde olduğu modeldir. Doğrusallaştırmak için eşitliğin her iki tarafının çarpmaya göre tersi alınır.

::: tip 🟢 Modelin Doğrusallaştırılması
**Genel Denklem:**
$$\Large Y = \frac{a_1 X}{b_1 + X}$$

**Dönüşüm Adımları:**
$$\frac{1}{Y} = \frac{b_1 + X}{a_1 X}$$
$$\frac{1}{Y} = \frac{b_1}{a_1 X} + \frac{X}{a_1 X}$$
$$\frac{1}{Y} = \left(\frac{b_1}{a_1}\right)\frac{1}{X} + \frac{1}{a_1}$$

**Lineer Format:** $Y^* = \frac{1}{Y}$ ve $X^* = \frac{1}{X}$ dersek denklem lineerleşir:
$$Y^* = C \cdot X^* + D \quad \text{(Burada } C = \frac{b_1}{a_1} \text{ ve } D = \frac{1}{a_1} \text{ )}$$
:::

---

## ⚙️ Adım Adım Çözüm Algoritması: Üstel Model Örneği

Dönüştürülebilir modellerde EKK (Gauss) denklemleri ile çalışırken şu adımları izleriz:

1. **Modeli Dönüştür:** Soruda verilen modeli logaritma veya ters alma işlemiyle $Y^* = c^* + aX^*$ formatına getir.
2. **Tabloyu Güncelle:** Verilen orijinal değerleri değil, bunların dönüştürülmüş hali olan yıldızlı ($^*$) değerleri hesaplayarak yeni bir tablo oluştur.
3. **Gauss Denklemlerini Yaz:** Yıldızlı değişkenlere göre normal denklemleri (EKK) oluştur.
4. **Denklemi Çöz:** Tablodaki toplamları yerlerine koyup bilinmeyen katsayıları bul.
5. **Orijinal Formata Dön:** Bulduğun geçici katsayıları ters işlemle asıl aranan sabitlere çevir ve modeli yaz.

<br>

### 📝 Örnekler

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Aşağıdaki verilere en uygun $\hat{Y} = c \cdot e^{aX}$ üstel regresyon eğrisini, En Küçük Kareler (EKK) yöntemini kullanarak uydurunuz.

  <div style="display: flex; justify-content: center;">

  | $\mathbf{X}$ | $0$ | $1$ | $2$ | $3$ | $4$ |
  | :--- | :--- | :--- | :--- | :--- | :--- |
  | $\mathbf{Y}$ | $1.5$ | $2.5$ | $3.5$ | $5.0$ | $7.5$ |

  </div>

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **1. Modelin Lineerleştirilmesi:**
  $Y = c \cdot e^{aX}$ denkleminin iki tarafının $\ln$'ini alıyoruz:
  $\ln(Y) = \ln(c) + aX \implies Y^* = c^* + aX$

  **2. Tablonun Oluşturulması ($n=5$):**
  Hesaplamalarımızda $Y$ yerine dönüştürülmüş değişken olan $Y^* = \ln(Y)$ kullanacağız. *(İşlemler virgülden sonra 5 basamaklı alınmıştır.)*

  <div style="display: flex; justify-content: center;">

  | $X_i$ | $Y_i$ | $Y^*_i = \ln(Y_i)$ | $X_i^2$ | $X_i \cdot Y^*_i$ |
  | :--- | :--- | :--- | :--- | :--- |
  | 0 | 1.5 | 0.40547 | 0 | 0.00000 |
  | 1 | 2.5 | 0.91629 | 1 | 0.91629 |
  | 2 | 3.5 | 1.25276 | 4 | 2.50552 |
  | 3 | 5.0 | 1.60944 | 9 | 4.82832 |
  | 4 | 7.5 | 2.01490 | 16 | 8.05960 |
  | **$\sum X_i = 10$** | | **$\sum Y^*_i = 6.19886$** | **$\sum X_i^2 = 30$** | **$\sum X_i Y^*_i = 16.30973$** |

  </div>

  **3. Gauss Normal Denklemlerinin Kurulması:**
  Doğrusal formumuz olan $Y^* = c^* + aX$ için normal denklemler:

  1) $\sum Y^*_i = n c^* + a \sum X_i \implies 6.19886 = 5 c^* + 10 a$
  2) $\sum X_i Y^*_i = c^* \sum X_i + a \sum X_i^2 \implies 16.30973 = 10 c^* + 30 a$

  **4. Denklemin Çözülmesi:**
  Birinci denklemi $-2$ ile çarpıp ikinci denkleme ekleyelim ki $c^*$'lar yok olsun:
  $(-2) \cdot (6.19886) = -12.39772 = -10 c^* - 20 a$
  $16.30973 = 10 c^* + 30 a$

  Taraf tarafa topladığımızda:
  $3.91201 = 10 a \implies \mathbf{a = 0.391201}$

  Bulduğumuz $a$'yı birinci denklemde yerine koyalım:
  $6.19886 = 5 c^* + 10(0.391201)$
  $6.19886 = 5 c^* + 3.91201 \implies 5 c^* = 2.28685 \implies \mathbf{c^* = 0.45737}$

  **5. Orijinal Katsayıya Dönüş:**
  $c^* = \ln(c)$ demiştik. O halde $c$'yi bulmak için ters işlem uygulayarak $e$'nin üssüne almalıyız:
  $c = e^{c^*} = e^{0.45737} \implies \mathbf{c = 1.5799}$

  **Sonuç:**
  Elde ettiğimiz değerleri orijinal üstel denklemde ($Y = c \cdot e^{aX}$) yerine koyarsak, regresyon modelimiz şu şekilde olur:
  $$\Large \hat{Y} = 1.5799 \cdot e^{0.3912 X}$$
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>
