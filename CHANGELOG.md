# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-10-28

## Release v0.4.0

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
- **Race Condition Fix**: Resolved critical race condition in progress updates by moving shutdown checks inside lock context to prevent UI corruption during multi-threaded operations.
- **Thread-Safe Shutdown**: Fixed shutdown behavior during concurrent downloads with better synchronization prevents state corruption.
- **Progress State Consistency**: Eliminated state corruption issues during concurrent operations and shutdown sequences.

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

For installation and usage instructions, please refer to the [README](https://github.com/rahaaatul/TokySnatcher/blob/main/README.md) file.


## [0.3.3] - 2025-10-XX

### Added
- **Rich Progress Bars**: Implemented beautiful, real-time progress visualization with time estimates and completion percentages
- **Direct URL Downloads**: Added `--url` argument to bypass interactive interface for direct audiobook downloads
- **Search Bypass**: Introduced `--search` flag for non-interactive searches without user input
- **FFmpeg HLS Support**: Enhanced download system to use FFmpeg for HLS streams with MP3 conversion and integrated progress tracking

### Fixed
- **Windows Compatibility**: Replaced deprecated `pick` library with `questionary` and added conditional imports
- **Search API Issues**: Resolved search functionality and pagination problems
- **API Endpoint Updates**: Adapted to TokyBook's player API changes
- **Library Version Pinning**: Fixed questionary to version 2.1.1 to resolve runtime bugs

### Technical
- **Multi-threaded Downloads**: Enhanced parallel downloading with sophisticated progress monitoring
- **FFmpeg Integration**: High-quality MP3 conversion with authentication headers
- **Enhanced Logging**: Comprehensive logging for better troubleshooting and error recovery

## [0.3.1] - 2025-01-XX

### Added
- Enhanced error handling and user interaction flows
- Better custom directory support for downloads

## [0.3.0] - 2024-XX-XX

### Changed
- Major overhaul of download system architecture
- Improved compatibility across platforms

## [0.2.0] - 2024-XX-XX

### Added
- Initial search functionality
- Chapter download capabilities
- Basic progress tracking

## [0.1.0] - 2024-XX-XX

### Added
- Initial release with basic TokyBook download functionality
- Simple CLI interface
- Core audiobook downloading from tokybook.com
