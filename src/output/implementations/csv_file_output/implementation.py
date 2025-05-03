"""Csv output implementation."""

import csv
from datetime import timedelta
from pathlib import Path

from output.interfaces import OutputService


class CsvFileOutputService(OutputService):
    """Output for sentences by speaker."""

    def __init__(self, filepath: Path) -> None:
        """Open file."""
        super().__init__()
        file = filepath.open("w", newline="", encoding="utf-8")
        writer = csv.writer(file)

        self._file = file
        self._csv_writer = writer

        writer.writerow(
            ("From (humanized)", "To (humanized)", "From (seconds)", "To (seconds)", "Speaker Title", "Sentence"),
        )

    def __del__(self) -> None:
        """Close file."""
        self._file.close()

    def output(self, time_from: float, time_to: float, sentence: str, speaker_title: str) -> None:
        """Output by speaker."""
        humanized_from = str(timedelta(seconds=time_from))
        humanized_to = str(timedelta(seconds=time_to))
        self._csv_writer.writerow((humanized_from, humanized_to, time_from, time_to, speaker_title, sentence))
