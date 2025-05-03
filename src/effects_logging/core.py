"""
Core components for the effects-based logging framework.

Defines log levels, log message effects, progress bar effects,
and functions for sending these effects.
"""

import contextvars
import dataclasses as dc
import re
import threading
import time
import uuid
import warnings
from typing import Any, Callable, Iterable, Optional, TextIO, TypeVar

import effects as fx

from .formatters import format_progressbar, format_text_message
from .types import (
    ClearProgressBars,
    CloseProgressBar,
    FlushSink,
    FormatLogMessage,
    FormatProgressBar,
    GetProgressBarLock,
    Lock,
    LogLevel,
    LogMessage,
    OpenProgressBar,
    ProgressBar,
    SetProgressBar,
    WriteProgressBars,
)


def log(level: LogLevel, message: Any) -> None:
    """Sends a LogMessage effect with the specified level and message."""
    progressbar_lock = fx.safe_send(GetProgressBarLock())
    if progressbar_lock is not None:
        progressbar_lock.acquire(timeout=1.0)
    try:
        fx.safe_send(ClearProgressBars())
        try:
            fx.send(LogMessage(message=message, level=level))
        except fx.NoHandlerError:
            warnings.warn(
                f"No handler processed log message (level={level.name}): {message!r}",
                stacklevel=2,
            )
        fx.safe_send(WriteProgressBars())
        fx.safe_send(FlushSink())
    finally:
        if progressbar_lock is not None and progressbar_lock.locked():
            progressbar_lock.release()


def log_debug(message: Any):
    """Logs a message with DEBUG level."""
    log(LogLevel.DEBUG, message)


def log_info(message: Any):
    """Logs a message with INFO level."""
    log(LogLevel.INFO, message)


def log_warning(message: Any):
    """Logs a message with WARNING level."""
    log(LogLevel.WARNING, message)


def log_error(message: Any):
    """Logs a message with ERROR level."""
    log(LogLevel.ERROR, message)


T = TypeVar("T")


def progressbar(
    iterable: Iterable[T],
    total: Optional[int] = None,
    desc_callback: Optional[Callable[[T], str]] = None,
    initial_desc: str | None = None,
) -> Iterable[T]:
    """
    Wraps an iterable with a progress bar display.

    Args:
        iterable: The iterable to wrap
        total: Total number of items (if known)
        desc_callback: Function to generate description from current item
        initial_desc: Initial description text
    """
    if total is None:
        try:
            total = len(iterable)  # type: ignore[arg-type]
        except TypeError:
            total = None

    try:
        bar_id = fx.send(OpenProgressBar())
    except fx.NoHandlerError:
        yield from iterable
        return
    try:
        k = 0
        for item in iterable:
            description = desc_callback(item) if desc_callback else initial_desc
            set_pbar = SetProgressBar(
                bar_id=bar_id,
                value=k,
                total=total,
                description=description,
            )
            fx.safe_send(set_pbar)
            yield item
            k += 1
            fx.safe_send(dc.replace(set_pbar, value=k))
    finally:
        fx.safe_send(CloseProgressBar(bar_id=bar_id))


def _text_writer_log_message_handler(
    file: TextIO, trim_escape_sequences: bool | None = None
):
    if trim_escape_sequences is None:
        trim_escape_sequences = not file.isatty()
    ansi_escape_pattern = re.compile(r'\x1b\[[0-9;]*m')

    def _handler_fn(effect: LogMessage):
        formatted_message = fx.send(FormatLogMessage(effect))
        if trim_escape_sequences:
            formatted_message = ansi_escape_pattern.sub('', formatted_message)
        file.write(f"{formatted_message}\n")
        fx.safe_send(effect, interpret_final=False)

    return fx.handler(_handler_fn, LogMessage)


def _text_writer_flush_sink_handler(file: TextIO):
    def _handler_fn(effect: FlushSink):
        file.flush()
        fx.safe_send(effect, interpret_final=False)

    return fx.handler(_handler_fn, FlushSink)


def _text_writer_open_progressbar(
    progressbars: dict,
    progress_updater_start: Callable[[], None] | None = None,
):
    def _handler_fn(effect: OpenProgressBar):
        with fx.send(GetProgressBarLock()):
            fx.send(ClearProgressBars())

            bar_id = effect.bar_id
            if bar_id is None:
                bar_id = uuid.uuid4()
            progressbars[bar_id] = ProgressBar(
                bar_id=bar_id, start_time=time.monotonic()
            )

            fx.send(WriteProgressBars())
            fx.send(FlushSink())

        fx.safe_send(dc.replace(effect, bar_id=bar_id), interpret_final=False)

        if progress_updater_start:
            progress_updater_start()

        return bar_id

    return fx.handler(_handler_fn, OpenProgressBar)


def _text_writer_close_progressbar(
    progressbars: dict,
    progress_updater_stop: Callable[[], None] | None = None,
):
    def _handler_fn(effect: CloseProgressBar):
        with fx.send(GetProgressBarLock()):
            fx.send(ClearProgressBars())

            bar_id = effect.bar_id
            if bar_id in progressbars:
                del progressbars[bar_id]
            fx.safe_send(effect, interpret_final=False)

            fx.send(WriteProgressBars())
            fx.send(FlushSink())

        if progress_updater_stop:
            progress_updater_stop()

    return fx.handler(_handler_fn, CloseProgressBar)


def _text_writer_set_progressbar(progressbars: dict):
    def _handler_fn(effect: SetProgressBar):
        progressbars[effect.bar_id] = dc.replace(
            progressbars[effect.bar_id],
            value=effect.value or progressbars[effect.bar_id].value,
            total=effect.total or progressbars[effect.bar_id].total,
            description=effect.description or progressbars[effect.bar_id].description,
            start_time=effect.start_time or progressbars[effect.bar_id].start_time,
        )
        fx.safe_send(effect, interpret_final=False)

    return fx.handler(_handler_fn, SetProgressBar)


