# CLI Commands

This page documents all available command-line options and arguments for TokySnatcher.

## Core Dependencies & Technical Details

### Dependencies
- **Python 3.9+**: Modern Python with excellent performance
- **FFmpeg**: Industry-standard audio/video processing (required)
- **Requests**: Reliable HTTP client for downloads
- **Rich**: Beautiful terminal interface components
- **Gazpacho**: Lightweight HTML parsing library
- **Halo**: Terminal progress spinners
- **Questionary**: Interactive command-line prompts
- **Pebble**: Concurrent thread pool management

### Architecture
- **Scraping Engine**: Custom HTML parsing with gazpacho
- **Download Manager**: Multi-threaded HLS stream processing with FFmpeg
- **Progress Tracking**: Real-time status with Rich library components
- **UI Framework**: Interactive menus using questionary

## Command Syntax

```bash
tokysnatcher [OPTIONS]
# or
toky [OPTIONS]
```

## Command Alias

Both `tokysnatcher` and `toky` are equivalent and provide the same functionality.

## Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--directory` | `-d` | string | Current directory | Specify custom download directory |
| `--search` | `-s` | string | None | Search query to bypass interactive menu |
| `--url` | `-u` | string | None | Direct URL to download, bypassing search |
| `--help` | `-h` | - | - | Show help message and exit |
| `--version` | `-v` | - | - | Show version number and exit |

## Usage Examples

### Interactive Mode (Default)
```bash
tokysnatcher
```
Starts the interactive menu where you can select actions step by step.

### Search and Download
```bash
# Search for books interactively, then download selected result
tokysnatcher

# Direct search and download (non-interactive)
tokysnatcher --search "building a second brain"
```

### Direct URL Download
```bash
tokysnatcher --url "https://tokybook.com/book/some-book-url"
```

### Custom Download Directory
```bash
# With interactive mode
tokysnatcher --directory "/path/to/audiobooks"

# With direct download
tokysnatcher --search "science fiction" --directory "~/Audiobooks/"
```

### Combined Options
```bash
tokysnatcher --search "productivity" --directory "~/Downloads/Audiobooks"
```

## Command Behavior

### Interactive Mode Behavior
When no arguments are provided, TokySnatcher enters interactive mode with the following flow:

1. **Menu Selection**: Choose between "Search book", "Download from URL", or "Exit"
2. **Search Mode**: Enter search query → Select from results → Choose download directory
3. **URL Mode**: Enter TokyBook URL → Choose download directory
4. **Download**: Process chapters and show progress

### Argument Priority
Arguments follow this priority order:
1. `--url` (highest priority - skips all interactive steps)
2. `--search` (medium priority - skips search menu)
3. No arguments (lowest priority - full interactive mode)

### Directory Resolution
- **Relative paths**: Resolved from current working directory
- **Absolute paths**: Used as-provided
- **Tilde expansion**: `~/folder` expands to user home directory
- **Default**: Current working directory if not specified

## Error Handling

### FFmpeg Check
TokySnatcher automatically checks for FFmpeg availability at startup:
- **Success**: Continues execution
- **Failure**: Shows installation instructions and exits

### Invalid URLs
When providing `--url`, the system validates:
- Must start with `https://tokybook.com/`
- Invalid URLs prompt for re-entry in interactive mode

### Network Issues
- Automatic retry for failed downloads
- Graceful handling of connection timeouts
- Resume capability for interrupted downloads

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (FFmpeg missing, network issues, etc.) |

## Configuration

### Environment Variables
Currently, TokySnatcher doesn't use environment variables for configuration.

### Configuration Files
No configuration files are currently supported.

## Advanced Usage

### Scripting
```bash
#!/bin/bash
# Download multiple books
BOOKS=("book1" "book2" "book3")
for book in "${BOOKS[@]}"; do
    tokysnatcher --search "$book" --directory "~/Audiobooks"
done
```

### Logging
Logs are written to stderr with format:
```
YYYY-MM-DD HH:MM:SS - LEVEL - Message
```

### Signal Handling
- `Ctrl+C` (SIGINT): Graceful shutdown with cleanup
- Progress saved for resume capability

::: info
For more advanced automation scenarios, consider integrating with download managers or scheduling systems that can call TokySnatcher with specific parameters.
:::
