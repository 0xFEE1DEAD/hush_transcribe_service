from typing import Protocol


class ProgressObserver(Protocol):
    async def update(self, percent: int) -> None: ...
