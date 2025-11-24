from dataclasses import dataclass
import argparse
import logging
import platform
import shutil
import sys
from os import name, system
from pathlib import Path

import questionary

from .chapters import get_chapters
from .search import search_book

# Terminal settings for Unix-like systems
if platform.system() != "Windows":
    import termios

    fd: int = sys.stdin.fileno()
    old_term_settings: list[int] = termios.tcgetattr(fd)
else:
    termios = None

from .utils import setup_colored_logging

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class DownloadConfig:
    directory: Path | None
    verbose: bool
    show_all_chapter_bars: bool


def check_ffmpeg() -> None:
    """Check if ffmpeg is available in PATH."""
    if not shutil.which("ffmpeg"):
        logger.error("ffmpeg is required but not found in PATH")
        logger.info("Please install ffmpeg:")
        logger.info("  macOS: brew install ffmpeg")
        logger.info("  Ubuntu/Debian: sudo apt install ffmpeg")
        logger.info("  Windows: Download from https://ffmpeg.org/download.html")
        sys.exit(1)


def clear_terminal() -> None:
    """Clear the terminal screen."""
    system("cls" if name == "nt" else "clear")  # noqa: S605


def validate_url(url: str) -> str:
    """Validate and return a validated url."""
    if not url.startswith("https://tokybook.com/"):
        raise ValueError(f"Invalid URL: {url}. Must start with https://tokybook.com/")
    return url


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="TokySnatcher - Download Audiobooks from TokyBook"
    )
    parser.add_argument(
        "-d", "--directory", type=str, default=None, help="Custom download directory"
    )
    parser.add_argument(
        "-s",
        "--search",
        type=str,
        default=None,
        help="Search query to bypass interactive menu",
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        default=None,
        help="Direct URL to download, bypassing search",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed logs during download",
    )
    parser.add_argument(
        "-a",
        "--show-all-chapter-bars",
        action="store_true",
        default=False,
        help="Show all chapter progress bars permanently",
    )
    return parser.parse_args()


def execute_download(url: str, config: DownloadConfig) -> None:
    """Execute the download process for a given URL."""
    from .utils import _shutdown_requested

    logger.info("Download starting.")
    get_chapters(
        url,
        config.directory,
        verbose=config.verbose,
        show_all_chapter_bars=config.show_all_chapter_bars,
    )

    # Check if download was interrupted
    if _shutdown_requested:
        logger.warning("Download was cancelled by user.")


def handle_url_action(url: str, config: DownloadConfig) -> None:
    """Handle direct URL download."""
    validated_url = validate_url(url)
    logger.info("Downloading from provided URL.")
    execute_download(validated_url, config)


def handle_search_action(query: str, config: DownloadConfig) -> None:
    """Handle search action."""
    result = search_book(query, interactive=True)
    if result:
        execute_download(result, config)


def handle_interactive_action(config: DownloadConfig) -> None:
    """Handle interactive menu selection."""
    choices = ["Search book", "Download from URL", "Exit"]
    selected_action = questionary.select("Choose action:", choices=choices).ask()

    if selected_action is None:
        logger.info("No action selected. Exiting.")
        return

    actions = {
        "Search book": lambda: handle_search_action(
            input("Enter search query: "), config
        ),
        "Download from URL": lambda: handle_url_action(get_validated_input(), config),
        "Exit": lambda: None,
    }

    action = actions.get(selected_action)
    if action:
        action()


def get_validated_input() -> str:
    """Get validated URL input from user."""
    url = input("Enter URL: ")
    try:
        return validate_url(url)
    except ValueError as e:
        print(f"Error: {e}")
        return get_validated_input()


def get_input() -> str:
    """Get URL input from user for manual download. Deprecated, use get_validated_input."""
    while True:
        url = input("Enter URL: ")
        try:
            return validate_url(url)
        except ValueError as e:
            print(f"Error: {e}")
            continue


def main() -> None:
    """Get argument from CLI and execute the selected action."""
    check_ffmpeg()
    args = parse_arguments()
    setup_colored_logging(args.verbose)

    config = DownloadConfig(
        directory=Path(args.directory) if args.directory else None,
        verbose=args.verbose,
        show_all_chapter_bars=args.show_all_chapter_bars,
    )

    try:
        if args.url:
            handle_url_action(args.url, config)
        elif args.search:
            handle_search_action(args.search, config)
        else:
            handle_interactive_action(config)
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user.")
        sys.exit(0)
    except Exception:
        logger.exception("An unexpected error occurred")
        sys.exit(1)
    finally:
        if termios:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_term_settings)


if __name__ == "__main__":
    main()
