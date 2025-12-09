import asyncio

from settings.settings import Settings
from telegram_integration.telegram_integration import TelegramBotApp

settings = Settings()


async def main() -> None:  # noqa: D103
    if settings.telegram_api_key is None:
        msg = "TELEGRAM API KEY NEEDED"
        raise RuntimeError(msg)

    app = TelegramBotApp(settings.telegram_api_key)
    await app.run()


asyncio.run(main())
