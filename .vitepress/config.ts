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
  base: '/acik-matematik/',
  title: '🌿 Açık Matematik Arşivi',
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
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/acik-matematik/favicon2.svg' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: 'true' }],
    ['link', { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Lora:ital,wght@0,400;0,600;1,400&family=Merriweather:wght@300;700&display=swap' }]
  ],
  themeConfig: {
    socialLinks: [{ icon: 'github', link: 'https://github.com/KaanBahaSever/math-notebook' }],
    i18nRouting: true,
    aside: false,
    footer: {
      message: 'Akademik amaçlarla tasarlanmış açık kaynaklı eğitim arşivi.',
      copyright: 'Copyright © 2026 | Tüm Hakları Saklıdır'
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
