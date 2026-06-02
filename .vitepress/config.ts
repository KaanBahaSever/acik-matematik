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
  themeConfig: {
    socialLinks: [{ icon: 'github', link: 'https://github.com/KaanBahaSever/math-notebook' }],
    i18nRouting: true,
    aside: false
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
