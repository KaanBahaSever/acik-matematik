---
title: Asimetrik Şifreleme ve Açık Anahtar Kriptografisi
description: Açık anahtar kriptografisinin temel fikrini, gizli-açık anahtar yapısını ve asimetrik şifrelemenin kullanım alanlarını özetler.

---

# Asimetrik Şifreleme ve Açık Anahtar Kriptografisine Giriş

Klasik kriptografi sistemlerinde (Sezar, Affine, Hill vb.) şifreleme ve deşifreleme işlemleri için aynı anahtar ya da birbirine doğrudan dönüştürülebilen simetrik anahtarlar kullanılır. Bu durum modern ağ yapılarında ciddi bir **Anahtar Dağıtım Problemi (Key Distribution Problem)** doğurur; çünkü güvenli iletişim kurmak isteyen iki tarafın öncelikle güvenli olmayan bir kanal üzerinden gizli anahtarı birbirine iletmesi gerekir. 

Asimetrik şifreleme (**Açık Anahtar Kriptografisi**), bu temel tıkanıklığı **çift anahtar** konseptiyle çözerek kriptografide tam anlamıyla bir paradigma değişimi yaratmıştır. Bu sistemde her kullanıcının matematiksel olarak birbirine bağlı olan, ancak birinden diğerinin hesaplanması bilgisayarsal olarak imkansız olan iki farklı anahtarı bulunur: **Açık Anahtar (Public Key)** ve **Gizli Anahtar (Private Key)**.

::: info 📌 Tarihsel Not
Asimetrik şifreleme fikri teorik olarak ilk kez 1976 yılında **Whitfield Diffie** ve **Martin Hellman** tarafından ortaya atılmış; pratik ve olgun ilk matematiksel model ise 1977 yılında **Ron Rivest, Adi Shamir ve Leonard Adleman** tarafından kendi soyadlarını taşıyan **RSA algoritması** ile kurulmuştur.
:::

---

## 🔒 Kriptosistemin Formal Tanımı

Asimetrik yaklaşım, klasik kriptosistem tanımındaki tekil anahtar uzayını ikiye ayırır ve fonksiyonel bağımlılıkları yeniden şekillendirir.

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Asimetrik Kriptosistem

  </div>
  
  Bir asimetrik kriptosistem, aşağıdaki koşulları sağlayan bir $(\mathcal{P}, \mathcal{C}, \mathcal{K}_{pub}, \mathcal{K}_{priv}, \mathcal{E}, \mathcal{D})$ altılısıdır:

  * **$\mathcal{P}$ (Plaintext):** Açık metinlerin oluşturduğu sonlu küme.
  * **$\mathcal{C}$ (Ciphertext):** Şifreli (kapalı) metinlerin oluşturduğu sonlu küme.
  * **$\mathcal{K}_{pub}$ (Public Key Space):** Şifreleme amacıyla kullanılan ve herkese açık olarak ilan edilen açık anahtarların ($pk$) sonlu kümesi.
  * **$\mathcal{K}_{priv}$ (Private Key Space):** Sadece şifreyi çözecek alıcı tarafından gizli tutulan gizli anahtarların ($sk$) sonlu kümesi.
  * **$\mathcal{E}$ (Encryption):** Şifreleme fonksiyonları kümesi.
  * **$\mathcal{D}$ (Decryption):** Deşifreleme fonksiyonları kümesi.

  Sistemden seçilen her bir $(pk, sk)$ anahtar çifti (Public Key, Secret Key) için, $\mathcal{E}$ kümesinden küçük $e$ ile gösterilen bir şifreleme fonksiyonu ve $\mathcal{D}$ kümesinden küçük $d$ ile gösterilen bir deşifreleme fonksiyonu tanımlanır:

  $$e_{pk}: \mathcal{P} \to \mathcal{C}$$
  $$d_{sk}: \mathcal{C} \to \mathcal{P}$$

  Sistemin matematiksel olarak tutarlı ve işlevsel olabilmesi için, her bir $x \in \mathcal{P}$ açık metni üzerinde şu **tersinelenebilirlik şartı** sağlanmalıdır:

  $$d_{sk}(e_{pk}(x)) = x, \quad \forall x \in \mathcal{P}$$
</div>