# DES - Data Encryption Standard ve Feistel Ağı

DES, modern kriptografinin dönüm noktasıdır. 1970'lerde IBM tarafından "Lucifer" projesi adıyla geliştirilen ve 1977'de Amerikan Ulusal Standartlar Bürosu (NBS, günümüzdeki NIST) tarafından federal bir standart olarak kabul edilen simetrik (gizli) anahtarlı bir blok şifreleme algoritmasıdır. 

Günümüzde 56 bitlik kısa anahtar boyutu nedeniyle kaba kuvvet (brute-force) saldırılarına karşı yetersiz kalıp yerini AES algoritmasına bırakmış olsa da, modern şifreleme mimarilerinin (Feistel Ağları, S-Box ve P-Box mantığı) temelini anlamak için DES'i öğrenmek bir kriptografi öğrencisi için zorunluluktur.

## 💻 Harflerden Bitlere Geçiş

Şu ana kadar gördüğümüz klasik şifrelemelerde (Sezar, Afin, Vigenère, Permütasyon) hep İngiliz alfabesi ($\mathbb{Z}_{26}$) üzerinden karakterlerin veya sayıların yerini/kimliğini değiştirdik. 

DES ile birlikte bu "insan odaklı" yapı tamamen terk edilir. Algoritma harflerin ne olduğunu bilmez; doğrudan **bilgisayar işlemcisinin dilinde (0'lar ve 1'ler)** çalışır. Açık metniniz (ister bir metin dosyası, ister bir fotoğraf, ister bir video olsun) önce makine diline çevrilir ve tamamen **bit (binary)** seviyesindeki işlemlerle (XOR, bit kaydırma, bit permütasyonları) şifrelenir.

## 🔑 Blok ve Anahtar Yapısı

DES algoritması veriyi bir bütün olarak değil, **64-bitlik bloklar** halinde işler. Yani mesajınız ne kadar uzun olursa olsun, sistem bunu 64 bitlik parçalara böler ve her bir bloğu sırayla şifreler.

Algoritmanın kalbindeki anahtar yapısı ise kriptografi tarihindeki en ilginç tasarımlardan biridir:
* **Girdi Anahtarı:** DES algoritmasına dışarıdan verilen orijinal anahtar **64 bittir**.
* **Efektif (Gerçek) Anahtar Boyutu:** Orijinal 64 bitlik anahtarın her 8. biti (8, 16, 24... 64) bir **Eşlik Biti (Parity Bit)** olarak hata kontrolü amacıyla kullanılır ve şifreleme işlemine dahil edilmez. Bu yüzden DES'in gerçek kriptografik gücü **56 bit** ile sınırlıdır.


## DES Anahtar Üretim Algoritması (Key Schedule)

DES algoritması, her biri 64 bitlik veri bloklarını şifrelemek için tam 16 döngü (round) kullanır. Şifrelemenin güvenli olabilmesi için bu 16 döngünün her birine, orijinal anahtardan türetilmiş **farklı ve benzersiz 48 bitlik alt anahtarlar ($K_1, K_2, \dots, K_{16}$)** verilmesi gerekir.

İşte 64 bitlik tek bir kök anahtardan, 16 farklı mermi (alt anahtar) üreten bu fabrikaya **Key Schedule (Anahtar Zamanlaması)** denir. İşlem 3 temel aşamada gerçekleşir:

### Adım 1: PC-1 (Eşlik Bitlerini Çöpe Atma ve İkiye Bölme)

$$K = b_1, b_2, b_3, \dots, b_{63}, b_{64}$$

Sisteme giren orijinal kök anahtar ($K$), 64 bitten oluşur. Ancak algoritma bu anahtarın her 8. bitini (8, 16, 24, 32, 40, 48, 56, 64) bir iletişim kontrolü olan **Eşlik Biti (Parity Bit)** olarak görür. 

<!-- center a div -->
<div style="display: flex; justify-content: center; margin: 0px 0;">

<table>
  <tr><td>57</td><td>49</td><td>41</td><td>33</td><td>25</td><td>17</td><td>9</td></tr>
  <tr><td>1</td><td>58</td><td>50</td><td>42</td><td>34</td><td>26</td><td>18</td></tr>
  <tr><td>10</td><td>2</td><td>59</td><td>51</td><td>43</td><td>35</td><td>27</td></tr>
  <tr><td>19</td><td>11</td><td>3</td><td>60</td><td>52</td><td>44</td><td>36</td></tr>
  <tr><td>63</td><td>55</td><td>47</td><td>39</td><td>31</td><td>23</td><td>15</td></tr>
  <tr><td>7</td><td>62</td><td>54</td><td>46</td><td>38</td><td>30</td><td>22</td></tr>
  <tr><td>14</td><td>6</td><td>61</td><td>53</td><td>45</td><td>37</td><td>29</td></tr>
  <tr><td>21</td><td>13</td><td>5</td><td>28</td><td>20</td><td>12</td><td>4</td></tr>
