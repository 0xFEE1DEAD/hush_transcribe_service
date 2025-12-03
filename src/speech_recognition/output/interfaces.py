"""Interfaces for output module."""

from typing import Protocol


class OutputService(Protocol):
    """Output for sentences by speaker."""

    def output(self, time_from: float, time_to: float, sentence: str, speaker_title: str) -> None:
        """Output by speaker."""
        ...
