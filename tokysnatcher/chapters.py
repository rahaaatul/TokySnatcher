from __future__ import annotations

import logging
from pathlib import Path
from re import search
from urllib.parse import urlparse

from gazpacho import Soup, get
from json5 import loads

from .download import download

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

SKIP_CHAPTER = "https://file.tokybook.com/upload/welcome-you-to-tokybook.mp3"
MEDIA_URL = "https://files01.tokybook.com/audio/"
MEDIA_FALLBACK_URL = "https://files02.tokybook.com/audio/"
SLASH_REPLACE_STRING = " out of "


def get_chapters(book_url: str, custom_folder: Path | None = None) -> None:
    """Get Chapters to download.

    Args:
    ----
        book_url (string): Link to the book.
        custom_folder (path): Custom folder set by user.

    """
    logging.debug(f"Fetching chapters for book: {book_url}")  # Log fetching start

    html = get(book_url)

    soup = Soup(html)
    js = soup.find("script")

    for crap in js:
        match = search(r"tracks\s*=\s*(\[[^\]]+\])\s*", crap.text)
        if match:
            string = match.group(1)
            break

    json = loads(string)
    chapters = [{"name": x["name"], "url": x["chapter_link_dropbox"]} for x in json if x["chapter_link_dropbox"] != SKIP_CHAPTER]

    o = urlparse(book_url)
    logging.debug(f"Custom folder provided: {custom_folder}")
    # Use provided download folder if available, otherwise use current directory
    download_folder = Path(custom_folder).joinpath(Path(o.path).name) or Path.cwd().joinpath((o.path).name)

    logging.info(f"Download folder: {download_folder}")

    try:
        # Create the directory if it doesn't exist
        download_folder.mkdir(parents=True, exist_ok=True)

    except OSError as e:
        logging.exception(f"Error creating download folder: {e}")
        return

    try:
        for item in chapters:
            download(
                MEDIA_URL + item["url"],
                download_folder.joinpath(f"{SLASH_REPLACE_STRING.join(item['name'].split('/'))}.mp3"),
            )
            logging.info(f"Downloaded: {item['name']}")

    except RuntimeError:
        logging.exception(f"Error downloading chapter: {item['name']}")
        logging.debug("Switching to fallback source.")

        for item in chapters:
            download(
                MEDIA_FALLBACK_URL + item["url"],
                download_folder.joinpath(f"{SLASH_REPLACE_STRING.join(item['name'].split('/'))}.mp3"),
            )
            logging.info(f"Downloaded: {item['name']}")

    except OSError as e:
        logging.exception(f"Error during download: {e}")
        return

    print()
