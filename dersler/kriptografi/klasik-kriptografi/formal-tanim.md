# Kriptosistemin Formal Tanımı

Matematiksel şifreleme algoritmalarına (Sezar, Affine, Hill vb.) geçmeden önce, bir şifreleme sisteminin evrensel anatomisini tanımlamamız gerekir. Tüm modern ve klasik kriptosistemler matematiksel olarak 5 bileşenli bir yapı ile ifade edilir.

Bir kriptosistem (şifreleme sistemi), aşağıdaki koşulları sağlayan bir $(\mathcal{P}, \mathcal{C}, \mathcal{K}, \mathcal{E}, \mathcal{D})$ beşlisidir:

* **$\mathcal{P}$ (Plaintext):** Açık metinlerin oluşturduğu sonlu küme.
* **$\mathcal{C}$ (Ciphertext):** Şifreli (kapalı) metinlerin oluşturduğu sonlu küme.
* **$\mathcal{K}$ (Key Space):** Anahtar uzayı; kullanılabilecek olası tüm anahtarların oluşturduğu sonlu küme.
* **$\mathcal{E}$ (Encryption):** Şifreleme (kapama) fonksiyonları kümesi.
* **$\mathcal{D}$ (Decryption):** Deşifreleme (açma) fonksiyonları kümesi.

### Fonksiyonların Çalışma Prensibi

Her $k \in \mathcal{K}$ anahtarı için, bir şifreleme kuralı $e_k \in \mathcal{E}$ ve buna karşılık gelen bir deşifreleme kuralı $d_k \in \mathcal{D}$ tanımlanır:

$$e_k: \mathcal{P} \to \mathcal{C}$$
$$d_k: \mathcal{C} \to \mathcal{P}$$

Sistemin tutarlı olabilmesi için, seçilen her bir anahtar $k \in \mathcal{K}$ ve her bir açık metin parçası $x \in \mathcal{P}$ için, şifrelenmiş metnin tekrar geri açılabileceğini garanti eden şu koşul sağlanmalıdır:

$$(d_k \circ e_k)(x) = d_k(e_k(x)) = x, \quad \forall x \in \mathcal{P}$$

::: warning Birebirlik (Injective) Şartı
Şifreleme fonksiyonu olan $e_k$, matematiksel olarak kesinlikle **birebir (1-1)** olmalıdır. 

Eğer fonksiyon birebir olmazsa ve farklı iki açık metin ($x_1 \neq x_2$) aynı şifreli metne ($C$) dönüşürse:
$$e_k(x_1) = e_k(x_2)$$
Bu durumda şifreyi çözen kişi, $C$ metnini deşifre ettiğinde orijinal metnin $x_1$ mi yoksa $x_2$ mi olduğunu bilemez. Benzersiz bir çözüm elde edilebilmesi için birebirlik şarttır.
:::