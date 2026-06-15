<script setup>
import ProblemBox from '/.vitepress/components/ProblemBox.vue'
</script>

# Alfabe Permütasyonu (Yerine Koyma) Şifrelemesi

Soyut cebirsel perspektiften bakıldığında, klasik şifreleme yöntemlerinin büyük bir kısmı alfabe kümesinin kendi üzerindeki birebir ve örten dönüşümleriyle, yani permütasyonlarıyla ifade edilir. Kriptografi literatüründe "Monoalfabetik Yerine Koyma Şifresi" olarak da bilinen bu yapı, matematiksel olarak tamamen bir simetrik grup ($S_n$) işlemidir.

Bu sistemde harflerin metin içindeki konumları (indeksleri olan $\tau$) sabit kalır; ancak her bir karakterin alfabedeki sayısal değeri ($x_\tau$), bir $\pi$ permütasyon fonksiyonuna sokularak karakterin kimliği değiştirilir. 

## Sistemin Formal Tanımı

İngiliz alfabesi üzerinde ($\mathbb{Z}_{26}$) çalıştığımızı varsayarsak, 5 bileşenli kriptosistem anatomisi şu şekilde tanımlanır:

* **Açık Metin ($\mathcal{P}$):** Elemanları $\mathbb{Z}_{26} = \{0, 1, 2, \dots, 25\}$ kümesinden seçilen karakter dizileridir.
* **Şifreli Metin ($\mathcal{C}$):** Elemanları $\mathbb{Z}_{26}$ kümesinden seçilen karakter dizileridir.
* **Anahtar Uzayı ($\mathcal{K}$):** $\mathbb{Z}_{26}$ kümesi üzerindeki tüm olası permütasyonların oluşturduğu **Simetrik Grup ($S_{26}$)**'dır. 
* **Şifreleme Fonksiyonu ($\mathcal{E}$):** Açık metindeki her bir $\tau$. karakterin sayısal değeri $x_\tau$, seçilen $\pi$ permütasyon fonksiyonuna girdi olarak verilir:
  $$e_{\pi}(x_\tau) = \pi(x_\tau)$$
* **Deşifreleme Fonksiyonu ($\mathcal{D}$):** Şifreli metindeki değeri çözmek için permütasyon fonksiyonunun tersi ($\pi^{-1}$) kullanılır:
  $$d_{\pi}(y_\tau) = \pi^{-1}(y_\tau)$$


## Anahtar Uzayı ve Güvenlik Analizi

Permütasyon tabanlı bu yerine koyma şifresinin anahtar uzayı, $\mathbb{Z}_{26}$ kümesinin tüm elemanlarının kendi aralarındaki dizilimlerinin sayısına eşittir. Toplam olası anahtar sayısı $26!$ faktöriyel işlemi ile hesaplanır:
$$|\mathcal{K}| = 26! \approx 4.03 \times 10^{26}$$

Bu değer, modern AES-128 şifrelemesindeki anahtar sayısına ($2^{128} \approx 3.4 \times 10^{38}$) kıyasla küçük kalsa da, kaba kuvvet (brute-force) saldırıları için klasik dönemde aşılamaz bir büyüklükteydi. Ancak bu sistem, harflerin kimliğini statik bir şekilde değiştirdiği için doğal dilin istatistiksel yapısını gizleyemez. Bir metindeki 'E' harfinin frekansı neyse, onun şifreli karşılığının frekansı da aynı kalır. Bu yüzden Frekans Analizi yöntemiyle saniyeler içinde kırılabilir.

## Döngü Gösterimi (Cycle Notation) ve Sabit Elemanlar Kuralı

Soyut cebir derslerinde permütasyonlar genellikle matris yerine **ayrık döngülerin çarpımı (product of disjoint cycles)** şeklinde yazılır. Bu notasyonda işlemi yaparken unutulmaması gereken en hayati matematiksel kural şudur:

