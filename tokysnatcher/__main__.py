from dataclasses import dataclass
from typing import Optional
import argparse
import logging
import shutil
import sys
from os import name, system
from pathlib import Path

import questionary
from rich.console import Console
from rich.table import Table

from .chapters import get_chapters
from .search import search_book
from .utils import setup_colored_logging

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
    system("cls" if name == "nt" else "clear")  # noqa: S605


class RichHelpFormatter(argparse.HelpFormatter):
    """Clean Rich formatter with colors but no decorations."""

    def __init__(self, prog, indent_increment=2, max_help_position=24, width=None):
        """Initialize with proper argparse.HelpFormatter attributes."""
        super().__init__(prog, indent_increment, max_help_position, width)

    def format_help(self) -> str:
        """Override format_help to use clean Rich grid layout."""
        import io

        # Use StringIO to capture Rich output as string
        output_buffer = io.StringIO()
        console = Console(file=output_buffer, width=self._width)

        # Rich title with centered styling
        output_parts = []
        output_parts.append("")
        rule_text = "─" * (self._width - 4)  # Simple unicode rule chars
        output_parts.append(f"────{rule_text}─")
        output_parts.append("[bold magenta]TokySnatcher[/bold magenta] [dim]-[/dim] [bold green]Download Audiobooks from TokyBook[/bold green]")
        output_parts.append(f"────{rule_text}─")
        output_parts.append("")

        # Commands section
        commands_table = Table.grid()
        commands_table.add_column(justify="left")
        commands_table.add_column(justify="left")



        # Options section
        options_table = Table.grid()
        options_table.add_column(justify="left", min_width=35)
        options_table.add_column(justify="left")

        options_table.add_row("  [green]-d, --directory[/green] [red]DIRECTORY[/red]",
                           "[dim cyan]Custom download directory[/dim cyan]")
        options_table.add_row("  [green]-s, --search[/green] [red]SEARCH[/red]",
                           "[dim cyan]Search query to bypass interactive menu[/dim cyan]")
        options_table.add_row("  [green]-u, --url[/green] [red]URL[/red]",
                           "[dim cyan]Direct URL to download[/dim cyan]")
        options_table.add_row("  [green]-v, --verbose[/green]",
                           "[dim cyan]Show detailed logs during download[/dim cyan]")
        options_table.add_row("  [green]-a, --show-all-chapter-bars[/green]",
                           "[dim cyan]Show all chapter progress bars permanently[/dim cyan]")
        options_table.add_row("  [green]-h, --help[/green]",
                           "[dim cyan]Show this help message and exit[/dim cyan]")

        console.print("[bold yellow]OPTIONS[/bold yellow]:")
        console.print(options_table)

        # Get the captured output
        captured_output = output_buffer.getvalue()
        return captured_output


def validate_url(url: str) -> str:
    """Validate and return a validated url."""
    if not url.startswith("https://tokybook.com/"):
        raise ValueError(f"Invalid URL: {url}. Must start with https://tokybook.com/")
    return url


class CustomHelpAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # Don't call parser.exit() here, let the normal help handling take place
        # But we'll catch the SystemExit if needed
        pass

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="TokySnatcher - Download Audiobooks from TokyBook",
        prog="tokysnatcher",
        formatter_class=RichHelpFormatter,
        add_help=True,  # Enable automatic help, it will use our formatter
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





def main() -> None:
    """Main entry point for TokySnatcher."""
    check_ffmpeg()

    args = parse_arguments()

    # Handle download/search commands (default behavior)
    setup_colored_logging(args.verbose if hasattr(args, "verbose") else False)

    config = DownloadConfig(
        directory=Path(args.directory)
        if hasattr(args, "directory") and args.directory
        else None,
        verbose=args.verbose if hasattr(args, "verbose") else False,
        show_all_chapter_bars=args.show_all_chapter_bars
        if hasattr(args, "show_all_chapter_bars")
        else False,
    )

    try:
        if hasattr(args, "url") and args.url:
            handle_url_action(args.url, config)
        elif hasattr(args, "search") and args.search:
            handle_search_action(args.search, config)
        else:
            handle_interactive_action(config)
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user.")
        sys.exit(0)
    except Exception:
        logger.exception("An unexpected error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()
