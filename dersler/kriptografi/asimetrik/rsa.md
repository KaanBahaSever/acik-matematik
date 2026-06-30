---
title: RSA Şifreleme Algoritması
description: RSA'nın anahtar üretimi, şifreleme ve deşifreleme adımlarını; asal çarpanlara ayırma probleminin rolüyle birlikte anlatan ders notu.
---

# RSA Şifreleme Algoritması

Asimetrik şifrelemenin teorik altyapısını inceledikten sonra, bu paradigmanın dünyadaki ilk ve en yaygın uygulaması olan **RSA (Rivest-Shamir-Adleman)** algoritmasını ele alacağız. RSA'in güvenliği, sayı teorisinin en temel ve çözülmesi zor problemlerinden biri olan **Büyük Sayıların Asal Çarpanlara Ayırılması (Integer Factorization Problem)** ilkesine dayanır. Bilgisayarlar için iki büyük asal sayıyı çarpmak (ileri yön) saliseler alırken, çarpım sonucundan hareketle orijinal asal çarpanları bulmak (geri yön) günümüz işlemcileriyle milyarlarca yıl sürebilir.

::: info 📌 Gerekli Matematiksel Ön Bilgiler
RSA adımlarını tam olarak kavrayabilmek için şu iki kavramın hatırlanması hayati önem taşır:
1. **Euler Totient Fonksiyonu ($\phi(n)$):** Bir $n$ pozitif tam sayısı için, $n$'den küçük ve $n$ ile aralarında asal olan pozitif tam sayıların adedidir. Eğer $p$ ve $q$ iki farklı asal sayı ise, fonksiyonun çarpanlara ayrılabilme özelliğinden dolayı $\phi(p \cdot q) = (p-1)(q-1)$ olur.
2. **Modüler Çarpımsal Ters:** $a \cdot d \equiv 1 \pmod{\phi(n)}$ denkliğini sağlayan $d$ değeridir. Bu değer **Genişletilmiş Öklid Algoritması (Extended Euclidean Algorithm)** kullanılarak polinomsal zamanda hızlıca hesaplanır.
:::

---

## 🔑 Anahtar Üretim Süreci (Key Generation)

Şifreli mesajı alacak olan taraf (örneğin Alıcı), kendi anahtar çiftini oluşturmak için şu adımları sırasıyla uygular:

1. Birbirinden bağımsız, rastgele ve çok büyük iki asal sayı olan $p$ ve $q$ seçilir.
2. Bu iki asal sayının çarpımı olan **kamusal modül** $n$ hesaplanır:
   $$n = p \cdot q$$
3. Bu modüle ait Euler Totient değeri $\phi(n)$ hesaplanır:
   $$\phi(n) = (p-1)(q-1)$$
4. $1 < a < \phi(n)$ aralığında, $\phi(n)$ ile aralarında asal olan bir **açık üs (encryption exponent)** $a$ seçilir:
   $$\operatorname{gcd}(a, \phi(n)) = 1$$
5. Seçilen $a$ değerinin mod $\phi(n)$ altındaki çarpımsal tersi olan **gizli üs (decryption exponent)** $d$ hesaplanır:
   $$a \cdot d \equiv 1 \pmod{\phi(n)}$$

* **Açık Anahtar ($pk$ - Public Key):** $(a, n)$ çiftidir ve herkesin erişebileceği şekilde ilan edilir.
* **Gizli Anahtar ($sk$ - Private Key):** $(d, n)$ çiftidir ve alıcı tarafından kesinlikle gizli tutulur. $p, q$ ve $\phi(n)$ değerleri de süreç sonunda güvenli bir şekilde imha edilmelidir.

::: tip 💡 Önemli Not: Carmichael Totient Fonksiyonu Alternatifi
Teorik anlatımlarda ve akademik kaynaklarda kolay anlaşılması açısından genellikle Euler Totient fonksiyonu ($\phi(n)$) tercih edilir. Ancak gerçek dünya uygulamalarında ve modern **PKCS#1** standartlarında, anahtar üretimi adımı sıklıkla **Carmichael Totient Fonksiyonu** ($\lambda(n)$) ile hesaplanır:
$$\lambda(n) = \operatorname{lcm}(p-1, q-1)$$
$\lambda(n)$ fonksiyonu, $p-1$ ve $q-1$ sayılarının en küçük ortak katını (EKOK) verir. Bu değer $\phi(n)$'e eşit veya ondan daha küçük bir çalışma alanı sunduğu için, modüler tersi alındığında bilgisayarsal olarak daha küçük ve işleme hızı daha yüksek bir gizli anahtar ($d$) üretilmesini sağlar. Algoritmanın şifreleme, deşifreleme ve genel matematiksel mantığı bu değişiklikten etkilenmez.
:::

