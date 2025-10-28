import logging
import re
import subprocess
import tempfile
import threading
import time
from pathlib import Path

from pebble import ThreadPool
from rich.progress import Progress

SLASH_REPLACE_STRING = " out of "

# Global flag for immediate shutdown
_shutdown_requested = False


class SharedProgressTracker:
    """Advanced tracker for cumulative and individual chapter progress with Rich."""

    def __init__(self, progress: Progress, chapters: list[dict]):
        self.progress = progress
        self.chapters = chapters
        self.total_chapters = len(chapters)

        # Track individual chapter tasks and their states
        self.chapter_tasks = {}  # chapter_index -> task_id
        self.chapter_states = {}  # chapter_index -> 'queued'|'running'|'complete'
        self.chapter_start_times = {}  # chapter_index -> start_time
        self.completed_count = 0
        self.running_count = 0
        self.lock = threading.Lock()

        # Create overall progress task
        self.overall_task = self.progress.add_task(
            f"[bold blue]Downloading [/bold blue]{self.total_chapters} chapters",
            total=100.0,
        )

        # Initialize individual chapter tasks
        for i, chapter in enumerate(chapters):
            clean_name = SLASH_REPLACE_STRING.join(chapter["name"].split("/"))
            task_id = self.progress.add_task(
                f"[dim]⏳ [/dim]{clean_name}.mp3",
                total=100.0,
                visible=False,  # Hide until started
            )
            self.chapter_tasks[i] = task_id
            self.chapter_states[i] = "queued"

    def start_chapter(self, chapter_index: int):
        """Mark chapter as started and show its progress."""
        with self.lock:
            if chapter_index not in self.chapter_states:
                return

            task_id = self.chapter_tasks[chapter_index]
            self.progress.update(
                task_id,
                description=f"[blue]⏳ [/blue]{self._get_truncated_name(chapter_index)}",
                visible=True,
            )
            self.chapter_states[chapter_index] = "running"
            self.running_count += 1
            self._update_overall()

    def update_individual_progress(self, chapter_index: int, progress_fraction: float):
        """Update progress for a specific chapter."""
        # Don't update progress if shutdown was requested
        if _shutdown_requested:
            return

        with self.lock:
            if chapter_index not in self.chapter_tasks:
                return

            task_id = self.chapter_tasks[chapter_index]
            completed = progress_fraction * 100

            # Update description based on progress
            if completed < 100:
                desc = f"[blue]🔄 [/blue]{self._get_truncated_name(chapter_index)}"
            else:
                desc = f"[green]✓ [/green]{self._get_truncated_name(chapter_index)}"
                self._complete_chapter(chapter_index)

            self.progress.update(task_id, completed=completed, description=desc)
            self._update_overall()

    def complete_chapter(self, chapter_index: int, success: bool):
        """Mark chapter as completed."""
        with self.lock:
            if (
                chapter_index in self.chapter_states
                and self.chapter_states[chapter_index] == "running"
            ):
                task_id = self.chapter_tasks[chapter_index]
                status = "✓" if success else "✗"
                color = "green" if success else "red"
                self.progress.update(
                    task_id,
                    completed=100.0,
                    description=f"[{color}]{status} [/{color}]{self._get_truncated_name(chapter_index)}",
                )
                self.chapter_states[chapter_index] = "complete"
                self.completed_count += 1
                if (
                    chapter_index in self.chapter_states
                    and self.chapter_states[chapter_index] == "running"
                ):
                    self.running_count -= 1
                self._update_overall()

    def _complete_chapter(self, chapter_index: int):
        """Internal method to mark chapter as complete when progress reaches 100%."""
        if self.chapter_states.get(chapter_index) == "running":
            self.chapter_states[chapter_index] = "complete"
            self.completed_count += 1
            self.running_count -= 1

    def _update_overall(self):
        """Update the overall progress display."""
        overall_progress = (self.completed_count / self.total_chapters) * 100

        # Detailed status description
        status_parts = []
        queued_count = sum(
            1 for state in self.chapter_states.values() if state == "queued"
        )

        if queued_count > 0:
            status_parts.append(f"⏳ Ready: {queued_count}")
        if self.running_count > 0:
            status_parts.append(f"🔄 Running: {self.running_count}")
        if self.completed_count > 0:
            status_parts.append(f"✅ Done: {self.completed_count}")

        status_str = " | ".join(status_parts) if status_parts else ""

        self.progress.update(
            self.overall_task,
            completed=overall_progress,
            description=f"[bold blue]Downloading ({self.completed_count}/{self.total_chapters}) chapters[/bold blue] {status_str}",
        )

    def _get_truncated_name(self, chapter_index: int) -> str:
        """Get truncated chapter name for display."""
        full_name = self.chapters[chapter_index]["name"]
        clean_name = SLASH_REPLACE_STRING.join(full_name.split("/"))
        # Truncate very long names to fit better in terminal
        max_length = 40
        if len(clean_name) > max_length:
            clean_name = clean_name[: max_length - 3] + "..."
        return clean_name


