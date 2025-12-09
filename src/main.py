import asyncio

from telegram_integration.telegram_integration import TelegramBotApp


async def main() -> None:  # noqa: D103
    app = TelegramBotApp("")
    await app.run()


asyncio.run(main())
