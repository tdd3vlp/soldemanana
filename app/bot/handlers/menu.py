from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.states import SettingsStates
from app.bot.keyboards import (
    get_main_menu_keyboard,
    get_settings_keyboard,
    get_level_keyboard,
    get_goal_keyboard,
    get_correction_intensity_keyboard,
)
from app.core.models.user import User
from app.core.constants import LEVEL_LABELS, GOAL_LABELS
from app.services.user_service import UserService
from app.services.limit_service import LimitService

router = Router()

INTENSITY_LABELS = {
    "all": "Исправлять всё",
    "important": "Только важные ошибки",
    "none": "Не исправлять",
}


@router.message(F.text == "⚙️ Настройки")
async def cmd_settings(message: Message, state: FSMContext, db_user: User) -> None:
    await state.clear()
    limit_service = LimitService(None)
    remaining = limit_service.get_remaining(db_user)
    remaining_text = f"{remaining}" if remaining is not None else "∞"

    level_label = LEVEL_LABELS.get(db_user.level or "", "не указан")
    goal_label = GOAL_LABELS.get(db_user.goal or "", "не указана")
    intensity_label = INTENSITY_LABELS.get(db_user.correction_intensity, "важные ошибки")

    text = (
        f"⚙️ <b>Настройки</b>\n\n"
        f"📊 Уровень: <b>{level_label}</b>\n"
        f"🎯 Цель: <b>{goal_label}</b>\n"
        f"✏️ Исправления: <b>{intensity_label}</b>\n"
        f"💬 Тариф: <b>{db_user.subscription_tier.upper()}</b>\n"
        f"📩 Осталось сегодня: <b>{remaining_text}</b> сообщений\n"
    )
    await message.answer(text, reply_markup=get_settings_keyboard())


@router.callback_query(F.data == "menu:main")
async def on_back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Главное меню 👇", reply_markup=get_main_menu_keyboard())
    await callback.answer()


@router.message(F.text == "🏠 В главное меню")
async def on_back_to_menu_text(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Главное меню 👇", reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data == "settings:level")
async def on_settings_level(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "📊 <b>Выбери новый уровень:</b>",
        reply_markup=get_level_keyboard(),
    )
    await state.set_state(SettingsStates.waiting_level)
    await callback.answer()


@router.callback_query(SettingsStates.waiting_level, F.data.startswith("level:"))
async def on_settings_level_selected(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, db_user: User
) -> None:
    level = callback.data.split(":")[1]
    user_service = UserService(session)
    await user_service.update_level(db_user, level)
    await state.clear()
    await callback.message.edit_text(
        f"✅ Уровень обновлён: <b>{LEVEL_LABELS.get(level, level)}</b>",
    )
    await callback.message.answer("Главное меню 👇", reply_markup=get_main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "settings:goal")
async def on_settings_goal(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "🎯 <b>Выбери новую цель:</b>",
        reply_markup=get_goal_keyboard(),
    )
    await state.set_state(SettingsStates.waiting_goal)
    await callback.answer()


@router.callback_query(SettingsStates.waiting_goal, F.data.startswith("goal:"))
async def on_settings_goal_selected(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, db_user: User
) -> None:
    goal = callback.data.split(":")[1]
    user_service = UserService(session)
    await user_service.update_goal(db_user, goal)
    await state.clear()
    await callback.message.edit_text(
        f"✅ Цель обновлена: <b>{GOAL_LABELS.get(goal, goal)}</b>",
    )
    await callback.message.answer("Главное меню 👇", reply_markup=get_main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "settings:correction")
async def on_settings_correction(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "✏️ <b>Как исправлять ошибки?</b>",
        reply_markup=get_correction_intensity_keyboard(),
    )
    await state.set_state(SettingsStates.waiting_correction)
    await callback.answer()


@router.callback_query(SettingsStates.waiting_correction, F.data.startswith("intensity:"))
async def on_settings_correction_selected(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, db_user: User
) -> None:
    intensity = callback.data.split(":")[1]
    user_service = UserService(session)
    await user_service.update_correction_intensity(db_user, intensity)
    await state.clear()
    await callback.message.edit_text(
        f"✅ Режим исправлений: <b>{INTENSITY_LABELS.get(intensity, intensity)}</b>",
    )
    await callback.message.answer("Главное меню 👇", reply_markup=get_main_menu_keyboard())
    await callback.answer()
