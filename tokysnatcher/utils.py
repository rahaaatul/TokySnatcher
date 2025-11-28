"""Unified utilities for TokySnatcher - logging and progress display."""

import logging
import os
import time
from contextlib import contextmanager
from typing import Generator

from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
)
from rich.text import Text


# Custom logging levels
SUCCESS_LEVEL_NUM = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")


# Formatting constants
LOG_LEVEL_COLORS = {
    "DEBUG": "white",
    "INFO": "blue",
    "WARNING": "yellow",
    "ERROR": "red",
    "SUCCESS": "green",
}

TIME_COLOR = "green"
LOCATION_COLOR = "dim"


class LogCapture(logging.Handler):
    """Print logs immediately with Rich formatting."""

    def __init__(self, console: Console):
        super().__init__()
        self.console = console
        self.setLevel(logging.DEBUG)  # Show DEBUG and all higher levels

    def _format_timestamp(self, created: float) -> str:
        """Format timestamp with milliseconds."""
        timestamp = time.strftime("%H:%M:%S", time.localtime(created))
        milliseconds = f"{int((created % 1) * 1000):03d}"
        return f"{timestamp}.{milliseconds}"

    def _get_level_style(self, level_name: str) -> str:
        """Get styled level name for output - use same color as message."""
        level_name_upper = level_name.upper()
        message_color = LOG_LEVEL_COLORS.get(level_name_upper, "white")
        if level_name_upper == "CRITICAL":
            return f"[white on #ffcccc]{level_name_upper}[/white on #ffcccc]"
        else:
            return f"[{message_color}]{level_name_upper}[/{message_color}]"

    def _build_log_line(
        self, time_part: str, level_part: str, file_part: str, message_part: str
    ) -> str:
        """Build the complete log line."""
        return f"{time_part} {level_part} {file_part} - {message_part}"

    def emit(self, record):
        """Print log records immediately with Rich formatting."""
        try:
            # TIME (green)
            time_part = f"[{TIME_COLOR}]{self._format_timestamp(record.created)}[/]"

            # Level styling
            level_part = self._get_level_style(record.levelname)

            # Location info (dim)
            filename = os.path.basename(getattr(record, "filename", "unknown")).replace(
                ".py", ""
            )
            lineno = getattr(record, "lineno", "unknown")
            location = f"{filename}:{lineno}"
            file_part = f"[{LOCATION_COLOR}]{location}[/]"

            # Message content
            message = record.getMessage()
            message_color = LOG_LEVEL_COLORS.get(record.levelname.upper(), "white")
            if record.levelname.upper() == "CRITICAL":
                message_part = f"[white on #ffcccc]{message}[/white on #ffcccc]"
            elif record.levelname.upper() == "WARNING":
                # Ensure warning color is explicitly set to yellow
                message_part = f"[{message_color}]{message}[/{message_color}]"
            else:
                message_part = f"[{message_color}]{message}[/]"

            # Combine and print
            log_line = self._build_log_line(
                time_part, level_part, file_part, message_part
            )
            self.console.print(log_line)

        except Exception as e:
            # Fallback for formatting errors
            fallback_msg = f"[ERROR FORMATTING LOG: {e}] {record.getMessage()}"
            self.console.print(fallback_msg)


# Progress display utilities
def format_elapsed_time(seconds: float) -> str:
    """Format elapsed time as HH:MM:SS or MM:SS."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


class CustomTimeColumn(TextColumn):
    """Custom time column that shows elapsed time only for started chapters."""

    def __init__(self):
        super().__init__("{task.fields[elapsed_time]}")

    def render(self, task):
        """Render the time column."""
        start_time = task.fields.get("start_time")
        completion_time = task.fields.get("completion_time")

        if start_time is None:
            return Text("")  # Empty for pending chapters

        # Use console.get_time() for consistency with Rich's timing
        console = (
            task._progress.console
            if hasattr(task, "_progress") and hasattr(task._progress, "console")
            else Console()
        )

        # If completed, use completion time, otherwise use current time
        if completion_time is not None:
            elapsed = completion_time - start_time
        else:
            current_time = console.get_time()
            elapsed = current_time - start_time

        formatted_time = format_elapsed_time(elapsed)
        return Text(formatted_time, style="cyan")


class CustomEmojiColumn(TextColumn):
    """Custom emoji column for chapter status."""

    def __init__(self):
        super().__init__("{task.fields[emoji]}")

    def render(self, task):
        """Render the emoji column."""
        emoji = task.fields.get("emoji", "?")
        return Text(emoji)


class CustomNameColumn(TextColumn):
    """Custom name column for chapter names."""

    def __init__(self):
        super().__init__("{task.fields[name]}")

    def render(self, task):
        """Render the name column."""
        name = task.fields.get("name", "")
        return Text(name)


def create_progress_display() -> Progress:
    """Create the progress display with custom columns."""
    return Progress(
        CustomEmojiColumn(),
        CustomNameColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        CustomTimeColumn(),
        console=Console(),
    )


# Global flag for immediate shutdown - TODO: move to a better location
_shutdown_requested = False


@contextmanager
def download_context() -> Generator[dict, None, None]:
    """Context manager for download operations that manages global state."""
    global _shutdown_requested

    # Initialize clean state for this context
    _shutdown_requested = False

    context_state = {"shutdown_requested": False}

    try:
        yield context_state
    except KeyboardInterrupt:
        _shutdown_requested = True
        context_state["shutdown_requested"] = True
        raise
    finally:
        # Restore or propagate shutdown state
        if context_state["shutdown_requested"]:
            _shutdown_requested = True


def setup_colored_logging(verbose_logging: bool = False) -> None:
    """Set up unified Rich colored logging for the entire application.

    Args:
        verbose_logging: Whether to enable Rich LogCapture formatting
    """
    # Always clear existing handlers first
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    if verbose_logging:
        console = Console()
        log_capture = LogCapture(console)

        # Configure logging to show ALL messages with ZERO suppression
        root_logger.addHandler(log_capture)
        root_logger.setLevel(logging.DEBUG)  # Show everything including DEBUG

        # NO log suppression in verbose mode - show ALL logs for debugging
        logging.info(
            "TokySnatcher VERBOSE logging enabled - ALL logs visible (no suppression)"
        )
    else:
        # For non-verbose mode, suppress all logging output by adding a NullHandler
        # This ensures only progress bars are shown without any informational output
        null_handler = logging.NullHandler()
        root_logger.addHandler(null_handler)
        root_logger.setLevel(
            logging.WARNING
        )  # Still suppress INFO/DEBUG even if we had to add a handler
