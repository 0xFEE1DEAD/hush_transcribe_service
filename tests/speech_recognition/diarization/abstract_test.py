from abc import ABC, abstractmethod
from pathlib import Path

import pytest

from speech_recognition.diarization.interfaces import DiarizationService


class AbstractTest(ABC):
    """Diarization service test."""

    @pytest.fixture
    @abstractmethod
    def service(self) -> DiarizationService:
        """Get fixture."""
        msg = "Override 'service' fixture in subclass"
        raise NotImplementedError(msg)

    @pytest.fixture
    def audio_path(self) -> Path:
        """Get test filepath."""
        filepath = Path(__file__).resolve().parent / Path("fixture.wav")
        if not filepath.exists():
            msg = "File does not exists"
            raise RuntimeError(msg)

        return filepath

    def test_return_segments(self, service: DiarizationService, audio_path: Path) -> None:
        """Run service full workflow test."""
        with Path.open(audio_path, "rb") as opened_file:
            list(service.get_segments_from_file(opened_file))
