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
    '{"unclear":bool,"has_errors":bool,"corrections":[{"original":str,"corrected":str,'
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
        "Mode: chat. "
        "If the user input is indecipherable (keyboard mashing, random characters), "
        "set unclear=true and all other fields to empty/default values. "
        f"Rules:\n{format_conversation_rules_for_prompt()}\n"
        "When there are errors, natural_variant must fix ALL of them and contain the full corrected phrase. "
        "When the message is Russian or mixed Russian-Spanish, natural_variant is required: "
        "translate the entire message into natural Spanish from Spain, set has_errors=false and corrections=[]. "
        "reply_translation must be Russian. Always provide reply_translation."
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
