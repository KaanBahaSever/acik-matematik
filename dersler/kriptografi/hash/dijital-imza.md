# Dijital İmzalar ve RSA İmza Şeması

Asimetrik şifreleme ile verinin "gizliliğini" (confidentiality) sağlamayı, kriptografik özet (hash) fonksiyonlarıyla da verinin "bütünlüğünü" (integrity) korumayı öğrendik. Ancak dijital dünyada çözülmesi gereken çok büyük bir problem daha vardır: **Kimlik Doğrulama (Authentication)** ve **İnkar Edememezlik (Non-repudiation)**. 

Bana internet üzerinden gelen bir e-postanın veya banka talimatının, *gerçekten* iddia edilen kişi tarafından gönderildiğini ve sonradan "bunu ben göndermedim" diyemeyeceğini nasıl garanti edebiliriz? İşte bu noktada, asimetrik şifreleme mantığının tam tersi yönünde çalışan **Dijital İmzalar (Digital Signatures)** devreye girer.

::: info 📌 Paradigma Değişimi: Şifreleme vs. İmzalama
Asimetrik sistemlerde (örneğin RSA) anahtar kullanım yönü amaca göre tamamen değişir:
* **Gizlilik (Şifreleme) Amacıyla:** Mesaj, alıcının **Açık Anahtarı** ile şifrelenir. Sadece alıcının **Gizli Anahtarı** ile çözülebilir. (Herkes mesaj gönderebilir, sadece alıcı okuyabilir).
* **Kimlik Doğrulama (İmzalama) Amacıyla:** Mesaj, göndericinin **Gizli Anahtarı** ile imzalanır. Herkes göndericinin **Açık Anahtarı** ile bu imzayı doğrulayabilir. (Sadece sahibi imza atabilir, herkes imzanın doğruluğunu teyit edebilir).
:::

---

## 🔒 Dijital İmzanın Formal Tanımı

Bir dijital imza şeması temelde üç algoritmadan oluşan bir bütündür:

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Dijital İmza Şeması (Digital Signature Scheme)

  </div>
  
  Bir dijital imza şeması, mesaj uzayı $\mathcal{M}$, imza uzayı $\mathcal{S}$ ve anahtar uzayı $\mathcal{K}$ olmak üzere şu 3 temel algoritmadan oluşur:
  
  1. **Anahtar Üretimi (KeyGen):** Göndericiye ait bir $(pk, sk)$ anahtar çifti üretir. Burada $pk$ herkesin bildiği açık anahtar (public key), $sk$ ise sadece göndericinin bildiği gizli anahtardır (secret key).
  2. **İmza Oluşturma (Sign):** Göndericinin $sk$ gizli anahtarı ve $m \in \mathcal{M}$ mesajı girdi olarak alınır, $s \in \mathcal{S}$ dijital imzası üretilir:
     $$s = \text{Sign}_{sk}(m)$$
  3. **İmza Doğrulama (Verify):** Göndericinin $pk$ açık anahtarı, $m$ mesajı ve $s$ imzası girdi olarak alınır. İmza gerçekten bu mesaj için ve bu gizli anahtar ile üretilmişse **Geçerli (True)**, aksi takdirde **Geçersiz (False)** çıktısı üretilir:
     $$\text{Verify}_{pk}(m, s) \in \{\text{True}, \text{False}\}$$
</div>



---

## 🏗️ Hash ve İmza Paradigması (Hash-and-Sign)

Teorik olarak koca bir dosyayı veya uzun bir metni doğrudan asimetrik anahtarla imzalayabilirsiniz. Ancak matematikte büyük sayılarla üs alma işlemleri son derece yavaştır. 2 GB'lık bir video dosyasını doğrudan RSA ile imzalamak saatler sürer. 

Ayrıca doğrudan mesajı imzalamak, "Varoluşsal Sahtecilik" (Existential Forgery) adı verilen matematiksel saldırılara kapı aralar. Bu nedenle modern kriptografide **asla doğrudan mesaj imzalanmaz.**

