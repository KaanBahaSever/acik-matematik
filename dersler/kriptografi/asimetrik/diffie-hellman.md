---
title: Diffie-Hellman Anahtar Değişimi
description: İki tarafın güvenli olmayan bir kanal üzerinden ortak gizli anahtar üretmesini sağlayan Diffie-Hellman protokolünü açıklar.
---

# Diffie-Hellman Anahtar Değişimi ve Matematiksel Temelleri

Asimetrik kriptografinin doğuşunu simgeleyen **Diffie-Hellman Anahtar Değişimi (Diffie-Hellman Key Exchange)**, 1976 yılında Whitfield Diffie ve Martin Hellman tarafından yayınlanmıştır. Bu protokol, iki tarafın (geleneksel olarak Alice ve Bob) güvenli olmayan ve herkes tarafından dinlenebilen bir iletişim kanalı üzerinden, önceden hiçbir gizli bilgi paylaşımında bulunmadan **ortak bir gizli anahtar (shared secret)** oluşturmasını sağlar. 

Diffie-Hellman bir şifreleme algoritması değil, bir **anahtar değişim protokolüdür**. Burada üretilen ortak gizli anahtar, daha sonraki iletişim sürecinde verileri çok daha hızlı şifreleyebilen simetrik şifreleme algoritmalarında (örneğin AES) kullanılacaktır. Sistemin matematiksel güvenliği, ElGamal kriptosisteminde olduğu gibi **Ayrık Logaritma Probleminin (Discrete Logarithm Problem - DLP)** bilgisayarsal zorluğuna dayanır.

::: info 📌 Temel Mantık: Renk Karışımı Analojisi
Diffie-Hellman protokolünün işleyişi genellikle bir renk karışımı benzetmesiyle açıklanır:
1. Alice ve Bob herkesin görebileceği **ortak bir başlangıç rengi** (örneğin sarı) seçer.
2. Her iki taraf da kimseye göstermediği **gizli birer renk** seçer (Alice tekil olarak mavi, Bob ise kırmızı).
3. Taraflar ortak renk ile kendi gizli renklerini karıştırıp elde ettikleri **karışımı birbirlerine gönderirler** (Alice yeşil gönderir, Bob turuncu gönderir). Kanaldan geçen bu karışımları dinleyen bir saldırgan, orijinal gizli renkleri ayırt edemez.
4. Alice, Bob'dan gelen turuncu karışıma kendi gizli rengi olan maviyi ekler. Bob ise Alice'ten gelen yeşil karışıma kendi gizli rengi olan kırmızıyı ekler.
5. Sonuçta her iki taraf da **tamamen aynı nihai rengi** (kahverengi) elde etmiş olur. Matematiksel olarak modüler üs alma işlemleri bu gizli renk karışımlarını birebir simüle eder.
:::

---

## 🔑 Protokolün Adımları ve İşleyişi

Diffie-Hellman protokolünün formal kurgusu, modüler aritmetik ve grup teorisi prensipleri üzerine kuruludur.

1. **Kamusal Parametrelerin Seçimi:** İletişim kuracak taraflar, herkesin erişebileceği şu iki parametre üzerinde anlaşırlar:
   * Büyük bir asal sayı: $p$
   * $\mathbb{Z}_p^*$ çarpımsal grubunun bir üreteci: $g$ (Burada $g < p$ şartı aranır ve $g$'nin kuvvetleri mod $p$'de gruptaki tüm elemanları üretebilmelidir).

2. **Gizli ve Açık Değerlerin Üretilmesi:**
   * **Alice**, $1 < a < p-1$ aralığında rastgele bir **gizli tam sayı** $a$ seçer. Ardından kendi açık değerini hesaplayıp Bob'a gönderir:
     $$A \equiv g^a \pmod p$$
   * **Bob**, $1 < b < p-1$ aralığında rastgele bir **gizli tam sayı** $b$ seçer. Ardından kendi açık değerini hesaplayıp Alice'e gönderir:
     $$B \equiv g^b \pmod p$$

3. **Ortak Gizli Anahtarın Hesaplanması:**
   * Alice, Bob'dan aldığı $B$ değerini kendi gizli anahtarı $a$ ile işler:
     $$K_A \equiv B^a \pmod p$$
   * Bob, Alice'ten aldığı $A$ değerini kendi gizli anahtarı $b$ ile işler:
     $$K_B \equiv A^b \pmod p$$

---

## 🔒 Matematiksel Yapı ve Doğruluk İspatı

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Diffie-Hellman Ortak Gizli Bilgisi

  </div>
  
  Alice ve Bob'un protokol adımları sonunda bağımsız olarak hesapladıkları $K_A$ ve $K_B$ değerleri matematiksel olarak birbirine eşittir. Bu ortak değere **Diffie-Hellman Ortak Gizli Anahtarı (Shared Secret)** denir:
  $$K = K_A = K_B$$
</div>

