# Usage

TokySnatcher offers multiple ways to download audiobooks from TokyBook, ranging from interactive mode to automated batch processing.

## 🎯 Interactive Mode (Default)

This is the easiest way to get started. TokySnatcher will guide you through the process step by step:

```bash
tokysnatcher
# or
toky
```

The interactive mode will prompt you to:
1. Search for books or enter a direct URL
2. Select your preferred book from search results
3. Choose a download directory
4. Begin the download process

## 📥 Direct Download

Download directly from a TokyBook URL:

```bash
tokysnatcher --url "https://tokybook.com/book/your-book-url"
```

## 🔍 Search and Download

Perform a search and download without interactive prompts:

```bash
tokysnatcher --search "book title"
```

## 📂 Custom Download Directory

Specify where to save your audiobooks:

```bash
tokysnatcher --directory "/path/to/your/audiobooks"
```

## 🔄 Combined Options

Combine multiple options for maximum automation:

```bash
tokysnatcher --search "science fiction" --directory "~/Audiobooks/"
```

## 📋 Command Help

Get detailed information about all available commands:

```bash
tokysnatcher --help
```

## 📊 Download Progress

While downloading, TokySnatcher shows real-time progress with:

- **Percentage completion**: Current download status
- **Time estimates**: Remaining time calculation
- **Transfer rates**: Current and average speed
- **File sizes**: Current and total file sizes
- **Status icons**: Visual indicators for different stages

### Example Progress Output

```
🚀 Downloading audiobooks (5/12 chapters) 📝 🔄 Running: 1, ⏳ Ready: 4, ✅ Done: 6

⏳ Speed and Scale                                                 1/? Sweated... 2024
⏳ Building a Second Brain 2/? The Three Stages of Saving...        0MB / 15.2MB
✅ Speed and Scale 1/? The Problem with Scale...                   12.4MB / 12.4MB
✅ Building a Second Brain 1/? What is a Second Brain?...          8.9MB / 8.9MB
```

## 📁 Output

TokySnatcher organizes downloaded audiobooks into folders with:
- **Main folder**: Named after the book title
- **Individual chapters**: Numbered MP3 files
- **Metadata**: Book information and cover images (when available)

### Example Structure
```
Audiobooks/
└── Building a Second Brain/
    ├── 001_Introduction.mp3
    ├── 002_The_Three_Stages_of_Saving.mp3
    ├── 003_Collecting_What_Resonates.mp3
    └── cover.jpg
```

## ⚠️ Important Notes

::: warning
Always ensure you have legal rights to download and keep the audiobooks you access through TokySnatcher. The tool is provided as-is, and users are responsible for complying with applicable laws and terms of service.
:::

::: tip
For large downloads, consider using a reliable internet connection and ensure you have sufficient disk space. The tool will automatically resume interrupted downloads where possible.
:::
