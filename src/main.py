"""Entrypoint."""

from pathlib import Path

from diarization.implementations import PyannoteDiarizationService
from diarization.interfaces import DiarizationService
from interval_storage.implementations import IntervalTreeStorageService
from interval_storage.interfaces import IntervalStorageService
from media.implementations import FfmpegPreparingService
from media.interfaces import MediaPreparationService
from transcription.implementations import FasterWhisperTranscriptionService
from transcription.interfaces import TranscriptionService


class App:
    """Application container."""

    def __init__(
        self,
        preparation: MediaPreparationService,
        diarization: DiarizationService,
        transcription: TranscriptionService,
        interval_storage: IntervalStorageService,
    ) -> None:
        """Dependency injection."""
        self._preparation = preparation
        self._diarization = diarization
        self._transcription = transcription
        self._interval_storage = interval_storage

    def run_pipeline(self, filename: Path) -> None:
        """Run audio computing."""
        with self._preparation.get_prepared_filepath(filename) as file:
            for word in self._transcription.transcribe(file):
                self._interval_storage.store(word.time[0], word.time[1], word.word)

            file.seek(0)
            for segment in self._diarization.get_segments_from_file(file):
                interval_data = self._interval_storage.get(segment.time[0], segment.time[1])
                print(segment.key, ": ", "".join(interval_data))


def main() -> None:
    """Start program."""
    app = App(
        FfmpegPreparingService(),
        PyannoteDiarizationService(),
        FasterWhisperTranscriptionService(),
        IntervalTreeStorageService(),
    )
    app.run_pipeline(Path() / "test.wav")


if __name__ == "__main__":
    main()
