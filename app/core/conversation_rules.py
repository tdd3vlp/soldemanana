from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationRule:
    code: str
    text: str


BOT_GUARD_RULES = (
    ConversationRule(
        "allowed_languages",
        (
            "If the user writes in a language other than Spanish or Russian, "
            "ask them to write in Spanish or Russian."
        ),
    ),
    ConversationRule(
        "gibberish",
        (
            "Treat meaningless text or wrong keyboard layout text as unclear input "
            "and ask the user to repeat what they meant."
        ),
    ),
    ConversationRule(
        "public_names",
        (
            "Song titles, band names, public brands and similar English proper names "
            "are allowed and must not be treated as wrong-language input."
        ),
    ),
    ConversationRule(
        "short_answers",
        (
            "Short user answers are handled before the LLM: ask for a fuller Spanish sentence, "
            "except greetings, farewells and polite phrases."
        ),
    ),
    ConversationRule(
        "global_commands",
        "/start and /subscribe must work from any dialogue state.",
    ),
)


LLM_RESPONSE_RULES = (
    ConversationRule(
        "latest_message_only",
        (
            "Correct all errors from the latest user message only. "
            "Never include old corrections from history."
        ),
    ),
    ConversationRule(
        "russian_to_spanish",
        (
            "If the latest user message is Russian/Cyrillic, translate it into "
            "natural Spanish from Spain, do not mark it as an error, then continue the dialogue."
        ),
    ),
    ConversationRule(
        "spanish_punctuation",
        "Track important Spanish punctuation, including paired ¿...? and ¡...! marks.",
    ),
    ConversationRule(
        "spanish_orthography",
        (
            "Correct Spanish orthography using grammar, vocabulary and context, including "
            "written accents and diacritics (á, é, í, ó, ú, ü, ñ). Treat missing or wrong "
            "diacritics as errors when standard Spanish requires them. "
            "Pay special attention to words that change meaning with an accent: "
            "si→sí (affirmative yes), mi→mí (pronoun me), tu→tú (pronoun you), "
            "el→él (pronoun he), mas→más (more), se→sé (I know), te→té (tea)."
        ),
    ),
    ConversationRule(
        "natural_reply",
        (
            "Replies must be short, natural and varied. Continue the topic like a person; "
            "do not drill into tiny details when a broader language-practice follow-up is better."
        ),
    ),
    ConversationRule(
        "no_explanations",
        "Do not explain mistakes in chat responses; show only the correction/variant and continue.",
    ),
    ConversationRule(
        "polished_variant",
        (
            "If the user makes many errors, natural_variant should be the logical phrase "
            "they probably meant, polished into a well-formed grammatical sentence."
        ),
    ),
)

UNCLEAR_MESSAGE_TEXT = (
    "Не совсем понял, что ты хотел сказать. Напиши фразу ещё раз "
    "на испанском или по-русски, если не знаешь, как сказать это по-испански."
)

UNSUPPORTED_LANGUAGE_TEXT = (
    "Пиши, пожалуйста, на испанском или русском. Если не знаешь, как сказать фразу "
    "по-испански, напиши её по-русски — я переведу и помогу продолжить."
)

SHORT_ANSWER_TEXT = (
    "Попробуй ответить чуть подробнее на испанском: одной полной фразой. "
    "Так ты лучше тренируешь грамматику и активную лексику."
)


def format_conversation_rules_for_prompt() -> str:
    return "\n".join(
        f"{index}. {rule.text}" for index, rule in enumerate(LLM_RESPONSE_RULES, 1)
    )
