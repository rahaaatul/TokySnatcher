import logging
import re
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from pebble import ThreadPool
from tqdm import tqdm


SLASH_REPLACE_STRING = " out of "

# Global flag for immediate shutdown
_shutdown_requested = False


class SharedProgressTracker:
    """Tracker for cumulative progress across all chapter downloads."""

    def __init__(self, total_chapters: int, overall_pbar):
        self.total_chapters = total_chapters
        self.overall_pbar = overall_pbar
        self.chapter_progress = [0.0] * total_chapters
        self.lock = threading.Lock()

    def update_chapter_progress(self, chapter_index: int, progress_fraction: float):
        """Update progress for a specific chapter."""
        # Don't update progress if shutdown was requested
        if _shutdown_requested:
            return

        with self.lock:
            self.chapter_progress[chapter_index] = progress_fraction

            # Calculate overall progress as percentage (0-100)
            total_progress = sum(self.chapter_progress) / self.total_chapters * 100

            # Update the overall progress bar
            self.overall_pbar.n = round(total_progress, 1)
            self.overall_pbar.set_description("Progress")
            self.overall_pbar.refresh()


class FfmpegProgressTracker(threading.Thread):
    """Track ffmpeg progress using a temporary file.
    From https://github.com/kkroening/ffmpeg-python/issues/43#issuecomment-2461007778
    """

    def __init__(self, chapter_index: int, shared_progress: SharedProgressTracker):
        threading.Thread.__init__(self, name=f'ProgressTracker-{chapter_index}')
        self.daemon = True
        self.stop_event = threading.Event()
        self.progress_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt')
        self.progress_file_path = self.progress_file.name
        self.progress_file.close()  # Close so ffmpeg can write to it

        self.chapter_index = chapter_index
        self.duration_seconds = None
        self.shared_progress = shared_progress

    def run(self):
        """Monitor progress file and update progress bar."""
        while not self.stop_event.is_set() and not _shutdown_requested:
            try:
                current_seconds = self._get_latest_progress()
                if current_seconds is not None and self.duration_seconds:
                    progress_fraction = min(current_seconds / self.duration_seconds, 1.0)
                    self.shared_progress.update_chapter_progress(self.chapter_index, progress_fraction)

                    if current_seconds >= self.duration_seconds:
                        # Ensure final 100% update
                        self.shared_progress.update_chapter_progress(self.chapter_index, 1.0)
                        break

            except Exception:
                pass  # Ignore errors in progress tracking

            time.sleep(0.5)  # Update every 500ms

    def _get_latest_progress(self):
        """Parse the latest progress from ffmpeg progress file."""
        try:
            with open(self.progress_file_path, 'r') as f:
                lines = f.readlines()

            # Look for out_time_ms in the latest progress block
            for line in reversed(lines):
                line = line.strip()
                if line.startswith('out_time_ms='):
                    microseconds = int(line.split('=')[1])
                    return microseconds / 1000000.0  # Convert to seconds

        except (FileNotFoundError, ValueError, IndexError):
            pass

        return None

    def set_duration(self, duration_seconds: int):
        """Set the total duration for progress calculation."""
        self.duration_seconds = duration_seconds

    def stop(self):
        """Stop the progress tracker."""
        self.stop_event.set()

        try:
            Path(self.progress_file_path).unlink()
        except FileNotFoundError:
            pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False


