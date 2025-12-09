"""Contains interfaces for diarization module."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol

from aiofiles.threadpool.binary import AsyncBufferedReader


@dataclass(frozen=True)
class SpeakerSegment:
    """Segment where speaker say."""

    time: tuple[float, float]
    key: str


class DiarizationService(Protocol):
    """Interface for diarization strategy."""

    def get_segments_from_file(
        self,
        file: AsyncBufferedReader,
        n_speakers: int | None = None,
    ) -> AsyncIterator[SpeakerSegment]:
        """Return iterator with segments where speaker say in audio file."""
        ...
