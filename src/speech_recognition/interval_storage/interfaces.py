"""Interfaces for interval storage."""

from typing import Protocol


class IntervalStorageService(Protocol):
    """Storage for storing data by interval."""

    def store(self, timestamp_from: float, timestamp_to: float, data: str) -> "IntervalStorageService":
        """Store data by interval."""
        ...

    def get(self, timestamp_from: float, timestamp_to: float) -> tuple[str, ...]:
        """Get data by interval.

        **[timestamp_from, timestamp_to)**.
        """
        ...
