from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.states import CorrectionStates
from app.bot.keyboards import get_exit_mode_keyboard
from app.core.models.user import User
from app.services.correction_service import CorrectionService
from app.services.limit_service import LimitService
from app.services.user_service import UserService

router = Router()


@router.message(F.text == "✏️ Исправить фразу")
async def start_correction(message: Message, state: FSMContext, db_user: User, session: AsyncSession) -> None:
    if not db_user.is_onboarded:
        await message.answer("❌ Сначала пройди /start для настройки бота.")
        return

    limit_service = LimitService(session)
    if not limit_service.can_send_message(db_user):
        await message.answer(limit_service.get_limit_exceeded_text(db_user))
        return

    await state.set_state(CorrectionStates.waiting_phrase)
    await message.answer(
        "✏️ <b>Режим исправления фразы</b>\n\n"
        "Отправь мне фразу на испанском, и я сделаю детальный разбор:\n"
        "• Укажу на все ошибки\n"
        "• Объясню каждую ошибку на русском\n"
        "• Покажу, как сказать естественнее\n"
        "• Дам примеры похожих конструкций\n\n"
        "Отправляй фразу 👇",
        reply_markup=get_exit_mode_keyboard(),
    )


@router.message(CorrectionStates.waiting_phrase)
async def handle_correction_phrase(
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

    correction_service = CorrectionService(session)
    typing_action = message.bot.send_chat_action(message.chat.id, "typing")
    await typing_action

    response = await correction_service.correct_phrase(db_user, message.text)

    if response.get("error"):
        await message.answer(response.get("message", "Ошибка обработки."))
        return

    parts = []

    if response.get("has_errors") and response.get("corrections"):
        parts.append("❌ <b>Найденные ошибки:</b>\n")
        for i, correction in enumerate(response["corrections"], 1):
            parts.append(
                f"{i}. <b>{correction['error_type']}</b>\n"
                f"   Было: <code>{correction['original']}</code>\n"
                f"   Правильно: <code>{correction['corrected']}</code>\n"
                f"   <i>{correction['explanation']}</i>\n"
            )
    else:
        parts.append("✅ <b>Отлично!</b> В твоей фразе нет ошибок! 🎉\n")

    if response.get("natural_variant"):
        parts.append(f"💬 <b>Как скажет носитель:</b>\n<code>{response['natural_variant']}</code>\n")

    if response.get("full_corrected"):
        parts.append(f"✅ <b>Исправленная версия:</b>\n<code>{response['full_corrected']}</code>\n")

    if response.get("tip"):
        parts.append(f"💡 <b>Совет:</b>\n{response['tip']}\n")

    if response.get("example_sentences"):
        parts.append("<b>📝 Примеры:</b>")
        for example in response["example_sentences"]:
            parts.append(f"• {example}")

    await message.answer("\n".join(parts))

    await message.answer(
        "Отправь ещё одну фразу или вернись в меню 👇",
        reply_markup=get_exit_mode_keyboard(),
    )