def _text_writer_clear_progressbars(file: TextIO, progressbars: dict):
    def _handler_fn(effect: ClearProgressBars):
        file.write("\r")
        if len(progressbars) > 1:
            file.write(f"\033[{len(progressbars) - 1}A")
        file.write("\033[J")
        fx.safe_send(effect, interpret_final=False)

    return fx.handler(_handler_fn, ClearProgressBars)


def _text_writer_write_progressbars(file: TextIO, progressbars: dict):
    def _handler_fn(effect: WriteProgressBars):
        progressbar_strings = []
        for state in progressbars.values():
            progressbar_strings.append(fx.send(FormatProgressBar(state)))
        file.write("\r")
        file.write("\n".join(progressbar_strings))
        file.write("\033[K")
        fx.safe_send(effect, interpret_final=False)

    return fx.handler(_handler_fn, WriteProgressBars)


def _text_writer_get_progressbar_lock(lock: Lock):
    def _handler_fn(effect: GetProgressBarLock):
        if lock_upstream := fx.safe_send(effect, interpret_final=False):
            return lock_upstream
        return lock

    return fx.handler(_handler_fn, GetProgressBarLock)


def _text_writer_format_log_message_handler():
    def _handler_fn(effect: FormatLogMessage):
        return format_text_message(
            effect.log_message.message,
            effect.log_message.level,
        )

    return fx.handler(_handler_fn, FormatLogMessage)


def _text_writer_format_progressbar_handler():
    def _handler_fn(effect: FormatProgressBar):
        return format_progressbar(effect.progressbar)

    return fx.handler(_handler_fn, FormatProgressBar)


def _text_writer_file(file: TextIO):
    return fx.stack(
        _text_writer_log_message_handler(file),
        _text_writer_flush_sink_handler(file),
        _text_writer_format_log_message_handler(),
    )


def _progressbar_background(file: TextIO, progressbar_update_interval: float = 0.1):
    progressbar_dict: dict[uuid.UUID, ProgressBar] = {}
    progressbar_lock = threading.Lock()

    updater_stop_event = threading.Event()
    updater_thread: threading.Thread | None = None

    def _display_updater():
        while not updater_stop_event.wait(progressbar_update_interval):
            with fx.send(GetProgressBarLock()):
                fx.safe_send(ClearProgressBars())
                fx.safe_send(WriteProgressBars())
                fx.safe_send(FlushSink())

    def _stop_progress_updater():
        nonlocal updater_thread
        if progressbar_dict:
            return
        if updater_thread is not None:
            updater_stop_event.set()
            updater_thread.join(timeout=1.0)
        updater_stop_event.clear()
        updater_thread = None

    def _start_progress_updater():
        nonlocal updater_thread
        if updater_thread:
            return
        ctx = contextvars.copy_context()
        updater_thread = threading.Thread(
            target=lambda: ctx.run(_display_updater), daemon=True
        )
        updater_thread.start()

    return fx.stack(
        _text_writer_open_progressbar(
            progressbar_dict, progress_updater_start=_start_progress_updater
        ),
        _text_writer_close_progressbar(
            progressbar_dict, progress_updater_stop=_stop_progress_updater
        ),
        _text_writer_get_progressbar_lock(progressbar_lock),
        _text_writer_set_progressbar(progressbar_dict),
        _text_writer_write_progressbars(file, progressbar_dict),
        _text_writer_clear_progressbars(file, progressbar_dict),
    )


def _progressbar_foreground(file: TextIO, progressbar_update_interval: float = 0.1):
    progressbar_dict: dict[uuid.UUID, ProgressBar] = {}

    class _dummy_lock:
        def acquire(self, blocking: bool = True, timeout: float = -1):
            return True
        def release(self):
            pass
        def locked(self) -> bool:
            return False
        def __enter__(self):
            return True
        def __exit__(self, type, value, traceback):
            pass
    progressbar_lock = _dummy_lock()

    last_update_time = 0.

    def _update_progressbars(effect: fx.Effect):
        nonlocal last_update_time
        fx.safe_send(effect, interpret_final=False)
        current_time = time.monotonic()
        if current_time - last_update_time > progressbar_update_interval:
            with fx.send(GetProgressBarLock()):
                fx.safe_send(ClearProgressBars())
                fx.safe_send(WriteProgressBars())
                fx.safe_send(FlushSink())
            last_update_time = current_time

    return fx.stack(
        _text_writer_open_progressbar(progressbar_dict),
        _text_writer_close_progressbar(progressbar_dict),
        _text_writer_get_progressbar_lock(progressbar_lock),
        _text_writer_set_progressbar(progressbar_dict),
        _text_writer_write_progressbars(file, progressbar_dict),
        _text_writer_clear_progressbars(file, progressbar_dict),
        fx.handler(_update_progressbars, SetProgressBar),
    )


def _text_writer_tty(
    file: TextIO,
    progressbar_update_interval: float = 0.1,
    progressbar_async: bool = True,
):
    if progressbar_async:
        progressbar_updater = _progressbar_background(
            file, progressbar_update_interval
        )
    else:
        progressbar_updater = _progressbar_foreground(
            file, progressbar_update_interval
        )
    return fx.stack(
        _text_writer_file(file),
        _text_writer_format_progressbar_handler(),
        progressbar_updater,
    )


def text_writer(
    file: TextIO,
    progressbar_update_interval: float = 0.1,
    progressbar_async: bool = False,
):
    if file.isatty():
        return _text_writer_tty(file, progressbar_update_interval, progressbar_async)
    else:
        return _text_writer_file(file)
