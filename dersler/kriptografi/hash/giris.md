# Kriptografik Özet (Hash) Fonksiyonlarına Giriş

Asimetrik ve simetrik şifreleme algoritmaları verinin "gizliliğini" (confidentiality) sağlarken, dijital dünyada mesajların yolda değiştirilmediğinden (bütünlük - integrity) ve gönderenin gerçekten iddia ettiği kişi olduğundan (kimlik doğrulama - authentication) emin olmamız gerekir. İşte bu noktada modern kriptografinin "İsviçre çakısı" olarak bilinen **Kriptografik Özet (Hash) Fonksiyonları** devreye girer.

::: info 📌 Kısa Tarihçe
Hash fonksiyonu kavramı ilk olarak 1950'lerde **Hans Peter Luhn** tarafından veritabanlarında metinleri hızlıca aramak ve sınıflandırmak amacıyla bir bilgisayar algoritması olarak ortaya atıldı. 1976'da Diffie ve Hellman'ın asimetrik şifrelemeyi icadıyla birlikte dijital imzalarda kullanılmak üzere kriptografik bir boyut kazandı. Ancak modern kriptografik hash fonksiyonlarının (MD5, SHA serisi) matematiksel bel kemiğini, 1979 ve 1989 yıllarında birbirinden bağımsız olarak çalışan **Ralph Merkle** ve **Ivan Damgård**'ın kurduğu mimari oluşturmuştur.
:::

## 🌍 Nerede ve Nasıl Kullanılır?

Özet fonksiyonları şifreleme **yapmazlar** (geri döndürülemezler); bunun yerine verinin benzersiz bir "dijital parmak izini" çıkarırlar. Kullanım alanları şunlardır:
* **Parola Saklama:** Şifreleriniz veritabanlarında düz metin olarak değil, hash değerleri olarak saklanır. Veritabanı çalınsa bile hash'ten orijinal şifreye dönülemez.
* **Dosya Bütünlüğü (Checksum):** İndirdiğiniz bir dosyanın eksik veya virüslü olup olmadığını kontrol etmek için dosyanın hash değeri yayıncının hash değeriyle karşılaştırılır.
* **Dijital İmzalar:** Devasa bir PDF dosyasını RSA ile imzalamak saatler sürer. Bunun yerine dosyanın kısa hash'i alınır ve sadece bu hash imzalanır.
* **Blokzincir (Blockchain):** Bitcoin ve Ethereum gibi ağlarda blokları birbirine kriptografik olarak bağlamak ve madencilik (Proof of Work) yapmak için yoğun olarak SHA-256 hash fonksiyonu kullanılır.

---

## 🔒 Matematiksel Tanım ve Güvenlik Kriterleri

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Kriptografik Özet (Hash) Fonksiyonu

  </div>
  
  Bir kriptografik hash fonksiyonu $H$, rastgele ve sonsuz uzunlukta olabilen herhangi bir $m \in \{0, 1\}^*$ mesajını girdi olarak alıp, sabit ve önceden belirlenmiş $n$ uzunluğunda (örneğin 256 bit) bir $h \in \{0, 1\}^n$ özet (hash) değerine dönüştüren deterministik bir fonksiyondur:
  $$H: \{0, 1\}^* \to \{0, 1\}^n$$
  $$h = H(m)$$
  
  Bu fonksiyonun kriptografik olarak güvenli kabul edilebilmesi için şu üç **direnç (resistance)** şartını sağlaması zorunludur:
  
  1. **Ön-görüntü Direnci (Pre-image Resistance - Tek Yönlülük):** Sadece $h$ hash değeri biliniyorken, $H(m) = h$ şartını sağlayan orijinal $m$ mesajını bulmak bilgisayarsal olarak imkansız olmalıdır.
  2. **İkinci Ön-görüntü Direnci (Second Pre-image Resistance):** Belirli bir $m_1$ mesajı elimizdeyken, aynı hash değerini üreten farklı bir $m_2$ mesajı ($m_1 \neq m_2$) bulmak ($H(m_1) = H(m_2)$) bilgisayarsal olarak imkansız olmalıdır.
  3. **Çakışma Direnci (Collision Resistance):** Hash değerleri aynı olan *herhangi* rastgele iki farklı mesaj ($m_1 \neq m_2$ ve $H(m_1) = H(m_2)$) bulmak bilgisayarsal olarak imkansız olmalıdır. (Güvercin Yuvası Prensibi gereği çakışmalar matematiksel olarak mevcuttur, ancak bulunmaları milyarlarca yıl sürmelidir).
</div>

---

## 📝 Çözümlü Uygulama: Basit Bir Hash Fonksiyonu 

