import argparse
from os import name, system

import questionary

from .chapters import get_chapters
from .download import get_input
from .search import search_book


def cls() -> None:
    """Clear terminal."""
    return system("cls" if name == "nt" else "clear")  # noqa: S605


choices = ["Search book", "Download from URL", "Exit"]


def main() -> None:
    """Get argument from CLI."""
    parser = argparse.ArgumentParser(description="TokySnatcher - Download Audiobooks from TokyBook")
    parser.add_argument("-d", "--directory", type=str, default=None, help="Custom download directory")
    args = parser.parse_args()

    selected_action = questionary.select("Choose action:", choices=choices).ask()

    options = [search_book, get_input, exit]
    res = options[choices.index(selected_action)]()

    if res:
        # cls()
        get_chapters(res, args.directory)


if __name__ == "__main__":
    main()
