import pytest

from speech_recognition.diarization.interfaces import DiarizationService
from speech_recognition.diarization.resemblyzer_with_silero_vad_diarization_service import (
    ResemblyzerWithSileroVADDiarizationService,
)

from .abstract_test import AbstractTest


class TestResemblyzerWithSileroVADDiarizationService(AbstractTest):
    @pytest.fixture
    def service(self) -> DiarizationService:
        """Get fixture."""
        return ResemblyzerWithSileroVADDiarizationService()