Özet fonksiyonlarının "ön-görüntü (pre-image)" bulma ve "çakışma (collision)" kavramlarını anlayabilmek için, modüler aritmetiğe dayanan çok basit bir hash fonksiyonu tanımlayalım. Gerçek dünyada ters görüntü bulmak imkansız olsa da, bu basit örnekte matematiğin nasıl işlediğini görebiliriz.

<div class="math-block example">
  <div class="math-block-title">

  Örnek 1: Basit Hash Fonksiyonu ve Girdi (Ters Görüntü) Bulma

  </div>

  $H: \mathbb{Z} \to \mathbb{Z}_{11}$ şeklinde tanımlanan ve kuralı $H(x) \equiv (4x + 5) \pmod{11}$ olan temel bir hash fonksiyonu verilmiştir. 
  
  **a)** Bu fonksiyon için hash özeti $H(x) = 2$ olan bir girdi (ters görüntü) bulunuz.
  **b)** Bulduğunuz bu girdi ile çakışan (aynı hash değerini veren) farklı bir girdi daha bularak bir çakışma (collision) çifti oluşturunuz.

  ::: details 💡 Çözümü Göster / Gizle
  **a) Ters Görüntü (Pre-image) Bulma:**
  Bizden $H(x) \equiv 2 \pmod{11}$ şartını sağlayan bir $x$ değeri bulmamız isteniyor. Denklemi kuralım:
  $$4x + 5 \equiv 2 \pmod{11}$$
  
  Bilinenleri bir tarafa toplayalım (her iki taraftan 5 çıkaralım):
  $$4x \equiv 2 - 5 \pmod{11}$$
  $$4x \equiv -3 \pmod{11}$$
  
  Negatif sayıyı mod 11'de pozitif dengiyle değiştirelim ($-3 + 11 = 8$):
  $$4x \equiv 8 \pmod{11}$$
  
  Eşitliğin her iki tarafını 4'e bölelim (çünkü 4 ile 11 aralarında asaldır):
  $$x \equiv 2 \pmod{11}$$
  
  Böylece $H(x) = 2$ sonucunu veren girdi değerlerinden birinin **$x = 2$** olduğunu bulduk. Gerçekten de sağlamasını yaparsak: $4(2) + 5 = 13 \equiv 2 \pmod{11}$.

  **b) Çakışma (Collision) Çifti Oluşturma:**
  Modüler aritmetiğin doğası gereği, modül değerinin (11) tam katlarını eklediğimizde sonuç değişmeyecektir. 
  Eğer $x = 2$ için hash değeri $2$ ise;
  $x = 2 + 11 = 13$ girdisi için de hash değeri aynı çıkmalıdır. 
  
  Sağlamasını yapalım:
  $$H(13) = 4(13) + 5 = 52 + 5 = 57$$
  $$57 = (11 \cdot 5) + 2 \implies 57 \equiv 2 \pmod{11}$$
  
  **Sonuç:** $H(2) = 2$ ve $H(13) = 2$ bulunmuştur. $2 \neq 13$ olmasına rağmen aynı hash değerini ürettikleri için **$\{2, 13\}$** kümesi bu fonksiyon için bir çakışma (collision) çiftidir.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

---

## 🏗️ Merkle-Damgård Mimarisinin (Construction) Anatomisi

Matematikçiler, "sonsuz uzunluktaki bir veriyi, sabit uzunlukta güvenli bir çıktıya dönüştüren bir fonksiyonu tek seferde nasıl yazarız?" sorusuyla karşılaştılar. Merkle ve Damgård, bu sorunu harika bir **zincirleme** mantığıyla çözdü. Günümüzde MD5, SHA-1 ve SHA-2 ailelerinin kullandığı bu mimari, süreci küçük bloklara böler.

**İşleyiş Mantığı:**
1. **Doldurma (Padding):** Gelen sonsuz mesaj, önce önceden belirlenmiş blok boyutunun tam katı olacak şekilde sonuna anlamsız veriler eklenerek tamamlanır. Mimarinin güvenliğinin kanıtı için en sona eklenen blok içine mesajın orijinal uzunluğu da yazılır (Buna *Merkle-Damgård Strengthening* denir).
2. **Sıkıştırma Fonksiyonu (Compression Function):** Mimari, sonsuz veriyi değil, sadece sabit $b$ uzunluğunda mesaj bloğu ile bir önceki adımdan gelen sabit $n$ uzunluğundaki durumu alıp yine $n$ uzunluğunda çıktı üreten tek yönlü bir $\tilde{H}$ veya $f$ fonksiyonu kullanır.
3. **Zincirleme (Chaining):** Sisteme başlangıç için sabit bir **Başlangıç Vektörü (IV - Initialization Vector)** olan $h_0$ (veya $h_1$) verilir. Mesaj bloklara ayrılır ve her blok sırayla sıkıştırma fonksiyonundan geçirilerek bir sonraki adımı besler. Zincirin en sonundaki iterasyon değeri, ana fonksiyonun Hash değeri olur.

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Merkle-Damgård Güvenlik İndirgemesi

  </div>
  
  Eğer içeride kullanılan blok bazlı sıkıştırma fonksiyonu **çakışmaya dayanıklı (collision-resistant)** ise, Merkle-Damgård yapısıyla kurulan ve her uzunluktaki mesajı işleyebilen ana $H$ özet fonksiyonu da matematiksel olarak **çakışmaya dayanıklıdır.**
