from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.states import ScenarioStates
from app.bot.keyboards import get_scenario_keyboard, get_exit_mode_keyboard
from app.core.models.user import User
from app.core.constants import SCENARIO_LIST
from app.services.scenario_service import ScenarioService
from app.services.limit_service import LimitService
from app.services.user_service import UserService

router = Router()


@router.message(F.text == "🎭 Ситуации в Испании")
async def show_scenarios(message: Message, state: FSMContext, db_user: User) -> None:
    if not db_user.is_onboarded:
        await message.answer("❌ Сначала пройди /start для настройки бота.")
        return

    await state.set_state(ScenarioStates.choosing_scenario)
    await message.answer(
        "🎭 <b>Ситуации в Испании</b>\n\n"
        "Выбери ситуацию — я сыграю роль собеседника, а ты практикуй реальные диалоги 👇",
        reply_markup=get_scenario_keyboard(),
    )


@router.callback_query(ScenarioStates.choosing_scenario, F.data.startswith("scenario:"))
async def start_scenario(
    callback: CallbackQuery,
    state: FSMContext,
    db_user: User,
    session: AsyncSession,
) -> None:
    scenario_id = callback.data.split(":")[1]
    scenario = next((s for s in SCENARIO_LIST if s["id"] == scenario_id), None)

    if not scenario:
        await callback.answer("Сценарий не найден.")
        return

    limit_service = LimitService(session)
    if not limit_service.can_send_message(db_user):
        await callback.message.answer(limit_service.get_limit_exceeded_text(db_user))
        await callback.answer()
        return

    user_service = UserService(session)
    await user_service.increment_message_count(db_user)

    await state.update_data(scenario_id=scenario_id, scenario_title=scenario["title"])
    await state.set_state(ScenarioStates.active)

    await callback.message.edit_text(
        f"{scenario['emoji']} <b>{scenario['title']}</b>\n\n"
        f"{scenario['description']}\n\n"
        "Сценарий начинается..."
    )

    scenario_service = ScenarioService(session)
    intro = await scenario_service.start_scenario(db_user, scenario_id, scenario["title"])

    await callback.message.answer(intro, reply_markup=get_exit_mode_keyboard())
    await callback.answer()


@router.message(ScenarioStates.active)
async def handle_scenario_message(
    message: Message,
    state: FSMContext,
    db_user: User,
    session: AsyncSession,
) -> None:
    if message.text == "🏠 В главное меню":
        return

    data = await state.get_data()
    scenario_id = data.get("scenario_id")

    if not scenario_id:
        await message.answer("Ошибка: сценарий не найден.")
        await state.clear()
        return

    limit_service = LimitService(session)
    if not limit_service.can_send_message(db_user):
        await message.answer(limit_service.get_limit_exceeded_text(db_user))
        await state.clear()
        return

    user_service = UserService(session)
    await user_service.increment_message_count(db_user)

    scenario_service = ScenarioService(session)
    typing_action = message.bot.send_chat_action(message.chat.id, "typing")
    await typing_action

    response = await scenario_service.process_scenario_message(db_user, message.text, scenario_id)

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

    role_reply = response.get("role_reply", "...")
    parts.append(f"🇪🇸 {role_reply}")

    if response.get("role_reply_translation"):
        parts.append(f"<i>({response['role_reply_translation']})</i>")

    if response.get("useful_phrase"):
        parts.append(f"\n💡 <b>Полезная фраза:</b> {response['useful_phrase']}")

    await message.answer("\n".join(parts))
