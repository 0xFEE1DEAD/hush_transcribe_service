from datetime import timedelta
from pathlib import Path

from .interfaces import OutputService


class TxtFileOutputService(OutputService):
    """Output for sentences by speaker."""

    def __init__(self, filepath: Path) -> None:
        """Open file."""
        super().__init__()
        self.__file = filepath.open("w", newline="", encoding="utf-8")

    def __del__(self) -> None:
        """Close file."""
        self.__file.close()

    def output(self, time_from: float, time_to: float, sentence: str, speaker_title: str) -> None:
        """Output by speaker."""
        humanized_from = str(timedelta(seconds=time_from))
        humanized_to = str(timedelta(seconds=time_to))
        self.__file.write(f"{speaker_title}: [{humanized_from} - {humanized_to}]\n")
        self.__file.write(f"\t{sentence}")