::: tip 💡 Altın Kural: Önce Özetle, Sonra İmzala!
Dijital imza atılmadan önce mesajın, çakışmaya dayanıklı bir $H$ kriptografik hash fonksiyonu (örneğin SHA-256) ile özeti çıkarılır. Daha sonra gizli anahtar ile sadece bu **küçük özet değeri (hash)** imzalanır.
$$s = \text{Sign}_{sk}(H(m))$$
Alıcı da mesajın hash'ini kendi hesaplar ve gelen imzadaki hash ile karşılaştırır. Dosya ne kadar büyük olursa olsun, imzalama işlemi daima sabit boyutlu (örneğin 256 bit) bir sayı üzerinden saniyeler içinde gerçekleşir.
:::

---

## 🔑 RSA Dijital İmza Algoritması

Dünyada en çok bilinen ve kök sertifikalarda hala yaygın olarak kullanılan imza yöntemi RSA tabanlıdır. Matematiksel altyapısı, daha önce öğrendiğimiz RSA şifrelemesi ile tamamen aynı asalları ve totient kurallarını kullanır.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: RSA İmza Şeması

  </div>

  **1. Anahtar Üretimi:** İki büyük asal sayı $p$ ve $q$ seçilir. Modül $n = p \cdot q$ ve $\phi(n) = (p-1)(q-1)$ hesaplanır. $\operatorname{gcd}(a, \phi(n)) = 1$ olacak şekilde açık üs **$a$** seçilir. $a \cdot d \equiv 1 \pmod{\phi(n)}$ denkliğini sağlayan gizli üs $d$ hesaplanır.
  * Açık Anahtar (Doğrulama için): $(a, n)$
  * Gizli Anahtar (İmzalama için): $(d, n)$

  **2. İmza Oluşturma (Gönderici):** Gönderici $m$ mesajının özetini $h = H(m)$ çıkarır. Kendi **gizli anahtarı ($d$)** ile bu özeti imzalar:
  $$s \equiv h^d \pmod n$$
  Oluşan $(m, s)$ çifti (mesaj ve imza) alıcıya gönderilir.

  **3. İmza Doğrulama (Alıcı):**
  Alıcı gelen $s$ imzasını, göndericinin **açık anahtarı ($a$)** ile çözerek orijinal hash değerine ($h'$) ulaşmaya çalışır:
  $$h' \equiv s^a \pmod n$$
  Alıcı aynı zamanda gelen $m$ mesajının hash'ini kendisi de hesaplar ($H(m)$). Eğer **$h' == H(m)$** ise imza geçerlidir, belge değiştirilmemiştir ve kesinlikle gönderici tarafından imzalanmıştır.
</div>

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: RSA İmzasının Doğruluğu

  </div>
  
  Doğrulama adımında $s^a \pmod n$ işleminin sonucu her zaman orijinal mesajın özeti olan $H(m)$ değerine denktir.

  ::: details İspat
  İmza oluşturma denkleminden biliyoruz ki $s \equiv H(m)^d \pmod n$. 
  
  Doğrulama fonksiyonunda $s$ yerine bu eşdeğerini koyduğumuzda:
  $$s^a \equiv (H(m)^d)^a \equiv H(m)^{d \cdot a} \pmod n$$

  Anahtar üretim adımından $a \cdot d \equiv 1 \pmod{\phi(n)}$ olduğunu biliyoruz. Çarpma işleminin değişme özelliği gereği $d \cdot a = a \cdot d$'dir. RSA şifrelemesinin doğruluk ispatında Euler ve Çin Kalan Teoremleri yardımıyla gösterdiğimiz kural (bkz. RSA Şifreleme İspatı) burada da birebir geçerlidir:
  $$H(m)^{a \cdot d} \equiv H(m) \pmod n$$
  
  Böylece $s^a \equiv H(m) \pmod n$ eşitliği sağlanır ve imzanın doğru şekilde eşleştiği kanıtlanmış olur.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

---

## 📝 Çözümlü Uygulama: Sayısal RSA İmzası

<div class="math-block example">
  <div class="math-block-title">

  Örnek: RSA İmza Oluşturma ve Doğrulama Adımları

  </div>

  Bir kullanıcının RSA anahtar çifti için başlangıç asalları $p = 5$ ve $q = 11$ olarak seçilmiştir. Açık üs değeri $a = 3$ olarak belirlenmiştir. Bu kullanıcı, hash değeri **$H(m) = 14$** olarak hesaplanan bir PDF dosyasını imzalayacaktır. 
  
  Gerekli anahtarları oluşturunuz, dosyanın dijital imzasını ($s$) hesaplayınız ve alıcı tarafında bu imzanın nasıl doğrulandığını gösteriniz.

  ::: details 💡 Çözümü Göster / Gizle
  **1. Anahtar Üretimi:**
  * Modül: $n = p \cdot q = 5 \cdot 11 = 55$
  * Euler Totient: $\phi(n) = (5-1)(11-1) = 4 \cdot 10 = 40$
  * Açık üs $a = 3$ verilmiş. $\operatorname{gcd}(3, 40) = 1$ şartı sağlanıyor.
  * Gizli üs $d$'nin bulunması ($3 \cdot d \equiv 1 \pmod{40}$):
    $3 \cdot 27 = 81 = (40 \cdot 2) + 1 \equiv 1 \pmod{40}$ olduğundan **$d = 27$**'dir.
  * **Açık Anahtar (Doğrulayıcı):** $(3, 55)$
  * **Gizli Anahtar (İmzalayıcı):** $(27, 55)$

  **2. İmza Oluşturma (Gönderici Adımı):**
  Gönderici dosyanın hash değerini ($H(m) = 14$) sadece kendisinin bildiği $d = 27$ gizli anahtarıyla imzalayacaktır:
  $$s \equiv 14^{27} \pmod{55}$$
  
  Hesaplamayı "Ardışık Kare Alma" yöntemiyle küçültelim:
  $$\begin{aligned}
  14^1 &\equiv 14 \pmod{55} \\
  14^2 &= 196 = (55 \cdot 3) + 31 \equiv 31 \pmod{55} \\
  14^4 &\equiv 31^2 = 961 = (55 \cdot 17) + 26 \equiv 26 \pmod{55} \\
  14^8 &\equiv 26^2 = 676 = (55 \cdot 12) + 16 \equiv 16 \pmod{55} \\
  14^{16} &\equiv 16^2 = 256 = (55 \cdot 4) + 36 \equiv 36 \pmod{55}
  \end{aligned}$$
  
  Üs değerini parçalayalım ($27 = 16 + 8 + 2 + 1$):
  $$14^{27} = 14^{16} \cdot 14^8 \cdot 14^2 \cdot 14^1$$
  $$14^{27} \equiv 36 \cdot 16 \cdot 31 \cdot 14 \pmod{55}$$
  
  Parçalı çarparak mod $55$ alalım:
  $36 \cdot 16 = 576 = (55 \cdot 10) + 26 \equiv 26$
  $31 \cdot 14 = 434 = (55 \cdot 7) + 49 \equiv 49 \equiv -6$ (İşlem kolaylığı için $-6$ yazdık)
  
  Son çarpımı yapalım:
  $$26 \cdot (-6) = -156$$
  $-156$'nın mod $55$ altındaki pozitif dengini bulalım ($55 \cdot 3 = 165$ ekleyelim):
  $$-156 + 165 = 9 \implies s = 9$$
  
  **Oluşturulan Dijital İmza:** $s = 9$

  **3. İmza Doğrulama (Alıcı Adımı):**
  Alıcı dosyayı ve $s = 9$ imzasını alır. Göndericinin açık anahtarı olan $a = 3$ ve $n = 55$ değerlerini kullanarak imzayı açar:
  $$h' \equiv s^a \pmod n \implies h' \equiv 9^3 \pmod{55}$$
  
  İşlemi yapalım:
  $$9^3 = 729$$
  $729$'un $55$ ile bölümünden kalanı bulalım ($55 \cdot 13 = 715$):
  $$729 - 715 = 14 \implies h' = 14$$
  
  **Sonuç:** Alıcının imzadan çıkardığı değer ($h' = 14$), dosyanın orijinal hash değeri ($H(m) = 14$) ile birebir eşleşmiştir. İmza KESİNLİKLE geçerlidir; belge yolda değiştirilmemiştir ve sadece $d=27$ anahtarına sahip kişi tarafından oluşturulmuştur.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>