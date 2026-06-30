---
title: Hill Şifreleme
description: Matris çarpımına dayanan Hill şifreleme sisteminin anahtar yapısını, blok mantığını ve deşifreleme sürecini açıklar.
---

# Hill Şifreleme

Klasik şifreleme sistemlerinin istatistiksel frekans analizine yenik düşmesini engellemek için tasarlanan Hill Şifrelemesi, kriptografiye **Lineer Cebiri (Matrisleri)** sokan ilk büyük devrimdir. 

Bu sistemde harfler tek başına değil, belirlenen bir $n$ uzunluğundaki **sütun vektörleri** halinde gruplanarak bir matris ile çarpılır.

## Sistemin Formal Tanımı

Hill sisteminde işlemler $n$ boyutlu vektörler ve $n \times n$ boyutlu kare matrisler üzerinden yürütülür. (Notlarımızda kolaylık olması adına $n=2$, yani $2 \times 2$ matrisler kullanacağız).

<div class="math-block definition">
  <div class="math-block-title">

  Tanım: Hill Şifrelemesinin Matematiksel Modeli

  </div>
  
  * **Açık Metin ($\mathcal{P}$):** Elemanları $\mathbb{Z}_{26}$'dan alınan $n$ boyutlu sütun vektörlerinin kümesi.
  * **Şifreli Metin ($\mathcal{C}$):** Elemanları $\mathbb{Z}_{26}$'dan alınan $n$ boyutlu sütun vektörlerinin kümesi.
  * **Anahtar Uzayı ($\mathcal{K}$):** Elemanları $\mathbb{Z}_{26}$'da olan ve mod 26'ya göre tersi alınabilen (invertible) tüm $n \times n$ boyutlu kare matrisler.
  * **Şifreleme Fonksiyonu ($\mathcal{E}$):** Her $K \in \mathcal{K}$ anahtar matrisi ve $\mathbf{x} \in \mathcal{P}$ açık metin vektörü için:
    $$e_K(\mathbf{x}) \equiv K \cdot \mathbf{x} \pmod{26}$$
  * **Deşifreleme Fonksiyonu ($\mathcal{D}$):** Her $\mathbf{y} \in \mathcal{C}$ şifreli metin vektörü için:
    $$d_K(\mathbf{y}) \equiv K^{-1} \cdot \mathbf{y} \pmod{26}$$
</div>

## ⚠️ Anahtar Seçme Koşulu: Determinant ve Ters Matris

