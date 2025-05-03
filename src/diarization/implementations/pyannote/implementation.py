"""Pyannote implementation."""

import io
from collections.abc import Iterator
from pathlib import Path

import torch
from pyannote.audio import Pipeline  # type: ignore  # noqa: PGH003

from diarization.interfaces import DiarizationService, SpeakerSegment


class PyannoteDiarizationService(DiarizationService):
    """Using pyannote."""

    def get_segments_from_file(
        self,
        file: io.BufferedReader,
    ) -> Iterator[SpeakerSegment]:
        """Return iterator with segments where speaker say in audio file."""
        model_path = Path(__file__).resolve().parent / "speaker-diarization-3.1" / "config.yaml"

        pipeline = Pipeline.from_pretrained(model_path)

        # send pipeline to GPU if available
        if torch.cuda.is_available():
            pipeline.to(torch.device("cuda"))

        diarization = pipeline(file)

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            if (turn.end - turn.start) > 0.05:
                yield SpeakerSegment((turn.start, turn.end), speaker)
