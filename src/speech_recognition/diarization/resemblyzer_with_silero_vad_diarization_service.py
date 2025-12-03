"""Implementation of diarization service using Resemblyzer and SileroVAD."""

import io
from collections.abc import Iterator
from operator import itemgetter

import librosa
import numpy as np
import torch
from resemblyzer import VoiceEncoder  # pyright: ignore[reportMissingTypeStubs]
from silero_vad import (  # pyright: ignore[reportMissingTypeStubs]
    get_speech_timestamps,  # pyright: ignore[reportUnknownVariableType]
    load_silero_vad,
)
from sklearn.cluster import AgglomerativeClustering  # pyright: ignore[reportMissingTypeStubs]

from .interfaces import DiarizationService, SpeakerSegment


class ResemblyzerWithSileroVADDiarizationService(DiarizationService):
    """Diarization service."""

    __MIN_SEGMENT_LENGTH = 0.3
    __SAMPLE_RATE = 16000
    __embeddings_model = None
    __vad_model = None

    def __init__(self, n_speakers: int | None = None) -> None:
        """Init service."""
        super().__init__()
        self.n_speakers = n_speakers

    def get_segments_from_file(self, file: io.BufferedReader) -> Iterator[SpeakerSegment]:
        """Return iterator with segments where speaker say in audio file."""
        self.__load_models()

        wav, _ = librosa.load(file, sr=self.__SAMPLE_RATE, mono=True)

        speech_timestamps = get_speech_timestamps(  # pyright: ignore[reportUnknownVariableType]
            torch.from_numpy(wav).float(),  # pyright: ignore[reportUnknownMemberType]
            self.__vad_model,  # pyright: ignore[reportUnknownMemberType]
            return_seconds=True,
        )
        empeddings, valid_segments = self.__get_embeddings_for_valid_segments(
            speech_timestamps,  # pyright: ignore[reportUnknownArgumentType]
            wav,
        )
        return self.__clustering(empeddings, valid_segments)

    def __load_models(self) -> None:
        self.__embeddings_model = VoiceEncoder("cpu")
        self.__vad_model = load_silero_vad(onnx=True)  # pyright: ignore[reportUnknownMemberType]

    def __get_embeddings_for_valid_segments(
        self,
        speech_timestamps: list[dict[str, float]],
        wav: np.ndarray,
    ) -> tuple[np.ndarray, list[dict[str, float]]]:
        embeddings = []
        valid_segments = []

        for start, end in map(itemgetter("start", "end"), speech_timestamps):
            start_sample = int(start * self.__SAMPLE_RATE)
            end_sample = int(end * self.__SAMPLE_RATE)

            segment = wav[start_sample:end_sample]

            need_samples_count = int(self.__SAMPLE_RATE * 0.4)
            if len(segment) < need_samples_count:
                segment = np.pad(segment, (0, need_samples_count - len(segment)))

            try:
                embeddings.append(self.__embeddings_model.embed_utterance(segment))  # pyright: ignore[reportOptionalMemberAccess, reportUnknownMemberType]
                valid_segments.append({"start": start, "end": end})  # pyright: ignore[reportUnknownMemberType]
            except Exception:  # noqa: BLE001, S112
                continue

        return np.array(embeddings), valid_segments  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]

    def __clustering(self, embeddings: np.ndarray, segments: list[dict[str, float]]) -> Iterator[SpeakerSegment]:
        if len(embeddings) > 1:
            clustering = AgglomerativeClustering(
                n_clusters=self.n_speakers,  # pyright: ignore[reportArgumentType]
                distance_threshold=0.90 if self.n_speakers is None else None,
            )
            labels = clustering.fit_predict(embeddings)  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]

            for i, seg in enumerate(segments):
                if seg["end"] - seg["start"] > self.__MIN_SEGMENT_LENGTH:
                    yield SpeakerSegment(
                        time=(seg["start"], seg["end"]),
                        key=f"SPEAKER_{labels[i]}",
                    )
