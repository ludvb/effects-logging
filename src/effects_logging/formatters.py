import os
import shutil
import time
from datetime import datetime as DateTime

from termcolor import colored

from .types import LogLevel, ProgressBar

MIN_PROGRESSBAR_LEN = 5


def format_text_message(text: str, level: LogLevel) -> str:
    match level:
        case LogLevel.DEBUG:
            level_color = "grey"
        case LogLevel.WARNING:
            level_color = "yellow"
        case LogLevel.ERROR:
            level_color = "red"
        case _:
            level_color = None
    level_str = colored(level.name, color=level_color)
    pid_str = colored(f"({os.getpid()})", color="dark_grey")
    timestamp = DateTime.now().isoformat(sep=" ", timespec="milliseconds")
    lines = text.split("\n")
    if len(lines) > 1:
        line1, *lines, lineN = lines
        line1 = f"+ {line1}"
        lines = [f"| {line}" for line in lines]
        lineN = f"+ {lineN}"
        lines = [line1] + lines + [lineN]
    formatted_lines = [
        f"[ {timestamp} ] {level_str} {pid_str} {line}" for line in lines
    ]
    return "\n".join(formatted_lines)


def _format_duration(total_seconds: float, sep="") -> str:
    if total_seconds == float('inf'):
        return "inf"
    days = int(total_seconds // (24 * 3600))
    remaining_seconds = total_seconds % (24 * 3600)
    hours = int(remaining_seconds // 3600)
    remaining_seconds %= 3600
    minutes = int(remaining_seconds // 60)
    seconds_val = remaining_seconds % 60
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if days > 0 or hours > 0:
        parts.append(f"{hours:2}h")
    if days > 0 or hours > 0 or minutes > 0:
        parts.append(f"{minutes:2}m")
    if hours == 0 and days == 0:
        formatted_seconds_str = f"{seconds_val:2.0f}s"
        parts.append(formatted_seconds_str)
    return sep.join(parts)


def format_progressbar(progressbar_state: ProgressBar):
    term_width = shutil.get_terminal_size((80, 20)).columns
    prefix = (
        f"{progressbar_state.description}: "
        if progressbar_state.description
        else ""
    )
    elapsed = time.monotonic() - progressbar_state.start_time

    if elapsed > 0 and progressbar_state.value > 0:
        rate = progressbar_state.value / elapsed
        if rate >= 1:
            rate_str = f", {rate:.2f}it/s"
        else:
            rate_str = f", {1/rate:.2f}s/it"
    else:
        rate_str = ", 0.00it/s"

    if progressbar_state.total is not None and progressbar_state.total > 0:
        total = max(progressbar_state.value, progressbar_state.total)
        percentage = min(100, int(100 * progressbar_state.value / total))
        progress_str = f"{percentage}%|"

        elapsed_str = _format_duration(elapsed)
        eta = (
            (elapsed / progressbar_state.value * (total - progressbar_state.value))
            if progressbar_state.value > 0
            else float("inf")
        )
        eta_str = _format_duration(eta)
        suffix = (
            f"| {progressbar_state.value}/{total} [{elapsed_str}<{eta_str}{rate_str}]"
        )

        progressbar_state_len = (
            term_width - len(prefix) - len(progress_str) - len(suffix)
        )
        progressbar_state_len = max(MIN_PROGRESSBAR_LEN, progressbar_state_len)

        filled_len = int(progressbar_state_len * progressbar_state.value / total)
        progressbar_state_render = (
            "█" * filled_len + "-" * (progressbar_state_len - filled_len)
        )
    else:
        percentage = None
        progress_str = ""

        elapsed_str = _format_duration(elapsed)
        suffix = f" {progressbar_state.value} [{elapsed_str}{rate_str}]"

        progressbar_state_len = (
            term_width - len(prefix) - len(progress_str) - len(suffix)
        )
        progressbar_state_len = max(MIN_PROGRESSBAR_LEN, progressbar_state_len)

        progressbar_state_render = "-" * progressbar_state_len

    line = f"{prefix}{progress_str}{progressbar_state_render}{suffix}"
    return line[:term_width]
