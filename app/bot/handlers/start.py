from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.states import OnboardingStates
from app.bot.keyboards import (
    get_level_keyboard,
    get_goal_keyboard,
    get_correction_intensity_keyboard,
    get_main_menu_keyboard,
)
from app.core.models.user import User
from app.core.constants import LEVEL_LABELS, GOAL_LABELS
from app.services.user_service import UserService

router = Router()

WELCOME_TEXT = """
👋 <b>¡Hola! Привет!</b>

Я <b>Sol de Mañana</b> — твой персональный преподаватель испанского языка.

Я помогу тебе практиковать испанский Испании в живых диалогах:
• Исправлю ошибки и объясню их на русском
• Предложу, как сказать это более естественно
• Поговорю с тобой на любую тему
• Разыграю реальные ситуации (ресторан, аптека, мэрия...)
• Объясню грамматику с примерами

Для начала — несколько вопросов, чтобы я мог адаптироваться под тебя.

<b>Какой у тебя уровень испанского?</b>
"""

GOAL_TEXT = """
Отлично! Теперь скажи — <b>зачем ты учишь испанский?</b>

Это поможет мне подбирать нужную лексику и темы разговоров 👇
"""

INTENSITY_TEXT = """
Последний вопрос!

<b>Как ты хочешь, чтобы я реагировал на ошибки?</b>

Это можно изменить в настройках в любой момент.
"""

ONBOARDING_DONE_TEXT = """
✅ <b>Всё готово!</b>

Уровень: <b>{level}</b>
Цель: <b>{goal}</b>
Исправления: <b>{intensity}</b>

Начнём? Выбери режим в меню 👇
"""

INTENSITY_LABELS = {
    "all": "Исправлять всё",
    "important": "Только важные ошибки",
    "none": "Не исправлять",
}


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db_user: User) -> None:
    await state.clear()
    if db_user.is_onboarded:
        await message.answer(
            f"👋 <b>¡Bienvenido de nuevo!</b> С возвращением, {db_user.first_name}!\n\n"
            "Выбери что хочешь делать 👇",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await message.answer(WELCOME_TEXT, reply_markup=get_level_keyboard())
    await state.set_state(OnboardingStates.waiting_level)


@router.callback_query(OnboardingStates.waiting_level, F.data.startswith("level:"))
async def on_level_selected(callback: CallbackQuery, state: FSMContext, db_user: User) -> None:
    level = callback.data.split(":")[1]
    await state.update_data(level=level)
    level_label = LEVEL_LABELS.get(level, level)
    await callback.message.edit_text(
        f"✅ Уровень: <b>{level_label}</b>\n\n{GOAL_TEXT}",
        reply_markup=get_goal_keyboard(),
    )
    await state.set_state(OnboardingStates.waiting_goal)
    await callback.answer()


@router.callback_query(OnboardingStates.waiting_goal, F.data.startswith("goal:"))
async def on_goal_selected(callback: CallbackQuery, state: FSMContext) -> None:
    goal = callback.data.split(":")[1]
    await state.update_data(goal=goal)
    goal_label = GOAL_LABELS.get(goal, goal)
    await callback.message.edit_text(
        f"✅ Цель: <b>{goal_label}</b>\n\n{INTENSITY_TEXT}",
        reply_markup=get_correction_intensity_keyboard(),
    )
    await state.set_state(OnboardingStates.waiting_correction_intensity)
    await callback.answer()


@router.callback_query(OnboardingStates.waiting_correction_intensity, F.data.startswith("intensity:"))
async def on_intensity_selected(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
) -> None:
    intensity = callback.data.split(":")[1]
    data = await state.get_data()
    level = data.get("level", "A2")
    goal = data.get("goal", "communication")

    user_service = UserService(session)
    await user_service.update_onboarding(db_user, level, goal, intensity)
    await state.clear()

    level_label = LEVEL_LABELS.get(level, level)
    goal_label = GOAL_LABELS.get(goal, goal)
    intensity_label = INTENSITY_LABELS.get(intensity, intensity)

    await callback.message.edit_text(
        ONBOARDING_DONE_TEXT.format(
            level=level_label,
            goal=goal_label,
            intensity=intensity_label,
        )
    )
    await callback.message.answer(
        "Главное меню 👇",
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()
