from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards import get_subscription_keyboard, get_subscription_webapp_keyboard
from app.config import settings
from app.core.models.user import User
from app.infrastructure.payments import YooKassaService

router = Router()


@router.message(F.text.in_(["/subscribe", "💎 Подписка"]))
async def cmd_subscribe(message: Message, db_user: User) -> None:
    web_app_url = settings.subscription_web_app_url
    if web_app_url:
        await message.answer(
            "💎 <b>Тарифы Habla Bot</b>\n\n"
            "Открой витрину подписок, чтобы посмотреть FREE, BASIC и PREMIUM в удобном окне.",
            reply_markup=get_subscription_webapp_keyboard(web_app_url),
        )
        return

    tier = db_user.subscription_tier
    messages_left = max(0, 10 - db_user.messages_today) if tier == "free" else "∞"
    
    subscription_info = (
        f"💎 <b>Твоя подписка: {'🆓 FREE' if tier == 'free' else '⭐ PREMIUM'}</b>\n\n"
        f"📊 Сообщений использовано сегодня: <b>{db_user.messages_today}</b>\n"
        f"📬 Доступно сообщений: <b>{messages_left}</b>\n\n"
    )
    
    if tier == "free":
        text = (
            subscription_info +
            "<b>🆓 FREE план</b>\n"
            "• 10 сообщений в день\n"
            "• Свободный разговор\n"
            "• Базовый функционал\n\n"
            "<b>⭐ PREMIUM</b> — 599₽/месяц\n"
            "• Безлимитные сообщения\n"
            "• Приоритетная поддержка\n"
            "• Голосовые сообщения (скоро)\n\n"
            "Оформи подписку — жми кнопку ниже 👇"
        )
    else:
        text = (
            subscription_info +
            "<b>⭐ PREMIUM активна</b>\n"
            "• Безлимитные сообщения\n"
            "• Приоритетная поддержка\n"
            "• Голосовые сообщения (скоро)\n\n"
            "Спасибо за поддержку! 🙏"
        )
    
    await message.answer(text, reply_markup=get_subscription_keyboard(tier))


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
    tier = db_user.subscription_tier
    messages_left = max(0, 10 - db_user.messages_today) if tier == "free" else "∞"
    
    subscription_info = (
        f"💎 <b>Твоя подписка: {'🆓 FREE' if tier == 'free' else '⭐ PREMIUM'}</b>\n\n"
        f"📊 Сообщений использовано сегодня: <b>{db_user.messages_today}</b>\n"
        f"📬 Доступно сообщений: <b>{messages_left}</b>\n\n"
    )
    
    if tier == "free":
        text = (
            subscription_info +
            "<b>🆓 FREE план</b>\n"
            "• 10 сообщений в день\n"
            "• Свободный разговор\n"
            "• Базовый функционал\n\n"
            "<b>⭐ PREMIUM</b> — 599₽/месяц\n"
            "• Безлимитные сообщения\n"
            "• Приоритетная поддержка\n"
            "• Голосовые сообщения (скоро)\n\n"
            "Оформи подписку — жми кнопку ниже 👇"
        )
    else:
        text = (
            subscription_info +
            "<b>⭐ PREMIUM активна</b>\n"
            "• Безлимитные сообщения\n"
            "• Приоритетная поддержка\n"
            "• Голосовые сообщения (скоро)\n\n"
            "Спасибо за поддержку! 🙏"
        )
    
    await callback.message.edit_text(text, reply_markup=get_subscription_keyboard(tier))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:"))
async def handle_subscription_payment(callback: CallbackQuery, db_user: User) -> None:
    tier = callback.data.split(":")[1]
    if tier == "premium":
        payment_url = YooKassaService.create_payment(
            user_id=db_user.id,
            telegram_id=db_user.telegram_id,
            amount=599.0
        )
        
        if payment_url:
            builder = InlineKeyboardBuilder()
            builder.button(text="💳 Оплатить 599 ₽", url=payment_url)
            builder.button(text="◀️ Назад", callback_data="settings:subscription")
            builder.adjust(1)
            
            await callback.message.edit_text(
                "⭐ <b>PREMIUM подписка</b>\n\n"
                "Нажми на кнопку ниже, чтобы перейти к оплате.\n"
                "После успешной оплаты подписка активируется автоматически.\n\n"
                "💰 Сумма: <b>599 ₽/месяц</b>\n"
                "💳 Принимаем: Visa, Mastercard, МИР, СБП",
                reply_markup=builder.as_markup()
            )
        else:
            await callback.answer(
                "❌ Ошибка создания платежа. Проверьте настройки YooKassa или попробуйте позже.",
                show_alert=True
            )
    await callback.answer()
