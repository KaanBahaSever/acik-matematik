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

### Kümelerin Somutlaştırılması: Alfabe ve Mod 26

Matematiksel şifreleme fonksiyonlarının harfler üzerinde işlem yapabilmesi için, harfleri sayılara dönüştürmemiz gerekir. Modern kriptografik sistemlerde ve bu notlardaki tüm klasik algoritmalarda uluslararası standart olan **26 harfli İngilizce alfabe** kullanılır. Türkçe karakterler (ç, ğ, ı, ö, ş, ü) modüler aritmetik sınırlarını ve standart ASCII tablolarını bozduğu için denklemlere dahil edilmez.

Bu bağlamda, açık metin ($\mathcal{P}$) ve şifreli metin ($\mathcal{C}$) kümelerimiz $\mathbb{Z}_{26}$ (Mod 26'ya göre kalanlar sınıfı) olarak tanımlanır:

$$\mathcal{P} = \mathcal{C} = \mathbb{Z}_{26} = \{0, 1, 2, \dots, 25\}$$

**Harf - Sayı Dönüşüm Tablosu:**
İşlemlerde sıfırdan başlama (0-index) kuralı geçerlidir. A harfi 0, Z harfi ise 25 değerini alır.

<div style="display: flex; justify-content: center;">

| Harf | Değer | Harf | Değer |
|:---:|:---:|:---:|:---:|
| **A** | 0 | **N** | 13 |
| **B** | 1 | **O** | 14 |
| **C** | 2 | **P** | 15 |
| **D** | 3 | **Q** | 16 |
| **E** | 4 | **R** | 17 |
| **F** | 5 | **S** | 18 |
| **G** | 6 | **T** | 19 |
| **H** | 7 | **U** | 20 |
| **I** | 8 | **V** | 21 |
| **J** | 9 | **W** | 22 |
| **K** | 10| **X** | 23 |
| **L** | 11| **Y** | 24 |
| **M** | 12| **Z** | 25 |

</div>

<figcaption style="text-align: center; font-style: italic; font-size: 0.8em; color: var(--vp-c-text-2);">Tablo 1: Harflerin Mod 26'ya Göre Sayısal Karşılıkları</figcaption>

> **💡 Not:** Klasik şifreleme algoritmalarının tamamında (Sezar, Affine, Vigenère, Hill) matematiksel işlemler bu tablo referans alınarak ve sonuçlar her zaman **Mod 26**'ya göre hesaplanarak yürütülecektir. Eğer bir işlem sonucu negatif çıkarsa veya 25'i geçerse, sonucun mod 26'daki denki bulunarak tabloya geri dönülür.