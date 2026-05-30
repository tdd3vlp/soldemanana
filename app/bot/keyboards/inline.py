from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_save_word_keyboard(message_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Сохранить слово в словарь", callback_data=f"vocab:save:{message_id}")
    return builder.as_markup()


def get_reply_translation_keyboard(token: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Перевести", callback_data=f"conv:translate:{token}")
    return builder.as_markup()


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def get_subscription_webapp_keyboard(web_app_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 Открыть тарифы", web_app=WebAppInfo(url=web_app_url))
    builder.button(text="◀️ Назад", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()
