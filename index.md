---
layout: home

title: TokySnatcher
titleTemplate: Modern Audiobook Downloader

hero:
  name: TokySnatcher
  text: Audiobook Downloader
  tagline: Download audiobooks from TokyBook with style and speed. Beautifully designed CLI tool with real-time progress tracking.
  image: /logo.png
  actions:
    - theme: brand
      text: 🚀 Quick Start
      link: /guide/installation
    - theme: alt
      text: 📖 Documentation
      link: /guide/
    - theme: alt
      text: 💻 View Source
      link: https://github.com/rahaaatul/TokySnatcher

features:
  - icon: 🔍
    title: Intelligent Search
    details: Powerful search through TokyBook's vast audiobook collection. Find books by title, author, or keywords with instant results.
  - icon: ⚡
    title: Lightning Fast
    details: Multi-threaded downloads with real-time progress tracking. See transfer speeds, completion percentages, and estimated time remaining.
  - icon: 📱
    title: Cross-Platform
    details: Seamlessly works on Windows, macOS, and Linux. Consistent experience across all platforms with native performance.
  - icon: 🎵
    title: Premium Quality
    details: FFmpeg-powered audio processing delivers high-quality MP3 files. Preserves original audio quality and adds proper metadata.
  - icon: 🔧
    title: CLI Automation
    details: Command-line interface perfect for scripting and automation. Non-interactive mode for scheduled downloads and batch processing.
  - icon: 💾
    title: Batch Downloads
    details: Download complete audiobooks automatically. Organizes chapters, handles interruptions, and resumes where you left off.

screenshots:
  - title: Real-Time Progress Display
    src: ./screenshots/progress.png
    alt: Beautiful progress display with real-time statistics

footer: '<div style="display: flex; align-items: center; justify-content: space-between; width: 100%;"><p>Released under the <a href="https://github.com/rahaaatul/TokySnatcher/blob/main/LICENSE" target="_blank">MIT License</a> | Copyright © 2025-present TokySnatcher</p><p>Built with <a href="https://vitepress.dev/" target="_blank">VitePress</a></p></div>'
---

<!-- Custom CSS for enhancements -->
<style>
:root {
  --vp-home-hero-name-color: #3b82f6;
  --vp-home-hero-name-background: -webkit-linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --vp-home-hero-background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.hero-image {
  max-width: 100px;
  margin: 0 auto 2rem;
}

.feature-icon {
  font-size: 2em;
  margin-bottom: 0.5em;
  display: block;
}

@media (min-width: 768px) {
  .hero-image {
    max-width: 120px;
  }
}
</style>
