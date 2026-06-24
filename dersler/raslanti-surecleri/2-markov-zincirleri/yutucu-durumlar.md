# 🎲 Markov Zincirleri: Yutucu Matrisler ve Yutulma Olasılıkları

Bir Markov zincirinde, regüler (düzenli) sistemlerin aksine "nereden başlarsan başla dengeye ulaşırsın" mantığı her zaman geçerli değildir. Bazı durumlara girildiğinde, sistem bir daha asla o durumdan çıkamaz. Bu tür "geri dönüşü olmayan" durumlara sahip zincirlere **Yutucu Markov Zincirleri** denir.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Yutucu Durum ve Yutucu Zincir

  </div>
  
  Bir Markov zincirinde, $i$ durumundan çıkış olasılığı sıfır ise ($P_{ii} = 1$ ve diğer tüm $P_{ij} = 0$), bu $i$ durumuna **yutucu durum (absorbing state)** denir.
  
  Bir Markov zincirinin "yutucu zincir" olabilmesi için şu **iki şartı** aynı anda sağlaması gerekir:
  1. En az bir tane yutucu duruma sahip olmalıdır.
  2. Yutucu olmayan her bir durumdan (geçici durumlardan), eninde sonunda bir yutucu duruma ulaşmak mümkün olmalıdır.
</div>

---

## 1. Kanonik Form (Matrisin Yeniden Düzenlenmesi)

Yutucu bir Markov matrisinin geleceğini analiz etmek için, matrisi rastgele sırayla değil, belirli bir hiyerarşiye göre yeniden düzenlememiz gerekir. Tüm **Geçici (Transient)** durumları matrisin üstüne ve soluna, tüm **Yutucu (Absorbing)** durumları ise matrisin altına ve sağına taşıyarak elde ettiğimiz yapıya **Kanonik Form** denir.

