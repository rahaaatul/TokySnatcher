import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'TokySnatcher',
  description: 'Modern audiobook downloader for TokyBook with real-time progress tracking',
  base: '/TokySnatcher/', // This will be the base path for GitHub Pages
  outDir: './dist', // Build to root dist folder for GitHub Actions
  ignoreDeadLinks: true, // Ignore all dead link checks for now
  head: [
    ['meta', { name: 'theme-color', content: '#3b82f6' }],
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['meta', { name: 'keywords', content: 'audiobook, downloader, tokybook, cli, python, ffmpeg' }],
    ['meta', { property: 'og:title', content: 'TokySnatcher - Modern Audiobook Downloader' }],
    ['meta', { property: 'og:description', content: 'Download audiobooks from TokyBook with style and speed' }],
    ['meta', { property: 'og:image', content: '/og-image.png' }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }]
  ],
  themeConfig: {
    nav: [
      { text: '🏠 Home', link: '/' },
      {
        text: '📚 Documentation',
        items: [
          { text: 'Getting Started', link: '/guide/' },
          { text: 'Installation', link: '/guide/installation' },
          { text: 'Usage Guide', link: '/guide/usage' },
          { text: 'Features', link: '/guide/features' },
        ]
      },
      { text: '🔧 API Reference', link: '/api/cli' },
      {
        text: '📋 More',
        items: [
          { text: 'Contributing', link: '/contributing' },
          { text: 'Changelog', link: '/changelog' },
          { text: 'View on GitHub', link: 'https://github.com/rahaaatul/TokySnatcher' },
        ]
      }
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
