# Changelog

All notable changes to TokySnatcher will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2025-XX-XX

This release introduces significant improvements to the download experience, enhanced Windows compatibility, and new command-line features for streamlined automation.

### 🚀 Added

- **Rich Progress Bars**: Implemented beautiful, real-time progress visualization using the Rich library, showing individual chapter progress with time estimates and completion percentages
- **Direct URL Downloads**: Added `--url` argument to bypass the interactive interface entirely for direct audiobook downloads
- **Non-interactive Search**: Introduced `--search` flag to perform searches and downloads without requiring user input
- **FFmpeg Integration**: Overhauled the download system to use FFmpeg for downloading HLS streams and converting them to high-quality MP3 files
- **Multi-threaded Progress Tracking**: Enhanced parallel downloading with sophisticated progress monitoring, including status icons (⏳ queued → 🔄 running → ✅ done)

### 🔧 Changed

- **Enhanced Error Handling**: Improved robustness in download operations and user interaction flows
- **Custom Directory Support**: Better handling of custom download directories
- **Logging Enhancements**: More comprehensive logging for better troubleshooting

### 🐛 Fixed

- **Windows Compatibility**: Replaced deprecated `pick` library with `questionary` and added conditional imports to fix Windows compatibility issues
- **Search API Fixes**: Resolved issues with book search functionality and result pagination
- **Player URL Update**: Adapted to changes in TokyBook's player API endpoint
- **Dependency Pinning**: Fixed questionary version to 2.1.1 to resolve runtime bugs

### 🔒 Dependencies

- **Added**: Rich library for enhanced terminal UI
- **Added**: FFmpeg requirement (must be installed and available in PATH)
- **Updated**: questionary to version 2.1.1

### ⚠️ Breaking Changes

- **FFmpeg Requirement**: FFmpeg is now required to run TokySnatcher. Users without FFmpeg should install it separately

### 📋 Compatibility

- **Backward Compatible**: Full backward compatibility with existing usage patterns maintained
- **Cross-Platform**: Windows compatibility restored, maintains support for macOS, Linux, and other Unix-like systems

### 🙏 Acknowledgments

Special thanks to [fiendish](https://github.com/fiendish) for contributions to fixing API compatibility issues and improving the overall stability of the application.

---

**Installation Note**: For installation and usage instructions, please refer to the [Installation Guide](./guide/installation.md).

## Version History

### 0.3.2 and Earlier

See git commit history for changes prior to v0.3.3.

---

## Contributing to the Changelog

When contributing to TokySnatcher, please:

1. **Keep CHANGELOG.md updated**: Add entries for new features, fixes, and breaking changes
2. **Follow the format**: Use the specified format with appropriate types (Added, Changed, Fixed, etc.)
3. **Update on releases**: The changelog should be updated when cutting new releases
4. **Link to issues/PRs**: Reference issue numbers and pull request links where applicable

### Types of Changes

- **🚀 Added** for new features
- **🔧 Changed** for changes in existing functionality
- **🐛 Fixed** for any bug fixes
- **🔒 Dependencies** for changes to dependencies or requirements
- **⚠️ Breaking Changes** for changes that break backward compatibility
- **📋 Compatibility** for platform or version compatibility notes
