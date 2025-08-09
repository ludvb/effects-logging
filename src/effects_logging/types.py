import dataclasses as dc
import uuid
from enum import IntEnum
from typing import Iterable, Protocol, TypeVar

import effects as fx


class LogLevel(IntEnum):
    DEBUG = 0
    INFO = 10
    WARNING = 50
    ERROR = 100


MessageType = TypeVar("MessageType")
SinkType = TypeVar("SinkType")


@dc.dataclass
class ProgressBar:
    bar_id: uuid.UUID
    value: int = 0
    total: int | None = None
    description: str = ""
    start_time: float = 0.0


@dc.dataclass
class LogMessage[MessageType](fx.Effect[None]):
    message: MessageType
    level: LogLevel


@dc.dataclass
class ClearProgressBars(fx.Effect[None]): ...


@dc.dataclass
class WriteProgressBars(fx.Effect[None]): ...


@dc.dataclass
class OpenProgressBar(fx.Effect[uuid.UUID]):
    bar_id: uuid.UUID | None = None


@dc.dataclass
class CloseProgressBar(fx.Effect[None]):
    bar_id: uuid.UUID


@dc.dataclass
class GetProgressBars(fx.Effect[Iterable[ProgressBar]]):
    bar_ids: Iterable[uuid.UUID] | None = None


@dc.dataclass
class SetProgressBar(fx.Effect[None]):
    bar_id: uuid.UUID
    value: int | None = None
    total: int | None = None
    description: str | None = None
    start_time: float | None = None


class Lock(Protocol):
    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool: ...
    def release(self) -> None: ...
    def locked(self) -> bool: ...
    def __enter__(self) -> bool: ...
    def __exit__(self, type, value, traceback) -> None: ...


@dc.dataclass
class GetProgressBarLock(fx.Effect[Lock]): ...


@dc.dataclass
class FormatLogMessage[MessageType, SinkType](fx.Effect[SinkType]):
    log_message: LogMessage[MessageType]


@dc.dataclass
class FormatProgressBar(fx.Effect[None]):
    progressbar: ProgressBar


@dc.dataclass
class FlushSink(fx.Effect[None]): ...
