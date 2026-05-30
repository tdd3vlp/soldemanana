from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🗣️ Свободный разговор")
    builder.button(text="📖 Мой словарь")
    builder.button(text="⚙️ Настройки")
    builder.adjust(1, 2)
    return builder.as_markup(resize_keyboard=True)


def get_exit_mode_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🏠 В главное меню")
    return builder.as_markup(resize_keyboard=True)


def get_settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 Подписка", callback_data="settings:subscription")
    builder.button(text="◀️ В главное меню", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()
