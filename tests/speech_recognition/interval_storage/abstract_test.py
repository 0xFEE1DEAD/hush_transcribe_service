from abc import ABC, abstractmethod

import pytest

from speech_recognition.interval_storage.interfaces import IntervalStorageService


class AbstractTest(ABC):
    """Diarization service test."""

    @pytest.fixture
    @abstractmethod
    def service(self) -> IntervalStorageService:
        """Get fixture."""
        msg = "Override 'service' fixture in subclass"
        raise NotImplementedError(msg)

    def test_insert_and_searching(self, service: IntervalStorageService) -> None:
        """Run service full workflow test."""
        data = "test_data"
        service.store(10, 15, data)

        inserted_data = service.get(10, 15)
        assert inserted_data[0] == data

        inserted_data = service.get(0, 20)
        assert inserted_data[0] == data

        data2 = "test_data2"
        service.store(15, 20, data2)
        inserted_data = service.get(0, 30)
        assert inserted_data[0] == data
        assert inserted_data[1] == data2

        inserted_data = service.get(17, 19)
        assert inserted_data[0] == data2
