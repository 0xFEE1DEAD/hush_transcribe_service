import pytest

from speech_recognition.interval_storage.interfaces import IntervalStorageService
from speech_recognition.interval_storage.intervaltree_storage_service import IntervalTreeStorageService

from .abstract_test import AbstractTest


class TestIntervalTreeStorageService(AbstractTest):
    @pytest.fixture
    def service(self) -> IntervalStorageService:
        """Get fixture."""
        return IntervalTreeStorageService()
