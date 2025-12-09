"""Ffmpeg implementation."""

import asyncio
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

import aiofiles
import ffmpeg

from speech_recognition.media.exceptions import MediaFileCanNotBeReadError, MediaFileNotFoundError, MediaUnknownError
from speech_recognition.media.interfaces import MediaPreparationService

from .exceptions import MediaFfmpegError


class FfmpegPreparationService(MediaPreparationService):
    """Implementation preparing strategy. Using ffmpeg for preparing."""

    @asynccontextmanager
    async def get_prepared_file(self, filename: Path):  # noqa: ANN201
        """Return path to prepared audio file."""
        if not filename.exists():
            msg = f"File: ({filename}) not found"
            raise MediaFileNotFoundError(msg)

        try:
            await asyncio.to_thread(ffmpeg.probe, filename)
        except Exception as e:
            raise MediaFileCanNotBeReadError from e

        tempfile_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                tempfile_path = Path(tmpfile.name)

            await asyncio.to_thread(self.__run_ffmpeg_pipeline, filename, tempfile_path)

            async with aiofiles.open(tempfile_path, "rb") as opened_file:
                yield opened_file

        except ffmpeg.exceptions.FFMpegError as e:
            msg = "Ffmpeg runtime error"
            raise MediaFfmpegError(msg) from e
        except Exception as e:
            raise MediaUnknownError from e
        finally:
            if tempfile_path is not None and tempfile_path.exists():
                tempfile_path.unlink()

    def __run_ffmpeg_pipeline(self, filename: Path, tempfile_path: Path) -> None:
        (
            ffmpeg.input(filename)
            .afftdn()
            .loudnorm(I=-16, LRA=5, TP=0)
            .output(filename=tempfile_path)
            .run(
                quiet=True,
                overwrite_output=True,
            )
        )
