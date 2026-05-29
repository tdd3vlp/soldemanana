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
    "important": "исправляй только важные ошибки",
    "none": "не исправляй, просто отвечай",
}

BASE_RULES = (
    "Ты Sol de Manana, преподаватель castellano для русскоязычных. "
    "Отвечай кратко, естественно, без лекций. "
    "Испанский: Espana, vosotros. "
    "Объяснения ошибок на русском. "
    "Не больше 2 исправлений за раз, кроме режима correction. "
    "JSON only."
)

JSON_SCHEMAS = {
    "conversation": (
        '{"has_errors":bool,"corrections":[{"original":str,"corrected":str,'
        '"error_type":str,"explanation":str}],"natural_variant":str|null,'
        '"reply":str,"reply_translation":str|null}'
    ),
    "correction": (
        '{"has_errors":bool,"corrections":[{"original":str,"corrected":str,'
        '"error_type":str,"explanation":str}],"natural_variant":str|null,'
        '"full_corrected":str,"tip":str|null,"example_sentences":[str]}'
    ),
    "scenarios": (
        '{"has_errors":bool,"corrections":[{"original":str,"corrected":str,'
        '"error_type":str,"explanation":str}],"role_reply":str,'
        '"role_reply_translation":str|null,"useful_phrase":str|null}'
    ),
    "grammar": (
        '{"is_correct":bool,"feedback":str,"correct_answer":str|null,'
        '"explanation":str|null,"next_exercise":str}'
    ),
}


def build_system_prompt(
    level: str,
    goal: str,
    correction_intensity: str,
    mode: str,
    extra_context: str = "",
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
    if extra_context:
        parts.append(extra_context)

    if mode == "conversation":
        parts.append(
            "Mode: chat. Reply in Spanish with one short follow-up question. "
            "Translation only for A0-A2 or hard words."
        )
    elif mode == "correction":
        parts.append(
            "Mode: correction. Analyze the user's phrase. Keep each explanation to 1 sentence. "
            "Give max 2 examples."
        )
    elif mode == "scenarios":
        parts.append(
            "Mode: roleplay. Stay in character. Reply 1-3 sentences. "
            "Correct briefly after reading the user's line."
        )
    elif mode == "grammar":
        parts.append(
            "Mode: grammar check. Check the answer to the current exercise. "
            "Explain only the rule needed for this answer."
        )

    parts.append(f"Return schema: {JSON_SCHEMAS[mode]}")
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


def build_scenario_context(scenario_id: str, scenario_title: str) -> str:
    contexts = {
        "restaurant": "Role: hurried but friendly waiter in Madrid; menu del dia, wine.",
        "pharmacy": "Role: pharmacist; ask symptoms, mention receta medica if needed.",
        "town_hall": "Role: ayuntamiento clerk; formal, empadronamiento/documents.",
        "doctor": "Role: medico de cabecera; symptoms, basic advice, next steps.",
        "market": "Role: market seller; lively, practical, mild bargaining.",
        "transport": "Role: station/metro worker; routes, tickets, schedule.",
        "bank": "Role: bank manager; account/card/documents.",
        "landlord": "Role: landlord; rent, fianza, bills, contract.",
        "police": "Role: police/NIE office; formal, documents, procedure.",
        "neighbors": "Role: friendly neighbor; origin, district, local life.",
    }
    return contexts.get(scenario_id, f"Roleplay situation: {scenario_title}.")


GRAMMAR_EXERCISES = {
    "ser_estar": {
        "explanation": (
            "Ser = постоянное/идентичность: Soy de Rusia, es medico. "
            "Estar = состояние/место: estoy cansado, esta en Madrid. "
            "Ловушка: es aburrido = он скучный, "
            "esta aburrido = ему скучно."
        ),
        "exercise": (
            "Вставь ser или estar: "
            "Hoy ___ contento porque mi ciudad ___ muy bonita."
        ),
        "hint": (
            "Сначала реши: это состояние сейчас "
            "или постоянная характеристика."
        ),
    },
    "past_tenses": {
        "explanation": (
            "Indefinido = завершенное действие: ayer fui. "
            "Imperfecto = фон/привычка: cuando era nino, vivia..."
        ),
        "exercise": (
            "Поставь формы: Cuando (ser/yo) pequeno, "
            "(vivir/yo) en un pueblo. Un dia (ver/yo) algo raro."
        ),
        "hint": (
            "Фон обычно imperfecto, "
            "разовое событие обычно indefinido."
        ),
    },
    "subjuntivo": {
        "explanation": (
            "Subjuntivo нужен после желания, сомнения, эмоции: "
            "quiero que vengas, dudo que sea verdad."
        ),
        "exercise": "Выбери: Espero que manana (hace/haga) buen tiempo.",
        "hint": "После espero que обычно нужен subjuntivo.",
    },
    "imperativo": {
        "explanation": (
            "Imperativo: habla, come, ven. "
            "С местоимениями: damelo. Отрицание: no hables."
        ),
        "exercise": (
            "Попроси друга на tu закрыть дверь "
            "и принести воду. Используй imperativo."
        ),
        "hint": "Для tu: cerrar -> cierra, traer -> trae.",
    },
    "pronouns": {
        "explanation": (
            "Прямые: lo/la/los/las. Косвенные: le/les. "
            "Порядок: se/me/te + lo/la."
        ),
        "exercise": (
            "Замени существительные: "
            "Doy el regalo a mi madre -> ___ ___ doy."
        ),
        "hint": "A mi madre = le, el regalo = lo, но le + lo превращается в se lo.",
    },
}


def get_grammar_intro(topic_id: str, topic_title: str, level: str) -> dict:
    topic = GRAMMAR_EXERCISES.get(
        topic_id,
        {
            "explanation": (
                f"Тема: {topic_title}. "
                "Сфокусируйся на одном простом "
                "правиле за раз."
            ),
            "exercise": (
                f"Составь одно предложение "
                f"по теме {topic_title}."
            ),
            "hint": None,
        },
    )
    hint = topic.get("hint") if level in {"A0", "A1", "A2"} else None
    return {"explanation": topic["explanation"], "exercise": topic["exercise"], "hint": hint}


def build_grammar_check_prompt(
    topic_id: str,
    topic_title: str,
    level: str,
    exercise: str | None = None,
) -> str:
    intro = get_grammar_intro(topic_id, topic_title, level)
    current_exercise = exercise or intro["exercise"]
    return build_system_prompt(
        level=level,
        goal="communication",
        correction_intensity="important",
        mode="grammar",
        extra_context=f"Topic: {topic_title}. Exercise: {current_exercise}",
    )


def build_grammar_exercise_prompt(topic_id: str, topic_title: str, level: str) -> str:
    intro = get_grammar_intro(topic_id, topic_title, level)
    return (
        f"Topic: {topic_title}\nExplanation: {intro['explanation']}\n"
        f"Exercise: {intro['exercise']}\nReturn JSON with explanation, exercise, hint."
    )
