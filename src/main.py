"""Entrypoint."""

from pathlib import Path

from speech_recognition.diarization.interfaces import DiarizationService
from speech_recognition.diarization.resemblyzer_with_silero_vad_diarization_service import (
    ResemblyzerWithSileroVADDiarizationService,
)
from speech_recognition.interval_storage.interfaces import IntervalStorageService
from speech_recognition.interval_storage.intervaltree_storage_service import IntervalTreeStorageService
from speech_recognition.media.ffmpeg.ffmpeg_preparation_service import FfmpegPreparationService
from speech_recognition.media.interfaces import MediaPreparationService
from speech_recognition.output.csv_file_output_service import CsvFileOutputService
from speech_recognition.output.interfaces import OutputService
from speech_recognition.transcription.faster_whisper_service import FasterWhisperTranscriptionService
from speech_recognition.transcription.interfaces import TranscriptionService


class TranscriptionPipeline:
    """Transcription pipeline with aggregated high level logic."""

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
        print("Preparation...")  # noqa: T201
        with self._preparation.get_prepared_file(filename) as file:
            print("Transcription...")  # noqa: T201
            for word in self._transcription.transcribe(file):
                self._interval_storage.store(word.time[0], word.time[1], word.word)

            file.seek(0)
            print("Diarization...")  # noqa: T201
            for segment in self._diarization.get_segments_from_file(file):
                interval_data = self._interval_storage.get(segment.time[0], segment.time[1])
                self._output.output(segment.time[0], segment.time[1], "".join(interval_data), segment.key)


transciption_pipeline = TranscriptionPipeline(
    FfmpegPreparationService(),
    ResemblyzerWithSileroVADDiarizationService(),
    FasterWhisperTranscriptionService(),
    IntervalTreeStorageService(),
    CsvFileOutputService(Path("./test.csv")),
).run_pipeline()
