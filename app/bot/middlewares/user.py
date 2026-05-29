from typing import Any, Awaitable, Callable
from datetime import date
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.models.user import User


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        telegram_user = data.get("event_from_user")
        session: AsyncSession = data.get("session")

        if telegram_user is None or session is None:
            return await handler(event, data)

        result = await session.execute(
            select(User).where(User.telegram_id == telegram_user.id)
        )
        db_user = result.scalar_one_or_none()

        if db_user is None:
            db_user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name or "Пользователь",
                last_name=telegram_user.last_name,
                correction_intensity="important",
                subscription_tier="free",
            )
            session.add(db_user)
            await session.flush()
            await session.refresh(db_user)
        else:
            changed = False
            if db_user.username != telegram_user.username:
                db_user.username = telegram_user.username
                changed = True
            if db_user.first_name != (telegram_user.first_name or "Пользователь"):
                db_user.first_name = telegram_user.first_name or "Пользователь"
                changed = True
            if changed:
                await session.flush()

        if db_user.last_message_date != date.today():
            db_user.messages_today = 0
            db_user.last_message_date = date.today()
            await session.flush()

        data["db_user"] = db_user
        return await handler(event, data)
