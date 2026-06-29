# ElGamal Kriptosistemi ve Ayrık Logaritma Problemi

RSA algoritmasının çarpanlara ayırma zorluğuna dayanan yapısını inceledikten sonra, asimetrik kriptografinin bir diğer devasa sütunu olan **ElGamal Kriptosistemini** ele alacağız. 1985 yılında Taher ElGamal tarafından geliştirilen bu algoritma, gücünü soyut cebir ve sayı teorisinin en güvenilir problemlerinden biri kabul edilen **Ayrık Logaritma Probleminden (Discrete Logarithm Problem - DLP)** alır. 

ElGamal algoritması, Diffie-Hellman anahtar değişim protokolünün şifreleme ve deşifreleme yapabilecek şekilde genişletilmiş bir modifikasyonudur. Günümüzde yaygın olarak kullanılan Eliptik Eğri Kriptografisinin (ECC) de temel mantıksal şemasını oluşturur.

::: info 📌 Gerekli Matematiksel Ön Bilgiler: Ayrık Logaritma Problemi (DLP)
Bir $p$ asal sayısı ve $\mathbb{Z}_p^*$ çarpımsal grubunun bir $g$ **üreteci (generator)** verildiğinde;
$$y \equiv g^a \pmod p$$
eşitliğini sağlayan $a$ üssünü bulma işlemine **ayrık logaritma problemi** denir ($a = \log_g y \pmod p$). 

Eğer $p$ yeterince büyük seçilirse (modern standartlarda en az 2048 bit), $a$ ve $g$ değerlerinden $y$'yi hesaplamak (üslü ifade) polinomsal zamanda çok kolayken; $y$ ve $g$ değerlerinden hareketle gizli olan $a$'yı bulmak bilgisayarsal olarak imkansızdır (üstel zaman gerektirir).
:::

---

## 🔑 Anahtar Üretim Süreci (Key Generation)

Mesaj alıcısı, kendisine ait açık ve gizli anahtar çiftini kurgulamak için şu adımları izler:

1. Çok büyük bir $p$ asal sayısı seçilir.
2. $\mathbb{Z}_p^*$ grubuna ait bir $g$ **üreteci** belirlenir. ($g$'nin kuvvetleri mod $p$'de gruptaki tüm elemanları üretmelidir).
3. $1 < a < p-1$ aralığında rastgele bir **gizli anahtar (private key)** $a$ seçilir.
4. Bu gizli anahtara karşılık gelen kamusal değer $y$ hesaplanır:
   $$y \equiv g^a \pmod p$$

* **Açık Anahtar (Public Key):** $(p, g, y)$ üçlüsüdür ve herkesin erişimine açılır.
* **Gizli Anahtar (Private Key):** Sadece alıcıda saklanan $a$ tam sayısıdır.

---

## 🔒 Fonksiyonların Tanımı ve Doğruluk İspatı

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: ElGamal Şifreleme ve Deşifreleme Fonksiyonları

  </div>
  
  Gönderici, iletmek istediği açık metni $m \in \mathbb{Z}_p$ şartını sağlayan sayısal bir mesaja dönüştürür. Burada:
  * **$g$:** $\mathbb{Z}_p^*$ grubunun kamusal **üreteci (generator)**,
  * **$y$:** Alıcının gizli anahtarına ($a$) karşılık gelen ve $y \equiv g^a \pmod p$ şeklinde hesaplanan kamusal **açık anahtarıdır (public key)**.
  
  **Şifreleme fonksiyonu** $e_{(p,g,y)}$, şifreleme sürecine **rastgelesellik** katmak amacıyla her mesaj için $1 < k < p-1$ aralığında, $\operatorname{gcd}(k, p-1) = 1$ şartını sağlayan geçici (ephemeral) bir $k$ tamsayısı seçer. Şifreli metin bir sayı çiftinden ($(c_1, c_2)$) oluşur:
  
  $$e_{(p,g,y)}(m, k) = (c_1, c_2)$$
  $$\begin{aligned}
  c_1 &\equiv g^k \pmod p \\
  c_2 &\equiv m \cdot y^k \pmod p
  \end{aligned}$$

  Alıcı, kendisine ulaşan $(c_1, c_2)$ şifreli metin çiftini kendi $a$ gizli anahtarını kullanan **deşifreleme fonksiyonu** $d_a$ ile çözer:
  
  $$d_a(c_1, c_2) \equiv c_2 \cdot (c_1^a)^{-1} \pmod p$$
</div>

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: ElGamal Algoritmasının Doğruluğu

  </div>
  
  Her $m \in \mathbb{Z}_p^*$ açık metni ve rastgele seçilen her $k$ geçici anahtarı için, deşifreleme fonksiyonu orijinal mesajı hatasız bir şekilde geri döndürür.

  ::: details İspat
  Deşifreleme fonksiyonunun tanımından yola çıkarak $c_1$ ve $c_2$ bileşenlerini yerlerine koyalım:
  $$d_a(c_1, c_2) \equiv c_2 \cdot (c_1^a)^{-1} \pmod p$$

  Şifreleme adımından biliyoruz ki $c_1 \equiv g^k \pmod p$ ve $c_2 \equiv m \cdot y^k \pmod p$'dir. Ayrıca açık anahtar tanımından $y \equiv g^a \pmod p$ eşitliği geçerlidir. Bu ifadeleri denklemde yerine yazıp üslü sayılar kurallarına göre düzenleyelim:
  
  $$\begin{aligned}
  c_2 \cdot (c_1^a)^{-1} &\equiv (m \cdot y^k) \cdot ((g^k)^a)^{-1} \pmod p \\
  &\equiv (m \cdot (g^a)^k) \cdot (g^{ka})^{-1} \pmod p \\
  &\equiv m \cdot g^{ak} \cdot g^{-ak} \pmod p \\
  &\equiv m \cdot g^{ak - ak} \pmod p \\
  &\equiv m \cdot g^0 \pmod p \\
  &\equiv m \cdot 1 \equiv m \pmod p
  \end{aligned}$$

  Burada $g^{ak}$ ifadesi ile şifreleme sırasında oluşturulan **ortak gizli bilgi (shared secret)**, deşifreleme esnasında $c_1^a$ işlemiyle alıcı tarafından yeniden üretilmiş ve çarpımsal tersi alınarak sistemden sadeleştirilmiştir. Böylece deşifre işleminin doğruluğu kanıtlanmış olur.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

