import asyncio

import structlog
from aiogram import Bot
from aiogram.types import BotCommand

from app.bot.dispatcher import create_bot, create_dispatcher
from app.config import settings
from app.infrastructure.redis import redis_client

logger = structlog.get_logger()


async def set_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="🚀 Начать / Перезапустить бота"),
        BotCommand(command="subscribe", description="💎 Подписка и лимиты"),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
    )

    logger.info("Starting Sol de Mañana Bot...", environment=settings.environment)

    await redis_client.connect()
    logger.info("Redis connected")

    bot = create_bot()
    dp = create_dispatcher(settings.redis_url)

    await set_bot_commands(bot)

    logger.info("Bot started successfully", bot_token=settings.bot_token[:10] + "...")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await redis_client.disconnect()
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
