"""Async TXT output implementation."""

from pathlib import Path
from types import TracebackType
from typing import Self

import aiofiles

from .interfaces import OutputService


class TxtFileSimpleOutputService(OutputService):
    """Async output for sentences by speaker."""

    def __init__(self, filepath: Path) -> None:  # noqa: D107
        super().__init__()
        self._filepath = filepath
        self._file = None

    async def __aenter__(self) -> Self:  # noqa: D105
        self._file = await aiofiles.open(
            self._filepath,
            "w",
            newline="",
            encoding="utf-8",
        )
        return self

    async def __aexit__(  # noqa: D105
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._file:
            await self._file.close()

    async def output(
        self,
        time_from: float,  # noqa: ARG002
        time_to: float,  # noqa: ARG002
        sentence: str,
        speaker_title: str,  # noqa: ARG002
    ) -> None:
        if not self._file:
            raise RuntimeError

        await self._file.write(sentence)
