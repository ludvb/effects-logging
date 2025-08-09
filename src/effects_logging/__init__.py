"""A logging framework built on algebraic effects.

Example:

>>> import effects as fx
>>> import effects_logging as logging
>>> from effects_logging import text_writer
>>>
>>> # Simple logging
>>> with text_writer():
...     logging.log_info("Application started")
...     logging.log_error("Something went wrong")
>>>
>>> # Progress bars
>>> with text_writer():
...     for item in logging.progressbar(range(100)):
...         process(item)  # Your processing logic
>>>
>>> # Composing effects - add prefix to all messages
>>> def add_prefix(effect: logging.LogMessage) -> None:
...     # Modify the message and forward it up the stack
...     modified = logging.LogMessage(
...         message=f"[APP] {effect.message}",
...         level=effect.level
...     )
...     fx.send(modified, interpret_final=False)
>>>
>>> # Stack handlers - prefix runs first, then text_writer handles output
>>> with text_writer(), fx.handler(add_prefix, logging.LogMessage):
...     logging.log_info("Server started")  # Will print: "[APP] Server started"
...     logging.log_error("Connection lost")  # Will print: "[APP] Connection lost"
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
from .formatters import format_duration, format_progressbar, format_text_message
from .types import LogMessage

__all__ = [
    "LogLevel",
    "LogMessage",
    "__version__",
    "format_duration",
    "format_progressbar",
    "format_text_message",
    "log",
    "log_debug",
    "log_error",
    "log_info",
    "log_warning",
    "progressbar",
    "text_writer",
]
