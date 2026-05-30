from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import get_subscription_keyboard, get_subscription_webapp_keyboard
from app.config import settings
from app.core.constants import DAILY_MESSAGE_LIMITS
from app.core.enums import SubscriptionTier
from app.core.models.user import User

router = Router()


def _build_subscription_text(db_user: User) -> str:
    tier = SubscriptionTier(db_user.subscription_tier)
    daily_limit = DAILY_MESSAGE_LIMITS[tier]
    messages_left = (
        "∞" if daily_limit is None else max(0, daily_limit - db_user.messages_today)
    )

    subscription_info = (
        f"💎 <b>Твоя подписка: {tier.value.upper()}</b>\n\n"
        f"📊 Сообщений использовано сегодня: <b>{db_user.messages_today}</b>\n"
        f"📬 Доступно сообщений: <b>{messages_left}</b>\n\n"
    )

    return (
        subscription_info +
        "<b>FREE</b>\n"
        "• 10 сообщений в день\n"
        "• Свободный разговор\n\n"
        "<b>BASIC</b> — 299₽/месяц\n"
        "• 50 сообщений в день\n"
        "• Больше ежедневной практики\n\n"
        "<b>PREMIUM</b> — 999₽/месяц\n"
        "• Безлимитные сообщения\n"
        "• Приоритетная скорость ответов\n\n"
        "Оплату подключим позже."
    )


@router.message(F.text.in_(["/subscribe", "💎 Подписка"]))
async def cmd_subscribe(message: Message, db_user: User) -> None:
    web_app_url = settings.subscription_web_app_url
    if web_app_url:
        await message.answer(
            "💎 <b>Тарифы Sol de Mañana</b>\n\n"
            "Открой витрину подписок, чтобы посмотреть FREE, BASIC и PREMIUM в удобном окне.",
            reply_markup=get_subscription_webapp_keyboard(web_app_url),
        )
        return

    await message.answer(
        _build_subscription_text(db_user),
        reply_markup=get_subscription_keyboard(),
    )


@router.message(F.text == "📖 Мой словарь")
async def cmd_vocabulary(message: Message, db_user: User) -> None:
    await message.answer(
        "📖 <b>Личный словарь</b>\n\n"
        "💎 Эта функция доступна для <b>Premium</b> подписчиков.\n\n"
        "После каждого ответа бота будет кнопка «Сохранить слово в словарь» — "
        "выбирай слова из диалогов и сохраняй в личную коллекцию для повторения.\n\n"
        "Оформи подписку — /subscribe"
    )


@router.callback_query(F.data == "settings:subscription")
async def show_subscription_from_settings(callback: CallbackQuery, db_user: User) -> None:
    await callback.message.edit_text(
        _build_subscription_text(db_user),
        reply_markup=get_subscription_keyboard(),
    )
    await callback.answer()
