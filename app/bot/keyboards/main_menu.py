from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from app.core.constants import SCENARIO_LIST, GRAMMAR_TOPICS


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🗣️ Свободный разговор")
    builder.button(text="✏️ Исправить фразу")
    builder.button(text="🎭 Ситуации в Испании")
    builder.button(text="📚 Грамматика")
    builder.button(text="📖 Мой словарь")
    builder.button(text="⚙️ Настройки")
    builder.adjust(2, 2, 2)
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


def get_exit_mode_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🏠 В главное меню")
    return builder.as_markup(resize_keyboard=True)


def get_settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Сменить уровень", callback_data="settings:level")
    builder.button(text="🎯 Сменить цель", callback_data="settings:goal")
    builder.button(text="✏️ Режим исправлений", callback_data="settings:correction")
    builder.button(text="💎 Подписка", callback_data="settings:subscription")
    builder.button(text="◀️ В главное меню", callback_data="menu:main")
    builder.adjust(2, 1, 1, 1)
    return builder.as_markup()
