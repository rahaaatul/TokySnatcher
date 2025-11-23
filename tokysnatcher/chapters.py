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

    # Extract slug from URL
    o = urlparse(book_url)
    slug = Path(o.path).name

    if not slug:
        logging.error("Could not extract slug from the provided URL.")
        return

    # Get post details via API
    try:
        response = requests.post(
            "https://tokybook.com/api/v1/search/post-details",
            json={"dynamicSlugId": slug},
        )
        response.raise_for_status()
        post_data = response.json()
    except Exception as e:
        logging.error(f"Error fetching post details from API: {e}")
        return

    # Extract book ID and token from response
    book_id = post_data.get("audioBookId")
    token = post_data.get("postDetailToken")

    if not book_id or not token:
        logging.error(
            "Could not find audioBookId or postDetailToken in the API response."
        )
        return

    o = urlparse(book_url)
    logging.debug(f"Custom folder provided: {custom_folder}")
    download_folder = (
        Path(custom_folder).joinpath(Path(o.path).name)
        if custom_folder
        else Path.cwd().joinpath(Path(o.path).name)
    )

    logging.info(f"Download folder: {download_folder}")

    try:
        download_folder.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logging.exception(f"Error creating download folder: {e}")
        return

    # Call playlist API to get track list
    try:
        response = requests.post(
            "https://tokybook.com/api/v1/playlist",
            json={"audioBookId": book_id, "postDetailToken": token},
        )
        response.raise_for_status()
        playlist_data = response.json()
    except Exception as e:
        logging.error(f"Error calling playlist API: {e}")
        return

    # Extract track sources and titles from playlist data
    tracks = playlist_data.get("tracks", [])
    if not tracks:
        logging.error("No tracks found in playlist API response.")
        return

    chapters = [
        {
            "name": track.get("trackTitle", "").strip(),
            "url": f"https://tokybook.com/{track.get('src', '').strip()}",
        }
        for track in tracks
    ]

    # Prepare headers for downloads
    stream_token = playlist_data.get("streamToken", token)
    headers = {
        "X-Audiobook-Id": book_id,
        "X-Playback-Token": stream_token,
        "Referer": "https://tokybook.com/",
    }

    # Start downloading chapters
    download_all_chapters(chapters, headers, download_folder)

    print()
