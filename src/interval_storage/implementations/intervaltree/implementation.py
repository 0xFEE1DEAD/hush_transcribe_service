"""Implementation interval storage service."""

from intervaltree import Interval as IntervalTreeInterval  # type: ignore  # noqa: PGH003
from intervaltree import IntervalTree  # type: ignore  # noqa: PGH003

from interval_storage.interfaces import IntervalStorageService


class IntervalTreeStorageService(IntervalStorageService):
    """Intervaltree lib storage service."""

    def __init__(self) -> None:
        """Init interval tree data structure."""
        super().__init__()
        self._tree = IntervalTree()

    def store(self, timestamp_from: float, timestamp_to: float, data: str) -> "IntervalStorageService":
        """Store data by interval."""
        if timestamp_from == timestamp_to:
            timestamp_to += 0.001

        self._tree.add(IntervalTreeInterval(timestamp_from, timestamp_to, data=data))  # type: ignore  # noqa: PGH003

        return self

    def get(self, timestamp_from: float, timestamp_to: float) -> tuple[str, ...]:
        """Get data by interval.

        **[timestamp_from, timestamp_to)**.
        """
        results = self._tree.overlap(timestamp_from, timestamp_to)  # type: ignore  # noqa: PGH003

        return tuple(iv.data for iv in sorted(results))  # type: ignore
