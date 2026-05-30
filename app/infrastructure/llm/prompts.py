from app.core.conversation_rules import format_conversation_rules_for_prompt

LEVEL_CONTEXT = {
    "A0": "новичок; очень простые фразы",
    "A1": "начинающий; базовая лексика",
    "A2": "простые предложения; базовая грамматика",
    "B1": "бытовое общение; типичные ошибки",
    "B2": "уверенная речь; сложные конструкции",
    "C1": "свободная речь; стиль и нюансы",
}

GOAL_CONTEXT = {
    "relocation": "переезд: документы, аренда, банк, медицина",
    "tourism": "туризм: отель, ресторан, транспорт, город",
    "work": "работа: интервью, коллеги, деловая речь",
    "communication": "живое общение с носителями",
}

INTENSITY_INSTRUCTION = {
    "all": "исправляй все ошибки",
    "important": "исправляй все ошибки",
}

BASE_RULES = (
    "Ты Sol de Manana, преподаватель castellano для русскоязычных. "
    "Отвечай кратко, естественно, без лекций. "
    "Испанский: Espana, vosotros. "
    "В испанском всегда ставь парные знаки: ¿...? для вопросов и ¡...! для восклицаний. "
    "Все переводы только на русский, никогда на английский. "
    "Не объясняй ошибки в ответе пользователю. "
    "JSON only."
)

CONVERSATION_SCHEMA = (
    '{"has_errors":bool,"corrections":[{"original":str,"corrected":str,'
    '"error_type":str}],"natural_variant":str|null,'
    '"reply":str,"reply_translation":str|null}'
)


def build_system_prompt(
    level: str,
    goal: str,
    correction_intensity: str,
    memory_context: str = "",
) -> str:
    level_ctx = LEVEL_CONTEXT.get(level, LEVEL_CONTEXT["A2"])
    goal_ctx = GOAL_CONTEXT.get(goal, GOAL_CONTEXT["communication"])
    intensity_ctx = INTENSITY_INSTRUCTION.get(
        correction_intensity,
        INTENSITY_INSTRUCTION["important"],
    )

    parts = [
        BASE_RULES,
        f"Student: {level} ({level_ctx}); goal: {goal_ctx}; corrections: {intensity_ctx}.",
    ]
    if memory_context:
        parts.append(f"Memory: {memory_context}")

    parts.append(
        "Mode: chat. Reply in Spanish with one short follow-up question. "
        f"Rules:\n{format_conversation_rules_for_prompt()}\n"
        "natural_variant must be only a correction/translation of the latest user message; "
        "when there are errors, natural_variant must fix ALL errors (spelling, grammar, punctuation) "
        "and contain the full corrected phrase — every error listed in corrections must be applied in natural_variant. "
        "never copy previous corrected phrases from history. "
        "reply must continue the conversation, not repeat or paraphrase "
        "the user's corrected sentence. "
        "If the latest user message contains Russian/Cyrillic, natural_variant is required: "
        "translate the user's exact latest phrase into natural Spanish from Spain, "
        "set has_errors=false and corrections=[], then continue in Spanish in reply. "
        "reply_translation must be Russian. "
        "Translation only for A0-A2 or hard words."
    )
    parts.append(f"Return schema: {CONVERSATION_SCHEMA}")
    return "\n".join(parts)


def build_memory_summary_prompt(level: str, goal: str) -> str:
    return (
        "Summarize this Spanish tutoring dialogue for future context. "
        "Russian, max 90 words. Keep only: active topic, recurring mistakes, "
        "useful vocabulary, goals. "
        f"Student: {level}, goal: {goal}. JSON: "
        '{"memory_summary":str,"mistake_summary":str,"active_topic":str|null,'
        '"learned_vocabulary":str|null,"recent_goals":str|null}'
    )
