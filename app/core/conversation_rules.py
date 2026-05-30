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
        "correct_spanish",
        (
            "Correct all errors in the latest Spanish message: spelling, grammar, "
            "punctuation, accents, style. Correct only the latest message, never history."
        ),
    ),
    ConversationRule(
        "russian_to_spanish",
        (
            "If the message is Russian, Cyrillic, or a mix of Russian and Spanish, "
            "translate the entire message into natural Spanish from Spain. "
            "Do not mark it as an error."
        ),
    ),
    ConversationRule(
        "other_languages",
        "If the message is in any other language, ask the user to write in Spanish or Russian.",
    ),
    ConversationRule(
        "conversation_goal",
        (
            "Goal: continue the conversation — answer the user's questions, "
            "ask your own questions, concisely correct their Spanish."
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
    "Попробуй ответить подробнее на испанском или русском: одной полной фразой. "
    "Так ты лучше тренируешь грамматику и активную лексику."
)


def format_conversation_rules_for_prompt() -> str:
    return "\n".join(
        f"{index}. {rule.text}" for index, rule in enumerate(LLM_RESPONSE_RULES, 1)
    )
