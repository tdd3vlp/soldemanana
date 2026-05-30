from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.constants import GOAL_LABELS, LEVEL_LABELS


def get_level_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for level_key, label in LEVEL_LABELS.items():
        builder.button(text=label, callback_data=f"level:{level_key}")
    builder.adjust(2)
    return builder.as_markup()


def get_goal_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for goal_key, label in GOAL_LABELS.items():
        builder.button(text=label, callback_data=f"goal:{goal_key}")
    builder.adjust(1)
    return builder.as_markup()


def get_correction_intensity_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Исправлять всё", callback_data="intensity:all")
    builder.button(text="⚖️ Только важные ошибки", callback_data="intensity:important")
    builder.adjust(1)
    return builder.as_markup()
