"""Csv output implementation."""

from pathlib import Path

from .csv_file_output_service import CsvFileOutputService
from .interfaces import OutputService
from .txt_file_output_service import TxtFileOutputService
from .txt_file_simple_output_service import TxtFileSimpleOutputService


class FullOutputPipeline(OutputService):
    """Output for sentences by speaker to csv, txt, simple txt without speakers."""

    def __init__(self, csv_filepath: Path, txt_filepath: Path, simple_txt_filepath: Path) -> None:
        """Init pipeline."""
        self.__csv_file = CsvFileOutputService(csv_filepath)
        self.__txt_file = TxtFileOutputService(txt_filepath)
        self.__simple_txt_file = TxtFileSimpleOutputService(simple_txt_filepath)

    def output(self, time_from: float, time_to: float, sentence: str, speaker_title: str) -> None:
        self.__csv_file.output(time_from, time_to, sentence, speaker_title)
        self.__txt_file.output(time_from, time_to, sentence, speaker_title)
        self.__simple_txt_file.output(time_from, time_to, sentence, speaker_title)
