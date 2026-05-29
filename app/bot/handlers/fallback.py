from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.conversation import handle_conversation_message
from app.bot.states import ConversationStates
from app.core.models.user import User

router = Router()


@router.message(F.text)
async def default_to_conversation(
    message: Message,
    state: FSMContext,
    db_user: User,
    session: AsyncSession,
) -> None:
    await state.clear()

    if not db_user.is_onboarded:
        await message.answer("Сначала пройди /start для настройки бота.")
        return

    await state.set_state(ConversationStates.active)
    await handle_conversation_message(message, state, db_user, session)
