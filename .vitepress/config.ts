import { defineConfig } from 'vitepress'
import mathjax3 from 'markdown-it-mathjax3'
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
  title: 'Matematik Defteri',
  description: 'Açık kaynak kapsamlı matematik ders notları',
  cleanUrls: true,
  locales: {
    root: {
      label: 'Türkçe',
      lang: 'tr-TR',
      themeConfig: {
        nav: [
          { text: 'Ana Sayfa', link: '/' },
          { text: 'Gerçek Analiz', link: '/real-analysis/' },
          { text: 'Lineer Cebir', link: '/linear-algebra/' }
        ],
        sidebar: [
          {
            text: 'Gerçek Analiz',
            items: [{ text: 'Diziler', link: '/real-analysis/sequences' }]
          },
          {
            text: 'Kompleks Analiz',
            items: [{ text: 'Giriş', link: '/complex-analysis/' }]
          },
          {
            text: 'Diferansiyel Denklemler',
            items: [{ text: 'Giriş', link: '/differential-equations/' }]
          },
          {
            text: 'Soyut Cebir',
            items: [{ text: 'Giriş', link: '/abstract-algebra/' }]
          },
          {
            text: 'Sayılar Teorisi',
            items: [{ text: 'Giriş', link: '/number-theory/' }]
          },
          {
            text: 'Topoloji',
            items: [{ text: 'Giriş', link: '/topology/' }]
          },
          {
            text: 'Diferansiyel Geometri',
            items: [{ text: 'Giriş', link: '/differential-geometry/' }]
          },
          {
            text: 'Lineer Cebir',
            items: [{ text: 'Giriş', link: '/linear-algebra/' }]
          },
          {
            text: 'Kriptografi',
            items: [{ text: 'Giriş', link: '/cryptography/' }]
          },
          {
            text: 'Stokastik Süreçler',
            items: [{ text: 'Giriş', link: '/stochastic-processes/' }]
          }
        ]
      }
    },
    en: {
      label: 'English',
      lang: 'en-US',
      link: '/en/',
      title: 'Math Notebook',
      description: 'Open-source comprehensive mathematics lecture notes'
    }
  },
  themeConfig: {
    socialLinks: [{ icon: 'github', link: 'https://github.com/KaanBahaSever/math-notebook' }],
    i18nRouting: true
  },
  markdown: {
    html: true,
    config: (md) => {
      md.use(mathjax3)
      md.use(...customContainer('theorem', 'Teorem'))
      md.use(...customContainer('formula', 'Formül'))
      md.use(...customContainer('example', 'Örnek'))
    }
  }
})
