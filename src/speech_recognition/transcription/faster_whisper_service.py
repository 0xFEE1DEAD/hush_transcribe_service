"""Faster whisper implementation for transcription service."""

import io
from collections.abc import Iterator

from faster_whisper import WhisperModel  # type: ignore  # noqa: PGH003

from .interfaces import SpeechWord, TranscriptionService


class FasterWhisperTranscriptionService(TranscriptionService):
    """Faster whisper service."""

    def transcribe(self, file: io.BufferedReader) -> Iterator[SpeechWord]:
        """Transcribe speech from wav file."""
        model_size = "medium"

        model = WhisperModel(model_size, device="auto")

        segments, _ = model.transcribe(file, word_timestamps=True, vad_filter=True)  # type: ignore  # noqa: PGH003

        for segment in segments:
            if segment.words is not None:
                for word in segment.words:
                    yield SpeechWord((word.start, word.end), word.word)
