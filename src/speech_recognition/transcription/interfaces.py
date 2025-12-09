"""Contains interfaces for transcription module."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol

from aiofiles.threadpool.binary import AsyncBufferedReader


@dataclass(frozen=True)
class SpeechWord:
    """Word and timestamp."""

    time: tuple[float, float]
    word: str


class TranscriptionService(Protocol):
    """Service for transcription speech in wav file."""

    def transcribe(self, file: AsyncBufferedReader) -> AsyncIterator[SpeechWord]:
        """Transcribe speech from wav file."""
        ...
