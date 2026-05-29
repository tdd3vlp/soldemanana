from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.keyboards import get_main_menu_keyboard
from app.core.models.user import User

router = Router()


@router.message(F.text)
async def ask_to_choose_mode(message: Message, state: FSMContext, db_user: User) -> None:
    await state.clear()

    if not db_user.is_onboarded:
        await message.answer("Сначала пройди /start для настройки бота.")
        return

    await message.answer(
        "Выбери режим, чтобы продолжить 👇",
        reply_markup=get_main_menu_keyboard(),
    )