---

## 🔒 Fonksiyonların Tanımı ve Doğruluk İspatı

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: RSA Şifreleme ve Deşifreleme Fonksiyonları

  </div>
  
  Gönderici, iletmek istediği açık metni $0 \le m < n$ şartını sağlayan bir $m \in \mathbb{Z}_n$ sayısına dönüştürür. 
  
  **Şifreleme fonksiyonu** $e_{pk}$, alıcının açık anahtarı $pk = (a, n)$ ile şifreli metni ($c$) üretir:
  $$c \equiv e_{pk}(m) \equiv m^a \pmod n$$

  Alıcı, güvenli olmayan kanaldan gelen $c$ metnini kendi **deşifreleme fonksiyonu** $d_{sk}$ ve gizli anahtarı $sk = (d, n)$ ile çözer:
  $$m \equiv d_{sk}(c) \equiv c^d \pmod n$$
</div>

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: RSA Algoritmasının Doğruluğu (Correctness of RSA)

  </div>
  
  Her $m \in \mathbb{Z}_n$ açık metni için, şifreleme ve ardından deşifreleme işlemleri uygulandığında orijinal mesaj hatasız bir şekilde elde edilir:
  $$(m^a)^d \equiv m^{ad} \equiv m \pmod n$$

  ::: details İspat
  Anahtar üretim adımından biliyoruz ki $a \cdot d \equiv 1 \pmod{\phi(n)}$ şartı geçerlidir. Modüler aritmetik tanımı gereği, bu eşitlik bize bir $k \in \mathbb{Z}$ tam sayısı için şu ifadeyi verir:
  $$ad = k \cdot \phi(n) + 1$$

  Bu durumda deşifreleme fonksiyonunun çıktısını üslü sayılar kuralıyla açalım:
  $$m^{ad} = m^{k \cdot \phi(n) + 1} = m \cdot (m^{\phi(n)})^k$$

  Bu ifadenin mod $n$ altındaki dengini ispatlamak için **Çin Kalan Teoremi (Chinese Remainder Theorem)** gereği ifadenin hem mod $p$ hem de mod $q$ altında $m$'ye denk olduğunu göstermemiz yeterlidir. İspatı mod $p$ için yapalım ($mod\ q$ için de tamamen simetriktir):

  * **Durum 1:** Eğer $\operatorname{gcd}(m, p) = 1$ ise, **Fermat'nın Küçük Teoremi (Fermat's Little Theorem)** uyarınca $m^{p-1} \equiv 1 \pmod p$ olur. O halde $\phi(n) = (p-1)(q-1)$ eşitliğini yerine koyarsak:
    $$m^{ad} \equiv m \cdot (m^{(p-1)(q-1)})^k \equiv m \cdot ((m^{p-1})^{q-1})^k \equiv m \cdot (1^{q-1})^k \equiv m \pmod p$$
  * **Durum 2:** Eğer $\operatorname{gcd}(m, p) \neq 1$ ise, $p$ bir asal sayı olduğundan $m$ sayısı $p$'nin bir tam katı olmak zorundadır. Bu durumda $m \equiv 0 \pmod p$ olur. Sıfırın her pozitif kuvveti sıfır olacağından:
    $$m^{ad} \equiv 0^{ad} \equiv 0 \equiv m \pmod p$$

  Her iki durumda da $m^{ad} \equiv m \pmod p$ olduğu gösterilmiş olur. Aynı adımlar mod $q$ için de uygulandığında $m^{ad} \equiv m \pmod q$ elde edilir. Aralarında asal iki asal sayıya ayrı ayrı bölünebilen bir ifade, bu sayıların çarpımına da tam bölünmek zorunda olduğundan:
  $$m^{ad} \equiv m \pmod{p \cdot q} \implies m^{ad} \equiv m \pmod n$$
  
  Böylece deşifreleme fonksiyonunun şifreli metni her koşulda orijinal açık metne dönüştürdüğü matematiksel olarak kanıtlanmış olur.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

---