<div class="math-block theorem">
  <div class="math-block-title">

  Kanonik Formun Yapısı

  </div>
  
  Kanonik forma getirilmiş bir $P$ geçiş olasılık matrisi, görsel ve matematiksel olarak $4$ farklı alt matrise bölünür:

  $$
  \Large
  P_{kanonik} = \left[ \begin{array}{c|c} 
  \color{#2563eb} Q & \color{#dc2626} R \\ 
  \hline 
  \color{#16a34a} 0 & \color{#9333ea} I 
  \end{array} \right] 
  $$
</div>

Bu bölümlerin anlamları şunlardır:
* **$\color{#2563eb} Q$ (Geçici $\to$ Geçici):** Geçici durumlardan yine geçici durumlara olan geçiş olasılıklarını barındıran kare alt matristir.
* **$\color{#dc2626} R$ (Geçici $\to$ Yutucu):** Geçici durumlardan yutucu durumlara (yani kapanlara) direkt geçiş olasılıklarını barındıran alt matristir.
* **$\color{#16a34a} 0$ (Yutucu $\to$ Geçici):** Yutucu bir durumdan tekrar geçici bir duruma dönmek imkansız olduğu için bu bölüm tamamen sıfırlardan oluşur.
* **$\color{#9333ea} I$ (Yutucu $\to$ Yutucu):** Yutucu duruma giren orada kalacağı için, bu bölüm sadece diyagonali $1$ olan bir birim matristir.

::: info 📌 Matris Nasıl Yeniden Sıralanır?
Bir matrisi kanonik forma sokarken rastgele yer değiştirme yapamayız. Bir $i$ durumunu $j$ durumu ile yer değiştireceksek; **önce $i$. satır ile $j$. satırı, ardından da $i$. sütun ile $j$. sütunu tamamen yer değiştirmeliyiz.** Yani durum isimleri (1, 2, 3...) matrisin hem üst (sütun) hem de sol (satır) kenarında mutlaka birebir aynı sırayla okunmalıdır.
:::

---

## 2. Temel Matris ve Yutulma Olasılıkları

Matrisi kanonik forma getirdikten sonra, sistemin analizini yapmak için o karmaşık lineer denklem sistemleri yerine doğrudan **Temel Matris ($N$)** kullanılır. 

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Temel Matris ($N$) ve Yutulma Matrisi ($B$)

  </div>
  
  **1. Temel Matris ($N$):** Sistemin yutulmadan önce geçici durumlarda ortalama kaç adım (zaman) geçireceğini gösterir ve şu formülle hesaplanır:
  $$N = (I - Q)^{-1}$$
  *(Buradaki $I$, $Q$ ile aynı boyutlara sahip birim matristir.)*

  **2. Yutulma Olasılıkları ($B$):** Herhangi bir geçici durumdan başlayan bir sürecin, nihai olarak hangi yutucu durumda sonlanacağının olasılıklarını verir. Temel matris ile $R$ matrisinin çarpımıyla bulunur:
  $$B = N \cdot R$$

  Bulunan bu $B$ matrisinin satırları **başlangıç (geçici) durumlarını**, sütunları ise **bitiş (yutucu) durumlarını** temsil eder.
</div>

---

## ⚙️ Adım Adım Çözüm Algoritması

1. **Durumları Sınıflandır:** Hangi durumlar geçici (T), hangi durumlar yutucu (A) tespit et.
2. **Kanonik Formu Kur:** Matrisin kenarlarına indekslerini yaz. Satır ve sütunları önce T, sonra A gelecek şekilde aynı anda yeniden sıralayarak $\color{#2563eb} Q$ ve $\color{#dc2626} R$ alt matrislerini elde et.
3. **Temel Matrisi Bul:** Önce $(I - Q)$ çıkarma işlemini yap, ardından bu matrisin tersini alarak $N = (I-Q)^{-1}$ matrisini bul.
4. **Çarpımı Gerçekleştir:** Son olarak $B = N \cdot R$ çarpımını yaparak tüm yutulma olasılıklarını tek bir matriste elde et.

<br>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: $6 \times 6$'lık Yutucu Matris Çözümü

  </div>

  Durum uzayı $M = \{1, 2, 3, 4, 5, 6\}$ olan bir Markov zincirine ait geçiş olasılık matrisi $P$ aşağıda verilmiştir. Sürecin **3 durumunda başlayıp, 2 durumunda yutulma olasılığını** bulunuz.

  $$
  P = \begin{bmatrix} 
  0 & 0.5 & 0 & 0.4 & 0.1 & 0 \\
  0 & 1 & 0 & 0 & 0 & 0 \\
  0.2 & 0 & 0.4 & 0.3 & 0 & 0.1 \\
  0 & 0.9 & 0 & 0 & 0.1 & 0 \\
  0 & 0 & 0 & 0 & 1 & 0 \\
  0 & 0 & 0 & 0 & 0 & 1 
  \end{bmatrix}
  $$

  ::: details 💡 Çözümü Göster / Gizle
  **1. Durumların Sınıflandırılması:**
  Matrisin diyagonaline baktığımızda $2, 5$ ve $6$ numaralı satırların sadece kendi üzerlerine ($P_{ii} = 1$) geçiş yaptığını, diğer yerlerin sıfır olduğunu görüyoruz.
  * Geçici Durumlar (T): $\{1, 3, 4\}$
  * Yutucu Durumlar (A): $\{2, 5, 6\}$

  **2. Kanonik Formun Oluşturulması:**
  Verilen matrisin kenarlarına $1$'den $6$'ya kadar olan indekslerini yazalım ve satır ile sütun sırasını önce T $\{1, 3, 4\}$, sonra A $\{2, 5, 6\}$ gelecek şekilde yeniden dizelim. (Örneğin 3. satırı komple alıp 2. sıraya taşıyor, ardından 3. sütunu komple alıp 2. sıraya taşıyoruz.) 
  
  Ortaya $\color{#2563eb} Q$, $\color{#dc2626} R$, $\color{#16a34a} 0$ ve $\color{#9333ea} I$ bloklarının net bir şekilde ayrıştığı şu kanonik form çıkıyor:

  $$
  P_{kanonik} = \begin{array}{c|ccc|ccc} 
  & \mathbf{1} & \mathbf{3} & \mathbf{4} & \mathbf{2} & \mathbf{5} & \mathbf{6} \\
  \hline
  \mathbf{1} & \color{#2563eb} 0 & \color{#2563eb} 0 & \color{#2563eb} 0.4 & \color{#dc2626} 0.5 & \color{#dc2626} 0.1 & \color{#dc2626} 0 \\
  \mathbf{3} & \color{#2563eb} 0.2 & \color{#2563eb} 0.4 & \color{#2563eb} 0.3 & \color{#dc2626} 0 & \color{#dc2626} 0 & \color{#dc2626} 0.1 \\
  \mathbf{4} & \color{#2563eb} 0 & \color{#2563eb} 0 & \color{#2563eb} 0 & \color{#dc2626} 0.9 & \color{#dc2626} 0.1 & \color{#dc2626} 0 \\
  \hline
  \mathbf{2} & \color{#16a34a} 0 & \color{#16a34a} 0 & \color{#16a34a} 0 & \color{#9333ea} 1 & \color{#9333ea} 0 & \color{#9333ea} 0 \\
  \mathbf{5} & \color{#16a34a} 0 & \color{#16a34a} 0 & \color{#16a34a} 0 & \color{#9333ea} 0 & \color{#9333ea} 1 & \color{#9333ea} 0 \\
  \mathbf{6} & \color{#16a34a} 0 & \color{#16a34a} 0 & \color{#16a34a} 0 & \color{#9333ea} 0 & \color{#9333ea} 0 & \color{#9333ea} 1 
  \end{array}
  $$

  Bu dizilimden bize lazım olan $Q$ ve $R$ matrislerini indeksleriyle birlikte çekelim:
  $$
  Q = \begin{array}{c|ccc} & \mathbf{1} & \mathbf{3} & \mathbf{4} \\ \hline \mathbf{1} & 0 & 0 & 0.4 \\ \mathbf{3} & 0.2 & 0.4 & 0.3 \\ \mathbf{4} & 0 & 0 & 0 \end{array} \quad \quad R = \begin{array}{c|ccc} & \mathbf{2} & \mathbf{5} & \mathbf{6} \\ \hline \mathbf{1} & 0.5 & 0.1 & 0 \\ \mathbf{3} & 0 & 0 & 0.1 \\ \mathbf{4} & 0.9 & 0.1 & 0 \end{array}
  $$

  **3. Temel Matrisin ($N$) Bulunması:**
  Önce $(I - Q)$ işlemini yapalım:
  $$
  (I - Q) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix} - \begin{bmatrix} 0 & 0 & 0.4 \\ 0.2 & 0.4 & 0.3 \\ 0 & 0 & 0 \end{bmatrix} = \begin{bmatrix} 1 & 0 & -0.4 \\ -0.2 & 0.6 & -0.3 \\ 0 & 0 & 1 \end{bmatrix}
  $$

  Bu matrisin tersini alarak $N$ matrisini elde ederiz:
  $$
  N = (I - Q)^{-1} = \begin{bmatrix} 1 & 0 & 0.4 \\ \frac{1}{3} & \frac{5}{3} & \frac{19}{30} \\ 0 & 0 & 1 \end{bmatrix}
  $$

  **4. Yutulma Olasılıklarının ($B$) Hesaplanması:**
  Son aşamada $B = N \cdot R$ çarpımını gerçekleştiriyoruz. Yeni matrisimizin **satırları (1, 3, 4)** başlangıç durumlarını, **sütunları (2, 5, 6)** ise bitiş (yutulma) durumlarını temsil edecektir:

  $$
  B = \begin{bmatrix} 1 & 0 & 0.4 \\ \frac{1}{3} & \frac{5}{3} & \frac{19}{30} \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} 0.5 & 0.1 & 0 \\ 0 & 0 & 0.1 \\ 0.9 & 0.1 & 0 \end{bmatrix} 
  = \begin{array}{c|ccc} 
  & \mathbf{2} & \mathbf{5} & \mathbf{6} \\ 
  \hline
  \mathbf{1} & 0.86 & 0.14 & 0 \\ 
  \mathbf{3} & \frac{221}{300} & \frac{29}{300} & \frac{50}{300} \\ 
  \mathbf{4} & 0.9 & 0.1 & 0 
  \end{array}
  $$

  **Sonuç:** Soru bizden **"$\mathbf{3}$ durumunda başlayıp, $\mathbf{2}$ durumunda yutulma"** olasılığını istiyor. Bulduğumuz $B$ matrisinde $\mathbf{3}$ numaralı satır ile $\mathbf{2}$ numaralı sütunun kesişimine bakıyoruz.

  $$\text{Olasılık} = B_{3 \to 2} = \frac{221}{300} \approx \mathbf{0.7366}$$
  
  *(Öz Kontrol: Bulduğumuz $B$ matrisinin her bir satırının toplamı mutlaka $1$ olmalıdır. Örneğin 3. satır için $\frac{221}{300} + \frac{29}{300} + \frac{50}{300} = \frac{300}{300} = 1$ sağlandığı için işlemlerimiz doğrudur.)*
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>