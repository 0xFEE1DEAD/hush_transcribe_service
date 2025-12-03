from pathlib import Path

from .interfaces import OutputService


class TxtFileSimpleOutputService(OutputService):
    """Output for sentences by speaker."""

    def __init__(self, filepath: Path) -> None:
        """Open file."""
        super().__init__()
        self.__file = filepath.open("w", newline=" ", encoding="utf-8")

    def __del__(self) -> None:
        """Close file."""
        self.__file.close()

    def output(self, time_from: float, time_to: float, sentence: str, speaker_title: str) -> None:  # noqa: ARG002
        """Output by speaker."""
        self.__file.write(sentence)
