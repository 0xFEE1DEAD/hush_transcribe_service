"""Contains interfaces for media module."""

from contextlib import AbstractAsyncContextManager
from pathlib import Path
from typing import Protocol

from aiofiles.threadpool.binary import AsyncBufferedReader


class MediaPreparationService(Protocol):
    """Interface for strategy preparing media for computing."""

    def get_prepared_file(self, filename: Path) -> AbstractAsyncContextManager[AsyncBufferedReader]:
        """Return path to prepared audio file."""
        ...