Afin şifrelemesinde anahtarın birebir olabilmesi için $a$ değerinin $26$ ile aralarında asal olmasını istemiştik. Hill şifrelemesinde ise matrisin **tersinin olabilmesi ($K^{-1}$'in hesaplanabilmesi)** şarttır.

Bir matrisin tersinin formülü şu şekildedir:
$$K^{-1} = \frac{1}{\det(K)} \cdot \text{adj}(K) \pmod{26}$$

Bu formülün mod 26'da çalışabilmesi için kesirli kısımdaki $\det(K)$ değerinin mod 26'da çarpımsal bir tersi olması gerekir.

::: info 📌 Geçerli Bir Hill Anahtarı İçin Altın Kural
Bir $K$ matrisinin Hill şifrelemesinde anahtar olarak kullanılabilmesi için determinantının $26$ ile aralarında asal olması **zorunludur**:
$$\gcd(\det(K), 26) = 1$$

Pratik bir deyişle; matrisin determinantı mod 26'da **çift sayı olamaz** (2'ye bölünür) ve **$13$ olamaz** (13'e bölünür). Eğer determinant bu kurala uymuyorsa, sistem o şifreyi bir daha asla geri açamaz!
:::

::: info 📌 Dolgu (Padding) Kuralı
Eğer şifreleyeceğiniz mesajın harf sayısı, vektör boyutu olan $n$'in tam katı değilse, mesajın sonuna anlamsız harfler (genellikle 'X' veya 'Z') eklenerek bloklar tamamlanır.
:::

## 📝 Çözümlü Uygulamalar

Aşağıdaki örneklerde işlemleri **Harf - Sayı Dönüşüm Tablosunu** kullanarak yapınız. Vektör boyutumuz $n=2$'dir.

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Açık metni "HELP" olan mesajı, aşağıda verilen K matrisi ile şifreleyiniz.
  
  Anahtar Matris: 
  $$K = \begin{pmatrix} 3 & 3 \\ 2 & 5 \end{pmatrix}$$

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **Çözüm:**
  Öncelikle anahtarın geçerli olup olmadığını determinant ile kontrol edelim:
  $\det(K) = (3 \cdot 5) - (3 \cdot 2) = 15 - 6 = 9$
  $\gcd(9, 26) = 1$ olduğu için bu kusursuz bir anahtardır.

  Metnimiz "HELP", 2'li bloklara ayrılır: **HE** ve **LP**.

  **1. Blok: HE ($7, 4$)**
  $$\begin{pmatrix} 3 & 3 \\ 2 & 5 \end{pmatrix} \begin{pmatrix} 7 \\ 4 \end{pmatrix} = \begin{pmatrix} 3(7) + 3(4) \\ 2(7) + 5(4) \end{pmatrix} = \begin{pmatrix} 21 + 12 \\ 14 + 20 \end{pmatrix} = \begin{pmatrix} 33 \\ 34 \end{pmatrix}$$
  Mod 26'ya göre denklerini alalım:
  $$\begin{pmatrix} 33 \\ 34 \end{pmatrix} \equiv \begin{pmatrix} 7 \\ 8 \end{pmatrix} \pmod{26}$$
  Tabloya göre $7 =$ **H**, $8 =$ **I**. (İlk şifreli blok: **HI**)

  **2. Blok: LP ($11, 15$)**
  $$\begin{pmatrix} 3 & 3 \\ 2 & 5 \end{pmatrix} \begin{pmatrix} 11 \\ 15 \end{pmatrix} = \begin{pmatrix} 33 + 45 \\ 22 + 75 \end{pmatrix} = \begin{pmatrix} 78 \\ 97 \end{pmatrix}$$
  Mod 26'ya göre denklerini alalım:
  $78 = 26 \cdot 3 + 0 \equiv 0 \pmod{26}$
  $97 = 26 \cdot 3 + 19 \equiv 19 \pmod{26}$
  $$\begin{pmatrix} 78 \\ 97 \end{pmatrix} \equiv \begin{pmatrix} 0 \\ 19 \end{pmatrix} \pmod{26}$$
  Tabloya göre $0 =$ **A**, $19 =$ **T**. (İkinci şifreli blok: **AT**)

  **Sonuç:** `HELP` kelimesi Hill şifrelemesiyle `HIAT` olarak şifrelenir.
  *(Dikkat edin: Açık metindeki 'E' ve 'L' tamamen farklı harflere dönüşürken, aralarındaki istatistiksel bağ matrisin içinde eridi gitti!)*
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>

<div class="math-block example">
  <div class="math-block-title">

  Örnek: Şifreli "HIAT" metnini, aynı K anahtar matrisini kullanarak deşifre ediniz.
  
  Anahtar Matris: 
  $$K = \begin{pmatrix} 3 & 3 \\ 2 & 5 \end{pmatrix}$$

  </div>

  ::: details 💡 Çözümü Göster / Gizle
  **Çözüm:**
  Deşifreleme için $d_K(\mathbf{y}) \equiv K^{-1} \cdot \mathbf{y} \pmod{26}$ formülünü kullanacağız. Önce $K^{-1}$ ters matrisini bulmalıyız.

  **Adım 1: Determinantın Tersini Bulmak**
  $\det(K) = 9$ bulmuştuk. 9'un mod 26'daki çarpımsal tersini ($9^{-1}$) arıyoruz:
  $9 \cdot x \equiv 1 \pmod{26} \implies x = 3$ (Çünkü $9 \cdot 3 = 27 \equiv 1$).

  **Adım 2: Adjoint (Ek) Matrisi Bulmak**
  $2 \times 2$ bir $\begin{pmatrix} a & b \\ c & d \end{pmatrix}$ matrisinin ek matrisi $\begin{pmatrix} d & -b \\ -c & a \end{pmatrix}$'dır.
  $$\text{adj}(K) = \begin{pmatrix} 5 & -3 \\ -2 & 3 \end{pmatrix}$$

  **Adım 3: Ters Matrisi ($K^{-1}$) Oluşturmak**
  $$K^{-1} \equiv 3 \cdot \begin{pmatrix} 5 & -3 \\ -2 & 3 \end{pmatrix} = \begin{pmatrix} 15 & -9 \\ -6 & 9 \end{pmatrix} \pmod{26}$$
  Eksi değerleri mod 26'da pozitife çevirelim ($-9 \equiv -9+26 = 17$, $-6 \equiv -6+26 = 20$):
  $$K^{-1} \equiv \begin{pmatrix} 15 & 17 \\ 20 & 9 \end{pmatrix} \pmod{26}$$

  **Adım 4: Şifreli Blokları Ters Matris İle Çarpmak**

  **1. Blok: HI ($7, 8$)**
  $$\begin{pmatrix} 15 & 17 \\ 20 & 9 \end{pmatrix} \begin{pmatrix} 7 \\ 8 \end{pmatrix} = \begin{pmatrix} 105 + 136 \\ 140 + 72 \end{pmatrix} = \begin{pmatrix} 241 \\ 212 \end{pmatrix}$$
  $241 \equiv 7 \pmod{26} \implies$ **H**
  $212 \equiv 4 \pmod{26} \implies$ **E**

  **2. Blok: AT ($0, 19$)**
  $$\begin{pmatrix} 15 & 17 \\ 20 & 9 \end{pmatrix} \begin{pmatrix} 0 \\ 19 \end{pmatrix} = \begin{pmatrix} 0 + 323 \\ 0 + 171 \end{pmatrix} = \begin{pmatrix} 323 \\ 171 \end{pmatrix}$$
  $323 \equiv 11 \pmod{26} \implies$ **L**
  $171 \equiv 15 \pmod{26} \implies$ **P**

  **Sonuç:** Matris çarpımları ve mod 26 kuralları bizi tekrar orijinal `HELP` mesajına ulaştırdı!
  
  <span style="float: right;">$\boxtimes$</span>
  <div style="clear: both;"></div>
  :::
</div>