::: info 📌 Olasılıksal Şifreleme (Probabilistic Encryption)
RSA kriptosisteminde aynı $m$ mesajı aynı açık anahtarla şifrelendiğinde her zaman aynı $c$ şifreli metnini üretir (deterministik yapı). Bu durum, saldırganların tahmin yürüterek frekans analizi yapmasına olanak tanır. 

ElGamal'de ise şifreleme fonksiyonuna dahil olan geçici **$k$ parametresi** sayesinde, aynı $m$ mesajı aynı anahtarla defalarca şifrelense bile **her seferinde tamamen farklı bir $(c_1, c_2)$ çifti** üretilir. Bu özellik ElGamal'i semantik olarak çok daha güvenli kılar.
:::

---

## 📝 Çözümlü Uygulama

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Bir ElGamal kurgusunda kamusal parametreler $p = 11$ ve üreteç $g = 2$ olarak seçilmiştir. Alıcının gizli anahtarı $a = 3$ olduğuna göre açık anahtarı hesaplayınız. Ardından göndericinin $k = 4$ geçici anahtarını kullanarak şifrelediği $m = 5$ açık metnine ait $(c_1, c_2)$ şifreli metnini bulunuz ve bu şifreli metni deşifre ediniz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **1. Anahtar Üretim Aşaması:**
  * Verilenler: $p = 11$, $g = 2$, $a = 3$.
  * Kamusal değer $y$ hesaplanır:
    $$y \equiv g^a \pmod p \implies y \equiv 2^3 \pmod{11} = 8$$
  * **Açık Anahtar:** $(p, g, y) = (11, 2, 8)$
  * **Gizli Anahtar:** $a = 3$

  **2. Şifreleme Aşaması:**
  Gönderici $m = 5$ mesajını ve rastgele seçtiği $k = 4$ değerini kullanarak şifreli metin bileşenlerini üretir:
  * $c_1$ bileşeni:
    $$c_1 \equiv g^k \pmod p \implies c_1 \equiv 2^4 \pmod{11} = 16 \equiv 5 \pmod{11}$$
  * $c_2$ bileşeni:
    $$c_2 \equiv m \cdot y^k \pmod p \implies c_2 \equiv 5 \cdot 8^4 \pmod{11}$$
    
    $8$'in kuvvetlerini mod $11$ altında indirgeyelim:
    $$\begin{aligned}
    8^1 &\equiv 8 \pmod{11} \\
    8^2 &= 64 \equiv 9 \equiv -2 \pmod{11} \\
    8^4 &\equiv (-2)^2 = 4 \pmod{11}
    \end{aligned}$$
    O halde $c_2$ değeri:
    $$c_2 \equiv 5 \cdot 4 = 20 \equiv 9 \pmod{11}$$
  * **Şifreli Metin Çifti:** $(c_1, c_2) = (5, 9)$

  **3. Deşifreleme Aşaması:**
  Alıcı $(5, 9)$ şifreli metnini alır ve kendi gizli anahtarı $a = 3$ ile deşifre fonksiyonunu çalıştırır:
  $$m \equiv c_2 \cdot (c_1^a)^{-1} \pmod p$$
  
  * **Adım A:** Öncelikle ortak gizli bilgi olan $c_1^a$ değerini hesaplayalım:
    $$c_1^a \equiv 5^3 \pmod{11} = 125 \pmod{11}$$
    $125$ sayısının $11$ ile bölümünden kalan ($11 \cdot 11 = 121$):
    $$125 - 121 = 4 \implies c_1^a \equiv 4 \pmod{11}$$
  
  * **Adım B:** Şimdi bu değerin mod $11$ altındaki çarpımsal tersini ($(4)^{-1}$) bulmalıyız. Sağlanması gereken şart:
    $$4 \cdot (4)^{-1} \equiv 1 \pmod{11}$$
    Deneme veya Genişletilmiş Öklid ile; $4 \cdot 3 = 12 \equiv 1 \pmod{11}$ olduğundan, çarpımsal ters **$3$** olarak bulunur.
  
  * **Adım C:** Son olarak formülü tamamlayıp mesajı çözelim:
    $$m \equiv 9 \cdot 3 \pmod{11} = 27 \pmod{11}$$
    $27$ sayısının mod $11$ altındaki dengi ($11 \cdot 2 = 22$):
    $$27 - 22 = 5 \implies m = 5$$

  **Sonuç:** Ayrık logaritma asimetrisine dayanan ElGamal kriptosistemi başarıyla çalışmış ve orijinal açık metin olan **$m = 5$** değerine kayıpsız bir şekilde geri dönülmüştür.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>