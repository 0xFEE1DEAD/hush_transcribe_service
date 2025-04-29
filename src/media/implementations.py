"""Implementations for interfaces media module."""

import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import ffmpeg

from .interfaces import MediaPreparation


class FfmpegPreparing(MediaPreparation):
    """Implementation preparing strategy. Using ffmpeg for preparing."""

    @contextmanager
    def get_stream_from_file(self, filename: Path) -> Iterator[Path]:
        """Return path to prepared audio file."""
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmpfile:
            ffmpeg.input(filename).afftdn().loudnorm(I=-16, LRA=5, TP=0).output(filename=tmpfile.name)
            yield Path(tmpfile.name)
