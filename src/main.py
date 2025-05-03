"""Entrypoint."""

from pathlib import Path

import click

from diarization.implementations import PyannoteDiarizationService
from diarization.interfaces import DiarizationService
from interval_storage.implementations import IntervalTreeStorageService
from interval_storage.interfaces import IntervalStorageService
from media.exceptions import MediaFileCanNotBeReadError
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
            print("Transcription...")
            for word in self._transcription.transcribe(file):
                self._interval_storage.store(word.time[0], word.time[1], word.word)

            file.seek(0)
            print("Diarization...")
            for segment in self._diarization.get_segments_from_file(file):
                interval_data = self._interval_storage.get(segment.time[0], segment.time[1])
                self._output.output(segment.time[0], segment.time[1], "".join(interval_data), segment.key)


def validate_output_path(value: str) -> str:
    """Validate output path for file."""
    path = Path(value).resolve()
    if path.exists():
        msg = f"File already exists: {path}"
        raise click.BadParameter(msg)

    if not str(path).lower().endswith(".csv"):
        msg = "File must have .csv extension"
        raise click.BadParameter(msg)

    return str(path)


@click.command()
@click.argument("path_to_media", type=click.Path(exists=True))
@click.argument("csv_file_path", type=validate_output_path)
def main(path_to_media: str, csv_file_path: str) -> None:
    """Transcribe and diarization some media file (audio or video) to csv file."""
    app = App(
        FfmpegPreparingService(),
        PyannoteDiarizationService(),
        FasterWhisperTranscriptionService(),
        IntervalTreeStorageService(),
        CsvFileOutputService(Path(csv_file_path)),
    )

    try:
        app.run_pipeline(Path(path_to_media))
    except MediaFileCanNotBeReadError as e:
        click.echo(f"File can not be read, may be invalid format file. Error: {e}", err=True)


if __name__ == "__main__":
    main()