</table>
</div>
<center style="font-size: 0.85em; color: #666; margin-top: -10px;"> PC-1 Tablosu (56-bit Seçim): </center>

Anahtar dizisi `PC-1 (Permuted Choice 1)` matrisinden geçirilir. Bu matrisin içinde eşlik bitlerinin indeksleri bulunmaz; bu sayede 8 adet eşlik biti otomatik olarak çöpe atılır. Kalan **56 bit**, matrisin üst yarısı ($C_0$) ve alt yarısı ($D_0$) olacak şekilde doğrudan karıştırılarak ikiye bölünür:

Matematiksel olarak bu ayrışma şöyledir:
$$
\begin{aligned}
K_{64} &\xrightarrow{\text{PC-1 Uygulanır}} K_{56} \\
\end{aligned}
$$

Sonra bu 56 bitlik anahtar ikiye bölünür:

$$
\begin{aligned}
K_{56} &= \underbrace{b_{57}, b_{49}, \dots, b_{36}}_{C_0 \text{ (28 bit)}} \ \ \underbrace{b_{63}, b_{55}, \dots, b_{4}}_{D_0 \text{ (28 bit)}}
\end{aligned}
$$

### Adım 2: Dairesel Sola Kaydırma (Circular Left Shift)
Algoritma 16 döngü boyunca $C$ ve $D$ yarılarını kendi içlerinde sola doğru kaydırarak sürekli günceller. "Dairesel" olmasının esprisi şudur: **Sınırın dışına çıkan bit silinmez, bloğun en sağına geri döner.**

> **🔍 Görsel Örnek (1-bit Kaydırma):**
> 8-bitlik örnek bir $X$ bloğumuz olsun: $\mathbf{1} 0 1 1 0 0 1 1$
> 1 bit sola kaydırıldığında, en soldaki $\mathbf{1}$ kopar ve en sağa kuyruk olur:
> Yeni $X$: $0 1 1 0 0 1 1 \mathbf{1}$

Kaydırma miktarı döngünün numarasına göre sabittir:
* **1., 2., 9. ve 16. Döngülerde:** Sadece **1 bit** dairesel kaydırılır.
* **Diğer tüm döngülerde:** **2 bit** dairesel kaydırılır.

*Örneğin 1. ve 2. döngüler için yeni yarılar şu şekilde oluşur:*
$C_1 = LeftShift(C_0, 1) \quad \text{ve} \quad D_1 = LeftShift(D_0, 1)$
$C_2 = LeftShift(C_1, 1) \quad \text{ve} \quad D_2 = LeftShift(D_1, 1)$

### Adım 3: PC-2 (Sıkıştırma Permütasyonu)
Döngüye ait kaydırılmış $C_i$ ve $D_i$ yarıları yan yana getirilerek birleştirilir ($28 + 28 = 56 \text{ bit}$). Ancak şifreleme çekirdeğimiz (Feistel fonksiyonu), her döngüde 48 bitlik bir anahtara ihtiyaç duymaktadır. 

Bu noktada `PC-2 (Permuted Choice 2)` tablosu devreye girer. Bu tablo tıpkı bir filtre gibi davranarak; 56 bitlik diziyi karıştırır ve içinden önceden belirlenmiş **8 biti atarak (sıkıştırarak)** o döngünün asıl silahı olan **48 bitlik $K_i$ alt anahtarını** üretir.

**PC-2 Matrisi (48-bit Seçim):**
> 14, 17, 11, 24,  1,  5,
>  3, 28, 15,  6, 21, 10,
> 23, 19, 12,  4, 26,  8,
> 16,  7, 27, 20, 13,  2,
> 41, 52, 31, 37, 47, 55,
> 30, 40, 51, 45, 33, 48,
> 44, 49, 39, 56, 34, 53,
> 46, 42, 50, 36, 29, 32

Matematiksel dönüşümün jilet gibi özeti:
$$
\begin{aligned}
\underbrace{C_i}_{28\text{-bit}} \ || \ \underbrace{D_i}_{28\text{-bit}} \quad &\xrightarrow{\text{Birleştirilir}} \quad CD_i \ (56\text{-bit}) \\
CD_i \ (56\text{-bit}) \quad &\xrightarrow{\text{PC-2 Filtresi}} \quad \mathbf{K_i \ (48\text{-bit Alt Anahtar})}
\end{aligned}
$$

Bu 3 adım, 16 döngünün tamamı için zincirleme olarak tekrarlanır ve şifreleme işleminde kullanılacak olan o meşhur 16 anahtar seti hazır hale getirilmiş olur.