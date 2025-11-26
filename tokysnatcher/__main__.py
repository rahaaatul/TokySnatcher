from dataclasses import dataclass
from typing import Optional
import argparse
import logging
import shutil
import sys
from pathlib import Path

import questionary
from rich.console import Console
from rich.table import Table

from .chapters import get_chapters
from .search import search_book
from .utils import setup_colored_logging


# Configure global Rich console
console = Console()

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class DownloadConfig:
    directory: Optional[Path]
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
    console.clear()


class RichArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that uses custom Rich help formatting."""

    def print_help(self, file=None):
        """Print beautiful Rich-formatted help."""

        console.print("\nAn extremely fast Tokybook downloader.\n")
        console.print(
            "[bold green]Usage:[/bold green] [yellow]tokysnatcher[/yellow] [cyan][OPTIONS][cyan]\n"
        )
        console.print("[bold green]Options:[/bold green]")

        options = [
            "[cyan]-h[/cyan], [cyan]--help[/cyan]",
            "[cyan]-d[/cyan], [cyan]--directory [blue]<DIRECTORY>[/blue][/cyan]",
            "[cyan]-s[/cyan], [cyan]--search [blue]<SEARCH>[/blue][/cyan]",
            "[cyan]-u[/cyan], [cyan]--url [blue]<URL>[/blue][/cyan]",
            "[cyan]-v[/cyan], [cyan]--verbose[/cyan]",
            "[cyan]-a[/cyan], [cyan]--show-all-chapter-bars[/cyan]",
        ]

        descriptions = [
            "Show this help message and exit",
            "Custom download directory",
            "Search query to bypass interactive menu",
            "Direct URL to download, bypassing search",
            "Show detailed logs during download",
            "Show all chapter progress bars permanently",
        ]

        table = Table(box=None, show_header=False, show_lines=False)
        table.add_column("Flag")
        table.add_column("Description")

        for opt, desc in zip(options, descriptions):
            table.add_row(opt, desc)

        console.print(table, markup=True)
        self.exit()


def print_usage_hint():
    """Print a quick usage hint."""
    console.print("\n[dim cyan]📖 For full help: tokysnatcher --help[/dim cyan]")


def validate_url(url: str) -> str:
    """Validate and return a validated url."""
    # More robust check (allows http, https, www, non-www)
    if "tokybook.com" not in url:
        raise ValueError(f"Invalid URL: {url}. Must be a tokybook.com URL")

    # Ensure protocol is present for requests library later
    if not url.startswith("http"):
        url = "https://" + url
    return url


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = RichArgumentParser(
        description="TokySnatcher - Download Audiobooks from TokyBook",
        prog="tokysnatcher",
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
    logger.info("Download starting.")
    get_chapters(
        url,
        config.directory,
        verbose=config.verbose,
        show_all_chapter_bars=config.show_all_chapter_bars,
    )


def handle_url_action(url: str, config: DownloadConfig) -> None:
    """Handle direct URL download."""
    validated_url = validate_url(url)
    logger.info("Downloading from provided URL.")
    execute_download(validated_url, config)


def handle_search_action(query: str, config: DownloadConfig) -> None:
    """Handle search action."""
    if not query:
        query = questionary.text("Enter search query:").ask()
        if not query:
            return
    result = search_book(query, interactive=True)
    if result:
        execute_download(result, config)


def handle_interactive_action(config: DownloadConfig) -> None:
    """Handle interactive menu selection."""

    while True:
        console.clear()
        console.print(
            "[bold magenta]Welcome to TokySnatcher Interactive Mode![/bold magenta]\n"
        )

        search_label = "🔍 Search Books"
        url_label = "🌍 Download book from URL"
        exit_label = "❌ Exit"

        choices = [url_label, search_label, exit_label]
        selected_action = questionary.select("Choose an action:", choices=choices).ask()

        if selected_action is None or selected_action == exit_label:
            logger.info("Exiting.")
            sys.exit(0)

        try:
            if selected_action == search_label:
                handle_search_action("", config)
            elif selected_action == url_label:
                url = get_validated_input()
                if url is not None:
                    handle_url_action(url, config)
        except Exception as e:
            console.print(f"[red]Error during download: {e}[/red]")


def get_validated_input() -> Optional[str]:
    """Get validated URL input from user."""
    while True:
        url = questionary.text("Enter URL:").ask()
        if url is None or url == "":  # User cancelled or empty
            return None
        try:
            return validate_url(url)
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")


def main() -> None:
    """Main entry point for TokySnatcher."""
    check_ffmpeg()

    # Let argparse handle the help flag automatically via CustomHelpAction
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
        logger.warning("\nProcess interrupted by user.")
        sys.exit(0)
    except Exception:
        logger.exception("An unexpected error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()
