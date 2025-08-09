"""
Functional tests for formatters.
"""

import time
import uuid
from unittest.mock import patch

from effects_logging.formatters import (
    format_duration,
    format_progressbar,
    format_text_message,
)
from effects_logging.types import LogLevel, ProgressBar


class TestTextMessageFormatting:
    """Test text message formatting functionality."""

    def test_format_text_message_basic(self):
        """Test basic text message formatting."""
        result = format_text_message("Hello world", LogLevel.INFO)

        # Should contain timestamp, level, PID, and message
        assert "INFO" in result
        assert "Hello world" in result
        assert "[" in result and "]" in result  # Timestamp brackets
        assert "(" in result and ")" in result  # PID brackets

    def test_format_text_message_different_levels(self):
        """Test formatting with different log levels."""
        message = "Test message"

        debug_result = format_text_message(message, LogLevel.DEBUG)
        info_result = format_text_message(message, LogLevel.INFO)
        warning_result = format_text_message(message, LogLevel.WARNING)
        error_result = format_text_message(message, LogLevel.ERROR)

        assert "DEBUG" in debug_result
        assert "INFO" in info_result
        assert "WARNING" in warning_result
        assert "ERROR" in error_result

        # All should contain the message
        for result in [debug_result, info_result, warning_result, error_result]:
            assert message in result

    def test_format_multiline_message(self):
        """Test formatting of multiline messages."""
        multiline_message = "First line\nSecond line\nThird line"
        result = format_text_message(multiline_message, LogLevel.INFO)

        lines = result.split("\n")
        assert len(lines) == 3

        # Check multiline formatting
        assert lines[0].endswith("+ First line")
        assert lines[1].endswith("| Second line")
        assert lines[2].endswith("+ Third line")


class TestProgressBarFormatting:
    """Test progress bar formatting functionality."""

    def test_format_progressbar_with_total(self):
        """Test progress bar formatting with known total."""
        bar_id = uuid.uuid4()
        progressbar = ProgressBar(
            bar_id=bar_id,
            value=50,
            total=100,
            description="Processing files",
            start_time=time.monotonic() - 10,  # 10 seconds elapsed
        )

        result = format_progressbar(progressbar)

        # Should contain description, percentage, progress indicator, and timing info
        assert "Processing files" in result
        assert "50%" in result or "50/100" in result
        assert "█" in result or "-" in result  # Progress bar characters

    def test_format_progressbar_without_total(self):
        """Test progress bar formatting without known total."""
        bar_id = uuid.uuid4()
        progressbar = ProgressBar(
            bar_id=bar_id,
            value=25,
            total=None,
            description="Scanning",
            start_time=time.monotonic() - 5,
        )

        result = format_progressbar(progressbar)

        # Should contain description, value, and timing info but no percentage
        assert "Scanning" in result
        assert "25" in result
        assert "%" not in result  # No percentage when total is unknown

    def test_format_progressbar_no_description(self):
        """Test progress bar formatting without description."""
        bar_id = uuid.uuid4()
        progressbar = ProgressBar(
            bar_id=bar_id, value=10, total=20, description="", start_time=time.monotonic() - 2
        )

        result = format_progressbar(progressbar)

        # Should still format properly without description
        assert "10/20" in result or "50%" in result
        assert len(result) > 0

    @patch("shutil.get_terminal_size")
    def test_format_progressbar_respects_terminal_width(self, mock_terminal_size):
        """Test that progress bar respects terminal width."""
        mock_terminal_size.return_value.columns = 50

        bar_id = uuid.uuid4()
        progressbar = ProgressBar(
            bar_id=bar_id,
            value=1,
            total=2,
            description="Very long description that might exceed terminal width",
            start_time=time.monotonic(),
        )

        result = format_progressbar(progressbar)

        # Result should not exceed terminal width
        assert len(result) <= 50


class TestDurationFormatting:
    """Test duration formatting helper function."""

    def test_format_duration_basic(self):
        """Test basic duration formatting."""
        assert format_duration(61) == " 1m 1s"  # 1 minute 1 second
        assert format_duration(3661) == " 1h 1m"  # 1h 1m (no secs)
        assert format_duration(30) == "30s"  # 30 seconds
        assert format_duration(0) == " 0s"  # 0 seconds

    def test_format_duration_complex(self):
        """Test complex duration formatting."""
        # 1 day, 2 hours, 3 minutes, 4 seconds
        total_seconds = 24 * 3600 + 2 * 3600 + 3 * 60 + 4
        result = format_duration(total_seconds)
        assert "1d" in result
        assert "2h" in result
        assert "3m" in result
        # Seconds should not be shown when days are present

    def test_format_duration_infinity(self):
        """Test formatting infinite duration."""
        result = format_duration(float("inf"))
        assert result == "inf"
