from aiogram.types import Message

from speech_recognition.pipeline.interfaces import ProgressObserver


class TelegramProgressObserver(ProgressObserver):
    def __init__(self, message: Message) -> None:
        """Update progress in message."""
        self.message = message

    async def update(self, percent: int) -> None:
        await self.message.edit_text(self.__progress_bar(percent))

    def __progress_bar(self, percent: int, size: int = 10) -> str:
        filled = int(size * percent / 100)
        empty = size - filled

        bar = "█" * filled + "░" * empty
        return f"[{bar}] {percent}%"