## 📝 Çözümlü Uygulama

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Bir RSA kurgusunda başlangıç asalları $p = 7$ ve $q = 11$ olarak seçilmiştir. Açık üs değeri $a = 7$ olduğuna göre anahtar çiftlerini hesaplayınız ve $m = 9$ açık metnini şifreleyip ardından deşifre ediniz.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **1. Anahtar Üretimi:**
  * Kamusal modül: $n = p \cdot q = 7 \cdot 11 = 77$
  * Totient değeri: $\phi(n) = (7-1)(11-1) = 6 \cdot 10 = 60$
  * Seçilen $a = 7$ değerinin $\phi(n) = 60$ ile aralarında asal olduğu doğrulanır ($\operatorname{gcd}(7, 60) = 1$).
  * Gizli üs $d$ hesabı ($7 \cdot d \equiv 1 \pmod{60}$):
    Genişletilmiş Öklid aritmetiği veya ardışık katlar incelendiğinde; $7 \cdot 43 = 301$ bulunur. $301 = (60 \cdot 5) + 1 \equiv 1 \pmod{60}$ olduğundan **$d = 43$** olarak belirlenir.
  
  * **Açık Anahtar:** $pk = (7, 77)$
  * **Gizli Anahtar:** $sk = (43, 77)$

  **2. Şifreleme Süreci:**
  Gönderici $m = 9$ mesajını alır ve şifreler:
  $$c \equiv e_{pk}(m) \equiv m^a \pmod n \implies c \equiv 9^7 \pmod{77}$$
  
  Hesabı kolaylaştırmak için üssü parçalayalım:
  $$\begin{aligned}
  9^1 &\equiv 9 \pmod{77} \\
  9^2 &= 81 \equiv 4 \pmod{77} \\
  9^4 &\equiv 4^2 = 16 \pmod{77}
  \end{aligned}$$
  O halde $9^7 = 9^4 \cdot 9^2 \cdot 9^1$ eşitliğinden:
  $$c \equiv 16 \cdot 4 \cdot 9 = 576 \pmod{77}$$
  $576$ sayısının $77$ ile bölümünden kalan ($77 \cdot 7 = 539$):
  $$576 - 539 = 37 \implies c = 37$$

  **3. Deşifreleme Süreci:**
  Alıcı gelen $c = 37$ şifreli metnini gizli anahtarı $sk$ ile çözer:
  $$m \equiv d_{sk}(c) \equiv c^d \pmod n \implies m \equiv 37^{43} \pmod{77}$$
  
  Ardışık kare alma (Square-and-Multiply) yöntemi ile büyük üssü mod 77'de indirgeyelim:
  $$\begin{aligned}
  37^1 &\equiv 37 \pmod{77} \\
  37^2 &= 1369 = (77 \cdot 17) + 60 \equiv 60 \equiv -17 \pmod{77} \\
  37^4 &\equiv (-17)^2 = 289 = (77 \cdot 3) + 58 \equiv 58 \equiv -19 \pmod{77} \\
  37^8 &\equiv (-19)^2 = 361 = (77 \cdot 4) + 53 \equiv 53 \equiv -24 \pmod{77} \\
  37^{16} &\equiv (-24)^2 = 576 \equiv 37 \pmod{77} \\
  37^{32} &\equiv 37^2 \equiv 60 \pmod{77}
  \end{aligned}$$
  
  $43$ sayısının ikilik tabandaki açılımı $43 = 32 + 8 + 2 + 1$ olduğundan:
  $$37^{43} = 37^{32} \cdot 37^8 \cdot 37^2 \cdot 37^1$$
  $$37^{43} \equiv 60 \cdot 53 \cdot 60 \cdot 37 \pmod{77}$$
  Daha kolay sayılar için negatif denklikleri ($60 \equiv -17$) geri koyalım:
  $$(-17) \cdot 53 \cdot (-17) \cdot 37 = 289 \cdot 1961$$
  Mod 77 karşılıkları: $289 \equiv 58 \equiv -19$ ve $1961 = (77 \cdot 25) + 36 \equiv 36$.
  $$(-19) \cdot 36 = -684$$
  $-684$ sayısının pozitif dengini bulalım ($77 \cdot 9 = 693$):
  $$-684 + 693 = 9$$
  
  **Sonuç:** Deşifreleme işlemi tamamlanmış ve orijinal açık metin olan **$m = 9$** değerine başarıyla geri dönülmüştür.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>