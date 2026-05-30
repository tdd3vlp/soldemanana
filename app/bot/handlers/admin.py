from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsAdmin
from app.core.enums import SubscriptionTier
from app.core.models.ai_usage import AIUsage
from app.core.models.message import Message as DBMessage
from app.core.models.user import User

router = Router()


@router.message(Command("admin"), IsAdmin())
async def cmd_admin(message: Message, session: AsyncSession) -> None:
    total_users = await session.scalar(select(func.count(User.id)))
    onboarded = await session.scalar(select(func.count(User.id)).where(User.is_onboarded.is_(True)))
    total_messages = await session.scalar(select(func.count(DBMessage.id)))

    await message.answer(
        f"🔐 <b>Админ-панель</b>\n\n"
        f"👥 Всего пользователей: <b>{total_users}</b>\n"
        f"✅ Прошли онбординг: <b>{onboarded}</b>\n"
        f"💬 Всего сообщений: <b>{total_messages}</b>\n\n"
        "Команды:\n"
        "/broadcast — рассылка всем пользователям\n"
        "/stats — детальная статистика"
    )


@router.message(Command("broadcast"), IsAdmin())
async def cmd_broadcast(message: Message) -> None:
    await message.answer(
        "📢 <b>Рассылка</b>\n\n"
        "Эта функция пока не реализована в MVP.\n"
        "В будущих версиях: отправка сообщений "
        "всем пользователям."
    )


@router.message(Command("stats"), IsAdmin())
async def cmd_stats(message: Message, session: AsyncSession) -> None:
    free_count = await session.scalar(
        select(func.count(User.id)).where(User.subscription_tier == SubscriptionTier.FREE)
    )
    basic_count = await session.scalar(
        select(func.count(User.id)).where(User.subscription_tier == SubscriptionTier.BASIC)
    )
    premium_count = await session.scalar(
        select(func.count(User.id)).where(User.subscription_tier == SubscriptionTier.PREMIUM)
    )
    usage = await session.execute(
        select(
            func.coalesce(func.sum(AIUsage.prompt_tokens), 0),
            func.coalesce(func.sum(AIUsage.completion_tokens), 0),
            func.coalesce(func.sum(AIUsage.estimated_cost_usd), 0),
        ).where(
            func.date_trunc("month", AIUsage.created_at)
            == func.date_trunc("month", func.now())
        )
    )
    prompt_tokens, completion_tokens, estimated_cost = usage.one()

    await message.answer(
        f"📊 <b>Статистика подписок</b>\n\n"
        f"🆓 FREE: <b>{free_count}</b>\n"
        f"💎 BASIC: <b>{basic_count}</b>\n"
        f"⭐ PREMIUM: <b>{premium_count}</b>\n\n"
        f"🤖 AI за месяц: "
        f"<b>{int(prompt_tokens) + int(completion_tokens)}</b> токенов\n"
        f"💵 Оценка cost: <b>${float(estimated_cost):.4f}</b>"
    )
