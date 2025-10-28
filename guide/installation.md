# Installation

## 📋 Requirements

TokySnatcher requires Python 3.9 or higher and FFmpeg to be installed on your system.

## 🛠 Installing FFmpeg

### macOS
```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install ffmpeg
```

### Windows

#### Using Chocolatey
```powershell
choco install ffmpeg
```

#### Using Scoop
```powershell
scoop install ffmpeg
```

#### Using Winget
```powershell
winget install ffmpeg
```

**Other systems**: Install FFmpeg using your package manager

## 🚀 Install TokySnatcher

### From PyPI (Recommended)
```bash
pip install tokysnatcher
```

### From Source
```bash
pip install git+https://github.com/rahaaatul/TokySnatcher.git
```

## ✅ Verify Installation

After installation, verify that TokySnatcher is working:

```bash
tokysnatcher --version
# or
toky --version
```

::: info
TokySnatcher provides two command aliases: `tokysnatcher` and `toky`. Both work identically.
:::

## 🐛 Troubleshooting

### FFmpeg Not Found
If you encounter FFmpeg-related errors:

1. Ensure FFmpeg is installed and accessible via your system's PATH
2. Restart your terminal/command prompt
3. If using virtual environments, install FFmpeg system-wide

### Python Version Issues
TokySnatcher requires Python 3.9+. Check your version:

```bash
python --version
```

If you have multiple Python versions, use `python3` instead of `python`
