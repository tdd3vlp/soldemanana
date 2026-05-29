from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import get_main_menu_keyboard, get_settings_keyboard
from app.core.models.user import User
from app.services.limit_service import LimitService

router = Router()


@router.message(F.text == "⚙️ Настройки")
async def cmd_settings(message: Message, state: FSMContext, db_user: User) -> None:
    await state.clear()
    limit_service = LimitService(None)
    remaining = limit_service.get_remaining(db_user)
    remaining_text = f"{remaining}" if remaining is not None else "∞"

    text = (
        f"⚙️ <b>Настройки</b>\n\n"
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
