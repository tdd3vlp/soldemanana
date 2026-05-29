from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.states import GrammarStates
from app.bot.keyboards import (
    get_grammar_topics_keyboard,
    get_grammar_next_keyboard,
    get_exit_mode_keyboard,
)
from app.core.models.user import User
from app.core.constants import GRAMMAR_TOPICS
from app.services.grammar_service import GrammarService
from app.services.limit_service import LimitService
from app.services.user_service import UserService

router = Router()


@router.message(F.text == "📚 Грамматика")
async def show_grammar_topics(message: Message, state: FSMContext, db_user: User) -> None:
    if not db_user.is_onboarded:
        await message.answer(
            "❌ Сначала пройди /start для настройки бота."
        )
        return

    await state.set_state(GrammarStates.choosing_topic)
    await message.answer(
        "📚 <b>Грамматика</b>\n\n"
        "Выбери тему — я объясню правила "
        "и дам упражнения 👇",
        reply_markup=get_grammar_topics_keyboard(),
    )


@router.callback_query(GrammarStates.choosing_topic, F.data.startswith("grammar:"))
async def start_grammar_topic(
    callback: CallbackQuery,
    state: FSMContext,
    db_user: User,
    session: AsyncSession,
) -> None:
    topic_id = callback.data.split(":")[1]
    if topic_id == "topics":
        await show_grammar_topics(callback.message, state, db_user)
        await callback.answer()
        return

    topic = next((t for t in GRAMMAR_TOPICS if t["id"] == topic_id), None)
    if not topic:
        await callback.answer("Тема не найдена.")
        return

    limit_service = LimitService(session)
    if not limit_service.can_send_message(db_user):
        await callback.message.answer(limit_service.get_limit_exceeded_text(db_user))
        await callback.answer()
        return

    user_service = UserService(session)
    await user_service.increment_message_count(db_user)

    await state.update_data(topic_id=topic_id, topic_title=topic["title"])
    await state.set_state(GrammarStates.doing_exercise)

    grammar_service = GrammarService(session)
    response = await grammar_service.start_topic(db_user, topic_id, topic["title"])

    if response.get("error"):
        await callback.message.answer(response.get("message", "Ошибка."))
        await callback.answer()
        return

    parts = [
        f"📚 <b>{topic['title']}</b>\n",
        response.get("explanation", ""),
        (
            f"\n<b>Упражнение:</b>\n"
            f"{response.get('exercise', 'Задание загружается...')}"
        ),
    ]
    if response.get("hint"):
        parts.append(f"\n💡 <i>Подсказка: {response['hint']}</i>")

    await callback.message.edit_text("\n".join(parts))
    await state.update_data(current_exercise=response.get("exercise"))
    await callback.message.answer(
        "Отправь свой ответ 👇",
        reply_markup=get_exit_mode_keyboard(),
    )
    await callback.answer()


@router.message(GrammarStates.doing_exercise)
async def handle_grammar_answer(
    message: Message,
    state: FSMContext,
    db_user: User,
    session: AsyncSession,
) -> None:
    if message.text == "🏠 В главное меню":
        return

    data = await state.get_data()
    topic_id = data.get("topic_id")
    topic_title = data.get("topic_title")
    current_exercise = data.get("current_exercise")

    if not topic_id:
        await message.answer("Ошибка: тема не найдена.")
        await state.clear()
        return

    limit_service = LimitService(session)
    if not limit_service.can_send_message(db_user):
        await message.answer(limit_service.get_limit_exceeded_text(db_user))
        await state.clear()
        return

    user_service = UserService(session)
    await user_service.increment_message_count(db_user)

    grammar_service = GrammarService(session)
    typing_action = message.bot.send_chat_action(message.chat.id, "typing")
    await typing_action

    response = await grammar_service.check_answer(
        db_user,
        topic_id,
        topic_title,
        message.text,
        exercise=current_exercise,
    )

    if response.get("error"):
        await message.answer(response.get("message", "Ошибка обработки."))
        return

    parts = []

    if response.get("is_correct"):
        parts.append("✅ <b>Правильно!</b> Молодец! 🎉\n")
    else:
        parts.append("❌ <b>Не совсем.</b>\n")

    parts.append(response.get("feedback", ""))

    if response.get("correct_answer"):
        parts.append(
            f"\n<b>Правильный ответ:</b>\n"
            f"<code>{response['correct_answer']}</code>"
        )

    if response.get("explanation"):
        parts.append(f"\n{response['explanation']}")

    if response.get("next_exercise"):
        await state.update_data(current_exercise=response["next_exercise"])

    await message.answer("\n".join(parts), reply_markup=get_grammar_next_keyboard())


@router.callback_query(GrammarStates.doing_exercise, F.data == "grammar:next")
async def show_next_grammar_exercise(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    next_exercise = data.get("current_exercise")
    if not next_exercise:
        await callback.answer("Задание не найдено.")
        return

    await callback.message.answer(
        f"<b>Следующее упражнение:</b>\n{next_exercise}",
        reply_markup=get_exit_mode_keyboard(),
    )
    await callback.answer()
