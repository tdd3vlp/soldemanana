import re
from html import escape
from uuid import uuid4

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import get_exit_mode_keyboard, get_reply_translation_keyboard
from app.bot.states import ConversationStates
from app.core.conversation_rules import (
    SHORT_ANSWER_TEXT,
    UNCLEAR_MESSAGE_TEXT,
    UNSUPPORTED_LANGUAGE_TEXT,
)
from app.core.models.user import User
from app.services.conversation_service import ConversationService
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

    await enter_conversation(message, state, db_user, is_new_user=False)


async def enter_conversation(
    message: Message,
    state: FSMContext,
    db_user: User,
    is_new_user: bool = False,
) -> None:
    await state.set_state(ConversationStates.active)

    base_text = (
        "🗣️ <b>Режим свободного разговора</b>\n\n"
        "Пиши мне на испанском — о чём угодно! "
        "Я буду отвечать и помогать формулировать фразы естественно.\n\n"
    )

    if is_new_user:
        starter_phrases = [
            "🇪🇸 <b>Hola, ¿cómo estás?</b>\n<i>(Привет, как дела?)</i>",
            "🇪🇸 <b>Me llamo [твоё имя]</b>\n<i>(Меня зовут [твоё имя])</i>",
            "🇪🇸 <b>Estoy aprendiendo español</b>\n<i>(Я учу испанский)</i>",
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
    if not message.text:
        await message.answer("Пиши текстом — фото и стикеры я пока не понимаю.")
        return

    if _is_likely_gibberish(message.text):
        await message.answer(UNCLEAR_MESSAGE_TEXT)
        return

    if _is_likely_english(message.text):
        await message.answer(UNSUPPORTED_LANGUAGE_TEXT)
        return

    if _is_too_short_spanish_answer(message.text):
        await message.answer(SHORT_ANSWER_TEXT)
        return

    conversation_service = ConversationService(session)
    typing_action = message.bot.send_chat_action(message.chat.id, "typing")
    await typing_action

    response = await conversation_service.process_message(db_user, message.text)

    if response.get("error"):
        await message.answer(response.get("message", "Ошибка обработки."))
        return

    user_service = UserService(session)
    await user_service.increment_message_count(db_user)

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

    bot_reply = response.get("reply", "")
    if bot_reply:
        parts.append(f"🇪🇸 {escape(bot_reply)}")

    reply_markup = None
    reply_translation = response.get("reply_translation")
    if reply_translation:
        token = uuid4().hex[:12]
        state_data = await state.get_data()
        translations = state_data.get("conversation_translations", {})
        if not isinstance(translations, dict):
            translations = {}
        translations[token] = str(reply_translation)
        translations = dict(list(translations.items())[-20:])
        await state.update_data(conversation_translations=translations)
        reply_markup = get_reply_translation_keyboard(token)

    await message.answer("\n".join(parts), reply_markup=reply_markup)


@router.callback_query(ConversationStates.active, F.data.startswith("conv:translate:"))
async def show_reply_translation(callback: CallbackQuery, state: FSMContext) -> None:
    token = (callback.data or "").removeprefix("conv:translate:")
    state_data = await state.get_data()
    translations = state_data.get("conversation_translations", {})
    if not isinstance(translations, dict):
        translations = {}

    translation = translations.pop(token, None)
    if not translation:
        await callback.answer("Перевод уже недоступен")
        return

    await state.update_data(conversation_translations=translations)
    message = callback.message
    if not message:
        await callback.answer()
        return

    current_text = message.html_text or message.text or ""
    await message.edit_text(f"{current_text}\n<i>({escape(str(translation))})</i>")
    await callback.answer()


def _contains_cyrillic(text: str | None) -> bool:
    return bool(text and any("а" <= char.lower() <= "я" or char.lower() == "ё" for char in text))


_RUSSIAN_VOWELS = frozenset("аеёиоуыэюя")


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

    # Two or more Cyrillic words with Russian vowels → valid Russian text
    cyrillic_words_with_vowels = sum(
        1 for w in words
        if len(w) >= 4 and re.fullmatch(r"[а-яё]+", w) and any(c in _RUSSIAN_VOWELS for c in w)
    )
    if cyrillic_words_with_vowels >= 2:
        return False

    bad_words = sum(_is_gibberish_word(word) for word in words)
    return bad_words >= 2 or (len(words) == 1 and bad_words == 1)


def _is_gibberish_word(word: str) -> bool:
    if len(word) < 4:
        return False

    if re.fullmatch(r"[a-z]+", word):
        vowels = sum(char in "aeiouy" for char in word)
        return vowels / len(word) < 0.2

    if re.fullmatch(r"[а-яё]+", word):
        return _looks_like_wrong_keyboard_layout_word(word) or _looks_like_cyrillic_mash(word)

    return False


def _looks_like_cyrillic_mash(word: str) -> bool:
    if len(word) < 5:
        return False

    russian_vowels = sum(char in "аеёиоуыэюя" for char in word)
    if russian_vowels / len(word) < 0.2:
        return True

    return len(set(word)) <= 3 and word[:2] == word[-2:]


def _looks_like_wrong_keyboard_layout_word(word: str) -> bool:
    keyboard_map = str.maketrans(
        {
            "й": "q",
            "ц": "w",
            "у": "e",
            "к": "r",
            "е": "t",
            "н": "y",
            "г": "u",
            "ш": "i",
            "щ": "o",
            "з": "p",
            "х": "[",
            "ъ": "]",
            "ф": "a",
            "ы": "s",
            "в": "d",
            "а": "f",
            "п": "g",
            "р": "h",
            "о": "j",
            "л": "k",
            "д": "l",
            "ж": ";",
            "э": "'",
            "я": "z",
            "ч": "x",
            "с": "c",
            "м": "v",
            "и": "b",
            "т": "n",
            "ь": "m",
            "б": ",",
            "ю": ".",
            "ё": "`",
        }
    )
    latin = word.translate(keyboard_map)
    if not re.fullmatch(r"[a-z]+", latin):
        return False

    vowels = sum(char in "aeiouy" for char in latin)
    return vowels >= 2 and vowels / len(latin) >= 0.25


def _is_likely_english(text: str | None) -> bool:
    if not text or _contains_cyrillic(text):
        return False
    if any(char in text.lower() for char in "áéíóúüñ¿¡"):
        return False

    if _looks_like_english_title_or_name(text):
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
        "ok",
        "okay",
        "overall",
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
        "yes",
    }
    marker_count = sum(word in english_markers for word in words)
    return marker_count >= 2 or (len(words) <= 3 and marker_count >= 1)


