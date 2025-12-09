"""Implementation of diarization service using Resemblyzer and SileroVAD."""

import asyncio
import io
import queue
import threading
from collections.abc import AsyncIterator
from operator import itemgetter

import librosa
import numpy as np
import torch
from aiofiles.threadpool.binary import AsyncBufferedReader
from resemblyzer import VoiceEncoder  # pyright: ignore[reportMissingTypeStubs]
from silero_vad import (  # pyright: ignore[reportMissingTypeStubs]
    get_speech_timestamps,  # pyright: ignore[reportUnknownVariableType]
    load_silero_vad,
)
from sklearn.cluster import AgglomerativeClustering  # pyright: ignore[reportMissingTypeStubs]

from .interfaces import DiarizationService, SpeakerSegment


class ResemblyzerWithSileroVADDiarizationService(DiarizationService):
    __MIN_SEGMENT_LENGTH = 0.3
    __SAMPLE_RATE = 16000

    def __init__(self) -> None:
        """Init service."""
        super().__init__()

        self._task_queue: queue.Queue[tuple[asyncio.Future[list[SpeakerSegment]], bytes, int | None] | None] = (
            queue.Queue()
        )
        self._stop_event = threading.Event()
        self._diarization_thread = threading.Thread(target=self._diarization_worker, daemon=True)
        self._diarization_thread.start()

    def _diarization_worker(self) -> None:
        embeddings_model = VoiceEncoder("cpu")
        vad_model = load_silero_vad(onnx=True)  # pyright: ignore[reportUnknownVariableType]

        while not self._stop_event.is_set():
            try:
                task = self._task_queue.get(timeout=1.0)
                if task is None:
                    break

                future, audio_bytes, n_speakers = task
                try:
                    wav, _ = librosa.load(io.BytesIO(audio_bytes), sr=self.__SAMPLE_RATE, mono=True)

                    speech_timestamps = get_speech_timestamps(  # pyright: ignore[reportUnknownVariableType]
                        torch.from_numpy(wav).float(),  # pyright: ignore[reportUnknownMemberType]
                        vad_model,
                        return_seconds=True,
                    )

                    embeddings = []
                    valid_segments = []
                    for start, end in map(itemgetter("start", "end"), speech_timestamps):  # pyright: ignore[reportUnknownArgumentType]
                        start_sample = int(start * self.__SAMPLE_RATE)
                        end_sample = int(end * self.__SAMPLE_RATE)
                        segment = wav[start_sample:end_sample]

                        need_samples_count = int(self.__SAMPLE_RATE * 0.4)
                        if len(segment) < need_samples_count:
                            segment = np.pad(segment, (0, need_samples_count - len(segment)))

                        embeddings.append(embeddings_model.embed_utterance(segment))  # pyright: ignore[reportUnknownMemberType]
                        valid_segments.append({"start": start, "end": end})  # pyright: ignore[reportUnknownMemberType]

                    embeddings = np.array(embeddings)  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]

                    labels = []
                    if len(embeddings) > 1:  # pyright: ignore[reportUnknownArgumentType]
                        clustering = AgglomerativeClustering(
                            n_clusters=n_speakers,  # pyright: ignore[reportArgumentType]
                            distance_threshold=0.90 if n_speakers is None else None,
                        )
                        labels = clustering.fit_predict(embeddings)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType]

                    result = []
                    for i, seg in enumerate(valid_segments):  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
                        if seg["end"] - seg["start"] > self.__MIN_SEGMENT_LENGTH:
                            result.append(  # pyright: ignore[reportUnknownMemberType]
                                SpeakerSegment(
                                    time=(seg["start"], seg["end"]),  # pyright: ignore[reportUnknownArgumentType]
                                    key=f"SPEAKER_{labels[i] if i < len(labels) else 'UNKNOWN'}",  # pyright: ignore[reportUnknownArgumentType]
                                ),
                            )

                    future.set_result(result)  # pyright: ignore[reportUnknownArgumentType]
                except Exception as exc:  # noqa: BLE001
                    future.set_exception(exc)
                finally:
                    self._task_queue.task_done()
            except queue.Empty:
                continue

    async def get_segments_from_file(
        self,
        file: AsyncBufferedReader,
        n_speakers: int | None = None,
    ) -> AsyncIterator[SpeakerSegment]:
        """Return iterator with segments where speaker say in audio file."""
        audio_bytes = await file.read()

        loop = asyncio.get_event_loop()
        future: asyncio.Future[list[SpeakerSegment]] = loop.create_future()

        self._task_queue.put((future, audio_bytes, n_speakers))
        result = await future

        for segment in result:
            yield segment

    def __del__(self) -> None:
        """Gracefully shut down the diarization thread."""
        self._stop_event.set()
        self._task_queue.put(None)
        self._diarization_thread.join(timeout=5.0)
