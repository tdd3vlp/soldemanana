from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.conversation import enter_conversation
from app.core.models.user import User
from app.services.user_service import UserService

router = Router()

WELCOME_TEXT = """
👋 <b>¡Hola! Привет!</b>

Я <b>Sol de Mañana</b> — твой персональный преподаватель испанского языка.

Я помогу тебе практиковать испанский Испании в живых диалогах:
• Исправлю ошибки в последней фразе
• Предложу, как сказать это более естественно
• Поговорю с тобой на любую тему

Начнём со свободного разговора.
"""


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    db_user: User,
    session: AsyncSession,
) -> None:
    await state.clear()
    if db_user.is_onboarded:
        await enter_conversation(message, state, db_user, is_new_user=False)
        return

    user_service = UserService(session)
    await user_service.update_onboarding(db_user, "A2", "communication", "important")
    await message.answer(WELCOME_TEXT)
    await enter_conversation(message, state, db_user, is_new_user=True)
