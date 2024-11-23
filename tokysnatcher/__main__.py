import argparse
from os import name, system
import questionary
import sys

from .chapters import get_chapters
from .download import get_input
from .search import search_book


def clear_terminal() -> None:
    """Clear the terminal screen."""
    system("cls" if name == "nt" else "clear")  # noqa: S605


def main() -> None:
    """Get argument from CLI and execute the selected action."""
    parser = argparse.ArgumentParser(
        description="TokySnatcher - Download Audiobooks from TokyBook"
    )
    parser.add_argument(
        "-d", "--directory", type=str, default=None, help="Custom download directory"
    )
    args = parser.parse_args()

    choices = ["Search book", "Download from URL", "Exit"]
    selected_action = questionary.select("Choose action:", choices=choices).ask()

    if selected_action is None:
        sys.exit(0)

    actions = [search_book, get_input, sys.exit]
    action = actions[choices.index(selected_action)]
    result = action()

    if result:
        # clear_terminal()
        get_chapters(result, args.directory)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
