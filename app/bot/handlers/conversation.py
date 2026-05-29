import re
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import get_exit_mode_keyboard
from app.bot.states import ConversationStates
from app.core.models.user import User
from app.services.conversation_service import ConversationService
from app.services.limit_service import LimitService
from app.services.user_service import UserService

router = Router()


@router.message(F.text == "🗣️ Свободный разговор")
async def start_conversation(
    message: Message,
    state: FSMContext,
    db_user: User,
    session: AsyncSession,
) -> None:
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
        "Пиши мне на испанском — о чём угодно! "
        "Я буду отвечать, исправлять ошибки и объяснять их.\n\n"
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

    if _is_likely_gibberish(message.text):
        await message.answer(
            "Не совсем понял, что ты хотел сказать. Напиши фразу ещё раз "
            "на испанском или по-русски, если не знаешь, как сказать это по-испански."
        )
        return

    if _is_likely_english(message.text):
        await message.answer(
            "Пиши, пожалуйста, на испанском. Если не знаешь, как сказать фразу "
            "по-испански, напиши её по-русски — я переведу и помогу продолжить."
        )
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
    is_russian_input = _contains_cyrillic(message.text)

    if response.get("has_errors") and response.get("corrections"):
        parts.append(
            _build_inline_corrections(
                message.text,
                response["corrections"],
                response.get("natural_variant"),
            )
        )
        parts.append("")

    if is_russian_input and response.get("natural_variant"):
        parts.append(_build_russian_input_translation(message.text, response["natural_variant"]))
        parts.append("")
    elif response.get("natural_variant"):
        parts.append(
            f"💬 <b>Естественный вариант:</b>\n"
            f"<code>{response['natural_variant']}</code>\n"
        )

    bot_reply = response.get("reply", "")
    if bot_reply:
        parts.append(f"🇪🇸 {bot_reply}")

    if response.get("reply_translation"):
        parts.append(f"<i>({response['reply_translation']})</i>")

    await message.answer("\n".join(parts))


def _contains_cyrillic(text: str | None) -> bool:
    return bool(text and any("а" <= char.lower() <= "я" or char.lower() == "ё" for char in text))


def _is_likely_gibberish(text: str | None) -> bool:
    if not text:
        return False

    normalized = text.strip().lower()
    if re.search(r"(.)\1{3,}", normalized):
        return True

    letters = re.findall(r"[a-zа-яёáéíóúüñ]", normalized)
    digits = re.findall(r"\d", normalized)
    if len(digits) >= 4 and not letters:
        return True

    words = re.findall(r"[a-zа-яёáéíóúüñ]+", normalized)
    if not words:
        return False

    bad_words = sum(_is_gibberish_word(word) for word in words)
    return bad_words >= 2 or (len(words) == 1 and bad_words == 1)


def _is_gibberish_word(word: str) -> bool:
    if len(word) < 5:
        return False

    if re.fullmatch(r"[a-z]+", word):
        vowels = sum(char in "aeiouy" for char in word)
        return vowels / len(word) < 0.2

    return False


def _is_likely_english(text: str | None) -> bool:
    if not text or _contains_cyrillic(text):
        return False
    if any(char in text.lower() for char in "áéíóúüñ¿¡"):
        return False

    words = re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())
    if not words:
        return False

    english_markers = {
        "am",
        "are",
        "but",
        "can",
        "do",
        "does",
        "don't",
        "from",
        "hello",
        "hi",
        "how",
        "i",
        "i'm",
        "is",
        "know",
        "my",
        "need",
        "please",
        "say",
        "thanks",
        "that",
        "the",
        "this",
        "to",
        "want",
        "what",
        "where",
        "with",
        "you",
        "your",
    }
    marker_count = sum(word in english_markers for word in words)
    return marker_count >= 2 or (len(words) <= 3 and marker_count >= 1)


def _build_russian_input_translation(text: str, natural_variant: str) -> str:
    return f"🇷🇺 {escape(text)}\n🇪🇸 <code>{escape(natural_variant)}</code>"


def _build_inline_corrections(
    text: str,
    corrections: list[dict],
    natural_variant: str | None = None,
) -> str:
    if natural_variant:
        diff = _build_inline_replacement(text, natural_variant)
        if diff:
            return diff

    result = escape(text)

    for correction in corrections:
        original = correction.get("original")
        corrected = correction.get("corrected")
        if not original or not corrected:
            continue

        escaped_original = escape(str(original))
        replacement = _build_inline_replacement(str(original), str(corrected))
        result = result.replace(escaped_original, replacement, 1)

    return result


def _build_inline_replacement(original: str, corrected: str) -> str:
    original_words = original.split()
    corrected_words = corrected.split()

    if len(original_words) != len(corrected_words):
        return ""

    parts = []
    for original_word, corrected_word in zip(original_words, corrected_words):
        if original_word == corrected_word:
            parts.append(escape(original_word))
        else:
            parts.append(_format_changed_word(original_word, corrected_word))

    return " ".join(parts)


def _format_changed_word(original: str, corrected: str) -> str:
    original_core, original_suffix = _split_trailing_punctuation(original)
    corrected_core, corrected_suffix = _split_trailing_punctuation(corrected)

    if original_suffix == corrected_suffix and original_core and corrected_core:
        return f"<s>{escape(original_core)}</s> {escape(corrected_core + corrected_suffix)}"

    return f"<s>{escape(original)}</s> {escape(corrected)}"


def _split_trailing_punctuation(word: str) -> tuple[str, str]:
    punctuation = ".,!?;:"
    index = len(word)
    while index > 0 and word[index - 1] in punctuation:
        index -= 1
    return word[:index], word[index:]
