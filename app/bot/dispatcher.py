import redis.asyncio as aioredis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from app.bot.middlewares import (
    DatabaseMiddleware,
    MessageLimitMiddleware,
    ThrottlingMiddleware,
    UserMiddleware,
)
from app.config import settings


def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher(redis_url: str) -> Dispatcher:
    redis = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())

    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(MessageLimitMiddleware())

    _register_handlers(dp)

    return dp


def _register_handlers(dp: Dispatcher) -> None:
    from app.bot.handlers import (
        admin,
        conversation,
        fallback,
        menu,
        start,
        subscription,
    )

    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(subscription.router)
    dp.include_router(admin.router)
    dp.include_router(conversation.router)
    dp.include_router(fallback.router)