def _looks_like_english_title_or_name(text: str) -> bool:
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text.strip())
    if len(words) < 2 or len(words) > 8:
        return False

    lower_words = [word.lower() for word in words]
    title_helpers = {"a", "an", "and", "of", "the", "to"}
    capitalized = [
        word
        for word in words
        if word[0].isupper() and word.lower() not in title_helpers
    ]
    if not capitalized:
        return False

    non_title_words = [
        word
        for word in words
        if not word[0].isupper() and word.lower() not in title_helpers
    ]
    if non_title_words:
        return False

    sentence_markers = {"am", "are", "can", "do", "does", "how", "what", "where", "you"}
    return not any(word in sentence_markers for word in lower_words)


def _is_too_short_spanish_answer(text: str | None) -> bool:
    if not text or _contains_cyrillic(text):
        return False
    if _looks_like_english_title_or_name(text):
        return False

    words = re.findall(r"[a-záéíóúüñ]+", text.lower())
    if not words or len(words) > 3:
        return False
    if any(word in _SPANISH_QUESTION_WORDS for word in words) or "por qué" in text.lower():
        return False
    if all(word in _SPANISH_ALLOWED_SHORT_PHRASE_WORDS for word in words):
        return False
    if len(words) == 1:
        return True

    insufficient_words = {
        "bien",
        "claro",
        "comida",
        "encanta",
        "encantan",
        "favorita",
        "favorito",
        "gusta",
        "gustan",
        "mal",
        "mucho",
        "muy",
        "no",
        "poco",
        "regular",
        "si",
        "sí",
        "tambien",
        "también",
        "vale",
    }
    filler_words = {
        "a", "al", "de", "del", "el", "en", "la", "las", "lo", "los",
        "me", "mi", "sobre", "un", "una",
    }
    fragment_starters = {
        "a", "al", "de", "del", "el", "en", "la", "las", "lo", "los",
        "sobre", "un", "una",
    }
    if words[0] in fragment_starters:
        return True

    meaningful_words = [word for word in words if word not in filler_words]
    return not meaningful_words or all(word in insufficient_words for word in meaningful_words)


_SPANISH_QUESTION_WORDS = {
    "adonde",
    "cómo",
    "como",
    "cuál",
    "cual",
    "cuándo",
    "cuando",
    "cuánto",
    "cuanto",
    "dónde",
    "donde",
    "qué",
    "que",
    "quién",
    "quien",
}


_SPANISH_ALLOWED_SHORT_PHRASE_WORDS = {
    "adios",
    "adiós",
    "buenas",
    "buenos",
    "chao",
    "dias",
    "días",
    "favor",
    "gracias",
    "hola",
    "lo",
    "noches",
    "no",
    "perdon",
    "perdón",
    "perdona",
    "perdone",
    "por",
    "si",
    "sí",
    "tardes",
}


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
        if not replacement:
            replacement = f"<s>{escaped_original}</s> {escape(str(corrected))}"
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


_LEADING_PUNCTUATION = frozenset("¡¿")


def _strip_leading_punctuation(word: str) -> str:
    i = 0
    while i < len(word) and word[i] in _LEADING_PUNCTUATION:
        i += 1
    return word[i:]


def _format_changed_word(original: str, corrected: str) -> str:
    original_core, original_suffix = _split_trailing_punctuation(original)
    corrected_core, corrected_suffix = _split_trailing_punctuation(corrected)

    if original_core == corrected_core:
        return escape(corrected)

    # Only leading punctuation (¡/¿) was added, word content is the same — no strikethrough needed
    if _strip_leading_punctuation(original_core) == _strip_leading_punctuation(corrected_core):
        return escape(corrected)

    if original_suffix == corrected_suffix and original_core and corrected_core:
        return f"<s>{escape(original_core)}</s> {escape(corrected_core + corrected_suffix)}"

    return f"<s>{escape(original)}</s> {escape(corrected)}"


def _split_trailing_punctuation(word: str) -> tuple[str, str]:
    punctuation = ".,!?;:"
    index = len(word)
    while index > 0 and word[index - 1] in punctuation:
        index -= 1
    return word[:index], word[index:]
