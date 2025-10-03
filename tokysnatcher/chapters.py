from __future__ import annotations

import logging
import re
from pathlib import Path
from urllib.parse import urlparse
import requests

from .download import download_all_chapters

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_chapters(book_url: str, custom_folder: Path | None = None) -> None:
    """Get Chapters to download.

    Args:
    ----
        book_url (string): Link to the book.
        custom_folder (path): Custom folder set by user.
    """
    logging.debug(f"Fetching chapters for book: {book_url}")  # Log fetching start

    # Get book page and extract credentials
    try:
        response = requests.get(book_url)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        logging.error(f"Error fetching book page: {e}")
        return

    # Extract book ID and token from HTML
    book_id_match = re.search(r'data-book-id="([^"]*)"', html)
    token_match = re.search(r'data-token="([^"]*)"', html)

    if not book_id_match or not token_match:
        logging.error("Could not find book ID or token in the provided URL.")
        return

    book_id = book_id_match.group(1)
    token = token_match.group(1)

    headers = {
        'X-Audiobook-Id': book_id,
        'X-Playback-Token': token,
    }

    # Call player API to get track list
    try:
        response = requests.get('https://tokybook.com/post/player', headers=headers)
        if response.status_code != 200:
            logging.error(f"Player API returned status {response.status_code}")
            return
    except Exception as e:
        logging.error(f"Error calling player API: {e}")
        return

    # Extract track sources and titles
    track_srcs = re.findall(r'data-track-src="([^"]*)"', response.text)
    track_titles = re.findall(r'data-track-title="([^"]*)"', response.text)

    if not track_srcs or not track_titles:
        logging.error("No tracks found in player API response.")
        return

    chapters = [
        {"name": title.strip(), "url": f"https://tokybook.com{src}"}
        for src, title in zip(track_srcs, track_titles)
    ]

    o = urlparse(book_url)
    logging.debug(f"Custom folder provided: {custom_folder}")
    download_folder = Path(custom_folder).joinpath(Path(o.path).name) if custom_folder else Path.cwd().joinpath(Path(o.path).name)

    logging.info(f"Download folder: {download_folder}")

    try:
        download_folder.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logging.exception(f"Error creating download folder: {e}")
        return

    # Start downloading chapters
    download_all_chapters(chapters, headers, download_folder)

    print()