<div class="math-block theorem">
  <div class="math-block-title">

  Teorem: Protokolün Matematiksel Tutarlılığı

  </div>
  
  Güvenli olmayan kanal üzerinden iletilen $A \equiv g^a \pmod p$ ve $B \equiv g^b \pmod p$ açık değerleri kullanılarak hesaplanan $B^a \pmod p$ ve $A^b \pmod p$ değerleri her zaman aynı $g^{ab} \pmod p$ sonucunu verir.

  ::: details İspat
  Alice'in hesaplama adımını ele alalım. Alice, Bob'dan gelen $B$ değerinin $a$. kuvvetini mod $p$ altında hesaplamaktadır:
  $$K_A \equiv B^a \pmod p$$

  Bob'un açık değer üretme fonksiyonundan biliyoruz ki $B \equiv g^b \pmod p$ eşitliği geçerlidir. Bu ifadeyi yerine koyarsak:
  $$K_A \equiv (g^b)^a \pmod p$$

  Üslü sayıların çarpımsal değişim özelliği ($({g^b})^a = g^{ba} = g^{ab}$) uyarınca denklem şu şekle dönüşür:
  $$K_A \equiv g^{ab} \pmod p$$

  Şimdi Bob'un hesaplama adımını inceleyelim. Bob, Alice'ten gelen $A$ değerinin $b$. kuvvetini mod $p$ altında hesaplamaktadır:
  $$K_B \equiv A^b \pmod p$$

  Alice'in açık değer tanımından $A \equiv g^a \pmod p$ olduğunu biliyoruz. Yerine koyduğumuzda:
  $$K_B \equiv (g^a)^b \pmod p \equiv g^{ab} \pmod p$$

  Görüldüğü üzere her iki işlem de modüler aritmetikteki üs değişme özelliği sayesinde aynı nihai değere ulaşmaktadır:
  $$K_A \equiv K_B \equiv g^{ab} \pmod p$$
  
  Böylece tarafların gizli anahtarlarını ($a$ ve $b$) kanala asla vermeden, sadece açık bileşenler üzerinden aynı gizli $K$ sayısında birleşebilecekleri kanıtlanmış olur.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

::: warning ⚠️ Kritik Güvenlik Uyarısı: Ortadaki Adam Saldırısı (Man-in-the-Middle)
Diffie-Hellman protokolü, pasif dinleyicilere (eavesdroppers) karşı Ayrık Logaritma Probleminin zorluğu sayesinde tamamen güvenlidir. Ancak protokolün asıl zayıflığı **kimlik doğrulama (authentication)** mekanizmasının olmamasıdır. 

Alice ve Bob karşı tarafın kimliğini doğrulamadığı için, araya giren aktif bir saldırgan (Eve); Alice'e kendisini Bob, Bob'a ise kendisini Alice olarak tanıtabilir. Alice ile ayrı ($g^{ae}$), Bob ile ayrı ($g^{be}$) ortak anahtarlar kurarak tüm iletişimi deşifre edebilir ve değiştirebilir. Bu tehlikeyi önlemek için modern sistemlerde Diffie-Hellman adımları **Dijital İmzalar (Digital Signatures)** veya sertifikalarla birlikte kullanılır.
:::

---

## 📝 Çözümlü Uygulama

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Bir Diffie-Hellman anahtar değişiminde ortak parametreler $p = 13$ ve üreteç $g = 2$ olarak belirlenmiştir. Alice kendi gizli değerini $a = 4$, Bob ise kendi gizli değerini $b = 3$ olarak seçmiştir. Tarafların üreteceği kamusal açık değerleri ve süreç sonunda elde edecekleri ortak gizli anahtarı ($K$) adım adım hesaplayınız.

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **1. Kamusal Açık Değerlerin Üretilmesi:**
  * **Alice'in Açık Değeri ($A$):**
    $$A \equiv g^a \pmod p \implies A \equiv 2^4 \pmod{13}$$
    $$2^4 = 16$$
    $16$ sayısının mod 13 altındaki kalanı:
    $$16 - 13 = 3 \implies A = 3$$
    *Alice, $A = 3$ değerini kanal üzerinden Bob'a gönderir.*

  * **Bob'un Açık Değeri ($B$):**
    $$B \equiv g^b \pmod p \implies B \equiv 2^3 \pmod{13}$$
    $$2^3 = 8 \implies B = 8$$
    *Bob, $B = 8$ değerini kanal üzerinden Alice'e gönderir.*

  **2. Ortak Gizli Anahtarın Hesaplanması:**
  * **Alice'in Hesaplaması ($K_A$):**
    Alice, Bob'dan gelen $B = 8$ değerini alır ve kendi gizli sayısı $a = 4$ ile işler:
    $$K_A \equiv B^a \pmod p \implies K_A \equiv 8^4 \pmod{13}$$
    Hesabı kolaylaştırmak için $8^2 = 64 \equiv 12 \equiv -1 \pmod{13}$ denkliğini kullanalım:
    $$8^4 = (8^2)^2 \equiv (-1)^2 = 1 \implies K_A = 1$$

  * **Bob'un Hesaplaması ($K_B$):**
    Bob, Alice'ten gelen $A = 3$ değerini alır ve kendi gizli sayısı $b = 3$ ile işler:
    $$K_B \equiv A^b \pmod p \implies K_B \equiv 3^3 \pmod{13}$$
    $$3^3 = 27$$
    $27$ sayısının mod 13 altındaki kalanı ($13 \cdot 2 = 26$):
    $$27 - 26 = 1 \implies K_B = 1$$

  **Sonuç:** Matematiksel doğrulama tam olarak çalışmış, Alice ve Bob gizli anahtarlarını paylaşmadan **$K = 1$** ortak gizli anahtarında başarıyla buluşmuşlardır.
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>