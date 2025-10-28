import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'TokySnatcher',
  description: 'Snatch audiobooks from Tokybook 😈',
  base: '/TokySnatcher/', // This will be the base path for GitHub Pages
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/' },
      { text: 'API', link: '/api/' }
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Introduction',
          items: [
            { text: 'What is TokySnatcher?', link: '/guide/' },
            { text: 'Installation', link: '/guide/installation' },
            { text: 'Usage', link: '/guide/usage' },
            { text: 'Features', link: '/guide/features' }
          ]
        }
      ],
      '/api/': [
        {
          text: 'API Reference',
          items: [
            { text: 'CLI Commands', link: '/api/cli' }
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/rahaaatul/TokySnatcher' }
    ],

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2025-present TokySnatcher'
    }
  }
})