class FfmpegProgressTracker(threading.Thread):
    """Track ffmpeg progress using a temporary file.
    From https://github.com/kkroening/ffmpeg-python/issues/43#issuecomment-2461007778
    """

    def __init__(self, chapter_index: int, shared_progress: SharedProgressTracker):
        threading.Thread.__init__(self, name=f"ProgressTracker-{chapter_index}")
        self.daemon = True
        self.stop_event = threading.Event()
        self.progress_file = tempfile.NamedTemporaryFile(
            mode="w+", delete=False, suffix=".txt"
        )
        self.progress_file_path = self.progress_file.name
        self.progress_file.close()  # Close so ffmpeg can write to it

        self.chapter_index = chapter_index
        self.duration_seconds = None
        self.shared_progress = shared_progress

    def run(self):
        """Monitor progress file and update individual chapter progress bar."""
        started = False
        while not self.stop_event.is_set() and not _shutdown_requested:
            try:
                current_seconds = self._get_latest_progress()
                if current_seconds is not None and self.duration_seconds:
                    progress_fraction = min(
                        current_seconds / self.duration_seconds, 1.0
                    )

                    # Mark as started on first progress update
                    if not started:
                        self.shared_progress.start_chapter(self.chapter_index)
                        started = True

                    self.shared_progress.update_individual_progress(
                        self.chapter_index, progress_fraction
                    )

                    if current_seconds >= self.duration_seconds:
                        # Ensure final 100% update
                        self.shared_progress.update_individual_progress(
                            self.chapter_index, 1.0
                        )
                        break

            except Exception:
                pass  # Ignore errors in progress tracking

            time.sleep(0.5)  # Update every 500ms

    def _get_latest_progress(self):
        """Parse the latest progress from ffmpeg progress file."""
        try:
            with open(self.progress_file_path, "r") as f:
                lines = f.readlines()

            # Look for out_time_ms in the latest progress block
            for line in reversed(lines):
                line = line.strip()
                if line.startswith("out_time_ms="):
                    microseconds = int(line.split("=")[1])
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


def download_hls_chapter(
    item: dict,
    download_headers: dict,
    download_folder: Path,
    chapter_index: int,
    shared_progress: SharedProgressTracker,
) -> tuple[str, bool]:
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
        return item["name"], False

    clean_name = SLASH_REPLACE_STRING.join(item["name"].split("/"))
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
                "ffmpeg",
                "-y",  # Overwrite output files
                "-headers",
                header_string,
                "-i",
                raw_url,
                "-c:a",
                "mp3",  # Convert audio to MP3
                "-progress",
                progress.progress_file_path,  # Write progress to file
                "-loglevel",
                "info",  # Show duration info
                str(mp3_filename),
            ]

            # Start ffmpeg process
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
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

                    return item["name"], False

                # Read stderr to get duration info
                if not duration_set and process.stderr:
                    try:
                        stderr_line = process.stderr.readline()
                        if stderr_line:
                            # Look for Duration line
                            duration_match = re.search(
                                r"Duration: (\d{2}):(\d{2}):(\d{2})", stderr_line
                            )
                            if duration_match:
                                hours, minutes, seconds = duration_match.groups()
                                duration_seconds = (
                                    int(hours) * 3600 + int(minutes) * 60 + int(seconds)
                                )
                                progress.set_duration(duration_seconds)
                                duration_set = True
                    except Exception:
                        pass

                time.sleep(0.1)  # Small delay to prevent busy waiting

            return_code = process.returncode

        # Check results
        success = False
        if return_code == 0 and mp3_filename.exists():
            file_size = mp3_filename.stat().st_size
            if file_size > 1000:  # At least 1KB
                success = True
            else:
                logging.error(
                    f"Downloaded file too small for {item['name']}: {file_size} bytes"
                )
                if mp3_filename.exists():
                    mp3_filename.unlink()
        else:
            if not _shutdown_requested:
                logging.error(
                    f"ffmpeg failed for {item['name']} (return code: {return_code})"
                )

            if mp3_filename.exists():
                mp3_filename.unlink()

        # Update progress with final status
        shared_progress.complete_chapter(chapter_index, success)
        return item["name"], success

    except Exception as e:
        # Don't log errors if shutdown was requested (Ctrl+C)
        if not _shutdown_requested:
            logging.error(f"Failed to process {item['name']}: {e}")
        if mp3_filename.exists():
            mp3_filename.unlink()

        # Mark as failed
        shared_progress.complete_chapter(chapter_index, False)
        return item["name"], False


def download_all_chapters(
    chapters: list[dict], headers: dict, download_folder: Path
) -> None:
    """Download all chapters using Pebble ThreadPool with progress tracking.

    Args:
        chapters: List of chapter dicts with 'name' and 'url' keys
        headers: HTTP headers for authenticated requests
        download_folder: Directory to save MP3 files

    """
    # Overall progress bar showing percentage (0-100) summed across all streams
    global _shutdown_requested
    with Progress(refresh_per_second=1) as progress:
        with ThreadPool(max_workers=2) as pool:
            try:
                shared_progress = SharedProgressTracker(progress, chapters)

                def _download_chapter_wrapper(chapter_data):
                    index, chapter = chapter_data
                    return download_hls_chapter(
                        chapter, headers, download_folder, index, shared_progress
                    )

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