def download_hls_chapter(item: dict, download_headers: dict, download_folder: Path, chapter_index: int, shared_progress: SharedProgressTracker) -> tuple[str, bool]:
    """Download and convert a single HLS chapter to MP3 using ffmpeg.

    Args:
        item: Chapter info dict with 'name' and 'url' keys
        download_headers: HTTP headers for authenticated requests
        download_folder: Directory to save the MP3 file
        chapter_index: Zero-based chapter index for progress display
        shared_progress: shared progress tracker

    Returns:
        tuple[str, bool]: (chapter_name, success)
    """
    if _shutdown_requested:
        return item['name'], False

    clean_name = SLASH_REPLACE_STRING.join(item['name'].split('/'))
    mp3_filename = download_folder.joinpath(f"{clean_name}.mp3")

    # Clean up any existing file
    if mp3_filename.exists():
        mp3_filename.unlink()

    try:
        # Build ffmpeg command with authentication headers
        # Use raw \r\n (will be interpreted by ffmpeg)
        header_string = (
            f"X-Audiobook-Id: {download_headers['X-Audiobook-Id']}\r\n"
            f"X-Playback-Token: {download_headers['X-Playback-Token']}\r\n"
            f"Referer: {download_headers.get('Referer', 'https://tokybook.com/')}"
        )

        raw_url = item["url"]

        # Use progress tracker for real-time feedback
        with FfmpegProgressTracker(chapter_index, shared_progress) as progress:
            # Build ffmpeg command with progress reporting
            cmd = [
                'ffmpeg', '-y',  # Overwrite output files
                '-headers', header_string,
                '-i', raw_url,
                '-c:a', 'mp3',  # Convert audio to MP3
                '-progress', progress.progress_file_path,  # Write progress to file
                '-loglevel', 'info',  # Show duration info
                str(mp3_filename)
            ]

            # Start ffmpeg process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Monitor stderr for duration info and shutdown signals
            duration_set = False
            while process.poll() is None:
                # Check for shutdown signal
                if _shutdown_requested:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()

                    if mp3_filename.exists():
                        mp3_filename.unlink()

                    return item['name'], False

                # Read stderr to get duration info
                if not duration_set and process.stderr:
                    try:
                        stderr_line = process.stderr.readline()
                        if stderr_line:
                            # Look for Duration line
                            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})', stderr_line)
                            if duration_match:
                                hours, minutes, seconds = duration_match.groups()
                                duration_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
                                progress.set_duration(duration_seconds)
                                duration_set = True
                    except Exception:
                        pass

                time.sleep(0.1)  # Small delay to prevent busy waiting

            return_code = process.returncode

        # Check results
        if return_code == 0 and mp3_filename.exists():
            file_size = mp3_filename.stat().st_size
            if file_size > 1000:  # At least 1KB
                # Ensure final progress update for successful completion (not after shutdown)
                if not _shutdown_requested:
                    shared_progress.update_chapter_progress(chapter_index, 1.0)

                return item['name'], True
            else:
                logging.error(f"Downloaded file too small for {item['name']}: {file_size} bytes")
                if mp3_filename.exists():
                    mp3_filename.unlink()

                return item['name'], False
        else:
            if not _shutdown_requested:
                logging.error(f"ffmpeg failed for {item['name']} (return code: {return_code})")

            if mp3_filename.exists():
                mp3_filename.unlink()

            return item['name'], False

    except Exception as e:
        # Don't log errors if shutdown was requested (Ctrl+C)
        if not _shutdown_requested:
            logging.error(f"Failed to process {item['name']}: {e}")
        if mp3_filename.exists():
            mp3_filename.unlink()
        return item['name'], False


def download_all_chapters(chapters: list[dict], headers: dict, download_folder: Path) -> None:
    """Download all chapters using Pebble ThreadPool with progress tracking.

    Args:
        chapters: List of chapter dicts with 'name' and 'url' keys
        headers: HTTP headers for authenticated requests
        download_folder: Directory to save MP3 files
    """
    # Overall progress bar showing percentage (0-100) summed across all streams
    global _shutdown_requested
    with tqdm(total=100, desc="Progress", unit="%") as chapter_progress:
        with ThreadPool(max_workers=8) as pool:
            try:
                shared_progress = SharedProgressTracker(len(chapters), chapter_progress)

                def _download_chapter_wrapper(chapter_data):
                    index, chapter = chapter_data
                    return download_hls_chapter(chapter, headers, download_folder, index, shared_progress)

                futures = pool.map(_download_chapter_wrapper, enumerate(chapters))
                for chapter_name, success in futures.result():
                    if success:
                        logging.info(f"Downloaded: {chapter_name}")
                    elif not _shutdown_requested:
                        logging.error(f"Failed: {chapter_name}")
            except KeyboardInterrupt:
                _shutdown_requested = True
                pool.stop()
                raise
