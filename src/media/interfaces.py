"""Contains interfaces for media module."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol


class MediaPreparation(Protocol):
    """Interface for strategy preparing media for computing."""

    @contextmanager
    def get_stream_from_file(self, filename: Path) -> Iterator[Path]:
        """Return path to prepared audio file."""
        ...