> **Sabit Eleman Kuralı:** Eğer alfabedeki bir sayı ($\mathbb{Z}_{26}$'nın bir elemanı) tanımlanan permütasyon döngüleri (cycles) içinde hiç yer almıyorsa, o eleman permütasyon altında sabit kalır ve **kendisine eşlenir** ($\pi(x) = x$).

Aşağıdaki örneklerde, 26 harflik alfabenin tamamını kapsayan büyük bir permütasyon anahtarı tanımlanmış, ancak bazı sayılar döngüye bilerek dahil edilmeyerek bu kuralın nasıl çalıştığı gösterilmiştir.

## Çözümlü Uygulamalar

<ProblemBox>
  <template #question>
  
  🟢 **Örnek 1:** $\mathbb{Z}_{26}$ alfabesi üzerinde tanımlı $\pi$ permütasyon anahtarı ayrık döngüler formunda aşağıda verilmiştir. Bu anahtarı kullanarak "MATHS" açık metnini şifreleyiniz.
  
  $$\pi = (0\ 12\ 2\ 19)(1\ 5\ 8\ 20\ 24)(3\ 14\ 17)(4\ 7\ 11\ 22)$$
  
  </template>
  
  <template #solution>
  
  **Çözüm:**
  
  Öncelikle "MATHS" açık metnindeki harflerin sayısal karşılıklarını ($x_\tau$) bulalım:
  * M $\rightarrow x_1 = 12$
  * A $\rightarrow x_2 = 0$
  * T $\rightarrow x_3 = 19$
  * H $\rightarrow x_4 = 7$
  * S $\rightarrow x_5 = 18$
  
  Şimdi şifreleme fonksiyonumuzu ($y_\tau = \pi(x_\tau)$) her bir değer için uygulayalım ve döngüdeki haritasını takip edelim:
  
  1. $\pi(12)$'yi bulalım: $(0\ 12\ 2\ 19)$ döngüsünde 12'den sonra 2 gelir.
     $$\pi(12) = 2 \implies \mathbf{C}$$
  
  2. $\pi(0)$'ı bulalım: Aynı döngüde 0'dan sonra 12 gelir.
     $$\pi(0) = 12 \implies \mathbf{M}$$
  
  3. $\pi(19)$'u bulalım: Döngünün son elemanı her zaman ilk elemana döner.
     $$\pi(19) = 0 \implies \mathbf{A}$$
  
  4. $\pi(7)$'yi bulalım: $(4\ 7\ 11\ 22)$ döngüsünde 7'den sonra 11 gelir.
     $$\pi(7) = 11 \implies \mathbf{L}$$
  
  5. $\pi(18)$'i bulalım: 18 sayısı tanımlanan hiçbir döngünün içinde yer **almamaktadır**. Sabit eleman kuralı gereği kendisine eşlenir.
     $$\pi(18) = 18 \implies \mathbf{S}$$
  
  **Sonuç:** `MATHS` açık metni, $\pi$ fonksiyonu altında `CMALS` olarak şifrelenir.
  
  </template>
</ProblemBox>

<ProblemBox>
  <template #question>
  
  🔵 **Örnek 2:** Aynı $\pi = (0\ 12\ 2\ 19)(1\ 5\ 8\ 20\ 24)(3\ 14\ 17)(4\ 7\ 11\ 22)$ permütasyon anahtarı kullanılarak şifrelenmiş olan "CMALS" kapalı metnini deşifre ediniz.
  
  </template>
  
  <template #solution>
  
  **Çözüm:**
  
  Deşifreleme yapabilmek için permütasyonun tersini ($\pi^{-1}$) almalıyız. Döngü (cycle) notasyonunda bir permütasyonun tersini almak, döngünün içindeki elemanları **sondan başa doğru** tersten yazmaktır:
  $$\pi^{-1} = (19\ 2\ 12\ 0)(24\ 20\ 8\ 5\ 1)(17\ 14\ 3)(22\ 11\ 7\ 4)$$
  *(Not: Döngü içinde yer almayan elemanlar ters permütasyonda da yine sabit kalır, yani kendilerine eşlenirler.)*
  
  Şifreli metnimiz "CMALS" harflerinin sayısal değerlerini ($y_\tau$) ters fonksiyona ($x_\tau = \pi^{-1}(y_\tau)$) sokalım:
  * C $\rightarrow y_1 = 2$
  * M $\rightarrow y_2 = 12$
  * A $\rightarrow y_3 = 0$
  * L $\rightarrow y_4 = 11$
  * S $\rightarrow y_5 = 18$
  
  Ters haritayı takip edelim:
  1. $\pi^{-1}(2)$'yi bulalım: $(19\ 2\ 12\ 0)$ döngüsünde 2'den sonra 12 gelir.
     $$\pi^{-1}(2) = 12 \implies \mathbf{M}$$
  
  2. $\pi^{-1}(12)$'yi bulalım: Aynı döngüde 12'den sonra 0 gelir.
     $$\pi^{-1}(12) = 0 \implies \mathbf{A}$$
  
  3. $\pi^{-1}(0)$'ı bulalım: Döngünün sonundan başına döneriz.
     $$\pi^{-1}(0) = 19 \implies \mathbf{T}$$
  
  4. $\pi^{-1}(11)$'i bulalım: $(22\ 11\ 7\ 4)$ döngüsünde 11'den sonra 7 gelir.
     $$\pi^{-1}(11) = 7 \implies \mathbf{H}$$
  
  5. $\pi^{-1}(18)$'i bulalım: 18 sayısı ters döngülerde de yoktur, dolayısıyla kendine eşlenir.
     $$\pi^{-1}(18) = 18 \implies \mathbf{S}$$
  
  **Sonuç:** Deşifreleme işlemi matematiksel olarak kusursuz çalışmış ve orijinal `MATHS` kelimesine ulaşılmıştır.
  
  </template>
</ProblemBox>