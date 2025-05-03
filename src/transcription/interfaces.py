"""Contains interfaces for transcription module."""

import io
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SpeechWord:
    """Word and timestamp."""

    time: tuple[float, float]
    word: str


class TranscriptionService(Protocol):
    """Service for transcription speech in wav file."""

    def transcribe(self, file: io.BufferedReader) -> Iterator[SpeechWord]:
        """Transcribe speech from wav file."""
        ...
