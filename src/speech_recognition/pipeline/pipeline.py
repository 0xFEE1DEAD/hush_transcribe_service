"""Entrypoint."""

from pathlib import Path

from speech_recognition.diarization.interfaces import DiarizationService
from speech_recognition.interval_storage.interfaces import IntervalStorageService
from speech_recognition.media.interfaces import MediaPreparationService
from speech_recognition.output.interfaces import OutputService
from speech_recognition.transcription.interfaces import TranscriptionService

from .interfaces import ProgressObserver


class TranscriptionPipeline:
    """Transcription pipeline with aggregated high level logic."""

    def __init__(  # noqa: PLR0913
        self,
        preparation: MediaPreparationService,
        diarization: DiarizationService,
        transcription: TranscriptionService,
        interval_storage: IntervalStorageService,
        output: OutputService,
        progress_observer: ProgressObserver,
    ) -> None:
        """Dependency injection."""
        self._preparation = preparation
        self._diarization = diarization
        self._transcription = transcription
        self._interval_storage = interval_storage
        self._output = output
        self.progress_observer = progress_observer

    async def run_pipeline(self, filename: Path, n_speakers: int | None) -> None:
        """Run audio computing."""
        await self.progress_observer.update(0)

        async with self._preparation.get_prepared_file(filename) as file:
            await self.progress_observer.update(5)

            async for word in self._transcription.transcribe(file):
                self._interval_storage.store(word.time[0], word.time[1], word.word)

            await file.seek(0)
            await self.progress_observer.update(50)
            async for segment in self._diarization.get_segments_from_file(file, n_speakers):
                interval_data = self._interval_storage.get(segment.time[0], segment.time[1])
                await self._output.output(segment.time[0], segment.time[1], "".join(interval_data), segment.key)

            await self.progress_observer.update(100)
