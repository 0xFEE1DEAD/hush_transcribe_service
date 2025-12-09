"""Faster whisper implementation for transcription service."""

import asyncio
import io
import queue
import threading
from collections.abc import AsyncIterator

from aiofiles.threadpool.binary import AsyncBufferedReader
from faster_whisper import WhisperModel  # type: ignore  # noqa: PGH003

from .interfaces import SpeechWord, TranscriptionService


class FasterWhisperTranscriptionService(TranscriptionService):
    def __init__(self, model_size: str = "./models/medium", device: str = "auto") -> None:
        """Init transcribe service."""
        self._model_size = model_size
        self._device = device
        self._task_queue: queue.Queue[tuple[asyncio.Future[list[SpeechWord]], bytes] | None] = queue.Queue()
        self._stop_event = threading.Event()

        self._inference_thread = threading.Thread(target=self._inference_worker, daemon=True)
        self._inference_thread.start()

    def _inference_worker(self) -> None:
        """Рабочий поток: загружает модель и обрабатывает задачи."""
        model = WhisperModel(self._model_size, device=self._device)

        while not self._stop_event.is_set():
            try:
                task = self._task_queue.get(timeout=1.0)

                if task is None:
                    break

                future, data = task
                try:
                    segments, _ = model.transcribe(  # pyright: ignore[reportUnknownMemberType]
                        io.BytesIO(data),
                        word_timestamps=True,
                        vad_filter=True,
                    )
                    result = [
                        SpeechWord((word.start, word.end), word.word)
                        for segment in segments
                        if segment.words
                        for word in segment.words
                    ]
                    future.set_result(result)
                except Exception as exc:  # noqa: BLE001
                    future.set_exception(exc)
                finally:
                    self._task_queue.task_done()
            except queue.Empty:
                continue

    async def transcribe(self, file: AsyncBufferedReader) -> AsyncIterator[SpeechWord]:
        """Отправляет задачу в выделенный поток и ждёт результата."""
        loop = asyncio.get_event_loop()
        future: asyncio.Future[list[SpeechWord]] = loop.create_future()

        self._task_queue.put((future, await file.read()))
        result = await future

        for word in result:
            yield word

    def __del__(self) -> None:
        """Gracefully shut down the diarization thread."""
        self._stop_event.set()
        self._task_queue.put(None)
        self._inference_thread.join(timeout=5.0)
