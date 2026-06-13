# 🔐 Kriptografiye Giriş ve Tarihsel Serüven

Etimolojik olarak Yunanca *kryptós* (gizli) ve *graphein* (yazmak) kelimelerinin birleşiminden doğan bu alana akademik dünyada üst başlık olarak **Kriptoloji** adı verilir. **Kriptoloji**, temelde birbirine zıt iki alt daldan oluşan geniş bir bilimdir: Bir yanda bilgiyi matematiksel algoritmalarla şifreleyip gizleme sanatı olan **Kriptografi**; diğer yanda ise bu şifreli metinleri anahtar olmadan kırma ve analiz etme bilimi olan **Kriptanaliz** bulunur. Yani kriptografi kalkanı inşa ederken, kriptanaliz o kalkanı delmeye çalışır.

Tarih boyunca bilginin gücü, onu koruma ihtiyacını doğurmuş; bu ihtiyaç da imparatorlukların kaderini belirlemiştir. Kriptografi sadece bir matematik oyunu değil, **savaşların seyrini değiştiren en kritik stratejik silahtır**. Savaşlar cephede tüfeklerle edilse de, arka planda **istihbarat ve şifreleme** ile kazanılır. Düşmanın haberleşmesini kırmak, orduların nerede konumlanacağını bilmek demektir. Bu kedi-fare oyunu, insan zekasının sınırlarını zorlayarak matematiğin en büyüleyici dallarından birini inşa etmiştir.

## 🏛️ Tarihsel Süreç: Antik Çağlardan Modern Algoritmalara

Kriptografinin evrimi, bir tarafın **kırılamaz bir şifre** icat etmesi ve diğer tarafın o şifreyi kıracak **yeni bir matematiksel yöntem** geliştirmesi döngüsüyle ilerlemiştir.

* **Antik Çağlar ve Fiziksel Şifreler:** Kriptografinin bilinen ilk askeri kullanımı **Spartalılara** dayanır. **"Scytale"** adı verilen silindirik bir sopaya sarılan derilerle mesajları fiziksel olarak şifreliyorlardı. Daha sonra Roma İmparatoru **Jül Sezar**, generalleriyle haberleşirken alfabedeki harfleri belirli bir sayıda kaydırarak tarihin en meşhur yer değiştirme algoritmalarından biri olan **Sezar Şifresi'ni** yarattı.
* **Orta Çağ ve Frekans Analizi:** Yüzyıllar boyunca Sezar tarzı tek alfabeli şifreler "kırılamaz" kabul edildi. Ta ki 9. yüzyılda Arap matematikçi **El-Kindi**, harflerin dillerdeki kullanım sıklıklarını analiz ederek **Frekans Analizi** yöntemini icat edene kadar. Bu olay, **dilbilim ve istatistiğin** kriptografiye indirdiği ilk büyük darbedir ve **kriptanalizin doğuşu** sayılır.
* **Rönesans ve Vigenère:** Tek alfabeli şifrelerin zayıflığının anlaşılmasının ardından, 16. yüzyılda Fransız diplomat Blaise de Vigenère, **birden fazla alfabe** kullanarak şifrelemeyi bir üst seviyeye taşıdı. **Vigenère Şifresi**, şifreleme tablosunun karmaşıklığı sayesinde yaklaşık 300 yıl boyunca **"Kırılamaz Şifre"** (Le Chiffre Indéchiffrable) unvanını korudu.
* **Dünya Savaşları ve Makineleşme:** 20. yüzyıla gelindiğinde şifreleme artık kağıt kalemden çıkıp **elektromekanik rotorlu makinelere** taşındı. II. Dünya Savaşı'nda Almanların kullandığı efsanevi **Enigma makinesi**, milyarlarca farklı kombinasyon üreterek Müttefiklere kan kusturuyordu. **Alan Turing** ve Bletchley Park'taki ekibinin bu makineyi kırmak için icat ettikleri devasa cihazlar, **modern bilgisayarların atası** sayılır ve savaşın süresini yıllarca kısalttığı kabul edilir.
* **Modern Çağ ve Bilgi Teorisi:** 1949'da **Claude Shannon'ın** yazdığı makalelerle kriptografi, bir "sanat" olmaktan çıkıp tamamen matematiksel ve istatistiksel bir **bilim dalına** dönüştü. Bilgisayarların icadıyla birlikte artık harfleri değil, **bitleri (0 ve 1)** devasa asal sayılar ve karmaşık cebirsel uzaylarda şifreliyoruz. Bugün internetteki tüm **güvenli iletişimimiz** bu modern matematiksel temellere dayanmaktadır.

## 🎭 Kriptografi Sahnesinin Değişmez Aktörleri: Alice, Bob ve Eve



Kriptografik protokolleri, ağ yapılarını veya şifreleme algoritmalarını incelerken "A kişisi B kişisine mesaj atarken C kişisi dinliyor" demek yerine, kriptografi literatürüne yerleşmiş olan o **meşhur üçlüyü** kullanırız. Bu isimler, karmaşık senaryoları insanileştirmek ve **evrensel bir standart** oluşturmak için seçilmiştir:

* 👩 **Alice (Gönderici):** Hikayenin her zaman **başlangıç noktasıdır**. Gizli ve önemli bir mesajı, güvenli bir şekilde karşı tarafa iletmek isteyen asıl kişidir.
* 👨 **Bob (Alıcı):** Alice'in mesajını bekleyen ve onu şifreli halinden kurtarıp **okuması gereken meşru alıcıdır**.
* 🦹‍♀️ **Eve (Dinleyici / Eavesdropper):** Alice ve Bob arasındaki iletişim kanalını sinsi bir şekilde **dinleyen saldırgandır**. Genellikle pasif bir saldırgandır; mesajı değiştiremez ama şifreli metni ele geçirip **matematiksel analizlerle (kriptanaliz)** içindeki orijinal bilgiyi çözmeye çalışır.