"""
Effects-based logging framework.

Provides logging functions, progress bar utilities, handlers, and formatters
that integrate with the `effects` library.
"""


from .__version__ import __version__
from .core import (
    LogLevel,
    log,
    log_debug,
    log_error,
    log_info,
    log_warning,
    progressbar,
    text_writer,
)
from .formatters import format_progressbar, format_text_message
from .types import LogMessage

__all__ = [
    "log",
    "log_debug",
    "log_info",
    "log_warning",
    "log_error",
    "progressbar",
    "LogLevel",
    "LogMessage",
    "format_text_message",
    "format_progressbar",
    "text_writer",
    "__version__",
]
