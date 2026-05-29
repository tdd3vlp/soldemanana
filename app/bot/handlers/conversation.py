from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.states import ConversationStates
from app.bot.keyboards import get_exit_mode_keyboard
from app.core.models.user import User
from app.services.conversation_service import ConversationService
from app.services.limit_service import LimitService
from app.services.user_service import UserService

router = Router()


@router.message(F.text == "🗣️ Свободный разговор")
async def start_conversation(message: Message, state: FSMContext, db_user: User, session: AsyncSession) -> None:
    if not db_user.is_onboarded:
        await message.answer("❌ Сначала пройди /start для настройки бота.")
        return

    limit_service = LimitService(session)
    if not limit_service.can_send_message(db_user):
        await message.answer(limit_service.get_limit_exceeded_text(db_user))
        return

    await state.set_state(ConversationStates.active)
    
    base_text = (
        "🗣️ <b>Режим свободного разговора</b>\n\n"
        "Пиши мне на испанском — о чём угодно! Я буду отвечать, исправлять ошибки и объяснять их.\n\n"
    )
    
    if db_user.level == "A0":
        starter_phrases = [
            "🇪🇸 <b>Hola, ¿cómo estás?</b>\n<i>(Привет, как дела?)</i>",
            "🇪🇸 <b>Me llamo [твоё имя]</b>\n<i>(Меня зовут [твоё имя])</i>",
            "🇪🇸 <b>¿Qué tal tu día?</b>\n<i>(Как твой день?)</i>",
            "🇪🇸 <b>Estoy aprendiendo español</b>\n<i>(Я учу испанский)</i>",
            "🇪🇸 <b>¿De dónde eres?</b>\n<i>(Откуда ты?)</i>",
        ]
        base_text += (
            "💡 <b>Выбери фразу для начала или напиши свою:</b>\n\n"
            + "\n\n".join(starter_phrases) + "\n\n"
        )
    
    base_text += "Для выхода в меню нажми кнопку внизу 👇"
    
    await message.answer(base_text, reply_markup=get_exit_mode_keyboard())


@router.message(ConversationStates.active)
async def handle_conversation_message(
    message: Message,
    state: FSMContext,
    db_user: User,
    session: AsyncSession,
) -> None:
    if message.text == "🏠 В главное меню":
        return

    limit_service = LimitService(session)
    if not limit_service.can_send_message(db_user):
        await message.answer(limit_service.get_limit_exceeded_text(db_user))
        await state.clear()
        return

    user_service = UserService(session)
    await user_service.increment_message_count(db_user)

    conversation_service = ConversationService(session)
    typing_action = message.bot.send_chat_action(message.chat.id, "typing")
    await typing_action

    response = await conversation_service.process_message(db_user, message.text)

    if response.get("error"):
        await message.answer(response.get("message", "Ошибка обработки."))
        return

    parts = []

    if response.get("has_errors") and response.get("corrections"):
        parts.append("✏️ <b>Исправления:</b>")
        for correction in response["corrections"]:
            parts.append(
                f"❌ <code>{correction['original']}</code> → "
                f"✅ <code>{correction['corrected']}</code>\n"
                f"<i>{correction['explanation']}</i>"
            )
        parts.append("")

    if response.get("natural_variant"):
        parts.append(f"💬 <b>Естественный вариант:</b>\n<code>{response['natural_variant']}</code>\n")

    bot_reply = response.get("reply", "")
    if bot_reply:
        parts.append(f"🇪🇸 {bot_reply}")

    if response.get("reply_translation"):
        parts.append(f"<i>({response['reply_translation']})</i>")

    await message.answer("\n".join(parts))
