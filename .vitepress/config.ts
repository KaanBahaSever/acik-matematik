import { defineConfig } from 'vitepress'
import container from 'markdown-it-container'

function customContainer(name: string, label: string) {
  return [
    container,
    name,
    {
      render(tokens: any[], idx: number) {
        const token = tokens[idx]
        if (token.nesting === 1) {
          const info = token.info.trim().slice(name.length).trim()
          const title = info || label
          return `<div class="custom-container ${name}"><div class="custom-container-title">${title}</div>\n`
        }
        return '</div>\n'
      }
    }
  ] as const
}

export default defineConfig({
  base: '/',
  title: '🌿 Açık Matematik',
  description: 'Açık kaynak kapsamlı matematik ders notları',
  cleanUrls: true,
  ignoreDeadLinks: true,
  locales: {
    root: {
      label: 'Türkçe',
      lang: 'tr-TR',
      themeConfig: {
        nav: [
          { text: 'Ana Sayfa', link: '/' },
          { text: 'Dersler', link: '/dersler/' }
        ],
      }
    },
    /* en: {
      label: 'English',
      lang: 'en-US',
      link: '/en/',
      title: 'Math Notebook',
      description: 'Open-source comprehensive mathematics lecture notes'
    } */
  },
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/favicon2.svg' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: 'true' }],
    ['link', { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Lora:ital,wght@0,400;0,600;1,400&family=Merriweather:wght@300;700&display=swap' }]
  ],
  themeConfig: {
    outline: {
      label: 'Bu Sayfada',
      level: [2, 3] // H2 ve H3 başlıklarını sağ menüde gösterir (Akademik notlar için idealdir)
    },

    // 2. YUKARI DÖN BUTONU ("Return to top") ÇEVİRİSİ
    returnToTopLabel: 'Başa Dön',

    // 3. MOBİL MENÜ VE TEMA BUTONLARI ÇEVİRİLERİ (Ekstra jiletlik katar)
    sidebarMenuLabel: 'Menü',
    darkModeSwitchLabel: 'Görünüm',
    lightModeSwitchTitle: 'Açık Tema Geç',
    darkModeSwitchTitle: 'Koyu Temaya Geç',

    socialLinks: [{ icon: 'github', link: 'https://github.com/KaanBahaSever/math-notebook' }],
    i18nRouting: true,
    /* aside: false, */
    docFooter: {
      prev: 'Önceki Konu',
      next: 'Sonraki Konu'
    },
    footer: {
      message: 'Akademik amaçlarla tasarlanmış açık kaynaklı eğitim arşivi.',
      copyright: 'Copyright © 2026 | Tüm Hakları Saklıdır'
    },
    sidebar: {
      '/dersler/analitik-geometri/': [
        {
          text: '📐 Analitik Geometri',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/analitik-geometri/' },
            {
              text: 'Temel Kavramlar',
              collapsed: true,
              items: [
                { text: 'Tanımlar', link: '/dersler/analitik-geometri/temel/tanimlar' },
                { text: 'Koordinat Sistemleri', link: '/dersler/analitik-geometri/temel/koordinat-sistemleri' },
                { text: 'Koordinat Dönüşümleri', link: '/dersler/analitik-geometri/temel/koordinat-donusumleri' }
              ]
            },
            {
              text: 'Vektörler',
              collapsed: true,
              items: [
                { text: 'R³\'te Vektörler', link: '/dersler/analitik-geometri/vektorler/r3-vektorler' },
                { text: 'İç Çarpım', link: '/dersler/analitik-geometri/vektorler/ic-carpim' },
                { text: 'Vektörel ve Karma Çarpım', link: '/dersler/analitik-geometri/vektorler/vektorel-karma-carpim' }
              ]
            },
            {
              text: 'Uzay Geometrisi',
              collapsed: true,
              items: [
                { text: 'Doğru Denklemleri', link: '/dersler/analitik-geometri/uzay/dogru-denklemleri' },
                { text: 'Düzlem Denklemleri', link: '/dersler/analitik-geometri/uzay/duzlem-denklemleri' },
                { text: 'Doğru ve Düzlem İlişkisi', link: '/dersler/analitik-geometri/uzay/dogru-duzlem-iliskisi' },
                { text: 'Simetri', link: '/dersler/analitik-geometri/uzay/simetri' }
              ]
            },
            {
              text: 'Konikler',
              collapsed: true,
              items: [
                { text: 'Giriş ve Çember', link: '/dersler/analitik-geometri/konikler/giris-cember' },
                { text: 'Elips, Hiperbol ve Parabol', link: '/dersler/analitik-geometri/konikler/elips-hiperbol-parabol' },
                { text: 'Sınıflandırma', link: '/dersler/analitik-geometri/konikler/siniflandirma' },
                { text: 'Kutupsal Denklemler', link: '/dersler/analitik-geometri/konikler/kutupsal-denklemler' }
              ]
            },
            {
              text: 'Yüzeyler',
              collapsed: true,
              items: [
                { text: 'Özel Eğriler', link: '/dersler/analitik-geometri/yuzeyler/ozel-egriler' },
                { text: 'Özel Yüzeyler', link: '/dersler/analitik-geometri/yuzeyler/ozel-yuzeyler' },
                { text: 'Silindirik ve Küresel Koordinatlar', link: '/dersler/analitik-geometri/yuzeyler/silindirik-kuresel' }
              ]
            }
          ]
        }
      ],
      '/dersler/analiz/': [
        {
          text: '📊 Analiz',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/analiz/' },
            {
              text: 'Analiz 1',
              collapsed: true,
              items: [
                {
                  text: 'Reel Sayılar',
                  collapsed: true,
                  items: [
                    { text: 'Temeller', link: '/dersler/analiz/analiz-1/reel-sayilar/temeller' },
                    { text: 'Yığılma Noktaları', link: '/dersler/analiz/analiz-1/reel-sayilar/yigilma-noktalari' },
                    { text: 'Bolzano-Weierstrass', link: '/dersler/analiz/analiz-1/reel-sayilar/bolzano-weierstrass' }
                  ]
                },
                {
                  text: 'Diziler',
                  collapsed: true,
                  items: [
                    { text: 'Limit', link: '/dersler/analiz/analiz-1/diziler/limit' },
                    { text: 'Sıkıştırma Teoremi', link: '/dersler/analiz/analiz-1/diziler/sikistirma' },
                    { text: 'Cauchy Dizileri', link: '/dersler/analiz/analiz-1/diziler/cauchy' }
                  ]
                },
                {
                  text: 'Limit',
                  collapsed: true,
                  items: [
                    { text: 'Kavram', link: '/dersler/analiz/analiz-1/limit/kavram' },
                    { text: 'Cauchy Ölçütü', link: '/dersler/analiz/analiz-1/limit/cauchy-olcutu' },
                    { text: 'Sonsuz Limitler', link: '/dersler/analiz/analiz-1/limit/sonsuz' }
                  ]
                },
                {
                  text: 'Süreklilik',
                  collapsed: true,
                  items: [
                    { text: 'Çeşitleri', link: '/dersler/analiz/analiz-1/sureklilik/cesitleri' },
                    { text: 'Teoremler', link: '/dersler/analiz/analiz-1/sureklilik/teoremler' },
                    { text: 'Düzgün Süreklilik', link: '/dersler/analiz/analiz-1/sureklilik/duzgun-sureklilik' }
                  ]
                }
              ]
            },
            {
              text: 'Analiz 2',
              collapsed: true,
              items: [
                {
                  text: 'Türev',
                  collapsed: true,
                  items: [
                    { text: 'Temel Kurallar', link: '/dersler/analiz/analiz-2/turev/temel-kurallar' },
                    { text: 'Leibniz Kuralı', link: '/dersler/analiz/analiz-2/turev/leibniz' },
                    { text: 'Ters ve Kapalı Fonksiyonların Türevi', link: '/dersler/analiz/analiz-2/turev/ters-kapali' }
                  ]
                },
                {
                  text: 'Uygulamalar',
                  collapsed: true,
                  items: [
                    { text: 'Ortalama Değer Teoremi', link: '/dersler/analiz/analiz-2/uygulamalar/ortalama-deger' },
                    { text: 'L\'Hôpital Kuralı', link: '/dersler/analiz/analiz-2/uygulamalar/lhopital' },
                    { text: 'Ekstremum Değerler', link: '/dersler/analiz/analiz-2/uygulamalar/ekstremum' }
                  ]
                },
                {
                  text: 'Belirsiz İntegral',
                  collapsed: true,
                  items: [
                    { text: 'Yöntemler', link: '/dersler/analiz/analiz-2/belirsiz-integral/yontemler' },
                    { text: 'Rasyonel Fonksiyonlar', link: '/dersler/analiz/analiz-2/belirsiz-integral/rasyonel' },
                    { text: 'Trigonometrik İntegraller', link: '/dersler/analiz/analiz-2/belirsiz-integral/trigonometrik' }
                  ]
                },
                {
                  text: 'Belirli İntegral',
                  collapsed: true,
                  items: [
                    { text: 'Riemann İntegrali', link: '/dersler/analiz/analiz-2/belirli-integral/riemann' },
                    { text: 'Kalkülüsün Temel Teoremi', link: '/dersler/analiz/analiz-2/belirli-integral/kalkulus-temel' },
                    { text: 'Uygulamalar', link: '/dersler/analiz/analiz-2/belirli-integral/uygulamalar' }
                  ]
                },
                {
                  text: 'Seriler',
                  collapsed: true,
                  items: [
                    { text: 'Yakınsaklık', link: '/dersler/analiz/analiz-2/seriler/yakinsaklik' },
                    { text: 'Alterne Seriler', link: '/dersler/analiz/analiz-2/seriler/alterne' },
                    { text: 'Mutlak ve Şartlı Yakınsaklık', link: '/dersler/analiz/analiz-2/seriler/mutlak-sartli' }
                  ]
                },
                {
                  text: 'Kuvvet Serileri',
                  collapsed: true,
                  items: [
                    { text: 'Giriş', link: '/dersler/analiz/analiz-2/kuvvet-serileri/giris' },
                    { text: 'Taylor Serileri', link: '/dersler/analiz/analiz-2/kuvvet-serileri/taylor' },
                    { text: 'Analitik Fonksiyonlar', link: '/dersler/analiz/analiz-2/kuvvet-serileri/analitik' }
                  ]
                }
              ]
            },
            {
              text: 'Analiz 3',
              collapsed: true,
              items: [
                {
                  text: 'Fonksiyon Dizileri',
                  collapsed: true,
                  items: [
                    { text: 'Noktasal Yakınsaklık', link: '/dersler/analiz/analiz-3/fonksiyon-dizileri/noktasal' },
                    { text: 'Düzgün Yakınsaklık', link: '/dersler/analiz/analiz-3/fonksiyon-dizileri/duzgun' }
                  ]
                },
                {
                  text: 'Seriler',
                  collapsed: true,
                  items: [
                    { text: 'Fonksiyon Serileri ve Yakınsaklık', link: '/dersler/analiz/analiz-3/fonksiyon-serileri/yakinsaklik' },
                    { text: 'Kuvvet Serileri', link: '/dersler/analiz/analiz-3/seriler/kuvvet-serileri' },
                    { text: 'Fourier Serilerine Giriş', link: '/dersler/analiz/analiz-3/seriler/fourier-giris' },
                    { text: 'Fourier Uygulamaları', link: '/dersler/analiz/analiz-3/seriler/fourier-uygulamalari' }
                  ]
                },
                {
                  text: 'Genelleştirilmiş İntegraller',
                  collapsed: true,
                  items: [
                    { text: '1. Tip Genelleştirilmiş İntegraller', link: '/dersler/analiz/analiz-3/genellestirilmis/tip-1' },
                    { text: '2. Tip Genelleştirilmiş İntegraller', link: '/dersler/analiz/analiz-3/genellestirilmis/tip-2' },
                    { text: 'Euler İntegralleri', link: '/dersler/analiz/analiz-3/genellestirilmis/euler' }
                  ]
                },
                { text: 'Parametrik Eğriler', link: '/dersler/analiz/analiz-3/parametrik/giris' }
              ]
            },
            {
              text: 'Analiz 4',
              collapsed: true,
              items: [
                {
                  text: 'R^n Uzayı',
                  collapsed: true,
                  items: [
                    { text: 'Cebirsel Yapı', link: '/dersler/analiz/analiz-4/rn-uzayi/cebirsel-yapi' },
                    { text: 'Topoloji', link: '/dersler/analiz/analiz-4/rn-uzayi/topoloji' },
                    { text: 'Diziler', link: '/dersler/analiz/analiz-4/rn-uzayi/diziler' }
                  ]
                },
                {
                  text: 'Limit ve Süreklilik',
                  collapsed: true,
                  items: [
                    { text: 'Limit', link: '/dersler/analiz/analiz-4/limit-sureklilik/limit' },
                    { text: 'Süreklilik', link: '/dersler/analiz/analiz-4/limit-sureklilik/sureklilik' }
                  ]
                },
                {
                  text: 'Türev',
                  collapsed: true,
                  items: [
                    { text: 'Kısmi Türev', link: '/dersler/analiz/analiz-4/turev/kismi-turev' },
                    { text: 'Yüksek Mertebeden Türevler', link: '/dersler/analiz/analiz-4/turev/yuksek-mertebe' },
                    { text: 'Taylor Teoremi', link: '/dersler/analiz/analiz-4/turev/taylor' }
                  ]
                },
                {
                  text: 'Optimizasyon',
                  collapsed: true,
                  items: [
                    { text: 'Ekstremum', link: '/dersler/analiz/analiz-4/optimizasyon/ekstremum' },
                    { text: 'Kapalı Fonksiyonlar', link: '/dersler/analiz/analiz-4/optimizasyon/kapali-fonksiyonlar' },
                    { text: 'Bağlı Ekstremum', link: '/dersler/analiz/analiz-4/optimizasyon/bagli-ekstremum' },
                    { text: 'Değişken Değişimi', link: '/dersler/analiz/analiz-4/optimizasyon/degisken-degisimi' }
                  ]
                }
              ]
            }
          ]
        }
      ],
      '/dersler/bilgisayarda-matematik-uygulamalari/': [
        {
          text: '💻 Bilgisayarda Matematik Uygulamaları',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/bilgisayarda-matematik-uygulamalari/' },
            {
              text: 'Temel Bilgiler',
              collapsed: true,
              items: [
                { text: 'Arayüz ve Hesaplamalar', link: '/dersler/bilgisayarda-matematik-uygulamalari/temel/arayuz-hesaplamalar' },
                { text: 'Değişkenler ve Listeler', link: '/dersler/bilgisayarda-matematik-uygulamalari/temel/degiskenler-listeler' },
                { text: 'Fonksiyon ve Sabit Tanımlama', link: '/dersler/bilgisayarda-matematik-uygulamalari/temel/fonksiyon-sabit-tanimlama' }
              ]
            },
            {
              text: 'Cebirsel İşlemler',
              collapsed: true,
              items: [
                { text: 'Türev, İntegral ve Limit', link: '/dersler/bilgisayarda-matematik-uygulamalari/cebir/turev-integral-limit' },
                { text: 'Seriler ve Kuvvet Serileri', link: '/dersler/bilgisayarda-matematik-uygulamalari/cebir/seriler-kuvvet-serileri' },
                { text: 'Denklem Sistemleri', link: '/dersler/bilgisayarda-matematik-uygulamalari/cebir/denklem-sistemleri' },
                { text: 'Sembolik ve Sayısal Dönüşümler', link: '/dersler/bilgisayarda-matematik-uygulamalari/cebir/sembolik-sayisal-donusumler' },
                { text: 'Koşullar ve Yerine Koyma', link: '/dersler/bilgisayarda-matematik-uygulamalari/cebir/kosullar-yerine-koyma' }
              ]
            },
            {
              text: 'Görselleştirme',
              collapsed: true,
              items: [
                { text: 'Grafikler ve Çizimler', link: '/dersler/bilgisayarda-matematik-uygulamalari/gorsellestirme/grafikler-cizimler' },
                { text: 'Çok Değişkenli Fonksiyonlar', link: '/dersler/bilgisayarda-matematik-uygulamalari/gorsellestirme/cok-degiskenli-fonksiyonlar' },
                { text: 'Vektörler ve Matrisler', link: '/dersler/bilgisayarda-matematik-uygulamalari/gorsellestirme/vektorler-matrisler' }
              ]
            },
            {
              text: 'Simülasyon ve Analiz',
              collapsed: true,
              items: [
                { text: 'Veri Analizi', link: '/dersler/bilgisayarda-matematik-uygulamalari/simulasyon/veri-analizi' },
                { text: 'Diferansiyel Denklemler', link: '/dersler/bilgisayarda-matematik-uygulamalari/simulasyon/diferansiyel-denklemler' },
                { text: 'İleri Düzey Uygulamalar', link: '/dersler/bilgisayarda-matematik-uygulamalari/simulasyon/ileri-duzey-uygulamalar' }
              ]
            },
            {
              text: 'İleri Konular',
              collapsed: true,
              items: [
                { text: 'İteratif Algoritmalar', link: '/dersler/bilgisayarda-matematik-uygulamalari/ileri/iteratif-algoritmalar' },
                { text: 'İleri Cebirsel Denklemler', link: '/dersler/bilgisayarda-matematik-uygulamalari/ileri/ileri-cebirsel-denklemler' },
                { text: 'Analitik Geometri Uygulamaları', link: '/dersler/bilgisayarda-matematik-uygulamalari/ileri/analitik-geometri-uygulamalari' }
              ]
            }
          ]
        }
      ],
      '/dersler/diferansiyel-denklemler/': [
        {
          text: '🧮 Diferansiyel Denklemler',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/diferansiyel-denklemler/' },
            {
              text: '1. Bölüm (Temeller ve 1. Mertebe)',
              collapsed: true,
              items: [
                { text: 'Kavram ve Sınıflandırma', link: '/dersler/diferansiyel-denklemler/1/kavram-siniflandirma' },
                { text: 'Başlangıç Değer Problemleri', link: '/dersler/diferansiyel-denklemler/1/baslangic-deger-problemleri' },
                { text: 'Değişkenlerine Ayrılabilen', link: '/dersler/diferansiyel-denklemler/1/degiskenlerine-ayrilabilen' },
                { text: 'Homojen Denklemler', link: '/dersler/diferansiyel-denklemler/1/homojen-denklemler' },
                { text: 'Birinci Mertebe Lineer', link: '/dersler/diferansiyel-denklemler/1/birinci-mertebe-lineer' },
                { text: 'Bernoulli ve Riccati Denklemleri', link: '/dersler/diferansiyel-denklemler/1/bernoulli-riccati' },
                { text: 'Tam Diferansiyel ve İntegrasyon Çarpanı', link: '/dersler/diferansiyel-denklemler/1/tam-diferansiyel-integrasyon-carpani' },
                { text: 'Değişken İçermeyen İndirgeme', link: '/dersler/diferansiyel-denklemler/1/degisken-icermeyen-indirgeme' },
                { text: 'İkinci Mertebe Uygulamalar', link: '/dersler/diferansiyel-denklemler/1/ikinci-mertebe-uygulamalar' },
                { text: 'Yüksek Dereceli', link: '/dersler/diferansiyel-denklemler/1/yuksek-dereceli' },
                { text: 'Yüksek Mertebe Lineer', link: '/dersler/diferansiyel-denklemler/1/yuksek-mertebe-lineer' }
              ]
            },
            {
              text: '2. Bölüm (Sistemler ve İleri Yöntemler)',
              collapsed: true,
              items: [
                { text: 'Sistemlere Giriş ve Matrisler', link: '/dersler/diferansiyel-denklemler/2/sistemlere-giris-matris' },
                { text: 'Sabit Katsayılı Sistemler', link: '/dersler/diferansiyel-denklemler/2/sabit-katsayili-sistemler' },
                { text: 'Değişken Katsayılı Sistemler', link: '/dersler/diferansiyel-denklemler/2/degisken-katsayili-sistemler' },
                { text: 'Homojen Olmayan Sistemler', link: '/dersler/diferansiyel-denklemler/2/homojen-olmayan-sistemler' },
                { text: 'Parametrelerin Değişimi', link: '/dersler/diferansiyel-denklemler/2/parametrelerin-degisimi' },
                { text: 'Laplace Dönüşümü', link: '/dersler/diferansiyel-denklemler/2/laplace-donusumu' },
                { text: 'Ters Laplace Dönüşümü', link: '/dersler/diferansiyel-denklemler/2/ters-laplace' },
                { text: 'Laplace ile Çözüm', link: '/dersler/diferansiyel-denklemler/2/laplace-ile-cozum' },
                { text: 'Seri Çözümleri', link: '/dersler/diferansiyel-denklemler/2/seri-cozumleri' },
                { text: 'Yok Etme ve Cramer Yöntemi', link: '/dersler/diferansiyel-denklemler/2/yok-etme-cramer' },
                { text: 'Yüksek Mertebeye Dönüştürme', link: '/dersler/diferansiyel-denklemler/2/yuksek-mertebeye-donusturme' }
              ]
            }
          ]
        }
      ],
      '/dersler/diferansiyel-geometri/': [
        {
          text: '🌀 Diferansiyel Geometri',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/diferansiyel-geometri/' },
            {
              text: '1. Bölüm (Eğriler Teorisi)',
              collapsed: true,
              items: [
                { text: 'Öklidyen Uzay ve Teğet Vektörler', link: '/dersler/diferansiyel-geometri/1/oklidyen-uzay-teget' },
                { text: 'Yön', link: '/dersler/diferansiyel-geometri/1/yon' },
                { text: 'Uzayda Eğriler', link: '/dersler/diferansiyel-geometri/1/uzayda-egriler' },
                { text: '1-Form ve 2-Form', link: '/dersler/diferansiyel-geometri/1/1-form-2-form' },
                { text: 'Wedge Çarpımı ve Dış Türev', link: '/dersler/diferansiyel-geometri/1/wedge-product-dis-turev' },
                { text: 'Çatı Alanları', link: '/dersler/diferansiyel-geometri/1/cati-alanlari' },
                { text: 'Teğet Dönüşümü', link: '/dersler/diferansiyel-geometri/1/teget-donusumu' },
                { text: 'Frenet-Serret Formülleri', link: '/dersler/diferansiyel-geometri/1/frenet-serret' },
                { text: 'Keyfi Hızlı Eğriler', link: '/dersler/diferansiyel-geometri/1/keyfi-hizli-egriler' },
                { text: 'Kovaryant Türev', link: '/dersler/diferansiyel-geometri/1/kovaryant-turev' },
                { text: 'Bağlantı', link: '/dersler/diferansiyel-geometri/1/baglanti' },
                { text: 'Cartan Yapı Denklemleri', link: '/dersler/diferansiyel-geometri/1/cartan-yapi' },
                { text: 'İzometri', link: '/dersler/diferansiyel-geometri/1/izometri' },
                { text: 'Kongrüans', link: '/dersler/diferansiyel-geometri/1/kongruans' }
              ]
            },
            {
              text: '2. Bölüm (Yüzeyler Teorisi)',
              collapsed: true,
              items: [
                { text: 'Yüzey Kavramı', link: '/dersler/diferansiyel-geometri/2/yuzey-kavrami' },
                { text: 'Yamalar', link: '/dersler/diferansiyel-geometri/2/yamalar' },
                { text: 'Vektörel Fonksiyonlar', link: '/dersler/diferansiyel-geometri/2/vektorel-fonksiyonlar' },
                { text: 'Birinci Temel Form', link: '/dersler/diferansiyel-geometri/2/birinci-temel-form' },
                { text: 'İkinci Temel Form', link: '/dersler/diferansiyel-geometri/2/ikinci-temel-form' },
                { text: 'Normal Eğrilik', link: '/dersler/diferansiyel-geometri/2/normal-egrilik' },
                { text: 'Gauss-Weingarten Formülleri', link: '/dersler/diferansiyel-geometri/2/gauss-weingarten' },
                { text: 'Gauss ve Ortalama Eğrilik', link: '/dersler/diferansiyel-geometri/2/gauss-ortalama' },
                { text: 'Eğrilik Çizgileri', link: '/dersler/diferansiyel-geometri/2/egrilik-cizgileri' },
                { text: 'Rodrigues ve Asimptotik Çizgiler', link: '/dersler/diferansiyel-geometri/2/rodrigues-asimptotik' },
                { text: 'Dupin Göstergesi', link: '/dersler/diferansiyel-geometri/2/dupin-gostergesi' },
                { text: 'İçsel Geometri', link: '/dersler/diferansiyel-geometri/2/icsel-geometri' },
                { text: 'Jeodezikler', link: '/dersler/diferansiyel-geometri/2/jeodezikler' }
              ]
            }
          ]
        }
      ],
      '/dersler/eliptik-egriler/': [
        {
          text: '🍩 Eliptik Eğriler',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/eliptik-egriler/' },
            {
              text: 'Temel Kavramlar',
              collapsed: true,
              items: [
                { text: 'Projektif Uzay ve Afin', link: '/dersler/eliptik-egriler/temel/projektif-uzay-afin' },
                { text: 'Kesişim ve Tekillik', link: '/dersler/eliptik-egriler/temel/kesisim-tekillik' },
                { text: 'Çift Periyotlu Fonksiyonlar', link: '/dersler/eliptik-egriler/temel/cift-periyotlu-fonksiyonlar' },
                { text: 'Weierstrass ℘ Fonksiyonu', link: '/dersler/eliptik-egriler/temel/weierstrass-p-fonksiyonu' }
              ]
            },
            {
              text: 'Grup Yapısı',
              collapsed: true,
              items: [
                { text: 'Konikler', link: '/dersler/eliptik-egriler/grup-yapisi/konikler' },
                { text: 'Weierstrass ve Genel Cisim', link: '/dersler/eliptik-egriler/grup-yapisi/weierstrass-genel-cisim' },
                { text: 'Grup Kuralları', link: '/dersler/eliptik-egriler/grup-yapisi/grup-kurallari' },
                { text: 'Endomorfizma ve Otomorfizma', link: '/dersler/eliptik-egriler/grup-yapisi/endomorfizma-otomorfizma' },
                { text: 'İzojeniler', link: '/dersler/eliptik-egriler/grup-yapisi/izojeniler' }
              ]
            },
            {
              text: 'Rasyonel Noktalar',
              collapsed: true,
              items: [
                { text: 'Q Üzerinde Eğriler', link: '/dersler/eliptik-egriler/rasyonel/q-uzerinde-egriler' },
                { text: 'Mordell-Weil Grubu', link: '/dersler/eliptik-egriler/rasyonel/mordell-weil-grubu' },
                { text: 'Örnekler ve Hesaplamalar', link: '/dersler/eliptik-egriler/rasyonel/ornekler-hesaplamalar' }
              ]
            },
            {
              text: 'Önemli Teoremler',
              collapsed: true,
              items: [
                { text: 'Weierstrass Sigma Fonksiyonu', link: '/dersler/eliptik-egriler/teorem/weierstrass-sigma' },
                { text: 'Yükseklik Fonksiyonu', link: '/dersler/eliptik-egriler/teorem/yukseklik-fonksiyonu' },
                { text: 'Mordell-Weil İspatı', link: '/dersler/eliptik-egriler/teorem/mordell-weil-ispati' }
              ]
            }
          ]
        }
      ],
      '/dersler/finans-matematigi/': [
        {
          text: '💰 Finans Matematiği',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/finans-matematigi/' },
            {
              text: 'Paranın Zaman Değeri',
              collapsed: true,
              items: [
                { text: 'Basit Faiz ve Denk Ödemeler', link: '/dersler/finans-matematigi/zaman-degeri/basit-faiz-denk-odemeler' },
                { text: 'Bileşik Faiz ve Eşdeğer Oranlar', link: '/dersler/finans-matematigi/zaman-degeri/bilesik-faiz-esdeger-oranlar' },
                { text: 'Basit İskonto ve Senetler', link: '/dersler/finans-matematigi/zaman-degeri/basit-iskonto-senetler' },
                { text: 'Bileşik İskonto ve Taksit', link: '/dersler/finans-matematigi/zaman-degeri/bilesik-iskonto-taksit' }
              ]
            },
            {
              text: 'Anüiteler',
              collapsed: true,
              items: [
                { text: 'Giriş ve Çeşitleri', link: '/dersler/finans-matematigi/anuiteler/giris-cesitleri' },
                { text: 'Dönem ve Faiz Hesabı', link: '/dersler/finans-matematigi/anuiteler/donem-faiz-hesabi' },
                { text: 'Amortisman', link: '/dersler/finans-matematigi/anuiteler/amortisman' },
                { text: 'Özel Anüiteler', link: '/dersler/finans-matematigi/anuiteler/ozel-anuiteler' }
              ]
            },
            {
              text: 'Finansal Araçlar',
              collapsed: true,
              items: [
                { text: 'Tahviller', link: '/dersler/finans-matematigi/araclar/tahviller' },
                { text: 'İndeksler', link: '/dersler/finans-matematigi/araclar/indeksler' },
                { text: 'Hayat Anüiteleri ve Sigorta', link: '/dersler/finans-matematigi/araclar/hayat-anuiteleri-sigorta' }
              ]
            },
            {
              text: 'Portföy Yönetimi',
              collapsed: true,
              items: [
                { text: 'Getiri ve Risk', link: '/dersler/finans-matematigi/portfoy/getiri-risk' },
                { text: 'Kovaryans ve Korelasyon', link: '/dersler/finans-matematigi/portfoy/kovaryans-korelasyon' },
                { text: 'Yeniden Dengeleme', link: '/dersler/finans-matematigi/portfoy/yeniden-dengeleme' },
                { text: 'Optimizasyon', link: '/dersler/finans-matematigi/portfoy/optimizasyon' }
              ]
            }
          ]
        }
      ],
      '/dersler/fonksiyonel-analiz/': [
        {
          text: '🧠 Fonksiyonel Analiz',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/fonksiyonel-analiz/' },
            {
              text: 'Temeller',
              collapsed: true,
              items: [
                { text: 'Alt Bölüm ve Uzaylar', link: '/dersler/fonksiyonel-analiz/temeller/alt-bolum-uzaylar' },
                { text: 'Vektör, Konveks ve Dengeli Kümeler', link: '/dersler/fonksiyonel-analiz/temeller/vektor-konveks-dengeli' },
                { text: 'Normlu Uzaylar ve Metrik', link: '/dersler/fonksiyonel-analiz/temeller/normlu-uzaylar-metrik' }
              ]
            },
            {
              text: 'Banach Uzayları',
              collapsed: true,
              items: [
                { text: 'Banach Uzayları Tanımı', link: '/dersler/fonksiyonel-analiz/banach/banach-uzaylari' },
                { text: 'Diziler ve Seriler', link: '/dersler/fonksiyonel-analiz/banach/diziler-seriler' },
                { text: 'Sonlu Boyut ve Kompaktlık', link: '/dersler/fonksiyonel-analiz/banach/sonlu-boyut-kompaktlik' },
                { text: 'Riesz Lemması ve Genişleme', link: '/dersler/fonksiyonel-analiz/banach/riesz-lemmasi-genisleme' }
              ]
            },
            {
              text: 'Hilbert Uzayları',
              collapsed: true,
              items: [
                { text: 'İç Çarpım ve Cauchy-Schwarz', link: '/dersler/fonksiyonel-analiz/hilbert/ic-carpim-cauchy-schwarz' },
                { text: 'Hilbert Uzayları Tanımı', link: '/dersler/fonksiyonel-analiz/hilbert/hilbert-uzaylari' },
                { text: 'Daralma ve Sabit Nokta', link: '/dersler/fonksiyonel-analiz/hilbert/daralma-sabit-nokta' }
              ]
            },
            {
              text: 'Operatörler',
              collapsed: true,
              items: [
                { text: 'Sürekli Doğrusal Dönüşümler', link: '/dersler/fonksiyonel-analiz/operatorler/surekli-dogrusal-donusumler' },
                { text: 'Dual Uzay', link: '/dersler/fonksiyonel-analiz/operatorler/dual-uzay' },
                { text: 'Bileşke ve Terslenebilirlik', link: '/dersler/fonksiyonel-analiz/operatorler/bileske-terslenebilirlik' }
              ]
            },
            {
              text: 'Önemli Teoremler',
              collapsed: true,
              items: [
                { text: 'Hahn-Banach Teoremi', link: '/dersler/fonksiyonel-analiz/teoremler/hahn-banach' },
                { text: 'Baire Kategori Teoremi', link: '/dersler/fonksiyonel-analiz/teoremler/baire-kategori' },
                { text: 'Banach-Steinhaus Teoremi', link: '/dersler/fonksiyonel-analiz/teoremler/banach-steinhaus' },
                { text: 'Açık Dönüşüm ve Kapalı Grafik', link: '/dersler/fonksiyonel-analiz/teoremler/acik-donusum-kapali-grafik' }
              ]
            }
          ]
        }
      ],
      '/dersler/ileri-analiz/': [
        {
          text: '🔬 İleri Analiz',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/ileri-analiz/' },
            {
              text: 'İnşalar ve Yapılar',
              collapsed: true,
              items: [
                { text: 'Sıralı Cisim ve Tamlık', link: '/dersler/ileri-analiz/insalar/sirali-cisim-tamlik' },
                { text: 'Tamlık ve Supremum', link: '/dersler/ileri-analiz/insalar/tamlik-supremum' },
                { text: 'Dedekind Kesimleri', link: '/dersler/ileri-analiz/insalar/dedekind-kesimleri' },
                { text: 'Zorn Lemması ve Seçme Aksiyomu', link: '/dersler/ileri-analiz/insalar/zorn-secme-aksiyomu' }
              ]
            },
            {
              text: 'Topolojik Yapılar',
              collapsed: true,
              items: [
                { text: 'Genişletilmiş Reel Sayılar', link: '/dersler/ileri-analiz/topoloji/genisletilmis-reel-sayilar' },
                { text: 'İç İçe Aralıklar', link: '/dersler/ileri-analiz/topoloji/ic-ice-araliklar' },
                { text: 'Heine-Borel ve Bolzano', link: '/dersler/ileri-analiz/topoloji/heine-borel-bolzano' },
                { text: 'Dizilerde Liminf ve Limsup', link: '/dersler/ileri-analiz/topoloji/dizilerde-liminf-limsup' }
              ]
            },
            {
              text: 'Fonksiyonlar',
              collapsed: true,
              items: [
                { text: 'Fonksiyonlarda Liminf ve Limsup', link: '/dersler/ileri-analiz/fonksiyonlar/fonksiyonlarda-liminf-limsup' },
                { text: 'Yarı Süreklilik', link: '/dersler/ileri-analiz/fonksiyonlar/yari-sureklilik' },
                { text: 'Parçalı Sürekli ve Monoton', link: '/dersler/ileri-analiz/fonksiyonlar/parcali-surekli-monoton' }
              ]
            },
            {
              text: 'Varyasyon',
              collapsed: true,
              items: [
                { text: 'Sınırlı Varyasyonlu Fonksiyonlar', link: '/dersler/ileri-analiz/varyasyon/sinirli-varyasyonlu-fonksiyonlar' },
                { text: 'Özellikler ve Teoremler', link: '/dersler/ileri-analiz/varyasyon/ozellikler-teoremler' }
              ]
            }
          ]
        }
      ],
      '/dersler/integral-calculus/': [
        {
          text: '📈 İntegral Calculus',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/integral-calculus/' },
            {
              text: 'Giriş ve Uygulamalar',
              collapsed: true,
              items: [
                { text: 'Alan ve Yay Uzunluğu', link: '/dersler/integral-calculus/giris/alan-yay-uzunlugu' },
                { text: 'Parametrik Teğetler', link: '/dersler/integral-calculus/giris/parametrik-tegetler' },
                { text: 'Kutupsal Koordinatlar ve Grafikler', link: '/dersler/integral-calculus/giris/kutupsal-koordinatlar-grafikler' }
              ]
            },
            {
              text: 'Çok Katlı İntegraller',
              collapsed: true,
              items: [
                { text: 'İki Katlı ve Kartezyen', link: '/dersler/integral-calculus/cok-katli/iki-katli-kartezyen' },
                { text: 'Kutupsal Değişken Geçişi', link: '/dersler/integral-calculus/cok-katli/kutupsal-degisken' },
                { text: 'Üç Katlı Koordinatlar', link: '/dersler/integral-calculus/cok-katli/uc-katli-koordinatlar' },
                { text: 'Has Olmayan ve Ortalama Değer', link: '/dersler/integral-calculus/cok-katli/has-olmayan-ortalama-deger' },
                { text: 'Parametreye Bağlı İntegraller', link: '/dersler/integral-calculus/cok-katli/parametreye-bagli' },
                { text: 'Geometrik Uygulamalar', link: '/dersler/integral-calculus/cok-katli/geometrik-uygulamalar' },
                { text: 'Fiziksel Uygulamalar', link: '/dersler/integral-calculus/cok-katli/fiziksel-uygulamalar' }
              ]
            },
            {
              text: 'Vektör Alanları',
              collapsed: true,
              items: [
                { text: 'Vektör ve Skaler Alanlar', link: '/dersler/integral-calculus/vektor-alanlari/vektor-skaler-alanlar' },
                { text: 'Eğrisel İntegraller', link: '/dersler/integral-calculus/vektor-alanlari/egrisel-integraller' },
                { text: 'Yoldan Bağımsızlık', link: '/dersler/integral-calculus/vektor-alanlari/yoldan-bagimsizlik' },
                { text: 'Konservatif Alanlar', link: '/dersler/integral-calculus/vektor-alanlari/konservatif-alanlar' }
              ]
            },
            {
              text: 'Yüzeyler',
              collapsed: true,
              items: [
                { text: 'Parametrik Normal', link: '/dersler/integral-calculus/yuzeyler/parametrik-normal' },
                { text: 'Yüzey İntegralleri', link: '/dersler/integral-calculus/yuzeyler/yuzey-integralleri' },
                { text: 'Yönlendirilmiş Akı', link: '/dersler/integral-calculus/yuzeyler/yonlendirilmis-aki' }
              ]
            },
            {
              text: 'Teoremler',
              collapsed: true,
              items: [
                { text: 'Gradyan, Diverjans ve Curl', link: '/dersler/integral-calculus/teoremler/gradyan-diverjans-curl' },
                { text: 'Green Teoremi', link: '/dersler/integral-calculus/teoremler/green-teoremi' },
                { text: 'Stokes Teoremi', link: '/dersler/integral-calculus/teoremler/stokes-teoremi' },
                { text: 'Diverjans (Gauss) Teoremi', link: '/dersler/integral-calculus/teoremler/diverjans-gauss-teoremi' },
                { text: 'Potansiyeller ve Özdeşlikler', link: '/dersler/integral-calculus/teoremler/potansiyeller-ozdeslikler' },
                { text: 'Delta Fonksiyonu', link: '/dersler/integral-calculus/teoremler/delta-fonksiyonu' }
              ]
            }
          ]
        }
      ],
      '/dersler/kismi-diferansiyel-denklemler/': [
        {
          text: '🌊 Kısmi Diferansiyel Denklemler',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/kismi-diferansiyel-denklemler/' },
            {
              text: 'Temeller',
              collapsed: true,
              items: [
                { text: 'ODE\'den KDD\'ye Geçiş', link: '/dersler/kismi-diferansiyel-denklemler/temeller/ode-kdd-gecis' },
                { text: 'Sınıflandırma', link: '/dersler/kismi-diferansiyel-denklemler/temeller/siniflandirma' },
                { text: 'Birinci Mertebe Denklemler', link: '/dersler/kismi-diferansiyel-denklemler/temeller/birinci-mertebe' },
                { text: 'Cauchy Problemi', link: '/dersler/kismi-diferansiyel-denklemler/temeller/cauchy-problemi' }
              ]
            },
            {
              text: 'Çözüm Metotları',
              collapsed: true,
              items: [
                { text: 'Cauchy Karakteristik Yöntemi', link: '/dersler/kismi-diferansiyel-denklemler/cozum-metotlari/cauchy-karakteristik' },
                { text: 'Charpit Metodu', link: '/dersler/kismi-diferansiyel-denklemler/cozum-metotlari/charpit' }
              ]
            },
            {
              text: 'İkinci Mertebe Denklemler',
              collapsed: true,
              items: [
                { text: 'Tip Sınıflandırması', link: '/dersler/kismi-diferansiyel-denklemler/ikinci-mertebe/tip-siniflandirmasi' },
                { text: 'Sabit Katsayılı Denklemler', link: '/dersler/kismi-diferansiyel-denklemler/ikinci-mertebe/sabit-katsayili' },
                { text: 'Değişken Katsayılı Denklemler', link: '/dersler/kismi-diferansiyel-denklemler/ikinci-mertebe/degisken-katsayili' }
              ]
            },
            {
              text: 'Modeller ve Uygulamalar',
              collapsed: true,
              items: [
                { text: 'Değişkenlerine Ayırma Yöntemi', link: '/dersler/kismi-diferansiyel-denklemler/modeller/degiskenlerine-ayirma' },
                { text: 'Parabolik ve Isı Denklemi', link: '/dersler/kismi-diferansiyel-denklemler/modeller/parabolik-isi' },
                { text: 'Hiperbolik ve Dalga Denklemi', link: '/dersler/kismi-diferansiyel-denklemler/modeller/hiperbolik-dalga' },
                { text: 'Eliptik ve Laplace Denklemleri', link: '/dersler/kismi-diferansiyel-denklemler/modeller/eliptik-laplace' }
              ]
            }
          ]
        }
      ],
      '/dersler/kodlama-teorisi/': [
        {
          text: '📡 Kodlama Teorisi',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/kodlama-teorisi/' },
            {
              text: 'Temel Kavramlar',
              collapsed: true,
              items: [
                { text: 'Kanallar ve Hata Modelleri', link: '/dersler/kodlama-teorisi/temel/kanallar-hata-modelleri' },
                { text: 'Luhn Algoritması', link: '/dersler/kodlama-teorisi/temel/luhn-algoritmasi' },
                { text: 'TC Kimlik Doğrulama', link: '/dersler/kodlama-teorisi/temel/tc-kimlik-dogrulama' },
                { text: 'Barkod Sistemleri', link: '/dersler/kodlama-teorisi/temel/barkod-sistemleri' },
                { text: 'ISBN Kodları', link: '/dersler/kodlama-teorisi/temel/isbn-kodlari' }
              ]
            },
            {
              text: 'Lineer Kodlar',
              collapsed: true,
              items: [
                { text: 'Vektör Uzayı Yapısı', link: '/dersler/kodlama-teorisi/lineer/vektor-uzayi-yapisi' },
                { text: 'Üreteç ve Eşlik Matrisleri', link: '/dersler/kodlama-teorisi/lineer/uretec-eslik-matrisleri' },
                { text: 'Sendrom Dekodlaması', link: '/dersler/kodlama-teorisi/lineer/sendrom-dekodlamasi' },
                { text: 'Dual Kodlar', link: '/dersler/kodlama-teorisi/lineer/dual-kodlar' },
                { text: 'Eşdeğer Kodlar', link: '/dersler/kodlama-teorisi/lineer/esdeger-kodlar' }
              ]
            },
            {
              text: 'Geometri ve Sınırlar',
              collapsed: true,
              items: [
                { text: 'Hamming Uzaklığı', link: '/dersler/kodlama-teorisi/geometri/hamming-uzakligi' },
                { text: 'En Yakın Komşuluk', link: '/dersler/kodlama-teorisi/geometri/en-yakin-komsuluk' },
                { text: 'Klasik Kod Sınırları', link: '/dersler/kodlama-teorisi/sinirlar/klasik-kod-sinirlari' },
                { text: 'Hamming ve Kusursuz Kodlar', link: '/dersler/kodlama-teorisi/sinirlar/hamming-kusursuz-kodlar' },
                { text: 'Singleton ve MDS Kodlar', link: '/dersler/kodlama-teorisi/sinirlar/singleton-mds-kodlar' }
              ]
            },
            {
              text: 'Devresel Kodlar',
              collapsed: true,
              items: [
                { text: 'Üreteç ve Kontrol Polinomları', link: '/dersler/kodlama-teorisi/devresel/uretec-kontrol-polinomlari' },
                { text: 'Matris Gösterimleri ve Yazmaçlar', link: '/dersler/kodlama-teorisi/devresel/matris-gosterimleri-yazmaclar' }
              ]
            },
            {
              text: 'İleri Kodlama',
              collapsed: true,
              items: [
                { text: 'Maksimum Olabilirlik', link: '/dersler/kodlama-teorisi/ileri/maksimum-olabilirlik' },
                { text: 'BCH Kodları', link: '/dersler/kodlama-teorisi/ileri/bch-kodlari' },
                { text: 'Reed-Solomon Kodları', link: '/dersler/kodlama-teorisi/ileri/reed-solomon' }
              ]
            }
          ]
        }
      ],
      '/dersler/kompleks-analiz/': [
        {
          text: '🧿 Kompleks Analiz',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/kompleks-analiz/' },
            {
              text: '1. Bölüm (Temeller)',
              collapsed: true,
              items: [
                {
                  text: 'Sayılar',
                  collapsed: true,
                  items: [
                    { text: 'Cebirsel ve Üstel Gösterim', link: '/dersler/kompleks-analiz/1/sayilar/cebirsel-ustel' },
                    { text: 'Argüman ve Kökler', link: '/dersler/kompleks-analiz/1/sayilar/arguman-kokler' },
                    { text: 'Bölgeler ve Tasvirler', link: '/dersler/kompleks-analiz/1/sayilar/bolgeler-tasvirler' }
                  ]
                },
                {
                  text: 'Fonksiyonlar',
                  collapsed: true,
                  items: [
                    { text: 'Analitik ve Harmonik Fonksiyonlar', link: '/dersler/kompleks-analiz/1/fonksiyonlar/analitik-harmonik' },
                    { text: 'Üstel ve Logaritmik', link: '/dersler/kompleks-analiz/1/fonksiyonlar/ustel-logaritmik' },
                    { text: 'Trigonometrik ve Hiperbolik', link: '/dersler/kompleks-analiz/1/fonksiyonlar/trigonometrik-hiperbolik' }
                  ]
                },
                {
                  text: 'Limit ve Türev',
                  collapsed: true,
                  items: [
                    { text: 'Limit ve Süreklilik', link: '/dersler/kompleks-analiz/1/limit-turev/limit-sureklilik' },
                    { text: 'Diferansiyellenebilirlik', link: '/dersler/kompleks-analiz/1/limit-turev/diferansiyellenebilirlik' },
                    { text: 'Cauchy-Riemann Denklemleri', link: '/dersler/kompleks-analiz/1/limit-turev/cauchy-riemann' }
                  ]
                },
                {
                  text: 'İntegrasyon',
                  collapsed: true,
                  items: [
                    { text: 'Belirli İntegraller', link: '/dersler/kompleks-analiz/1/integrasyon/belirli' },
                    { text: 'Çevre İntegralleri', link: '/dersler/kompleks-analiz/1/integrasyon/cevre' },
                    { text: 'Ters Türevler', link: '/dersler/kompleks-analiz/1/integrasyon/ters-turevler' }
                  ]
                }
              ]
            },
            {
              text: '2. Bölüm (İleri Konular)',
              collapsed: true,
              items: [
                {
                  text: 'Cauchy Teoremleri',
                  collapsed: true,
                  items: [
                    { text: 'Goursat Teoremi', link: '/dersler/kompleks-analiz/2/cauchy/goursat' },
                    { text: 'İntegral Formülü', link: '/dersler/kompleks-analiz/2/cauchy/integral-formulu' },
                    { text: 'Maksimum Modül İlkesi', link: '/dersler/kompleks-analiz/2/cauchy/maksimum-modul' },
                    { text: 'Liouville Teoremi', link: '/dersler/kompleks-analiz/2/cauchy/liouville' }
                  ]
                },
                {
                  text: 'Seriler',
                  collapsed: true,
                  items: [
                    { text: 'Yakınsaklık', link: '/dersler/kompleks-analiz/2/seriler/yakinsaklik' },
                    { text: 'İşlemler', link: '/dersler/kompleks-analiz/2/seriler/islemler' },
                    { text: 'Taylor Serileri', link: '/dersler/kompleks-analiz/2/seriler/taylor' },
                    { text: 'Kuvvet Serileri', link: '/dersler/kompleks-analiz/2/seriler/kuvvet-serileri' },
                    { text: 'Laurent Serileri', link: '/dersler/kompleks-analiz/2/seriler/laurent' }
                  ]
                },
                {
                  text: 'Rezidü',
                  collapsed: true,
                  items: [
                    { text: 'Sıfırlar ve Kutuplar', link: '/dersler/kompleks-analiz/2/rezidu/sifirlar-kutuplar' },
                    { text: 'Tekillikler', link: '/dersler/kompleks-analiz/2/rezidu/tekillikler' },
                    { text: 'Cauchy Rezidü Teoremi', link: '/dersler/kompleks-analiz/2/rezidu/cauchy-rezidu' },
                    { text: 'Sonsuzda Rezidü', link: '/dersler/kompleks-analiz/2/rezidu/sonsuzda-rezidu' }
                  ]
                },
                {
                  text: 'Uygulamalar',
                  collapsed: true,
                  items: [
                    { text: 'Has Olmayan İntegraller', link: '/dersler/kompleks-analiz/2/uygulamalar/improper' },
                    { text: 'Trigonometrik İntegraller', link: '/dersler/kompleks-analiz/2/uygulamalar/trigonometrik' },
                    { text: 'Dal Kesimi', link: '/dersler/kompleks-analiz/2/uygulamalar/dal-kesimi' },
                    { text: 'Jordan Lemması', link: '/dersler/kompleks-analiz/2/uygulamalar/jordan-lemmasi' },
                    { text: 'Argüman İlkesi ve Rouché', link: '/dersler/kompleks-analiz/2/uygulamalar/arguman-rouche' },
                    { text: 'Ters Laplace Dönüşümü', link: '/dersler/kompleks-analiz/2/uygulamalar/ters-laplace' }
                  ]
                }
              ]
            }
          ]
        }
      ],
      '/dersler/konveks-analiz/': [
        {
          text: '🔺 Konveks Analiz',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/konveks-analiz/' },
            {
              text: 'Temeller',
              collapsed: true,
              items: [
                { text: 'Vektör, Norm ve Metrik', link: '/dersler/konveks-analiz/temeller/vektor-norm-metrik' },
                { text: 'Topolojik Kümeler', link: '/dersler/konveks-analiz/temeller/topolojik-kumeler' },
                { text: 'Yakınsaklık ve Süreklilik', link: '/dersler/konveks-analiz/temeller/yakinsaklik-sureklilik' }
              ]
            },
            {
              text: 'Kümeler',
              collapsed: true,
              items: [
                { text: 'Afin Kümeler ve Örtü', link: '/dersler/konveks-analiz/kumeler/afin-kumeler-ortu' },
                { text: 'Özellikler ve Dönüşümler', link: '/dersler/konveks-analiz/kumeler/ozellikler-donusumler' },
                { text: 'Konveks Polihedral', link: '/dersler/konveks-analiz/kumeler/konveks-polihedral' }
              ]
            },
            {
              text: 'Koniler ve Fonksiyonlar',
              collapsed: true,
              items: [
                { text: 'Konveks Fonksiyonlar', link: '/dersler/konveks-analiz/koniler-fonksiyonlar/konveks-fonksiyonlar' },
                { text: 'Belirleme ve Eşitsizlikler', link: '/dersler/konveks-analiz/koniler-fonksiyonlar/belirleme-esitsizlikler' },
                { text: 'Dual, Polar ve Resesyon', link: '/dersler/konveks-analiz/koniler-fonksiyonlar/dual-polar-resesyon' }
              ]
            },
            {
              text: 'Teoremler',
              collapsed: true,
              items: [
                { text: 'Konveks Örtü ve Carathéodory', link: '/dersler/konveks-analiz/teoremler/konveks-ortu-caratheodory' },
                { text: 'Simpleks ve İzafi İç', link: '/dersler/konveks-analiz/teoremler/simpleks-izafi-ic' },
                { text: 'Ayrılma Teoremleri', link: '/dersler/konveks-analiz/teoremler/ayrilma-teoremleri' }
              ]
            },
            {
              text: 'İleri Analiz',
              collapsed: true,
              items: [
                { text: 'Yönlü Türev', link: '/dersler/konveks-analiz/ileri-analiz/yonlu-turev' },
                { text: 'Subdiferansiyel', link: '/dersler/konveks-analiz/ileri-analiz/subdiferansiyel' }
              ]
            }
          ]
        }
      ],
      '/dersler/kriptografi/': [
        {
          text: '🔐 Kriptografi',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/kriptografi/' },
            {
              text: 'Kriptografiye Giriş',
              collapsed: true,
              items: [
                { text: 'Giriş', link: '/dersler/kriptografi/kriptografiye-giris/terminoloji' },
                { text: 'Kerckhoffs Prensibi', link: '/dersler/kriptografi/kriptografiye-giris/kerckhoffs-prensibi' },
                { text: 'Matematiksel Temeller ve Notasyon', link: '/dersler/kriptografi/kriptografiye-giris/matematiksel-temeller' },
              ]
            },
            {
              text: 'Klasik Şifreler',
              collapsed: true,
              items: [
                { text: 'Skytale', link: '/dersler/kriptografi/klasik/skytale' },
                { text: 'Sezar Şifresi', link: '/dersler/kriptografi/klasik/sezar-sifreleme' },
                { text: 'Affine Şifresi', link: '/dersler/kriptografi/klasik/affine-sifreleme' },
                { text: 'Bacon Şifresi', link: '/dersler/kriptografi/klasik/bacon-sifreleme' },
                { text: 'Playfair Şifresi', link: '/dersler/kriptografi/klasik/playfair-sifreleme' },
                { text: 'Vigenère Şifresi', link: '/dersler/kriptografi/klasik/vigenere-sifreleme' },
                { text: 'Hill Şifresi', link: '/dersler/kriptografi/klasik/hill-sifreleme' }
              ]
            },
            {
              text: 'Modern Döneme Geçiş',
              collapsed: true,
              items: [
                { text: 'One-Time Pad', link: '/dersler/kriptografi/modern-gecis/one-time-pad' },
                { text: 'Shannon Maksimi', link: '/dersler/kriptografi/modern-gecis/shannon' },
                { text: 'XOR İşlemi', link: '/dersler/kriptografi/modern-gecis/xor' }
              ]
            },
            {
              text: 'Simetrik Şifreleme',
              collapsed: true,
              items: [
                {
                  text: 'Akan Şifreler',
                  collapsed: true,
                  items: [
                    { text: 'Akan Şifrelere Giriş', link: '/dersler/kriptografi/simetrik/akan-sifreler/giris' },
                    { text: 'LFSR', link: '/dersler/kriptografi/simetrik/akan-sifreler/lfsr' },
                    { text: 'RC4 Algoritması', link: '/dersler/kriptografi/simetrik/akan-sifreler/rc4' }
                  ]
                },
                {
                  text: 'Blok Şifreler',
                  collapsed: true,
                  items: [
                    { text: 'DES Algoritması', link: '/dersler/kriptografi/simetrik/blok-sifreler/des' },
                    { text: 'AES Algoritması', link: '/dersler/kriptografi/simetrik/blok-sifreler/aes' }
                  ]
                }
              ]
            },
            {
              text: 'Asimetrik Şifreleme',
              collapsed: true,
              items: [
                { text: 'Asimetrik Şifrelemeye Giriş', link: '/dersler/kriptografi/asimetrik/giris' },
                { text: 'Diffie-Hellman', link: '/dersler/kriptografi/asimetrik/diffie-hellman' },
                { text: 'RSA Algoritması', link: '/dersler/kriptografi/asimetrik/rsa' }
              ]
            },
            {
              text: 'Hash ve Doğrulama',
              collapsed: true,
              items: [
                { text: 'Hash Fonksiyonlarına Giriş', link: '/dersler/kriptografi/hash/giris' },
                { text: 'Dijital İmza', link: '/dersler/kriptografi/hash/dijital-imza' }
              ]
            }
          ]
        }
      ],
      '/dersler/lineer-cebir/': [
        {
          text: '📏 Lineer Cebir',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/lineer-cebir/' },
            {
              text: '1. Bölüm (Vektör Uzayları ve Matrisler)',
              collapsed: true,
              items: [
                { text: 'Tek İşlemli Yapılar', link: '/dersler/lineer-cebir/1/tek-islemli-yapilar' },
                { text: 'İki İşlemli Yapılar', link: '/dersler/lineer-cebir/1/iki-islemli-yapilar' },
                { text: 'Vektör Uzayları', link: '/dersler/lineer-cebir/1/vektor-uzaylari' },
                { text: 'Alt Uzaylar', link: '/dersler/lineer-cebir/1/alt-uzaylar' },
                { text: 'Lineer Bağımsızlık', link: '/dersler/lineer-cebir/1/lineer-bagimsizlik' },
                { text: 'Taban ve Boyut', link: '/dersler/lineer-cebir/1/taban-boyut' },
                { text: 'Toplamlar ve Direkt Toplam', link: '/dersler/lineer-cebir/1/toplamlar-direkt-toplam' },
                { text: 'Matrisler 1', link: '/dersler/lineer-cebir/1/matrisler-1' },
                { text: 'Matrisler 2', link: '/dersler/lineer-cebir/1/matrisler-2' },
                { text: 'Denklem Sistemleri', link: '/dersler/lineer-cebir/1/denklem-sistemleri' },
                { text: 'Çözüm Yöntemleri', link: '/dersler/lineer-cebir/1/cozum-yontemleri' },
                { text: 'Satır Uzayı ve Rank', link: '/dersler/lineer-cebir/1/satir-uzayi-rank' }
              ]
            },
            {
              text: '2. Bölüm (Dönüşümler ve Özdeğerler)',
              collapsed: true,
              items: [
                { text: 'Dönüşüm Tanımı', link: '/dersler/lineer-cebir/2/donusum-tanimi' },
                { text: 'Çekirdek ve Görüntü', link: '/dersler/lineer-cebir/2/cekirdek-goruntu' },
                { text: 'Operatörler Cebri', link: '/dersler/lineer-cebir/2/operatorler-cebri' },
                { text: 'Koordinat Vektörleri', link: '/dersler/lineer-cebir/2/koordinat-vektorleri' },
                { text: 'Dönüşüm Matrisi', link: '/dersler/lineer-cebir/2/donusum-matrisi' },
                { text: 'Baz Değişimi', link: '/dersler/lineer-cebir/2/baz-degisimi' },
                { text: 'Determinantlar', link: '/dersler/lineer-cebir/2/determinantlar' },
                { text: 'Minör ve Kofaktör', link: '/dersler/lineer-cebir/2/minor-kofaktor' },
                { text: 'Benzer Matrisler', link: '/dersler/lineer-cebir/2/benzer-matrisler' },
                { text: 'Özdeğer ve Özvektör', link: '/dersler/lineer-cebir/2/ozdeger-ozvektor' },
                { text: 'Karakteristik Polinom', link: '/dersler/lineer-cebir/2/karakteristik-polinom' },
                { text: 'Minimal Polinom', link: '/dersler/lineer-cebir/2/minimal-polinom' },
                { text: 'Cayley-Hamilton Teoremi', link: '/dersler/lineer-cebir/2/cayley-hamilton' },
                { text: 'Köşegenleştirme', link: '/dersler/lineer-cebir/2/kosegenlestirme' },
                { text: 'Sistem Uygulamaları', link: '/dersler/lineer-cebir/2/sistem-uygulamalari' }
              ]
            }
          ]
        }
      ],
      '/dersler/lineer-programlama/': [
        {
          text: '📉 Lineer Programlama',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/lineer-programlama/' },
            {
              text: 'Temel Kavramlar',
              collapsed: true,
              items: [
                { text: 'Model Kurma', link: '/dersler/lineer-programlama/temel/model-kurma' },
                { text: 'Grafik Yöntem', link: '/dersler/lineer-programlama/temel/grafik-yontem' },
                { text: 'Temel Çözümler', link: '/dersler/lineer-programlama/temel/temel-cozumler' }
              ]
            },
            {
              text: 'Simpleks Yöntemi',
              collapsed: true,
              items: [
                { text: 'Cebirsel Mantık', link: '/dersler/lineer-programlama/simpleks/cebirsel-mantik' },
                { text: 'Simpleks Tablosu', link: '/dersler/lineer-programlama/simpleks/simpleks-tablosu' },
                { text: 'Büyük M Metodu', link: '/dersler/lineer-programlama/simpleks/buyuk-m-metodu' },
                { text: 'İki Faz Metodu', link: '/dersler/lineer-programlama/simpleks/iki-faz-metodu' },
                { text: 'Kısıtsız ve Sınırlı Değişkenler', link: '/dersler/lineer-programlama/simpleks/kisitsiz-sinirli-degiskenler' }
              ]
            },
            {
              text: 'Dualite',
              collapsed: true,
              items: [
                { text: 'Dualite Teorisi', link: '/dersler/lineer-programlama/dualite/dualite-teorisi' },
                { text: 'Dual Simpleks', link: '/dersler/lineer-programlama/dualite/dual-simpleks' },
                { text: 'Duyarlılık Analizi', link: '/dersler/lineer-programlama/dualite/duyarlilik-analizi' }
              ]
            },
            {
              text: 'İleri Konular',
              collapsed: true,
              items: [
                { text: 'Tam Sayılı Programlama', link: '/dersler/lineer-programlama/ileri/tam-sayili' },
                { text: 'Hiperbolik Programlama', link: '/dersler/lineer-programlama/ileri/hiperbolik' }
              ]
            }
          ]
        }
      ],
      '/dersler/matematigin-temelleri/': [
        {
          text: '🏛 Matematiğin Temelleri',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/matematigin-temelleri/' },
            {
              text: 'Mantık',
              collapsed: true,
              items: [
                { text: 'Önermeler', link: '/dersler/matematigin-temelleri/mantik/onermeler' },
                { text: 'Doğruluk Tabloları', link: '/dersler/matematigin-temelleri/mantik/dogruluk-tablolari' },
                { text: 'Mantıksal Denklik', link: '/dersler/matematigin-temelleri/mantik/mantiksal-denklik' },
                { text: 'Totoloji ve Çelişki', link: '/dersler/matematigin-temelleri/mantik/totoloji-celiski' },
                { text: 'Çıkarım Kuralları', link: '/dersler/matematigin-temelleri/mantik/cikarim-kurallari' },
                { text: 'Niceleme Mantığı', link: '/dersler/matematigin-temelleri/mantik/niceleme-mantigi' }
              ]
            },
            {
              text: 'İspat Yöntemleri',
              collapsed: true,
              items: [
                { text: 'İspatlara Giriş', link: '/dersler/matematigin-temelleri/ispatlar/giris' },
                { text: 'Doğrudan İspat', link: '/dersler/matematigin-temelleri/ispatlar/dogrudan-ispat' },
                { text: 'Karşıt Ters ile İspat', link: '/dersler/matematigin-temelleri/ispatlar/karsit-ters' },
                { text: 'Çelişki ile İspat', link: '/dersler/matematigin-temelleri/ispatlar/celiski' },
                { text: 'Durum İnceleme', link: '/dersler/matematigin-temelleri/ispatlar/durum-inceleme' },
                { text: 'Varlık ve Teklik İspatları', link: '/dersler/matematigin-temelleri/ispatlar/varlik-teklik' }
              ]
            },
            {
              text: 'Kümeler',
              collapsed: true,
              items: [
                { text: 'Kavram ve Alt Kümeler', link: '/dersler/matematigin-temelleri/kumeler/kavram-altkumeler' },
                { text: 'Küme İşlemleri', link: '/dersler/matematigin-temelleri/kumeler/islemler' },
                { text: 'Kartezyen Çarpım', link: '/dersler/matematigin-temelleri/kumeler/kartezyen-carpim' },
                { text: 'Küme Aileleri', link: '/dersler/matematigin-temelleri/kumeler/kume-aileleri' }
              ]
            },
            {
              text: 'Bağıntılar ve Fonksiyonlar',
              collapsed: true,
              items: [
                { text: 'Bağıntı Kavramı', link: '/dersler/matematigin-temelleri/bagintilar-fonksiyonlar/baginti' },
                { text: 'Denklik Bağıntısı', link: '/dersler/matematigin-temelleri/bagintilar-fonksiyonlar/denklik' },
                { text: 'Parçalanışlar', link: '/dersler/matematigin-temelleri/bagintilar-fonksiyonlar/parcalanislar' },
                { text: 'Sıralama Bağıntısı', link: '/dersler/matematigin-temelleri/bagintilar-fonksiyonlar/siralama' },
                { text: 'Fonksiyon Tanımı', link: '/dersler/matematigin-temelleri/bagintilar-fonksiyonlar/fonksiyon-tanimi' },
                { text: 'Birebir ve Örten', link: '/dersler/matematigin-temelleri/bagintilar-fonksiyonlar/birebir-orten' },
                { text: 'Ters ve Bileşke Fonksiyonlar', link: '/dersler/matematigin-temelleri/bagintilar-fonksiyonlar/ters-bileske' }
              ]
            },
            {
              text: 'Sayı Sistemleri',
              collapsed: true,
              items: [
                { text: 'Sayı Sistemlerinin İnşası', link: '/dersler/matematigin-temelleri/sayi-sistemleri/insa' },
                { text: 'Matematiksel Tümevarım', link: '/dersler/matematigin-temelleri/sayi-sistemleri/tumevarim' }
              ]
            }
          ]
        }
      ],
      '/dersler/matematik-uygulamalari/': [
        {
          text: '🛠 Matematik Uygulamaları',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/matematik-uygulamalari/' },
            {
              text: 'Temel Bilgiler',
              collapsed: true,
              items: [
                { text: 'Arayüz ve Hesaplamalar', link: '/dersler/matematik-uygulamalari/temel/arayuz-hesaplamalar' },
                { text: 'Değişkenler ve Listeler', link: '/dersler/matematik-uygulamalari/temel/degiskenler-listeler' },
                { text: 'Fonksiyon ve Sabit Tanımlama', link: '/dersler/matematik-uygulamalari/temel/fonksiyon-sabit-tanimlama' }
              ]
            },
            {
              text: 'Cebirsel İşlemler',
              collapsed: true,
              items: [
                { text: 'Türev, İntegral ve Limit', link: '/dersler/matematik-uygulamalari/cebir/turev-integral-limit' },
                { text: 'Seriler ve Kuvvet Serileri', link: '/dersler/matematik-uygulamalari/cebir/seriler-kuvvet-serileri' },
                { text: 'Denklem Sistemleri', link: '/dersler/matematik-uygulamalari/cebir/denklem-sistemleri' },
                { text: 'Sembolik ve Sayısal Dönüşümler', link: '/dersler/matematik-uygulamalari/cebir/sembolik-sayisal-donusumler' },
                { text: 'Koşullar ve Yerine Koyma', link: '/dersler/matematik-uygulamalari/cebir/kosullar-yerine-koyma' }
              ]
            },
            {
              text: 'Görselleştirme',
              collapsed: true,
              items: [
                { text: 'Grafikler ve Çizimler', link: '/dersler/matematik-uygulamalari/gorsellestirme/grafikler-cizimler' },
                { text: 'Çok Değişkenli Fonksiyonlar', link: '/dersler/matematik-uygulamalari/gorsellestirme/cok-degiskenli-fonksiyonlar' },
                { text: 'Vektörler ve Matrisler', link: '/dersler/matematik-uygulamalari/gorsellestirme/vektorler-matrisler' }
              ]
            },
            {
              text: 'Simülasyon ve Analiz',
              collapsed: true,
              items: [
                { text: 'Veri Analizi', link: '/dersler/matematik-uygulamalari/simulasyon/veri-analizi' },
                { text: 'Diferansiyel Denklemler', link: '/dersler/matematik-uygulamalari/simulasyon/diferansiyel-denklemler' },
                { text: 'İleri Düzey Uygulamalar', link: '/dersler/matematik-uygulamalari/simulasyon/ileri-duzey-uygulamalar' }
              ]
            },
            {
              text: 'İleri Konular',
              collapsed: true,
              items: [
                { text: 'İteratif Algoritmalar', link: '/dersler/matematik-uygulamalari/ileri/iteratif-algoritmalar' },
                { text: 'İleri Cebirsel Denklemler', link: '/dersler/matematik-uygulamalari/ileri/ileri-cebirsel-denklemler' },
                { text: 'Analitik Geometri Uygulamaları', link: '/dersler/matematik-uygulamalari/ileri/analitik-geometri-uygulamalari' }
              ]
            }
          ]
        }
      ],
      '/dersler/matematiksel-istatistik/': [
        {
          text: '📉 Matematiksel İstatistik',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/matematiksel-istatistik/' },
            {
              text: 'Örnekleme',
              collapsed: true,
              items: [
                { text: 'İstatistiğe Giriş', link: '/dersler/matematiksel-istatistik/ornekleme/istatistige-giris' },
                { text: 'Örnekleme Kavramı', link: '/dersler/matematiksel-istatistik/ornekleme/ornekleme-kavrami' },
                { text: 'Örnekleme Dağılımları', link: '/dersler/matematiksel-istatistik/ornekleme/ornekleme-dagilimlari' }
              ]
            },
            {
              text: 'Dağılımlar',
              collapsed: true,
              items: [
                { text: 'Önemli Sürekli Dağılımlar', link: '/dersler/matematiksel-istatistik/dagilimlar/onemli-surekli-dagilimlar' },
                { text: 'Normal Dağılım', link: '/dersler/matematiksel-istatistik/dagilimlar/normal-dagilim' },
                { text: 'Binom ve Normal Yaklaşım', link: '/dersler/matematiksel-istatistik/dagilimlar/binom-normal-yaklasim' }
              ]
            },
            {
              text: 'Tahmin Teorisi',
              collapsed: true,
              items: [
                { text: 'Teori ve Özellikler', link: '/dersler/matematiksel-istatistik/tahmin/teori-ozellikler' },
                { text: 'Momentler Yöntemi', link: '/dersler/matematiksel-istatistik/tahmin/momentler-yontemi' },
                { text: 'En Çok Olabilirlik (MLE)', link: '/dersler/matematiksel-istatistik/tahmin/en-cok-olabilirlik-mle' }
              ]
            },
            {
              text: 'Karar Teorisi ve Hipotez',
              collapsed: true,
              items: [
                { text: 'Güven Aralıkları', link: '/dersler/matematiksel-istatistik/karar/guven-araliklari' },
                { text: 'Hipotez Giriş', link: '/dersler/matematiksel-istatistik/karar/hipotez-giris' },
                { text: 'Hata Tipleri ve Güç', link: '/dersler/matematiksel-istatistik/karar/hata-tipleri-guc' },
                { text: 'Hipotez Testleri ve P Değeri', link: '/dersler/matematiksel-istatistik/karar/hipotez-testleri-p-degeri' }
              ]
            },
            {
              text: 'Asimptotik Dağılımlar',
              collapsed: true,
              items: [
                { text: 'Eşitsizlikler ve Yakınsama', link: '/dersler/matematiksel-istatistik/asimptotik/esitsizlikler-yakinsama' },
                { text: 'Büyük Sayılar ve Merkezi Limit', link: '/dersler/matematiksel-istatistik/asimptotik/buyuk-sayilar-merkezi-limit' }
              ]
            }
          ]
        }
      ],
      '/dersler/numerik-analiz/': [
        {
          text: '🖥 Nümerik Analiz',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/numerik-analiz/' },
            {
              text: 'Temeller',
              collapsed: true,
              items: [
                { text: 'Hatalar ve Makine Sayıları', link: '/dersler/numerik-analiz/temeller/hatalar-makine-sayilari' },
                { text: 'Taylor Serileri', link: '/dersler/numerik-analiz/temeller/taylor-serileri' },
                { text: 'Hata Büyümesi ve Yakınsama', link: '/dersler/numerik-analiz/temeller/hata-buyumesi-yakinsama' }
              ]
            },
            {
              text: 'Kök Bulma Yöntemleri',
              collapsed: true,
              items: [
                { text: 'İkiye Bölme (Bisection)', link: '/dersler/numerik-analiz/kok-bulma/ikiye-bolme' },
                { text: 'Sabit Nokta', link: '/dersler/numerik-analiz/kok-bulma/sabit-nokta' },
                { text: 'Newton-Raphson', link: '/dersler/numerik-analiz/kok-bulma/newton-raphson' },
                { text: 'Sekant ve Regula Falsi', link: '/dersler/numerik-analiz/kok-bulma/sekant-regula-falsi' }
              ]
            },
            {
              text: 'İnterpolasyon',
              collapsed: true,
              items: [
                { text: 'Lagrange İnterpolasyonu', link: '/dersler/numerik-analiz/interpolasyon/lagrange' },
                { text: 'Bölünmüş Farklar', link: '/dersler/numerik-analiz/interpolasyon/bolunmus-farklar' },
                { text: 'İleri, Geri ve Merkezi Farklar', link: '/dersler/numerik-analiz/interpolasyon/ileri-geri-merkezi-farklar' }
              ]
            },
            {
              text: 'Modelleme ve Sayısal İşlemler',
              collapsed: true,
              items: [
                { text: 'En Küçük Kareler', link: '/dersler/numerik-analiz/modelleme/en-kucuk-kareler' },
                { text: 'Nümerik Türev', link: '/dersler/numerik-analiz/modelleme/numerik-turev' },
                { text: 'Nümerik İntegral', link: '/dersler/numerik-analiz/modelleme/numerik-integral' }
              ]
            }
          ]
        }
      ],
      '/dersler/olasilik-teorisi/': [
        {
          text: '🎲 Olasılık Teorisi',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/olasilik-teorisi/' },
            {
              text: 'Temeller',
              collapsed: true,
              items: [
                { text: 'Kümeler ve Örnek Uzay', link: '/dersler/olasilik-teorisi/temeller/kumeler-ornek-uzay' },
                { text: 'Sayma Teknikleri', link: '/dersler/olasilik-teorisi/temeller/sayma-teknikleri' },
                { text: 'Olasılık Uzayı', link: '/dersler/olasilik-teorisi/temeller/olasilik-uzayi' },
                { text: 'Koşullu Olasılık ve Bayes', link: '/dersler/olasilik-teorisi/temeller/kosullu-olasilik-bayes' }
              ]
            },
            {
              text: 'Rastgele Değişkenler',
              collapsed: true,
              items: [
                { text: 'Kavram ve Dağılım', link: '/dersler/olasilik-teorisi/rastgele-degiskenler/kavram-dagilim' },
                { text: 'Kesikli Rastgele Değişkenler', link: '/dersler/olasilik-teorisi/rastgele-degiskenler/kesikli' },
                { text: 'Sürekli Rastgele Değişkenler', link: '/dersler/olasilik-teorisi/rastgele-degiskenler/surekli' },
                { text: 'Dönüşümler', link: '/dersler/olasilik-teorisi/rastgele-degiskenler/donusumler' }
              ]
            },
            {
              text: 'Rastgele Vektörler',
              collapsed: true,
              items: [
                { text: 'Ortak Dağılımlar', link: '/dersler/olasilik-teorisi/rastgele-vektorler/ortak-dagilimlar' },
                { text: 'Marjinal Dağılımlar', link: '/dersler/olasilik-teorisi/rastgele-vektorler/marjinal-dagilimlar' },
                { text: 'Koşullu Dağılımlar', link: '/dersler/olasilik-teorisi/rastgele-vektorler/kosullu-dagilimlar' },
                { text: 'Vektör Dönüşümleri', link: '/dersler/olasilik-teorisi/rastgele-vektorler/vektor-donusumleri' }
              ]
            },
            {
              text: 'Beklenen Değer',
              collapsed: true,
              items: [
                { text: 'Beklenen Değer ve Varyans', link: '/dersler/olasilik-teorisi/beklenen-deger/beklenen-deger-varyans' },
                { text: 'Koşullu Beklenen Değer', link: '/dersler/olasilik-teorisi/beklenen-deger/kosullu-beklenen-deger' },
                { text: 'Üretici Fonksiyonlar', link: '/dersler/olasilik-teorisi/beklenen-deger/uretici-fonksiyonlar' },
                { text: 'Karakteristik Fonksiyonlar', link: '/dersler/olasilik-teorisi/beklenen-deger/karakteristik-fonksiyonlar' }
              ]
            },
            {
              text: 'Dağılımlar',
              collapsed: true,
              items: [
                { text: 'Dağılım İlişkileri', link: '/dersler/olasilik-teorisi/dagilimlar/dagilim-iliskileri' },
                { text: 'Binom ve Poisson', link: '/dersler/olasilik-teorisi/dagilimlar/binom-poisson' },
                { text: 'Düzgün, Hipergeometrik ve Geometrik', link: '/dersler/olasilik-teorisi/dagilimlar/duzgun-hipergeometrik-geometrik' },
                { text: 'Negatif Binom', link: '/dersler/olasilik-teorisi/dagilimlar/negatif-binom' }
              ]
            }
          ]
        }
      ],
      '/dersler/python-bilimsel/': [
        {
          text: '🐍 Python ile Bilimsel Hesaplama',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/python-bilimsel/' },
            {
              text: 'Temel Python',
              collapsed: true,
              items: [
                { text: 'Sözdizimi ve Kontrol Yapıları', link: '/dersler/python-bilimsel/temel/sozdizimi-kontrol-yapilari' },
                { text: 'Veri Yapıları ve Comprehension', link: '/dersler/python-bilimsel/temel/veri-yapilari-comprehension' },
                { text: 'Fonksiyonlar ve Hata Yakalama', link: '/dersler/python-bilimsel/temel/fonksiyonlar-hata-yakalama' }
              ]
            },
            {
              text: 'NumPy ve Vektörel İşlemler',
              collapsed: true,
              items: [
                { text: 'NumPy N-Boyutlu Diziler', link: '/dersler/python-bilimsel/vektorel/numpy-n-boyutlu-diziler' },
                { text: 'Vektörizasyon ve Broadcasting', link: '/dersler/python-bilimsel/vektorel/vektorizasyon-broadcasting' },
                { text: 'Lineer Sistemler ve Özdeğer', link: '/dersler/python-bilimsel/vektorel/lineer-sistemler-ozdeger' },
                { text: 'NumPy Polinom Analizi', link: '/dersler/python-bilimsel/vektorel/numpy-polinom-analizi' }
              ]
            },
            {
              text: 'Sayısal Hesaplama (SciPy & SymPy)',
              collapsed: true,
              items: [
                { text: 'SymPy ve Sembolik Matematik', link: '/dersler/python-bilimsel/sayisal/sympy-sembolik-matematik' },
                { text: 'Kök Bulma ve Optimizasyon', link: '/dersler/python-bilimsel/sayisal/kok-bulma-optimizasyon' },
                { text: 'Sayısal İntegral ve Türev', link: '/dersler/python-bilimsel/sayisal/sayisal-integral-turev' },
                { text: 'Diferansiyel Çözümleri', link: '/dersler/python-bilimsel/sayisal/diferansiyel-cozumleri' }
              ]
            },
            {
              text: 'Görselleştirme',
              collapsed: true,
              items: [
                { text: 'Matplotlib, Seaborn ve Çizimler', link: '/dersler/python-bilimsel/gorsellestirme/matplotlib-seaborn-cizimler' },
                { text: 'Faz Düzlemleri', link: '/dersler/python-bilimsel/gorsellestirme/faz-duzlemleri' },
                { text: 'Monte Carlo ve Rastgele Yürüyüş', link: '/dersler/python-bilimsel/gorsellestirme/monte-carlo-rastgele-yuruyus' }
              ]
            },
            {
              text: 'Veri Analizi (Pandas)',
              collapsed: true,
              items: [
                { text: 'Pandas DataFrames', link: '/dersler/python-bilimsel/veri/pandas-dataframes' },
                { text: 'Veri Temizleme ve Gruplama', link: '/dersler/python-bilimsel/veri/veri-temizleme-gruplama' },
                { text: 'Zaman Serileri', link: '/dersler/python-bilimsel/veri/zaman-serileri' }
              ]
            }
          ]
        }
      ],
      '/dersler/raslanti-surecleri/': [
        {
          text: '⏱ Raslantı Süreçleri',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/raslanti-surecleri/' },
            {
              text: 'Temeller',
              collapsed: true,
              items: [
                { text: 'Stokastik Kavramı', link: '/dersler/raslanti-surecleri/temeller/stokastik-kavrami' },
                { text: 'Notasyon', link: '/dersler/raslanti-surecleri/temeller/notasyon' },
                { text: 'Sınıflandırma', link: '/dersler/raslanti-surecleri/temeller/siniflandirma' },
                { text: 'Poisson Süreçleri', link: '/dersler/raslanti-surecleri/temeller/poisson' },
                { text: 'Varış Süreçleri', link: '/dersler/raslanti-surecleri/temeller/varis-surecleri' }
              ]
            },
            {
              text: 'Markov Zincirleri',
              collapsed: true,
              items: [
                { text: 'Geçiş Matrisleri', link: '/dersler/raslanti-surecleri/markov/gecis-matrisleri' },
                { text: 'Chapman-Kolmogorov Denklemleri', link: '/dersler/raslanti-surecleri/markov/chapman-kolmogorov' },
                { text: 'Kesikli Zaman', link: '/dersler/raslanti-surecleri/markov/kesikli-zaman' },
                { text: 'Sürekli Zaman', link: '/dersler/raslanti-surecleri/markov/surekli-zaman' },
                { text: 'Yutucu Durumlar', link: '/dersler/raslanti-surecleri/markov/yutucu-durumlar' }
              ]
            },
            {
              text: 'Kuyruk Modelleri',
              collapsed: true,
              items: [
                { text: 'Giriş', link: '/dersler/raslanti-surecleri/kuyruk/giris' },
                { text: 'Modeller', link: '/dersler/raslanti-surecleri/kuyruk/modeller' },
                { text: 'Little Kanunu', link: '/dersler/raslanti-surecleri/kuyruk/little-kanunu' }
              ]
            },
            {
              text: 'Tahmin ve Analiz',
              collapsed: true,
              items: [
                { text: 'Zaman Serileri', link: '/dersler/raslanti-surecleri/tahmin/zaman-serileri' },
                { text: 'Regresyona Giriş', link: '/dersler/raslanti-surecleri/tahmin/regresyona-giris' },
                { text: 'Lineer Regresyon', link: '/dersler/raslanti-surecleri/tahmin/lineer-regresyon' },
                { text: 'Hata Analizi', link: '/dersler/raslanti-surecleri/tahmin/hata-analizi' },
                { text: 'Dönüştürülebilir Denklemler', link: '/dersler/raslanti-surecleri/tahmin/donusturulebilir-denklemler' },
                { text: 'Eksponansiyel Düzleştirme', link: '/dersler/raslanti-surecleri/tahmin/eksponansiyel' },
                { text: 'Hareketli Mevsimsellik', link: '/dersler/raslanti-surecleri/tahmin/hareketli-mevsimsellik' },
                { text: 'Holt-Winters Yöntemi', link: '/dersler/raslanti-surecleri/tahmin/holt-winter' }
              ]
            },
            {
              text: 'Karar Teorisi',
              collapsed: true,
              items: [
                { text: 'Stratejik Kararlar', link: '/dersler/raslanti-surecleri/karar/stratejik-kararlar' },
                { text: 'Oyun Teorisi', link: '/dersler/raslanti-surecleri/karar/oyun-teorisi' }
              ]
            }
          ]
        }
      ],
      '/dersler/reel-analiz/': [
        {
          text: '📚 Reel Analiz',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/reel-analiz/' },
            {
              text: 'Ölçü Teorisi',
              collapsed: true,
              items: [
                { text: 'Cantor Kümesi ve Fonksiyonu', link: '/dersler/reel-analiz/olcu/cantor-kumesi-fonksiyonu' },
                { text: 'Dış Ölçü ve Ölçülebilir Kümeler', link: '/dersler/reel-analiz/olcu/dis-olcu-olculebilir-kumeler' },
                { text: 'Sigma Cebiri ve Borel Kümeleri', link: '/dersler/reel-analiz/olcu/sigma-cebiri-borel' },
                { text: 'İç ve Dış Yaklaşım', link: '/dersler/reel-analiz/olcu/ic-dis-yaklasim' },
                { text: 'Toplamsallık ve Süreklilik', link: '/dersler/reel-analiz/olcu/toplamsallik-sureklilik' },
                { text: 'Ölçülemez Kümeler ve Vitali', link: '/dersler/reel-analiz/olcu/olculemez-kumeler-vitali' }
              ]
            },
            {
              text: 'Fonksiyonlar',
              collapsed: true,
              items: [
                { text: 'Ölçülebilir Fonksiyonlar', link: '/dersler/reel-analiz/fonksiyonlar/olculebilir-fonksiyonlar' },
                { text: 'Noktasal Limitler ve Yaklaşım', link: '/dersler/reel-analiz/fonksiyonlar/noktasal-limitler-yaklasim' },
                { text: 'Littlewood, Egoroff ve Lusin Teoremleri', link: '/dersler/reel-analiz/fonksiyonlar/littlewood-egoroff-lusin' }
              ]
            },
            {
              text: 'İntegral Teorisi',
              collapsed: true,
              items: [
                { text: 'Riemann vs Lebesgue', link: '/dersler/reel-analiz/integral/riemann-vs-lebesgue' },
                { text: 'Sınırlı Fonksiyonların İntegrali', link: '/dersler/reel-analiz/integral/sinirli-fonksiyonlarin-integrali' },
                { text: 'Negatif Olmayan Fonksiyonların İntegrali', link: '/dersler/reel-analiz/integral/negatif-olmayan-integral' },
                { text: 'Genel Lebesgue İntegrali', link: '/dersler/reel-analiz/integral/genel-lebesgue-integrali' },
                { text: 'İntegrasyon Toplamsallığı', link: '/dersler/reel-analiz/integral/integrasyon-toplamsalligi' }
              ]
            }
          ]
        }
      ],
      '/dersler/sayilar-teorisi/': [
        {
          text: '🔢 Sayılar Teorisi',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/sayilar-teorisi/' },
            {
              text: 'Sayılar Teorisi I (Temel Kavramlar)',
              collapsed: true,
              items: [
                { text: 'Bölünebilme', link: '/dersler/sayilar-teorisi/1/bolunebilme' },
                { text: 'Öklid Algoritması', link: '/dersler/sayilar-teorisi/1/oklid-algoritmasi' },
                { text: 'EBOB ve EKOK', link: '/dersler/sayilar-teorisi/1/ebob-ekok' },
                { text: 'Bézout Teoremi', link: '/dersler/sayilar-teorisi/1/bezout-teoremi' },
                { text: 'Asal Sayılar', link: '/dersler/sayilar-teorisi/1/asal-sayilar' },
                { text: 'Aritmetiğin Temel Teoremi', link: '/dersler/sayilar-teorisi/1/aritmetigin-temel-teoremi' },
                { text: 'Diofant Denklemleri', link: '/dersler/sayilar-teorisi/1/denklemler' },
                { text: 'Kalan Sınıfları', link: '/dersler/sayilar-teorisi/1/kalan-siniflari' },
                { text: 'Çin Kalan Teoremi', link: '/dersler/sayilar-teorisi/1/cin-kalan-teoremi' },
                { text: 'Euler ve Fermat Teoremleri', link: '/dersler/sayilar-teorisi/1/euler-fermat' },
                { text: 'Wilson Teoremi', link: '/dersler/sayilar-teorisi/1/wilson' },
                { text: 'Aritmetik ve Çarpımsal Fonksiyonlar', link: '/dersler/sayilar-teorisi/1/aritmetik-carpimsal-giris' },
                { text: 'Euler Phi (φ) Fonksiyonu', link: '/dersler/sayilar-teorisi/1/euler-phi' },
                { text: 'Tau ve Sigma (τ, σ) Fonksiyonları', link: '/dersler/sayilar-teorisi/1/tau-sigma' },
                { text: 'Dirichlet Çarpımı', link: '/dersler/sayilar-teorisi/1/dirichlet-carpimi' },
                { text: 'Möbius Tersine Çevirme Formülü', link: '/dersler/sayilar-teorisi/1/mobius-tersine-cevirme' }
              ]
            },
            {
              text: 'Sayılar Teorisi II (İleri Kavramlar ve Rezidüler)',
              collapsed: true,
              items: [
                {
                  text: '1. İleri Kongrüanslar ve Kök Taşıma',
                  collapsed: true,
                  items: [
                    { text: 'Yüksek Mertebeden Kongrüanslar', link: '/dersler/sayilar-teorisi/2/yuksek-mertebe' },
                    { text: 'Hensel Lemması', link: '/dersler/sayilar-teorisi/2/hensel-lemmasi' },
                    { text: 'n. Kuvvetten Rezidüler', link: '/dersler/sayilar-teorisi/2/n-kuvvet-rezidu' }
                  ]
                },
                {
                  text: '2. Kuadratik (İkinci Dereceden) Rezidüler',
                  collapsed: true,
                  items: [
                    { text: 'Kuadratik Rezidü Kavramı', link: '/dersler/sayilar-teorisi/2/rezidu-kavrami' },
                    { text: 'Legendre Sembolü', link: '/dersler/sayilar-teorisi/2/legendre-sembolu' },
                    { text: 'Gauss Lemması', link: '/dersler/sayilar-teorisi/2/gauss-lemmasi' },
                  ]
                },
                {
                  text: '3. Kuadratik Resiprosite ve Semboller',
                  collapsed: true,
                  items: [
                    { text: 'Kuadratik Resiprosite Teoremi', link: '/dersler/sayilar-teorisi/2/kuadratik-resiprosite' },
                    { text: 'Jacobi Sembolü', link: '/dersler/sayilar-teorisi/2/jacobi-sembolu' }
                  ]
                },
                {
                  text: '4. Diofant Denklemleri',
                  collapsed: true,
                  items: [
                    { text: 'Doğrusal Diofant Denklemleri', link: '/dersler/sayilar-teorisi/2/lineer-olmayan' },
                  ]
                }
              ]
            }
          ]
        }
      ],
      '/dersler/soyut-cebir/': [
        {
          text: '🧩 Soyut Cebir',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/soyut-cebir/' },
            {
              text: '1. Bölüm (Grup Teorisi)',
              collapsed: true,
              items: [
                { text: 'Cebirsel Yapılara Giriş', link: '/dersler/soyut-cebir/1/cebirsel-yapilar' },
                { text: 'Gruplar', link: '/dersler/soyut-cebir/1/gruplar' },
                { text: 'Alt Yapılar', link: '/dersler/soyut-cebir/1/alt-yapilar' },
                { text: 'Alt ve Devresel Gruplar', link: '/dersler/soyut-cebir/1/alt-devresel-gruplar' },
                { text: 'Simetrik Gruplar', link: '/dersler/soyut-cebir/1/simetrik-gruplar' },
                { text: 'Normal Alt Gruplar', link: '/dersler/soyut-cebir/1/normal-alt-gruplar' },
                { text: 'Bölüm Yapıları', link: '/dersler/soyut-cebir/1/bolum-yapilari' },
                { text: 'Bölüm Grupları', link: '/dersler/soyut-cebir/1/bolum-gruplari' },
                { text: 'Homomorfizmalar', link: '/dersler/soyut-cebir/1/homomorfizmalar' },
                { text: 'İzomorfizma Teoremleri', link: '/dersler/soyut-cebir/1/izomorfizma-teoremleri' },
                { text: 'Sylow Teoremleri', link: '/dersler/soyut-cebir/1/sylow-teoremleri' }
              ]
            },
            {
              text: '2. Bölüm (Halka Teorisi)',
              collapsed: true,
              items: [
                { text: 'İki İşlemli Yapılar', link: '/dersler/soyut-cebir/2/iki-islemli-yapilar' },
                { text: 'Halka ve Alt Halka', link: '/dersler/soyut-cebir/2/halka-alt-halka' },
                { text: 'Aritmetik ve Birimler', link: '/dersler/soyut-cebir/2/aritmetik-birimler' },
                { text: 'Karakteristik ve Binom Formülü', link: '/dersler/soyut-cebir/2/karakteristik-binom' },
                { text: 'Tamlık Bölgesi ve Kesirler Cisimleri', link: '/dersler/soyut-cebir/2/tamlik-bolgesi-kesirler' },
                { text: 'İdealler', link: '/dersler/soyut-cebir/2/idealler' },
                { text: 'Maksimal ve Asal İdealler', link: '/dersler/soyut-cebir/2/maksimal-asal-idealler' },
                { text: 'Halka Homomorfizmaları', link: '/dersler/soyut-cebir/2/halka-homomorfizmalari' },
                { text: 'Polinom Halkaları', link: '/dersler/soyut-cebir/2/polinom-halkalari' },
                { text: 'Öklid Bölgeleri', link: '/dersler/soyut-cebir/2/oklid-bolgeleri' },
                { text: 'PID ve Bölüm Halkası', link: '/dersler/soyut-cebir/2/pid-bolum-halkasi' },
                { text: 'UFD (Tek Türlü Çarpanlara Ayrılma Bölgeleri)', link: '/dersler/soyut-cebir/2/ufd' }
              ]
            },
            {
              text: '3. Bölüm (Cisimler)',
              collapsed: true,
              items: [
                { text: 'Cisim Tanımı', link: '/dersler/soyut-cebir/3/cisim-tanimi' },
                { text: 'Cisim Genişlemeleri', link: '/dersler/soyut-cebir/3/genislemeler' },
                { text: 'Cebirsel ve Transandant Elemanlar', link: '/dersler/soyut-cebir/3/cebirsel-transandant' },
                { text: 'İndirgenebilirlik Kriterleri', link: '/dersler/soyut-cebir/3/indirgenebilirlik' },
                { text: 'Cebirsel Kapanış', link: '/dersler/soyut-cebir/3/cebirsel-kapanis' },
                { text: 'Parçalanış Cisimleri', link: '/dersler/soyut-cebir/3/parcalanis-cisimleri' },
                { text: 'Sonlu Genişlemeler', link: '/dersler/soyut-cebir/3/sonlu-genislemeler' },
                { text: 'Sonlu Cisimler', link: '/dersler/soyut-cebir/3/sonlu-cisimler' },
                { text: 'Cisim Otomorfizmaları', link: '/dersler/soyut-cebir/3/cisim-otomorfizmalari' },
                { text: 'Daire Bölümü Polinomları', link: '/dersler/soyut-cebir/3/daire-bolumu' }
              ]
            },
            {
              text: 'Değişmeli Cebir',
              collapsed: true,
              items: [
                { text: 'Halkalar ve İdealler', link: '/dersler/soyut-cebir/degismeli/halkalar-idealler' },
                { text: 'Maksimal ve Asal İdealler', link: '/dersler/soyut-cebir/degismeli/maksimal-asal' },
                { text: 'Sıfır Bölenler ve Nilpotent Elemanlar', link: '/dersler/soyut-cebir/degismeli/sifir-bolenler-nilpotent' },
                { text: 'Radikaller', link: '/dersler/soyut-cebir/degismeli/radikaller' },
                { text: 'Modül Kavramı', link: '/dersler/soyut-cebir/degismeli/modul-kavrami' },
                { text: 'Modül İşlemleri', link: '/dersler/soyut-cebir/degismeli/modul-islemleri' },
                { text: 'Alt Bölüm ve Modülleri', link: '/dersler/soyut-cebir/degismeli/alt-bolum-modulleri' },
                { text: 'Sonlu Doğuraylı Modüller', link: '/dersler/soyut-cebir/degismeli/sonlu-dogurayli' },
                { text: 'Modül Homomorfizmaları', link: '/dersler/soyut-cebir/degismeli/modul-homomorfizmalari' },
                { text: 'Schur Lemması', link: '/dersler/soyut-cebir/degismeli/schur-lemmasi' },
                { text: 'İndirgenebilirlik', link: '/dersler/soyut-cebir/degismeli/indirgenebilirlik' }
              ]
            }
          ]
        }
      ],
      '/dersler/topoloji/': [
        {
          text: '🥨 Topoloji',
          collapsed: false,
          items: [
            { text: 'Genel Bakış', link: '/dersler/topoloji/' },
            {
              text: 'Temeller',
              collapsed: true,
              items: [
                { text: 'Giriş', link: '/dersler/topoloji/temeller/giris' },
                { text: 'Tanım ve Örnekler', link: '/dersler/topoloji/temeller/tanim-ornekler' },
                { text: 'Açık ve Kapalı Kümeler', link: '/dersler/topoloji/temeller/acik-kapali' },
                { text: 'Komşuluklar ve Yerel Baz', link: '/dersler/topoloji/temeller/komsuluklar-yerel-baz' },
                { text: 'Baz ve Altbaz', link: '/dersler/topoloji/temeller/baz-altbaz' }
              ]
            },
            {
              text: 'Nokta-Küme Topolojisi',
              collapsed: true,
              items: [
                { text: 'İç, Dış ve Sınır Noktaları', link: '/dersler/topoloji/nokta-kume/ic-dis-sinir' },
                { text: 'Yığılma ve İzole Noktalar', link: '/dersler/topoloji/nokta-kume/yigilma-izole' },
                { text: 'Kapanış ve Yoğun Kümeler', link: '/dersler/topoloji/nokta-kume/kapanis-yogun' }
              ]
            },
            {
              text: 'Süreklilik ve İnşa',
              collapsed: true,
              items: [
                { text: 'Topolojik Süreklilik', link: '/dersler/topoloji/sureklilik/topolojik-sureklilik' },
                { text: 'Alt Uzay Topolojisi', link: '/dersler/topoloji/sureklilik/alt-uzay' },
                { text: 'Çarpım Topolojisi', link: '/dersler/topoloji/sureklilik/carpim-topolojisi' },
                { text: 'Bölüm Topolojisi', link: '/dersler/topoloji/sureklilik/bolum-topolojisi' }
              ]
            },
            {
              text: 'Metrik Uzaylar',
              collapsed: true,
              items: [
                { text: 'Metrik Uzaylar ve Topoloji', link: '/dersler/topoloji/metrik/uzaylar-topoloji' },
                { text: 'Süreklilik ve Yakınsaklık', link: '/dersler/topoloji/metrik/sureklilik-yakinsaklik' }
              ]
            },
            {
              text: 'Ayırma Aksiyomları',
              collapsed: true,
              items: [
                { text: 'T0, T1 ve T2 (Hausdorff) Uzayları', link: '/dersler/topoloji/ayirma/t0-t1-t2' },
                { text: 'Düzenli ve Normal Uzaylar', link: '/dersler/topoloji/ayirma/duzenli-normal' },
                { text: 'Sayılabilirlik Aksiyomları', link: '/dersler/topoloji/ayirma/sayilabilirlik' },
                { text: 'Ayrılabilirlik', link: '/dersler/topoloji/ayirma/ayrilabilir' }
              ]
            },
            {
              text: 'Kompaktlık ve Bağlantılılık',
              collapsed: true,
              items: [
                { text: 'Bağlantılılık', link: '/dersler/topoloji/kompaktlik/baglantililik' },
                { text: 'Tanım ve Örtüler', link: '/dersler/topoloji/kompaktlik/tanim-ortuler' },
                { text: 'Temel Teoremler', link: '/dersler/topoloji/kompaktlik/temel-teoremler' },
                { text: 'Ayırma İlişkisi', link: '/dersler/topoloji/kompaktlik/ayirma-iliskisi' }
              ]
            }
          ]
        }
      ]
    }
  },
  markdown: {
    html: true,
    math: true,
    config: (md) => {
      md.use(...customContainer('theorem', 'Teorem'))
      md.use(...customContainer('formula', 'Formül'))
      md.use(...customContainer('example', 'Örnek'))
    }
  }
})


