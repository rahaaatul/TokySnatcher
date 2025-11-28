from typing import Callable, Optional, Any
import logging
import re
import requests
from pathlib import Path
from rich.console import Console, Group
from rich.live import Live
from rich.text import Text
from . import utils

_shutdown_requested = utils._shutdown_requested


def _create_standardized_filename(chapter_index: int, book_title: str) -> str:
    """Create standardized filename for a chapter using book title."""
    chapter_num = str(chapter_index + 1).zfill(2)

    # Apply title case to book title
    title_case_book_title = book_title.title()

    return f"{chapter_num} - {title_case_book_title}"


def _parse_hls_playlist(playlist_url: str, headers: dict) -> list[str]:
    """Parse HLS playlist and return list of segment URLs."""
    import traceback

    logger = logging.getLogger(__name__)

    logging.debug(f"Request headers: {headers}")

    headers_copy = headers.copy()
    headers_copy["X-Track-Src"] = playlist_url.replace("https://tokybook.com", "")

    logging.debug(f"Modified headers for X-Track-Src: {headers_copy}")

    try:
        response = requests.get(playlist_url, headers=headers_copy, timeout=30)
        logging.debug(f"HTTP {response.status_code} from {playlist_url}")
        logging.debug(f"Response headers: {dict(response.headers)}")

        response.raise_for_status()

        playlist_text = response.text
        logging.debug(
            f"Playlist content ({len(playlist_text)} chars): {playlist_text[:200]}..."
        )

        base_url = playlist_url.rsplit("/", 1)[0] + "/"
        logging.debug(f"Base URL for relative segments: {base_url}")

        segments = []
        for line in playlist_text.splitlines():
            line = line.strip()
            if (
                line
                and not line.startswith("#")
                and (line.startswith("http") or line.startswith("https"))
            ):
                logging.debug(f"Absolute segment URL: {line}")
                segments.append(line)
            elif line and not line.startswith("#") and not line.startswith("http"):
                full_url = base_url + line
                logging.debug(f"Relative segment URL resolved: {line} → {full_url}")
                segments.append(full_url)

        logging.debug(f"Found {len(segments)} total segments")
        if not segments:
            raise ValueError("No segments found in HLS playlist")

        logging.info(f"Successfully parsed {len(segments)} segments for chapter")
        return segments

    except requests.HTTPError as e:
        logger.error(f"HTTP {e.response.status_code} for playlist URL: {playlist_url}")
        logger.error(
            f"Response headers: {dict(e.response.headers) if hasattr(e.response, 'headers') else 'None'}"
        )
        logger.error(
            f"Response body: {e.response.text[:500] if hasattr(e.response, 'text') else 'None'}"
        )
        raise
    except requests.RequestException as e:
        logger.error(f"Network error fetching playlist: {playlist_url}")
        logger.error(f"Error details: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error parsing playlist: {playlist_url}")
        logger.error(f"Error details: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        raise


def download_segments_sequential(
    segments: list[str],
    mp3_filename: Path,
    download_headers: dict,
    item: dict,
    chapter_index: int,
    total_segments: int,
    progress_callback: Optional[Callable[..., Any]] = None,
) -> bool:
    """Download HLS segments sequentially and write to file."""
    downloaded_segments = [0]  # Use list to allow modification in nested function

    with mp3_filename.open("wb") as f:
        for segment_url in segments:
            if _shutdown_requested:
                if mp3_filename.exists():
                    mp3_filename.unlink()
                return False

            # Add X-Track-Src for each segment
            seg_headers = download_headers.copy()
            seg_headers["X-Track-Src"] = segment_url.replace("https://tokybook.com", "")

            # Log each TS segment URL being downloaded
            logging.debug(f"Downloading TS segment: {segment_url}")

            seg_response = requests.get(
                segment_url, headers=seg_headers, stream=True, timeout=30
            )
            seg_response.raise_for_status()

            # Write segment data
            for chunk in seg_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

            # Update progress
            downloaded_segments[0] += 1
            progress_pct = int((downloaded_segments[0] / total_segments) * 100)
            if progress_callback is None:
                logging.info(
                    f"Downloaded segment {downloaded_segments[0]}/{total_segments} for {item['name']} - {progress_pct}% complete"
                )
            else:
                progress_callback(
                    chapter_index,
                    progress_pct,
                    downloaded_segments[0] == total_segments,
                )

    return True


def download_segments_concurrent(
    segments: list[str],
    mp3_filename: Path,
    download_headers: dict,
    item: dict,
    chapter_index: int,
    total_segments: int,
    progress_callback: Optional[Callable[..., Any]] = None,
    max_concurrent_segments: int = 4,
) -> bool:
    """Download HLS segments concurrently and write to file."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading

    downloaded_segments = [0]  # Use list to allow modification in nested function
    segment_data: list[Optional[bytes]] = [
        None
    ] * total_segments  # List to store segment data in correct order
    progress_lock = threading.Lock()

    def download_segment(segment_index, segment_url):
        if _shutdown_requested:
            return None

        # Add X-Track-Src for each segment
        seg_headers = download_headers.copy()
        seg_headers["X-Track-Src"] = segment_url.replace("https://tokybook.com", "")

        # Log each TS segment URL being downloaded
        logging.debug(f"Downloading TS segment: {segment_url}")

        seg_response = requests.get(
            segment_url, headers=seg_headers, stream=True, timeout=30
        )
        seg_response.raise_for_status()

        # Read all segment data with shutdown checks
        data = b""
        for chunk in seg_response.iter_content(chunk_size=8192):
            if _shutdown_requested:
                return None  # Abort this segment
            if chunk:
                data += chunk

        # Store data in correct position and update progress
        segment_data[segment_index] = data

        with progress_lock:
            downloaded_segments[0] += 1
            progress_pct = int((downloaded_segments[0] / total_segments) * 100)
            if progress_callback is None:
                logging.info(
                    f"Downloaded segment {downloaded_segments[0]}/{total_segments} for {item['name']} - {progress_pct}% complete"
                )
            else:
                progress_callback(
                    chapter_index,
                    progress_pct,
                    downloaded_segments[0] == total_segments,
                )

        return data

    # Download segments concurrently
    with ThreadPoolExecutor(max_workers=max_concurrent_segments) as executor:
        futures = [
            executor.submit(download_segment, i, segment_url)
            for i, segment_url in enumerate(segments)
        ]

        # Wait for all downloads to complete
        try:
            for future in as_completed(futures):
                if _shutdown_requested:
                    # Cancel all pending futures
                    for f in futures:
                        f.cancel()
                    if mp3_filename.exists():
                        mp3_filename.unlink()
                    return False
                future.result()  # Raise any exceptions
        except KeyboardInterrupt:
            # Cancel all pending futures on keyboard interrupt
            for f in futures:
                f.cancel()
            if mp3_filename.exists():
                mp3_filename.unlink()
            return False

    # Write segments to file in correct order
    with mp3_filename.open("wb") as f:
        for data in segment_data:
            if data is None:
                # This shouldn't happen if all downloads succeeded
                if mp3_filename.exists():
                    mp3_filename.unlink()
                return False
            f.write(data)

    return True


def download_hls_chapter_core(
    item: dict,
    download_headers: dict,
    download_folder: Path,
    chapter_index: int,
    book_title: str,
    progress_callback: Optional[Callable[..., Any]] = None,
    total_chapters: Optional[int] = None,
    max_concurrent_segments: int = 4,
) -> tuple[str, bool]:
    """Core download logic shared between all download functions.

    Args:
        item: Chapter info dict with 'name' and 'url' keys
        download_headers: HTTP headers for authenticated requests
        download_folder: Directory to save the MP3 file
        chapter_index: Zero-based chapter index
        book_title: Book title for filename generation
        progress_callback: Callable for progress updates (optional)
        total_chapters: Total number of chapters (optional for verbose logging)
        max_concurrent_segments: Maximum concurrent segment downloads per chapter

    Returns:
        tuple[str, bool]: (chapter_name, success)
    """
    if _shutdown_requested:
        return item["name"], False

    clean_name = _create_standardized_filename(chapter_index, book_title)
    mp3_filename = download_folder.joinpath(f"{clean_name}.mp3")

    # Clean up any existing file
    if mp3_filename.exists():
        mp3_filename.unlink()

    try:
        if progress_callback is None:
            # Verbose logging mode
            logging.info(
                f"Starting download: {item['name']} (Chapter {chapter_index + 1}/{total_chapters})"
            )
            logging.debug(f"Fetching HLS playlist: {item['url']}")

        segments = _parse_hls_playlist(item["url"], download_headers)

        if progress_callback is None:
            logging.info(
                f"Downloading {item['name']}: Found {len(segments)} audio segments"
            )

        total_segments = len(segments)

        if max_concurrent_segments == 0:
            # Sequential download (original behavior)
            success = download_segments_sequential(
                segments,
                mp3_filename,
                download_headers,
                item,
                chapter_index,
                total_segments,
                progress_callback,
            )
            if not success:
                return item["name"], False
        else:
            # Concurrent download
            success = download_segments_concurrent(
                segments,
                mp3_filename,
                download_headers,
                item,
                chapter_index,
                total_segments,
                progress_callback,
                max_concurrent_segments,
            )
            if not success:
                return item["name"], False

        # Check result
        file_size = mp3_filename.stat().st_size
        if not _shutdown_requested and progress_callback is None:
            logging.log(
                utils.SUCCESS_LEVEL_NUM,
                f"Successfully downloaded: {item['name']} ({file_size:,} bytes)",
            )
        return item["name"], True

    except requests.HTTPError as e:
        logger = logging.getLogger(__name__)
        logger.error(
            f"HTTP {e.response.status_code} downloading chapter '{item['name']}'"
        )
        logger.error(f"Failed URL: {item['url']}")
        logger.error(
            f"Response headers: {dict(e.response.headers) if e.response else 'None'}"
        )
        logger.error(
            f"Response body: {e.response.text[:500] if e.response and e.response.text else 'None'}"
        )
        if mp3_filename.exists():
            mp3_filename.unlink()
        return item["name"], False
    except requests.RequestException as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Network error downloading chapter '{item['name']}'")
        logger.error(f"Failed URL: {item['url']}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        if mp3_filename.exists():
            mp3_filename.unlink()
        return item["name"], False
    except Exception as e:
        import traceback

        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error downloading chapter '{item['name']}'")
        logger.error(f"Chapter URL: {item['url']}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        if mp3_filename.exists():
            mp3_filename.unlink()
        return item["name"], False


def download_hls_chapter_simple(
    item: dict,
    download_headers: dict,
    download_folder: Path,
    chapter_index: int,
    book_title: str,
    total_chapters: int,
) -> tuple[str, bool]:
    """Download and concatenate a single HLS chapter with simple logging."""
    return download_hls_chapter_core(
        item,
        download_headers,
        download_folder,
        chapter_index,
        book_title,
        total_chapters=total_chapters,
    )


def download_hls_chapter_with_progress(
    item: dict,
    download_headers: dict,
    download_folder: Path,
    chapter_index: int,
    book_title: str,
    progress_updater: Callable[..., Any],
    max_concurrent_segments: int = 4,
) -> tuple[str, bool]:
    """Download and concatenate a single HLS chapter with progress updates."""
    return download_hls_chapter_core(
        item,
        download_headers,
        download_folder,
        chapter_index,
        book_title,
        progress_updater,
        max_concurrent_segments,
    )


def _format_chapter_name(name: str) -> str:
    """Format chapter name for display. Handle already formatted names."""
    name = name.strip()

    # If already starts with "Chapter" (properly formatted), return as-is
    if name.lower().startswith("chapter"):
        return name

    # Try to extract number from the beginning and format properly
    # Match patterns like "01. Title", "1. Title", "01 Title", "01   Title", etc.
    match = re.match(r"^\s*(\d+)\.?\s*(.*)$", name)
    if match:
        num = match.group(1).zfill(2)  # Pad with zero to make 2 digits
        title = match.group(2).strip()
        # Title case the title part
        title = title.title() if title else ""
        return f"Chapter {num}{f' - {title}' if title else ''}"
    else:
        # If no number found, return title case
        return name.title() if name else name


def _download_chapters_verbose(
    chapters: list[dict],
    headers: dict,
    download_folder: Path,
    book_title: str,
) -> None:
    """Download chapters with verbose logging."""
    global _shutdown_requested

    # Suppress library loggers for clean output
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    total_chapters = len(chapters)

    def _download_wrapper(chapter_data):
        index, chapter = chapter_data
        return download_hls_chapter_simple(
            chapter, headers, download_folder, index, book_title, total_chapters
        )

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=2) as pool:
        try:
            futures = [
                pool.submit(_download_wrapper, (index, chapter))
                for index, chapter in enumerate(chapters)
            ]
            for future in futures:
                future.result()

            # Check if download was interrupted (double check before completion)
            if _shutdown_requested:
                logging.warning(
                    "Download cancelled by user - partial download completed"
                )
                return

            successful_downloads = sum(1 for future in futures if future.result()[1])
            failed_downloads = total_chapters - successful_downloads

            # Final check for interruption right before logging success
            if _shutdown_requested:
                logging.warning("Download was interrupted during final steps")
                return

            if failed_downloads > 0:
                logging.info(
                    f"Download completed: {successful_downloads}/{total_chapters} chapters downloaded successfully, {failed_downloads} failed"
                )
            else:
                logging.log(
                    utils.SUCCESS_LEVEL_NUM,
                    f"Download completed successfully: All {total_chapters} chapters downloaded",
                )

        except KeyboardInterrupt:
            _shutdown_requested = True
            logging.warning("Download cancelled by user - partial download completed")
            return  # Exit early, don't show completion message


def download_all_chapters(
    chapters: list[dict],
    headers: dict,
    download_folder: Path,
    book_title: str = "Unknown Book",
    author: str = "Unknown Author",
    verbose: bool = False,
    show_chapter_bars: bool = True,
    show_all_chapter_bars: bool = False,
    hide_completed_bars: bool = False,
    max_concurrent_segments: int = 4,
    interactive: bool = True,
) -> None:
    """Download all chapters with modern progress tracking.

    Args:
        chapters: List of chapter dicts with 'name' and 'url' keys
        headers: HTTP headers for authenticated requests
        download_folder: Directory to save MP3 files
        book_title: Book title for display
        author: Author name for display
        verbose: Enable verbose logging (default False)
        show_chapter_bars: Show individual chapter progress bars alongside overall progress (default True)
        show_all_chapter_bars: Show all chapter bars at once from the start, including pending chapters (default False)
        hide_completed_bars: Hide completed chapter bars when using dynamic display (default False)
        max_concurrent_segments: Maximum concurrent segment downloads per chapter (0 = sequential)
    """
    utils.setup_colored_logging(verbose)

    if verbose:
        _download_chapters_verbose(chapters, headers, download_folder, book_title)
    else:
        _download_chapters_with_progress(
            chapters,
            headers,
            download_folder,
            book_title,
            author,
            download_hls_chapter_with_progress,  # Pass the download function
            max_concurrent_segments,
            interactive,
            show_all_chapter_bars,
            hide_completed_bars,
        )


def _download_chapters_with_progress(
    chapters: list[dict],
    headers: dict,
    download_folder: Path,
    book_title: str,
    author: str,
    download_hls_chapter_func: Callable[..., Any],
    max_concurrent_segments: int = 4,
    interactive: bool = True,
    show_all_chapter_bars: bool = False,
    hide_completed_bars: bool = False,
) -> None:
    """Download chapters with progress bars using custom columns.

    Args:
        chapters: List of chapter dicts with 'name' and 'url' keys
        headers: HTTP headers for authenticated requests
        download_folder: Directory to save MP3 files
        book_title: Book title for display
        author: Author name for display
        download_hls_chapter_func: Function to download individual chapters
        max_concurrent_segments: Maximum concurrent segment downloads per chapter
        interactive: Whether to prompt for input on completion
        show_all_chapter_bars: Show all chapter bars at once from the start
        hide_completed_bars: Hide completed chapter bars after completion
    """
    global _shutdown_requested

    console = Console()
    total_chapters = len(chapters)
    chapter_progresses = [
        0
    ] * total_chapters  # Track progress (0-100%) for each chapter
    downloaded_count = 0  # Count of fully completed chapters
    active_tasks = {}  # chapter_index -> task_id for dynamic bars
    start_times: list[Optional[float]] = [
        None
    ] * total_chapters  # Track when each chapter starts

    # Create single progress display for all items
    progress = utils.create_progress_display()

    # Add overall progress bar
    overall_task_id = progress.add_task(
        "", total=100, emoji="⬇️", name="Overall", start_time=console.get_time()
    )

    # Add all chapters initially only if show_all_chapter_bars is True
    if show_all_chapter_bars:
        for i, chapter in enumerate(chapters):
            chapter_num = str(i + 1).zfill(2)
            task_id = progress.add_task(
                "",
                total=None,  # Indeterminate progress bar for unstarted tasks
                emoji="🔄️",
                name=f"Chapter {chapter_num}",
                start_time=None,  # No time initially
            )
            active_tasks[i] = task_id
    else:
        # When show_all_chapter_bars is False, chapters will be added dynamically
        # only when they start downloading
        pass

    def update_progress(chapter_index, progress_pct, completed=False):
        nonlocal downloaded_count

        # Store old progress to detect completion transition
        old_progress = chapter_progresses[chapter_index]

        # Create chapter bar dynamically when show_all_chapter_bars is False
        if (
            not show_all_chapter_bars
            and chapter_index not in active_tasks
            and progress_pct > 0
        ):
            chapter_num = str(chapter_index + 1).zfill(2)
            task_id = progress.add_task(
                "",
                total=100,
                emoji="🔄️",
                name=f"Chapter {chapter_num}",
                start_time=None,  # Will be set below
            )
            active_tasks[chapter_index] = task_id

        # Update individual chapter progress
        chapter_progresses[chapter_index] = progress_pct

        # Only update task if it exists (it might not exist if show_all_chapter_bars=False and chapter hasn't started)
        if chapter_index in active_tasks:
            # Mark chapter as started when progress > 0
            if progress_pct > 0 and start_times[chapter_index] is None:
                start_times[chapter_index] = console.get_time()
                # Switch from indeterminate to determinate bar when download starts
                progress.update(
                    active_tasks[chapter_index],
                    total=100,  # Switch to determinate progress bar
                    start_time=start_times[chapter_index],
                )

            # Mark chapter as completed when finished
            if progress_pct >= 100 and start_times[chapter_index] is not None:
                # Set completion time to freeze the timer
                completion_time = console.get_time()
                progress.update(
                    active_tasks[chapter_index], completion_time=completion_time
                )
                # Only increment once per chapter when it first reaches 100%
                if old_progress < 100:
                    downloaded_count += 1

            # Update individual chapter bar
            progress.update(active_tasks[chapter_index], completed=progress_pct)

            # Calculate overall progress
            overall_pct = sum(chapter_progresses) / total_chapters
            progress.update(overall_task_id, completed=overall_pct)

            # Determine emoji based on state
            if completed or progress_pct >= 100:
                emoji = "✅"  # Completed
                # Hide completed chapter bar if hide_completed_bars is True
                if hide_completed_bars:
                    progress.remove_task(active_tasks[chapter_index])
                    del active_tasks[chapter_index]
                    return  # Exit early since we removed the task
            elif progress_pct > 0:
                emoji = "⬇️"  # Downloading
            else:
                emoji = "🔄️"  # Pending

            # Update chapter emoji (only if task still exists)
            if chapter_index in active_tasks:
                progress.update(active_tasks[chapter_index], emoji=emoji)

    def create_display():
        header_lines = [
            f"📖 Book: {book_title}",
            f"👨 Author: {author}",
            f"📂 Location: {download_folder}",
            f"📃 Chapters: {total_chapters}",
            f"✅ Downloaded: {downloaded_count}",
            "",
        ]

        display_elements = [Text("\n".join(header_lines), style="bold"), progress]

        return Group(*display_elements)

    with Live(create_display(), console=console) as live:
        def download_with_progress(chapter_data):
            index, chapter = chapter_data
            result = download_hls_chapter_func(
                chapter,
                headers,
                download_folder,
                index,
                book_title,
                lambda ch_idx, pct, comp: update_progress(ch_idx, pct, comp),
                max_concurrent_segments,
            )
            chapter_name, success = result

            if not success and index in active_tasks:
                progress.update(active_tasks[index], emoji="❌")

            live.update(create_display())
            return result

        # Concurrency - up to 2 chapters at a time
        from concurrent.futures import ThreadPoolExecutor

        try:
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [
                    pool.submit(download_with_progress, (index, chapter))
                    for index, chapter in enumerate(chapters)
                ]
                for future in futures:
                    future.result()
        except KeyboardInterrupt:
            _shutdown_requested = True
            logging.warning("Download cancelled by user")

            # Smart emoji assignment based on progress state
            for chapter_index, task_id in active_tasks.items():
                progress_pct = chapter_progresses[chapter_index]
                if progress_pct >= 100:
                    progress.update(task_id, emoji="✅")  # Already complete
                elif progress_pct > 0:
                    progress.update(task_id, emoji="⚠️")  # Was downloading
                else:
                    progress.update(task_id, emoji="❗")  # Never started

            return  # Exit early

    if downloaded_count >= total_chapters:
        console.print("\n[green]✨ Download Complete![/green]")
        if interactive:
            input()
