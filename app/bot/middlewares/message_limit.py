from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.services.limit_service import LimitService


class MessageLimitMiddleware(BaseMiddleware):
    SKIP_TEXTS = {
        "🏠 В главное меню",
        "🗣️ Свободный разговор",
        "📖 Мой словарь",
        "⚙️ Настройки",
    }

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        db_user: User = data.get("db_user")
        session: AsyncSession = data.get("session")

        if not db_user or not session:
            return await handler(event, data)

        if event.text and (event.text.startswith("/") or event.text in self.SKIP_TEXTS):
            return await handler(event, data)

        limit_service = LimitService(session)
        if not limit_service.can_send_message(db_user):
            await event.answer(
                limit_service.get_limit_exceeded_text(db_user)
            )
            return

        return await handler(event, data)
