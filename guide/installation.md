# Installation

## 📋 System Requirements

<Tip>
TokySnatcher requires **Python 3.9 or higher** and **FFmpeg** to be installed on your system.
</Tip>

<div class="requirements-grid">
  <div class="requirement">
    <h4>🐍 Python</h4>
    <p>Version 3.9+</p>
    <code>python --version</code>
  </div>
  <div class="requirement">
    <h4>🎵 FFmpeg</h4>
    <p>Audio processing</p>
    <code>ffmpeg -version</code>
  </div>
</div>

<style>
.requirements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1.5rem 0;
}

.requirement {
  background: var(--vp-c-bg-alt);
  border: 1px solid var(--vp-c-border);
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
}

.requirement h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2em;
}

.requirement code {
  background: var(--vp-c-text-3);
  color: var(--vp-c-bg);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.9em;
}
</style>

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

## 🚀 Quick Installation

### One-Line Install (Recommended)
```bash
pip install tokysnatcher
```

### Alternative: Install from Source
If you want the latest development version:
```bash
pip install git+https://github.com/rahaaatul/TokySnatcher.git
```

### Using uv (Modern Package Manager)
```bash
uv pip install tokysnatcher
```

## 🎯 Quick Start

After installation, run TokySnatcher for the first time:

```bash
# Basic usage
tokysnatcher

# Or use the short alias
toky
```

### First Run Example
```
🚀 TokySnatcher - Audiobook Downloader

Choose action:
❯ Search book
  Download from URL
  Exit
```

## ✅ Verify Your Setup

Ensure everything is working correctly:

### Check Installation
```bash
tokysnatcher --version
# Output: TokySnatcher v0.3.3
```

### Check FFmpeg
```bash
ffmpeg -version | head -1
# Output: ffmpeg version 6.1.1
```

::: tip Aliases Available
TokySnatcher provides two convenient aliases:
- `tokysnatcher` (full name)
- `toky` (short alias)

Both commands work identically!
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
