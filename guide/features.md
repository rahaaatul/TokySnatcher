# Features

TokySnatcher comes packed with features designed to make audiobook downloading as smooth and efficient as possible.

## 🔍 Smart Search

Browse through TokyBook's extensive audiobook library with powerful search capabilities:

- **Keyword matching**: Find books by title, author, or description
- **Interactive selection**: Choose from search results in an easy-to-use interface
- **Direct URLs**: Support for direct book page links

## 📥 Batch Downloads

Never worry about downloading chapters one by one again:

- **Complete books**: Download entire audiobooks automatically
- **Chapter management**: Organizes all chapters into numbered MP3 files
- **Queue system**: Downloads multiple chapters simultaneously where possible
- **Resume capability**: Pick up where you left off if downloads are interrupted

## 📊 Progress Tracking

Get detailed insights into your download progress:

- **Real-time updates**: Live progress bars and status indicators
- **Detailed statistics**: File sizes, transfer speeds, and time remaining
- **Multi-chapter overview**: See the status of each chapter in your book
- **Visual indicators**: Status icons (⏳ Ready, 🔄 Running, ✅ Done, ❌ Failed)

### Progress Display Example

```
🚀 Downloading audiobooks (5/12 chapters) 📝 🔄 Running: 1, ⏳ Ready: 4, ✅ Done: 6

⏳ Speed and Scale                                                 1/? Sweated... 2024
⏳ Building a Second Brain 2/? The Three Stages of Saving...        0MB / 15.2MB
✅ Speed and Scale 1/? The Problem with Scale...                   12.4MB / 12.4MB
✅ Building a Second Brain 1/? What is a Second Brain?...          8.9MB / 8.9MB
```

## 🔧 CLI Automation

Perfect for scripting and automation:

- **Command-line interface**: Full command-line operation
- **Multiple flags**: Search, URL, directory options
- **Non-interactive mode**: Run without user input
- **Help system**: Comprehensive command documentation

## 🌐 Cross-Platform

Works seamlessly across different operating systems:

- **Windows**: Full support with Chocolatey/Scoop/Winget FFmpeg installation
- **macOS**: Native FFmpeg support via Homebrew
- **Linux**: Aptitude package manager integration
- **Consistent behavior**: Same interface and functionality everywhere

## 🎵 High Quality Output

Audio processing powered by industry-standard tools:

- **FFmpeg integration**: Professional audio processing
- **MP3 format**: Widely compatible output format
- **Quality preservation**: Maintains original audio quality where possible
- **Metadata support**: Chapter naming and book information

## 🏗️ Key Technologies

### Core Dependencies
- **Python 3.9+**: Modern Python with excellent performance
- **FFmpeg**: Industry-standard audio/video processing
- **Requests**: Reliable HTTP client for downloads
- **Rich**: Beautiful terminal interface components

### Library Highlights

#### [`gazpacho`](https://github.com/maxhumber/gazpacho) - HTML Parsing
Lightweight and familiar web scraping library that works like BeautifulSoup but with a different API.

#### [`halo`](https://github.com/manrajgrover/halo) - Progress Spinners
Beautiful spinners for terminal applications with custom frames, colors, and text.

#### [`questionary`](https://github.com/tmbo/questionary) - Interactive Prompts
Powerful library for interactive command-line prompts and questions.

#### [`pebble`](https://github.com/noxdafox/pebble) - Thread Pool
Excellent library for managing concurrent threads with proper error handling.

## 🎯 Use Cases

### For Individual Users
- **Personal library building**: Curate your own audiobook collection
- **Offline listening**: Download for transport or areas with poor connectivity
- **Backup**: Preserve access to books you enjoy

### For Automation
- **Bulk downloads**: Batch processing of multiple books
- **Scheduled downloads**: Automated periodic updates
- **Integration**: Part of larger media management systems

### For Advanced Users
- **API building**: Foundation for programmatic interfaces
- **Custom workflows**: Extend with your own processing scripts
- **Research**: Access to educational content offline

::: info
TokySnatcher is designed to be both user-friendly for beginners and powerful enough for advanced automation scenarios.
:::
