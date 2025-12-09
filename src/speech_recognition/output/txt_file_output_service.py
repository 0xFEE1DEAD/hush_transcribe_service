"""Async TXT output implementation."""

from datetime import timedelta
from pathlib import Path
from types import TracebackType
from typing import Self

import aiofiles

from .interfaces import OutputService


class TxtFileOutputService(OutputService):
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
        time_from: float,
        time_to: float,
        sentence: str,
        speaker_title: str,
    ) -> None:
        if not self._file:
            raise RuntimeError

        humanized_from: str = str(timedelta(seconds=time_from))
        humanized_to: str = str(timedelta(seconds=time_to))

        await self._file.write(f"{speaker_title}: [{humanized_from} - {humanized_to}]\n")
        await self._file.write(f"\t{sentence}\n")
