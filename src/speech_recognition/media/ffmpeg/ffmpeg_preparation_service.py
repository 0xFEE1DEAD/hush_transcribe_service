"""Ffmpeg implementation."""

import io
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import ffmpeg

from speech_recognition.media.exceptions import MediaFileCanNotBeReadError, MediaFileNotFoundError, MediaUnknownError
from speech_recognition.media.interfaces import MediaPreparationService

from .exceptions import MediaFfmpegError


class FfmpegPreparationService(MediaPreparationService):
    """Implementation preparing strategy. Using ffmpeg for preparing."""

    @contextmanager
    def get_prepared_file(self, filename: Path) -> Iterator[io.BufferedReader]:
        """Return path to prepared audio file."""
        if not filename.exists():
            msg = f"File: ({filename}) not found"
            raise MediaFileNotFoundError(msg)

        try:
            ffmpeg.probe(filename)
        except Exception as e:
            raise MediaFileCanNotBeReadError from e

        tempfile_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                tempfile_path = Path(tmpfile.name)

            ffmpeg.input(filename).afftdn().loudnorm(I=-16, LRA=5, TP=0).output(filename=tempfile_path).run(
                quiet=True,
                overwrite_output=True,
            )

            with Path.open(tempfile_path, "rb") as opened_file:
                yield opened_file
        except ffmpeg.exceptions.FFMpegError as e:
            msg = "Ffmpeg runtime error"
            raise MediaFfmpegError(msg) from e
        except Exception as e:
            raise MediaUnknownError from e
        finally:
            if tempfile_path is not None:
                Path.unlink(tempfile_path)
