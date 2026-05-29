from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_save_word_keyboard(message_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Сохранить слово в словарь", callback_data=f"vocab:save:{message_id}")
    return builder.as_markup()


def get_subscription_keyboard(tier: str = "free") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if tier == "free":
        builder.button(text="⭐ Оформить PREMIUM", callback_data="sub:premium")
    builder.button(text="◀️ Назад", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def get_grammar_next_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➡️ Следующее упражнение", callback_data="grammar:next")
    builder.button(text="📚 Другая тема", callback_data="grammar:topics")
    builder.button(text="◀️ В главное меню", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()
