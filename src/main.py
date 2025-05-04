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


def run_pipeline_once(path_to_media: Path, csv_file_path: Path) -> None:
    """Run pipeline."""
    app = App(
        FfmpegPreparingService(),
        PyannoteDiarizationService(),
        FasterWhisperTranscriptionService(),
        IntervalTreeStorageService(),
        CsvFileOutputService(csv_file_path),
    )

    try:
        app.run_pipeline(path_to_media)
    except MediaFileCanNotBeReadError as e:
        click.echo(f"File can not be read, may be invalid format file. Error: {e}", err=True)


@click.command()
@click.argument("path_to_media", type=click.Path(exists=True))
@click.argument("csv_output_path", type=click.Path())
def main(path_to_media: str, csv_output_path: str) -> None:
    """Transcribe and diarization some media file (audio or video) to csv file."""
    media_path = Path(path_to_media)
    output_path = Path(csv_output_path)

    if media_path.is_file() and (not output_path.exists() and str(output_path).lower().endswith(".csv")):
        run_pipeline_once(media_path.resolve(), output_path.resolve())
    elif media_path.is_dir() and output_path.exists() and output_path.is_dir():
        for media_file in media_path.iterdir():
            output_file_path = output_path / (media_file.stem + ".csv")
            if media_file.is_file() and not output_file_path.exists():
                resolved_input = media_file.resolve()
                resolved_output = output_file_path.resolve()
                click.echo(f"Start work with file: {resolved_input}, output dir: {resolved_output}")
                run_pipeline_once(resolved_input, resolved_output)
    else:
        click.echo(
            (
                "The first and second arguments must either both be files or both be directories. "
                "If they are files, the output must end with .csv."
            ),
        )


if __name__ == "__main__":
    main()
