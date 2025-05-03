"""Entrypoint."""

from pathlib import Path

from diarization.implementations import PyannoteDiarizationService
from diarization.interfaces import DiarizationService
from interval_storage.implementations import IntervalTreeStorageService
from interval_storage.interfaces import IntervalStorageService
from media.implementations import FfmpegPreparingService
from media.interfaces import MediaPreparationService
from output.implementations import CsvFileOutputService
from output.interfaces import OutputService
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
        output: OutputService,
    ) -> None:
        """Dependency injection."""
        self._preparation = preparation
        self._diarization = diarization
        self._transcription = transcription
        self._interval_storage = interval_storage
        self._output = output

    def run_pipeline(self, filename: Path) -> None:
        """Run audio computing."""
        print("Preparation...")
        with self._preparation.get_prepared_file(filename) as file:
            print("Transcription")
            for word in self._transcription.transcribe(file):
                self._interval_storage.store(word.time[0], word.time[1], word.word)

            file.seek(0)
            print("Diarization")
            for segment in self._diarization.get_segments_from_file(file):
                interval_data = self._interval_storage.get(segment.time[0], segment.time[1])
                self._output.output(segment.time[0], segment.time[1], "".join(interval_data), segment.key)


def main() -> None:
    """Start program."""
    app = App(
        FfmpegPreparingService(),
        PyannoteDiarizationService(),
        FasterWhisperTranscriptionService(),
        IntervalTreeStorageService(),
        CsvFileOutputService(Path() / "test.csv"),
    )
    app.run_pipeline(Path() / "test.wav")


if __name__ == "__main__":
    main()
