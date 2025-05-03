"""
Tests for package types and data structures.
"""

import uuid

from effects_logging.types import (
    CloseProgressBar,
    LogLevel,
    LogMessage,
    OpenProgressBar,
    ProgressBar,
    SetProgressBar,
)


class TestLogLevel:
    """Test LogLevel enum."""

    def test_log_level_values(self):
        """Test that log levels have expected values."""
        assert LogLevel.DEBUG.value == 0
        assert LogLevel.INFO.value == 10
        assert LogLevel.WARNING.value == 50
        assert LogLevel.ERROR.value == 100

    def test_log_level_ordering(self):
        """Test that log levels can be compared."""
        assert LogLevel.DEBUG < LogLevel.INFO
        assert LogLevel.INFO < LogLevel.WARNING
        assert LogLevel.WARNING < LogLevel.ERROR


class TestLogMessage:
    """Test LogMessage dataclass."""

    def test_log_message_creation(self):
        """Test creating LogMessage instances."""
        msg = LogMessage(message="test", level=LogLevel.INFO)
        assert msg.message == "test"
        assert msg.level == LogLevel.INFO

    def test_log_message_with_different_types(self):
        """Test LogMessage with different message types."""
        string_msg = LogMessage(message="string", level=LogLevel.INFO)
        int_msg = LogMessage(message=42, level=LogLevel.ERROR)
        list_msg = LogMessage(message=[1, 2, 3], level=LogLevel.DEBUG)

        assert string_msg.message == "string"
        assert int_msg.message == 42
        assert list_msg.message == [1, 2, 3]


class TestProgressBar:
    """Test ProgressBar dataclass."""

    def test_progress_bar_creation(self):
        """Test creating ProgressBar instances."""
        bar_id = uuid.uuid4()
        bar = ProgressBar(bar_id=bar_id)

        assert bar.bar_id == bar_id
        assert bar.value == 0
        assert bar.total is None
        assert bar.description == ""
        assert bar.start_time == 0.0

    def test_progress_bar_with_values(self):
        """Test ProgressBar with custom values."""
        bar_id = uuid.uuid4()
        bar = ProgressBar(
            bar_id=bar_id,
            value=50,
            total=100,
            description="Processing",
            start_time=123.45
        )

        assert bar.bar_id == bar_id
        assert bar.value == 50
        assert bar.total == 100
        assert bar.description == "Processing"
        assert bar.start_time == 123.45


class TestProgressBarEffects:
    """Test progress bar effect types."""

    def test_open_progress_bar_effect(self):
        """Test OpenProgressBar effect."""
        # With explicit bar_id
        bar_id = uuid.uuid4()
        effect = OpenProgressBar(bar_id=bar_id)
        assert effect.bar_id == bar_id

        # Without bar_id (should default to None)
        effect = OpenProgressBar()
        assert effect.bar_id is None

    def test_set_progress_bar_effect(self):
        """Test SetProgressBar effect."""
        bar_id = uuid.uuid4()
        effect = SetProgressBar(
            bar_id=bar_id,
            value=25,
            total=100,
            description="Working",
            start_time=1.0
        )

        assert effect.bar_id == bar_id
        assert effect.value == 25
        assert effect.total == 100
        assert effect.description == "Working"
        assert effect.start_time == 1.0

    def test_set_progress_bar_effect_partial(self):
        """Test SetProgressBar with partial updates."""
        bar_id = uuid.uuid4()
        effect = SetProgressBar(bar_id=bar_id, value=10)

        assert effect.bar_id == bar_id
        assert effect.value == 10
        assert effect.total is None
        assert effect.description is None
        assert effect.start_time is None

    def test_close_progress_bar_effect(self):
        """Test CloseProgressBar effect."""
        bar_id = uuid.uuid4()
        effect = CloseProgressBar(bar_id=bar_id)
        assert effect.bar_id == bar_id
