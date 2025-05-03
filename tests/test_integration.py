"""
Integration tests covering main usage scenarios.
"""

import io
import time
from unittest.mock import patch

from effects_logging import log_info, log_warning, progressbar
from effects_logging.core import text_writer


class TestIntegrationScenarios:
    """Test real-world usage scenarios."""

    def test_basic_logging_workflow(self):
        """Test a basic logging workflow like in the README."""
        output = io.StringIO()

        with text_writer(output):
            log_info("Starting process")
            log_warning("Something to watch out for")
            log_info("Process completed")

        result = output.getvalue()
        lines = result.strip().split('\n')

        assert len(lines) == 3
        assert "Starting process" in result
        assert "Something to watch out for" in result
        assert "Process completed" in result
        assert "INFO" in result
        assert "WARNING" in result

    def test_progress_bar_with_logging(self):
        """Test progress bar combined with logging."""
        output = io.StringIO()
        output.isatty = lambda: False  # Simulate non-TTY to simplify testing

        items = [1, 2, 3, 4, 5]

        with text_writer(output):
            log_info(f"Starting processing for {len(items)} items")

            processed = []
            for item in progressbar(items, initial_desc="Processing"):
                processed.append(item)
                # Simulate some work
                time.sleep(0.001)

            log_info(f"Finished processing {len(processed)} items")

        result = output.getvalue()

        assert "Starting processing for 5 items" in result
        assert "Finished processing 5 items" in result
        assert len(processed) == 5

    def test_progress_bar_with_description_callback(self):
        """Test progress bar with dynamic descriptions."""
        output = io.StringIO()
        output.isatty = lambda: False

        files = ["config.txt", "data.csv", "report.pdf"]

        def get_description(filename):
            return f"Processing {filename}"

        with text_writer(output):
            processed_files = []
            for file in progressbar(files, desc_callback=get_description):
                processed_files.append(file)
                time.sleep(0.001)

        assert processed_files == files

    @patch('time.sleep')  # Speed up the test
    def test_nested_progress_bars(self, mock_sleep):
        """Test nested progress bars scenario."""
        output = io.StringIO()
        output.isatty = lambda: False

        outer_items = [1, 2]
        inner_items = [1, 2, 3]

        results = []

        with text_writer(output):
            for outer in progressbar(outer_items, initial_desc="Outer"):
                for inner in progressbar(inner_items, initial_desc="Inner"):
                    results.append((outer, inner))

        # Should have processed all combinations
        expected = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3)]
        assert results == expected

    def test_error_handling_with_progress_bar(self):
        """Test that progress bars handle exceptions gracefully."""
        output = io.StringIO()
        output.isatty = lambda: False

        items = [1, 2, 3, 4, 5]
        processed = []

        with text_writer(output):
            try:
                for item in progressbar(items, initial_desc="Processing"):
                    processed.append(item)
                    if item == 3:
                        raise ValueError("Simulated error")
            except ValueError:
                pass  # Expected error

        # Should have processed items before the error
        assert processed == [1, 2, 3]

        # Progress bar should have been cleaned up (no easy way to test this
        # without mocking, but at least it shouldn't crash)

    def test_no_progress_bar_handler_graceful_fallback(self):
        """Test that progress bar gracefully falls back when no handler is available."""
        # Don't set up any text_writer, so no progress bar handler
        items = [1, 2, 3, 4, 5]

        # This should work without errors, just returning the original iterable
        result = list(progressbar(items, initial_desc="Should fallback"))
        assert result == items

    def test_mixed_tty_and_file_behavior(self):
        """Test behavior difference between TTY and file output."""
        # File output (non-TTY)
        file_output = io.StringIO()
        file_output.isatty = lambda: False

        # TTY output
        tty_output = io.StringIO()
        tty_output.isatty = lambda: True

        items = [1, 2, 3]

        # Test with file output
        with text_writer(file_output):
            log_info("File test")
            list(progressbar(items, initial_desc="File progress"))

        # Test with TTY output
        with patch('time.sleep'):  # Speed up TTY test
            with text_writer(tty_output):
                log_info("TTY test")
                list(progressbar(items, initial_desc="TTY progress"))

        file_result = file_output.getvalue()
        tty_result = tty_output.getvalue()

        # Both should contain the log message
        assert "File test" in file_result
        assert "TTY test" in tty_result

        # TTY might have more complex output due to progress bar rendering
        # But both should complete without errors
