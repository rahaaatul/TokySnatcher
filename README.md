# TokySnatcher 🤫

> > Snatch audiobooks from Tokybook 😈

## 📋 Requirements

- Python 3.9 or higher
- **FFmpeg** (required for v0.3.3+) - Must be installed and available in your system PATH

### Installing FFmpeg

#### macOS
```shell
brew install ffmpeg
```

#### Linux
```shell
sudo apt update && sudo apt install ffmpeg
```

#### Windows

- Choco
```powershell
choco install ffmpeg
```

- Scoop
```powershell
scoop install ffmpeg
```

- Winget

```powershell
winget install ffmpeg
```

**Other systems**: Install FFmpeg using your package manager

## 🛠 Installation

```shell
pip install tokysnatcher
```

Or install from source:
```shell
pip install git+https://github.com/rahaaatul/TokySnatcher.git
```

## 🎯 Usage

### Interactive Mode (Default)
Run TokySnatcher for the full interactive experience:
```bash
tokysnatcher
```

or

```bash
toky
```
You'll be prompted to search for books or enter a direct URL.

### Direct Download
Download directly from a TokyBook URL:
```bash
tokysnatcher --url "https://tokybook.com/book/your-book-url"
```

### Search and Download (Automated)
Perform a search and download without interactive prompts:
```bash
tokysnatcher --search "book title"
```

### Custom Download Directory
Specify where to save your audiobooks:
```bash
tokysnatcher --directory "/path/to/your/audiobooks"
```

Combine options:
```bash
tokysnatcher --search "science fiction" --directory "~/Audiobooks/"
```

### Command Help
```bash
tokysnatcher --help
```

## 📊 Features

- **🔍 Smart Search**: Search TokyBook's extensive audiobook library
- **📥 Batch Downloads**: Download entire audiobooks with multiple chapters
- **📊 Progress Tracking**: Real-time download progress with percentage, time estimates, and status icons
- **🔧 CLI Automation**: Direct URL and search arguments for scripting and automation
- **🌐 Cross-Platform**: Works on Windows, macOS, and Linux
- **🎵 High Quality**: Outputs to MP3 format using FFmpeg

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
>
