---

prev:
  text: 'Kriptografiye Giriş'
  link: '/dersler/kriptografi/kriptografiye-giris'
next:
  text: 'Terminoloji ve Notasyon'
  link: '/dersler/kriptografi/terminoloji-ve-notasyon'
---

# 🏛️ Kriptografinin Altın Kuralı: Kerckhoffs Prensibi

19.yüzyılda telgrafın icadı, askeri iletişimi radikal bir şekilde hızlandırdı ancak aynı zamanda mesajların düşman tarafından yakalanma riskini de devasa ölçüde artırdı. Savaş alanında taşıması zor olan ve ele geçirildiğinde tüm sistemi çökerten "gizli kod kitaplarına" bir alternatif gerekiyordu. 

İşte bu kaotik ortamda, Hollandalı kriptograf **Auguste Kerckhoffs**, 1883 yılında yayınladığı *La Cryptographie Militaire* adlı makalesinde kriptografi dünyasını sonsuza dek değiştiren o ünlü prensibi ortaya koydu.

<div class="math-block definition">
  <div class="math-block-title">Kerckhoffs Prensibi (1883)</div>

  Bir şifreleme sisteminin güvenliği, **algoritmanın gizliliğine değil**, yalnızca **anahtarın gizliliğine** dayanmalıdır. Düşman (Eve), kullanılan sistemin tüm iç işleyişini, donanımını ve yazılım kodlarını bilse bile; anahtara sahip olmadığı sürece şifreli metni çözememelidir.

</div>

Bu prensip, günümüzde siber güvenlik dünyasında sıklıkla eleştirilen **"Gizlilikle Sağlanan Güvenlik" (Security through Obscurity)** yaklaşımının tam zıttıdır. Güvenliği algoritmayı saklayarak sağlamaya çalışmak, algoritma ifşa olduğunda tüm sistemin kalıcı olarak çökmesi (brittleness/kırılganlık) anlamına gelir.

## 🗣️ Tarihten Çarpıcı Alıntılar

Kerckhoffs'un bu devrimsel fikri, ilerleyen yıllarda kriptografi ve siber güvenlik devleri tarafından kendi sözleriyle yeniden formüle edilmiştir:

> *"Düşman sistemi biliyor." (The enemy knows the system) - **Claude Shannon (Bilgi Teorisinin Kurucusu)**, bu söz literatüre "Shannon'ın Maksimi" olarak geçmiştir.*

> *"Sisteminizi, rakiplerinizin onu tüm detaylarıyla bildiğini varsayarak tasarlayın. (NSA'daki standart varsayım, üretilen herhangi bir yeni cihazın 1 numaralı seri üretiminin doğrudan Kremlin'e teslim edildiği yönündeydi!)" - **Steven M. Bellovin***

> *"Her sır, potansiyel bir çöküş noktası yaratır. Sırrın açığa çıkması, sistemin feci şekilde çökmesine neden olur. Açıklık (openness) ise sisteme esneklik (ductility) sağlar." - **Bruce Schneier***

## 📜 Kerckhoffs'un Askeri Şifreler İçin 6 Temel Kuralı

Kerckhoffs, makalesinde sadece bu prensibi vermekle kalmamış, aynı zamanda pratik bir askeri şifreleme sisteminin sahip olması gereken **6 altın kuralı** listelemiştir:

<div class="math-block">
  <div class="math-block-title">Kerckhoffs'un 6 Orijinal Tasarım Kuralı</div>

  1. Sistem matematiksel olarak olmasa bile **pratik olarak kırılamaz** olmalıdır.
  2. Sistem **gizlilik gerektirmemeli** ve düşman eline geçmesi bir sorun teşkil etmemelidir. *(İşte o meşhur Kerckhoffs Prensibi budur!)*
  3. Anahtar, yazılı notlara ihtiyaç duymadan **akılda tutulabilmeli** ve taraflarca kolayca değiştirilebilmelidir.
  4. Sistem, **telgraf iletişimine** (günümüzde dijital veri aktarımına) uygulanabilir olmalıdır.
  5. Cihaz **taşınabilir** olmalı ve kullanımı için birden fazla kişiye ihtiyaç duyulmamalıdır.
  6. Sistem **kullanımı kolay** olmalı; kullanıcıları uzun kural listelerine veya zihinsel strese maruz bırakmamalıdır.

</div>

Bugün bilgisayarların muazzam işlem güçleri sayesinde 5. ve 6. kurallar (taşınabilirlik ve insan hafızası) şekil değiştirmiş olsa da; **2. kural (Kerckhoffs Prensibi)** modern kriptografinin tartışılamaz anayasası olmaya devam etmektedir.

::: tip 📝 Neden Sadece Anahtarı Gizliyoruz?
Eğer bir algoritma ifşa olursa (ki savaşta veya siber dünyada ifşa olması kesindir), tüm cihazları, yazılımları ve altyapıyı değiştirmek aylar sürer ve devasa bir maliyet yaratır. Ancak sadece **anahtar** ifşa olursa, sistemin geri kalanına hiç dokunmadan **yeni bir anahtar üreterek** güvenliği saniyeler içinde tekrar sağlayabilirsiniz.
:::