</div>

---

## 📝 Çözümlü Uygulamalar: MD Yapısı

<div class="math-block example">
  <div class="math-block-title">

  Örnek 2: Bit Düzeyinde Sıkıştırma ve Merkle-Damgård Zincirlemesi

  </div>

  $\tilde{H} : \{0,1\}^3 \to \{0,1\}^2$ şeklinde tanımlanan bir sıkıştırma fonksiyonu verilmiştir. 
  
  Bu fonksiyonun çıktı kuralı şu şekildedir: **İlk bit**, girdideki bitlerin toplamının (mod 2) değerini (parite); **ikinci bit** ise girdinin ortasındaki (ikinci) biti temsil eder.

  <div style="display: flex; justify-content: center; margin: 15px 0;">
  
  | $x$ (Girdi) | $\tilde{H}(x)$ (Çıktı) |
  |:---:|:---:|
  | $000$ | $00$ |
  | $001$ | $10$ |
  | $010$ | $11$ |
  | $011$ | $01$ |
  | $100$ | $10$ |
  | $101$ | $00$ |
  | $110$ | $01$ |
  | $111$ | $11$ |

  </div>
  
  **a)** $\tilde{H}$ sıkıştırma fonksiyonu için bir çakışma (collision) çifti bulunuz.
  **b)** Başlatma vektörü (IV) $h_1 = 00$ olan ve $\tilde{H}$ kullanılarak Merkle-Damgård yapısı ile oluşturulan genel $H$ hash fonksiyonu için **$H(1101)$** değerini hesaplayınız.
  **c)** $H(1101)$ ile çakışan, farklı uzunlukta bir girdi bulunuz.

  ::: details 💡 Çözümü Göster / Gizle
  **a) Çakışma Analizi (Sıkıştırma Fonksiyonu için):**
  Çakışma, $\tilde{H}(x) = \tilde{H}(x')$ ve $x \neq x'$ durumunda gerçekleşir. Doğruluk tablosu incelendiğinde birden fazla çakışma görülmektedir:
  * $\tilde{H}(001) = 10$ ve $\tilde{H}(100) = 10 \implies$ **$\{001, 100\}$** bir çakışmadır.
  * $\tilde{H}(010) = 11$ ve $\tilde{H}(111) = 11 \implies$ **$\{010, 111\}$** bir çakışmadır.
  
  **b) Merkle-Damgård Hesaplaması ($H(1101)$):**
  Sıkıştırma fonksiyonumuz $3$ bit girdi alıp $2$ bit çıktı veriyor. Her iterasyonda bir önceki adımın $2$ bitlik çıktısı ile mesajın sıradaki $1$ biti birleştirilir (Concatenation, $\parallel$).
  
  Girdi mesajımız $x = x_1x_2x_3x_4 = 1101$ için adımlar (Girdi blok uzunluğu $c=1$, durum uzunluğu $b=2$):
  
  1. **Adım 1 (Başlangıç):** $h_1 = 00$ 
  2. **Adım 2 ($x_1 = 1$ işlenir):** $h_2 = \tilde{H}(h_1 \parallel x_1) = \tilde{H}(00 \parallel 1) = \tilde{H}(001) = 10$
  3. **Adım 3 ($x_2 = 1$ işlenir):** $h_3 = \tilde{H}(h_2 \parallel x_2) = \tilde{H}(10 \parallel 1) = \tilde{H}(101) = 00$
  4. **Adım 4 ($x_3 = 0$ işlenir):** $h_4 = \tilde{H}(h_3 \parallel x_3) = \tilde{H}(00 \parallel 0) = \tilde{H}(000) = 00$
  5. **Adım 5 ($x_4 = 1$ işlenir):** $h_5 = \tilde{H}(h_4 \parallel x_4) = \tilde{H}(00 \parallel 1) = \tilde{H}(001) = 10$
     
  **Nihai Sonuç:** Zincirin son elemanı hash değerimizdir. $H(1101) = 10$.
  
  **c) Hash Çakışması Bulma (Ana Fonksiyon için):**
  Hesaplama sürecindeki ara değerlere (durumlara) bakıldığında, 2. adımda elde edilen $h_2 = 10$ değeri dikkat çekicidir. 
  Bu ara değer, aslında sadece $x = 1$ (tek bitlik) girdisinin hash özetidir:
  $$H(1) = \tilde{H}(h_1 \parallel 1) = \tilde{H}(00 \parallel 1) = \tilde{H}(001) = 10$$
  
  Böylece $H(1) = 10$ ve $H(1101) = 10$ olduğu saptanmıştır. $1 \neq 1101$ olduğundan ve farklı uzunluklarda olmalarına rağmen aynı sonucu verdiklerinden, **$\{1, 1101\}$** çifti genel $H$ hash fonksiyonu için bir çakışma teşkil eder.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek 3: Metin Tabanlı Merkle-Damgård Zincirlemesi

  </div>

  Kendi tasarımımız olan ve Merkle-Damgård mimarisini kullanan $H$ özet fonksiyonu ile $m = \text{"MATH"}$ mesajının hash değerini, yani $H(\text{MATH})$ sonucunu bulunuz.
  
  <b>Sistem Kuralları ve $H$ Fonksiyonunun Tanımı:</b>
  * $H$ fonksiyonu, gelen $m$ mesajını 1 harflik bloklara bölerek işler. Dolayısıyla 4 harfli $m = \text{"MATH"}$ girdisi için $m_1=M, m_2=A, m_3=T, m_4=H$ olmak üzere zincirleme mimari gereği $4$ iterasyon gereklidir.
  * Harflerin sayısal değerleri 0-25 tablosuna göredir (A=0, M=12, T=19, H=7).
  * Sistemin Başlangıç Vektörü (IV) $h_0 = 5$ olarak sabitlenmiştir.
  * İçeride çalışan sabit boyutlu sıkıştırma fonksiyonu $f$, bir önceki iterasyonun durumu ile yeni mesaj bloğunu şu formülle birleştirir:
    $$f(h_{i-1}, m_i) = (h_{i-1} \cdot 3 + m_i) \pmod{26}$$
  * Buna göre genel hash fonksiyonumuz $H(m)$, Merkle-Damgård'ın birbirini çağıran zincirleme yapısı gereği şu formülle tanımlanır:
    $$H(m) = f(f(f(f(h_0, m_1), m_2), m_3), m_4) = h_4$$

  ::: details 💡 Çözümü Göster / Gizle
  İstenen $H(\text{MATH})$ değerini bulmak için $H$ fonksiyonunun iç yapısındaki $f$ sıkıştırma adımını sırasıyla 4 kez (her bir blok için) uygulayacağız. Başlangıç durumumuz $h_0 = 5$'tir.

  **1. İterasyon ($m_1 = M \implies 12$):**
  $$h_1 = f(h_0, m_1) \implies h_1 \equiv (5 \cdot 3 + 12) \pmod{26}$$
  $$h_1 = 15 + 12 = 27$$
  $27 \equiv 1 \pmod{26} \implies h_1 = 1$

  **2. İterasyon ($m_2 = A \implies 0$):**
  Bir önceki adımın zincir çıktısı olan $h_1 = 1$ kullanılarak fonksiyon tekrar çalıştırılır.
  $$h_2 = f(h_1, m_2) \implies h_2 \equiv (1 \cdot 3 + 0) \pmod{26}$$
  $$h_2 = 3 + 0 = 3 \implies h_2 = 3$$

  **3. İterasyon ($m_3 = T \implies 19$):**
  Bir önceki çıktımız olan $h_2 = 3$ devreye girer.
  $$h_3 = f(h_2, m_3) \implies h_3 \equiv (3 \cdot 3 + 19) \pmod{26}$$
  $$h_3 = 9 + 19 = 28$$
  $28 \equiv 2 \pmod{26} \implies h_3 = 2$

  **4. İterasyon ($m_4 = H \implies 7$):**
  Son mesaj bloğumuz olan H harfi, $h_3 = 2$ değeriyle birlikte işlenir.
  $$h_4 = f(h_3, m_4) \implies h_4 \equiv (2 \cdot 3 + 7) \pmod{26}$$
  $$h_4 = 6 + 7 = 13 \implies h_4 = 13$$

  **Sonuç:** Bütün mesaj blokları iç içe geçmiş bir şekilde zincirleme kuralla (Merkle-Damgård) işlendiği için son iterasyon değeri bütünüyle $H(m)$'e eşittir.
  $$H(\text{MATH}) = h_4 = 13$$
  Tabloya göre 13 sayısının karşılığı **N** harfidir. Böylece "MATH" kelimesinin sistemimizdeki nihai hash (özet) değeri **N** olarak hesaplanmıştır.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>