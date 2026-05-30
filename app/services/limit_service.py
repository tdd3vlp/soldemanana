from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.constants import DAILY_MESSAGE_LIMITS
from app.core.enums import SubscriptionTier
from app.core.models.user import User


class LimitService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def get_daily_limit(self, user: User) -> int | None:
        if user.telegram_id in settings.admin_ids:
            return None

        tier = SubscriptionTier(user.subscription_tier)
        return DAILY_MESSAGE_LIMITS.get(tier)

    def can_send_message(self, user: User) -> bool:
        limit = self.get_daily_limit(user)
        if limit is None:
            return True
        today = date.today()
        if user.last_message_date != today:
            return True
        return user.messages_today < limit

    def get_remaining(self, user: User) -> int | None:
        limit = self.get_daily_limit(user)
        if limit is None:
            return None
        today = date.today()
        if user.last_message_date != today:
            return limit
        return max(0, limit - user.messages_today)

    def get_limit_exceeded_text(self, user: User) -> str:
        tier = SubscriptionTier(user.subscription_tier)
        limit = self.get_daily_limit(user)
        if tier == SubscriptionTier.FREE:
            return (
                f"⛔ Ты использовал все <b>{limit}</b> бесплатных сообщений на сегодня.\n\n"
                "Лимит обновится завтра в 00:00.\n\n"
                "💎 Хочешь больше? Перейди на <b>BASIC</b> (50/день) "
                "или <b>PREMIUM</b> (безлимит).\n"
                "Нажми /subscribe чтобы узнать подробности."
            )
        if tier == SubscriptionTier.BASIC:
            return (
                f"⛔ Ты использовал все <b>{limit}</b> сообщений BASIC на сегодня.\n\n"
                "Лимит обновится завтра в 00:00.\n\n"
                "Для безлимитного доступа подойдёт <b>PREMIUM</b>."
            )
        return (
            f"⛔ Ты использовал все <b>{limit}</b> сообщений на сегодня.\n\n"
            "Лимит обновится завтра."
        )
