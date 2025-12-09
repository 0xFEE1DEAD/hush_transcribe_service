"""Csv output implementation."""

from datetime import timedelta
from pathlib import Path
from types import TracebackType
from typing import Self

import aiofiles
from aiocsv import AsyncWriter

from .interfaces import OutputService


class CsvFileOutputService(OutputService):
    """Output for sentences by speaker."""

    def __init__(self, filepath: Path) -> None:
        """Open file."""
        super().__init__()
        self._filepath = filepath
        self._file = None
        self._csv_writer = None

    async def __aenter__(self) -> Self:  # noqa: D105
        self._file = await aiofiles.open(self._filepath, "w", newline="", encoding="utf-8")
        self._csv_writer = AsyncWriter(self._file, dialect="unix")

        # Header row
        await self._csv_writer.writerow(
            ("From (humanized)", "To (humanized)", "From (seconds)", "To (seconds)", "Speaker Title", "Sentence"),
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

    async def output(self, time_from: float, time_to: float, sentence: str, speaker_title: str) -> None:
        humanized_from = str(timedelta(seconds=time_from))
        humanized_to = str(timedelta(seconds=time_to))

        if self._csv_writer is None:
            raise RuntimeError

        await self._csv_writer.writerow((humanized_from, humanized_to, time_from, time_to, speaker_title, sentence))
