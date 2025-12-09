"""Interfaces for output module."""

from types import TracebackType
from typing import Protocol, Self


class OutputService(Protocol):
    """Output for sentences by speaker."""

    async def output(self, time_from: float, time_to: float, sentence: str, speaker_title: str) -> None:
        """Output by speaker."""
        ...

    async def __aenter__(self) -> Self:  # noqa: D105
        ...

    async def __aexit__(  # noqa: D105
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
