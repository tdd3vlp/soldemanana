from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from app.infrastructure.redis.client import redis_client
from app.core.constants import THROTTLE_RATE, THROTTLE_KEY_PREFIX


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate: float = THROTTLE_RATE) -> None:
        self.rate = rate

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        key = f"{THROTTLE_KEY_PREFIX}:{user.id}"
        is_throttled = await redis_client.exists(key)

        if is_throttled:
            await event.answer("⏳ Не так быстро! Подожди секунду.")
            return

        await redis_client.set(key, "1", ttl=int(self.rate))
        return await handler(event, data)
