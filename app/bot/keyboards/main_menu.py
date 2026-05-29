from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.core.constants import GRAMMAR_TOPICS, SCENARIO_LIST


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


def get_scenario_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for scenario in SCENARIO_LIST:
        builder.button(
            text=f"{scenario['emoji']} {scenario['title']}",
            callback_data=f"scenario:{scenario['id']}",
        )
    builder.button(text="◀️ В главное меню", callback_data="menu:main")
    builder.adjust(2)
    return builder.as_markup()


def get_grammar_topics_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for topic in GRAMMAR_TOPICS:
        builder.button(text=topic["title"], callback_data=f"grammar:{topic['id']}")
    builder.button(text="◀️ В главное меню", callback_data="menu:main")
    builder.adjust(2)
    return builder.as_markup()


def get_settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 Подписка", callback_data="settings:subscription")
    builder.button(text="◀️ В главное меню", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()
