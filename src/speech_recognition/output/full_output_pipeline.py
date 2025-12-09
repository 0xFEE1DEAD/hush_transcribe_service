"""Csv output implementation."""

from pathlib import Path
from types import TracebackType
from typing import Self

from .csv_file_output_service import CsvFileOutputService
from .interfaces import OutputService
from .txt_file_output_service import TxtFileOutputService
from .txt_file_simple_output_service import TxtFileSimpleOutputService


class FullOutputPipeline(OutputService):
    """Pipeline: CSV + TXT (with speaker) + TXT simple."""

    def __init__(self, csv_filepath: Path, txt_filepath: Path, simple_txt_filepath: Path) -> None:  # noqa: D107
        self._csv = CsvFileOutputService(csv_filepath)
        self._txt = TxtFileOutputService(txt_filepath)
        self._simple = TxtFileSimpleOutputService(simple_txt_filepath)

    async def __aenter__(self) -> Self:  # noqa: D105
        await self._csv.__aenter__()
        await self._txt.__aenter__()
        await self._simple.__aenter__()
        return self

    async def __aexit__(  # noqa: D105
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self._csv.__aexit__(exc_type, exc, tb)
        await self._txt.__aexit__(exc_type, exc, tb)
        await self._simple.__aexit__(exc_type, exc, tb)

    async def output(self, time_from: float, time_to: float, sentence: str, speaker_title: str) -> None:
        await self._csv.output(time_from, time_to, sentence, speaker_title)
        await self._txt.output(time_from, time_to, sentence, speaker_title)
        await self._simple.output(time_from, time_to, sentence, speaker_title)
