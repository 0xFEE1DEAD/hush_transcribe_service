"""Contains interfaces for diarization module."""

import io
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SpeakerSegment:
    """Segment where speaker say."""

    time: tuple[int, int]
    key: str


class DiarizationService(Protocol):
    """Interface for diarization strategy."""

    def get_segments_from_file(self, file: io.BufferedReader) -> Iterator[SpeakerSegment]:
        """Return iterator with segments where speaker say in audio file."""
        ...
