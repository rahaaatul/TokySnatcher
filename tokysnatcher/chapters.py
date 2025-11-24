from __future__ import annotations
from dataclasses import dataclass

import logging
import platform
import re
from pathlib import Path
from urllib.parse import urlparse, quote
import requests

from .download import download_all_chapters

# Unified logging is handled by logger.py module


@dataclass
class BookInfo:
    """Represents book metadata."""

    author: str
    title: str
    directory: Path


def parse_book_url(book_url: str) -> str:
    """Extract slug from book URL."""
    o = urlparse(book_url)
    slug = Path(o.path).name
    if not slug:
        print("❌ Could not extract slug from the provided URL.")
        return ""
    return slug


def fetch_post_details(slug: str) -> dict | None:
    """Fetch post details from API."""
    try:
        response = requests.post(
            "https://tokybook.com/api/v1/search/post-details",
            json={"dynamicSlugId": slug},
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching book details from API: {e}")
        return None


def extract_book_metadata(post_data: dict, slug: str) -> tuple[str, str]:
    """Extract author and book title from post data."""
    author = None
    authors_data = post_data.get("authors", [])
    if authors_data and isinstance(authors_data, list) and len(authors_data) > 0:
        author = authors_data[0].get("name")

    book_title = (
        post_data.get("title")
        or post_data.get("bookTitle")
        or post_data.get("album")
        or post_data.get("name")
        or post_data.get("bookName")
        or slug  # fallback to slug if no title found
    )

    logging.info(f"Metadata found - Author: '{author}', Book Title: '{book_title}'")

    # Provide clean debug info
    logging.debug(f"Post data metadata keys: {list(post_data.keys())}")
    for key in [
        "title",
        "bookTitle",
        "album",
        "name",
        "bookName",
        "audioBookId",
        "postDetailToken",
    ]:
        if key in post_data:
            logging.debug(f"post_data['{key}']: {post_data[key]}")
    if "authors" in post_data:
        logging.debug(f"post_data['authors']: {post_data['authors']}")

    # Clean and sanitize folder names
    author = author or "Unknown Author"
    author = re.sub(r'[<>:"/\\|?*]', "", author).strip()
    book_title = re.sub(r'[<>:"/\\|?*]', "", book_title).strip()

    return author, book_title


def get_default_music_directory() -> Path:
    """Get platform-specific default Music directory for audiobooks.

    Returns:
        Path: Default directory for audiobooks
    """
    system = platform.system().lower()

    if system == "windows":
        # Windows: C:\Users\<Username>\Music
        music_dir = Path.home() / "Music"
    elif system == "darwin":
        # macOS: /Users/<Username>/Music
        music_dir = Path.home() / "Music"
    elif system == "linux":
        # Linux: /home/<Username>/Music
        music_dir = Path.home() / "Music"
    else:
        # Fallback for other systems (including Android)
        # Try common locations or fallback to home/Music
        music_dir = Path.home() / "Music"

    return music_dir


def create_download_directory(
    book_url: str, custom_folder: Path | None, author: str, book_title: str
) -> Path | None:
    """Create download directory with Audiobooks/Author/Book structure."""
    logging.debug(f"Custom folder provided: {custom_folder}")

    if custom_folder:
        # Use custom folder as base: custom/Audiobooks/Author/Book
        audiobooks_folder = Path(custom_folder).joinpath("Audiobooks")
        author_folder = audiobooks_folder.joinpath(author)
        download_folder = author_folder.joinpath(book_title)
    else:
        # Use platform-specific Music directory: Music/Audiobooks/Author/Book
        music_dir = get_default_music_directory()
        audiobooks_folder = music_dir.joinpath("Audiobooks")
        author_folder = audiobooks_folder.joinpath(author)
        download_folder = author_folder.joinpath(book_title)

    logging.info(f"Download folder: {download_folder}")

    try:
        download_folder.mkdir(parents=True, exist_ok=True)
        return download_folder
    except OSError as e:
        logging.exception(f"Error creating download folder: {e}")
        return None


def fetch_playlist_data(book_id: str, token: str) -> dict | None:
    """Fetch playlist data from API."""
    try:
        response = requests.post(
            "https://tokybook.com/api/v1/playlist",
            json={"audioBookId": book_id, "postDetailToken": token},
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error calling playlist API: {e}")
        return None


def prepare_chapters(
    playlist_data: dict, book_id: str, token: str
) -> tuple[list[dict], dict]:
    """Prepare chapters list and headers for download."""
    # Debug: Log full playlist_data to see available metadata
    logging.debug(f"Full playlist_data keys: {list(playlist_data.keys())}")
    for key, value in playlist_data.items():
        logging.debug(f"playlist_data[{key}]: {value}")

    tracks = playlist_data.get("tracks", [])
    if not tracks:
        logging.error("No tracks found in playlist API response.")
        return [], {}

    # Extract track sources and titles from playlist data
    chapters = []
    for track in tracks:
        track_title = track.get("trackTitle", "").strip()
        src_value = track.get("src", "").strip()

        if not src_value:
            logging.warning(f"Chapter '{track_title}' has no src, skipping")
            continue

        # URL Construction with proper encoding
        logging.trace(f"Raw src value from API: '{src_value}'")
        if " " in src_value:
            logging.trace(f"API src contains SPACES - needs encoding: '{src_value}'")
        if "%20" in src_value:
            logging.trace(f"API src already encoded: '{src_value}'")

        # Encode the src_value for URLs - the server expects encoded URLs
        encoded_src = quote(src_value)
        logging.trace(f"After encoding: '{encoded_src}'")

        full_url = f"https://tokybook.com/api/v1/public/audio/{encoded_src}"
        logging.trace(f"Final constructed URL: '{full_url}'")

        chapters.append(
            {
                "name": track_title,
                "url": full_url,
            }
        )

    # Prepare headers for downloads
    stream_token = playlist_data.get("streamToken", token)
    headers = {
        "X-Audiobook-Id": book_id,
        "X-Stream-Token": stream_token,
        "Referer": "https://tokybook.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    logging.info(f"stream_token: {stream_token}")
    logging.info(f"using token for headers: {token}")

    return chapters, headers


def validate_and_extract_book_info(slug: str) -> tuple[str, str, dict] | None:
    """Validate book info and extract book_id, token, and post_data.

    Args:
        slug: Book slug extracted from URL

    Returns:
        tuple[str, str, dict]: (book_id, token, post_data) or None if invalid
    """
    # Get post details via API
    post_data = fetch_post_details(slug)
    if not post_data:
        return None

    # Extract book ID and token from response
    book_id = post_data.get("audioBookId")
    token = post_data.get("postDetailToken")

    if not book_id or not token:
        logging.error(
            "Could not find audioBookId or postDetailToken in the API response."
        )
        return None

    logging.info(f"book_id: {book_id}, postDetailToken: {token}")
    return book_id, token, post_data


def get_chapters(
    book_url: str,
    custom_folder: Path | None = None,
    verbose: bool = False,
    show_all_chapter_bars: bool = False,
) -> None:
    """Get Chapters to download.

    Args:
        book_url: Link to the book.
        custom_folder: Custom folder set by user.
        verbose: Enable verbose logging.
        show_all_chapter_bars: Show all chapter progress bars permanently.
    """

    logging.debug(f"Fetching chapters for book: {book_url}")

    # Extract slug from URL
    slug = parse_book_url(book_url)
    if not slug:
        return

    # Validate book and extract tokens with post_data
    book_info = validate_and_extract_book_info(slug)
    if not book_info:
        return

    book_id, token, post_data = book_info

    # Extract author and book title
    author, book_title = extract_book_metadata(post_data, slug)

    # Create nested folder structure: Author/Book Title/
    download_folder = create_download_directory(
        book_url, custom_folder, author, book_title
    )
    if not download_folder:
        return

    # Call playlist API to get track list
    playlist_data = fetch_playlist_data(book_id, token)
    if not playlist_data:
        return

    # Prepare chapters and headers
    chapters, headers = prepare_chapters(playlist_data, book_id, token)
    if not chapters:
        return

    # Start downloading chapters
    download_all_chapters(
        chapters,
        headers,
        download_folder,
        book_title=book_title,
        author=author,
        verbose=verbose,
        show_all_chapter_bars=show_all_chapter_bars,
    )

    print()
