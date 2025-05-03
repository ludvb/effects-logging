"""
Functional tests for logging functionality.
"""

import io
import warnings

import effects as fx

from effects_logging import log_debug, log_error, log_info, log_warning
from effects_logging.core import text_writer
from effects_logging.types import LogLevel, LogMessage


class TestBasicLogging:
    """Test basic logging functionality."""

    def test_log_functions_send_correct_effects(self):
        """Test that log functions send the correct LogMessage effects."""
        effects_sent = []

        def capture_effect(effect):
            effects_sent.append(effect)

        with fx.handler(capture_effect, LogMessage):
            log_debug("debug message")
            log_info("info message")
            log_warning("warning message")
            log_error("error message")

        assert len(effects_sent) == 4
        assert effects_sent[0] == LogMessage(
            message="debug message", level=LogLevel.DEBUG
        )
        assert effects_sent[1] == LogMessage(
            message="info message", level=LogLevel.INFO
        )
        assert effects_sent[2] == LogMessage(
            message="warning message", level=LogLevel.WARNING
        )
        assert effects_sent[3] == LogMessage(
            message="error message", level=LogLevel.ERROR
        )

    def test_log_with_text_writer_to_file(self):
        """Test logging with text_writer to a non-TTY file."""
        output = io.StringIO()

        with text_writer(output):
            log_info("Hello, world!")
            log_error("An error occurred")

        result = output.getvalue()
        lines = result.strip().split('\n')

        # Should have 2 lines of output
        assert len(lines) == 2

        # Check that messages contain the expected content
        assert "INFO" in lines[0] and "Hello, world!" in lines[0]
        assert "ERROR" in lines[1] and "An error occurred" in lines[1]

        # Check timestamp format is present
        assert "[" in lines[0] and "]" in lines[0]

    def test_log_without_handler_shows_warning(self):
        """Test that logging without a handler shows a warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            log_info("This should warn")

            assert len(w) == 1
            assert "No handler processed log message" in str(w[0].message)
            assert "INFO" in str(w[0].message)

    def test_log_with_various_message_types(self):
        """Test logging with different message types."""
        effects_sent = []

        def capture_effect(effect):
            effects_sent.append(effect)

        with fx.handler(capture_effect, LogMessage):
            log_info("string message")
            log_info(42)
            log_info(["list", "message"])
            log_info({"dict": "message"})

        assert len(effects_sent) == 4
        assert effects_sent[0].message == "string message"
        assert effects_sent[1].message == 42
        assert effects_sent[2].message == ["list", "message"]
        assert effects_sent[3].message == {"dict": "message"}


class TestTextWriterBehavior:
    """Test text_writer behavior for different file types."""

    def test_text_writer_detects_tty_vs_file(self):
        """Test that text_writer behaves differently for TTY vs file."""
        # Mock a TTY file
        tty_file = io.StringIO()
        tty_file.isatty = lambda: True

        # Mock a regular file
        regular_file = io.StringIO()
        regular_file.isatty = lambda: False

        # Both should return handler stacks, but different ones
        tty_handler = text_writer(tty_file)
        file_handler = text_writer(regular_file)

        # Both should be context managers (they return fx.stack objects)
        assert hasattr(tty_handler, '__enter__') and hasattr(tty_handler, '__exit__')
        assert hasattr(file_handler, '__enter__') and hasattr(file_handler, '__exit__')

    def test_multiline_log_message_formatting(self):
        """Test that multiline messages are formatted correctly."""
        output = io.StringIO()

        multiline_message = "First line\nSecond line\nThird line"

        with text_writer(output):
            log_info(multiline_message)

        result = output.getvalue()
        lines = result.strip().split('\n')

        # Should have 3 lines for the multiline message
        assert len(lines) == 3

        # Check multiline formatting markers
        assert lines[0].endswith("+ First line")
        assert lines[1].endswith("| Second line")
        assert lines[2].endswith("+ Third line")
