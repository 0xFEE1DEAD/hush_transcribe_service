"""Contains interfaces for media module."""

import io
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol


class MediaPreparationService(Protocol):
    """Interface for strategy preparing media for computing."""

    @contextmanager
    def get_prepared_filepath(self, filename: Path) -> Iterator[io.BufferedReader]:
        """Return path to prepared audio file."""
        ...
