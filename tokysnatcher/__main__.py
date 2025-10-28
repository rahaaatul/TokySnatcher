import argparse
from os import name, system
import questionary
import shutil
import sys
import logging
import platform

from .chapters import get_chapters
from .search import search_book

# Terminal settings for Unix-like systems
if platform.system() != "Windows":
    import termios
    fd: int = sys.stdin.fileno()
    old_term_settings: list[int] = termios.tcgetattr(fd)
else:
    termios = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def check_ffmpeg() -> None:
    """Check if ffmpeg is available in PATH."""
    if not shutil.which("ffmpeg"):
        print("Error: ffmpeg is required but not found in PATH")
        print("Please install ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        sys.exit(1)


def clear_terminal() -> None:
    """Clear the terminal screen."""
    system("cls" if name == "nt" else "clear")  # noqa: S605


def get_input():
    """Get URL input from user for manual download."""
    url = input("Enter URL: ")

    if not url.startswith("https://tokybook.com/"):
        print("Invalid URL!")
        return get_input()

    return url


def main() -> None:
    """Get argument from CLI and execute the selected action."""
    # Check for ffmpeg first
    check_ffmpeg()

    parser = argparse.ArgumentParser(
        description="TokySnatcher - Download Audiobooks from TokyBook"
    )
    parser.add_argument(
        "-d", "--directory", type=str, default=None, help="Custom download directory"
    )
    parser.add_argument(
        "-s", "--search", type=str, default=None, help="Search query to bypass interactive menu"
    )
    parser.add_argument(
        "-u", "--url", type=str, default=None, help="Direct URL to download, bypassing search"
    )
    args = parser.parse_args()

    try:
        # If URL provided, skip everything and download directly
        if args.url:
            logging.info("Downloading from provided URL.")
            get_chapters(args.url, args.directory)
            return

        # If search query provided, skip interactive menu
        if args.search:
            result = search_book(args.search)
            if result:
                logging.info("Action completed successfully.")
                get_chapters(result, args.directory)
            return

        # Define available choices
        choices = ["Search book", "Download from URL", "Exit"]
        selected_action = questionary.select("Choose action:", choices=choices).ask()

        if selected_action is None:
            logging.info("No action selected. Exiting.")
            sys.exit(0)

        # Map actions to corresponding functions
        actions = [search_book, get_input, sys.exit]
        action = actions[choices.index(selected_action)]
        result = action()

        if result:
            logging.info("Action completed successfully.")
            get_chapters(result, args.directory)

    except KeyboardInterrupt:
        logging.warning("Process interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        if termios:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_term_settings)

if __name__ == "__main__":
    main()
