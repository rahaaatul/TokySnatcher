# TokySnatcher Release Notes

## Version 0.3.3

This release introduces significant improvements to the download experience, enhanced Windows compatibility, and new command-line features for streamlined automation.

### 🚀 New Features

- **Rich Progress Bars**: Implemented beautiful, real-time progress visualization using the Rich library, showing individual chapter progress with time estimates and completion percentages.
- **Direct URL Downloads**: Added `--url` argument to bypass the interactive interface entirely for direct audiobook downloads.
- **Bypassing Search UI**: Introduced `--search` flag to perform searches non-interactively without requiring user input.
- **FFmpeg Integration**: Overhauled the download system to use FFmpeg for downloading HLS streams and converting them to high-quality MP3 files, with integrated progress tracking.
- **Multi-threaded Progress Tracking**: Enhanced parallel downloading with sophisticated progress monitoring, including status icons (queued ⏳ → running 🔄 → done ✅) and detailed metrics.

### 🔧 Improvements

- **Enhanced Error Handling**: Improved robustness in download operations and user interaction flows.
- **Custom Directory Support**: Better handling of custom download directories.
- **Logging Enhancements**: More comprehensive logging for better troubleshooting.

### 🐛 Bug Fixes

- **Windows Compatibility**: Replaced deprecated `pick` library with `questionary` and added conditional imports to fix Windows compatibility issues.
- **Search API Fixes**: Resolved issues with book search functionality and result pagination.
- **Player URL Update**: Adapted to changes in TokyBook's player API endpoint.
- **Dependency Pinning**: Fixed questionary version to 2.1.1 to resolve runtime bugs.

### 🔒 Dependencies & Requirements

- Added Rich library for enhanced terminal UI
- Added FFmpeg requirement (must be installed and available in PATH)
- Updated questionary to version 2.1.1

**Breaking Changes**: FFmpeg is now required to run TokySnatcher. Users without FFmpeg should install it separately.

### 📋 Compatibility

- Full backward compatibility with existing usage patterns
- Windows compatibility restored
- Maintains support for macOS, Linux, and other Unix-like systems

### 🙏 Acknowledgments

Special thanks to [fiendish](https://github.com/fiendish) for contributions to fixing API compatibility issues and improving the overall stability of the application.

---

For installation and usage instructions, please refer to the README.md file.
