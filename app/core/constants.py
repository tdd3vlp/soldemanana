from app.core.enums import SubscriptionTier

DAILY_MESSAGE_LIMITS: dict[SubscriptionTier, int | None] = {
    SubscriptionTier.FREE: 10,
    SubscriptionTier.BASIC: 50,
    SubscriptionTier.PREMIUM: None,
}

LEVEL_LABELS: dict[str, str] = {
    "A0": "A0 — Полный ноль 🌱",
    "A1": "A1 — Начинающий",
    "A2": "A2 — Элементарный",
    "B1": "B1 — Средний",
    "B2": "B2 — Выше среднего",
    "C1": "C1 — Продвинутый",
}

GOAL_LABELS: dict[str, str] = {
    "relocation": "🏠 Переезд в Испанию",
    "tourism": "✈️ Туризм и путешествия",
    "work": "💼 Работа в Испании",
    "communication": "🗣️ Общение с носителями",
}

GOAL_DESCRIPTIONS: dict[str, str] = {
    "relocation": "документы, аренда, банк, медицина, школа",
    "tourism": "отель, ресторан, транспорт, шопинг, экскурсии",
    "work": "интервью, коллеги, деловое общение, переговоры",
    "communication": "повседневные разговоры, дружба, культура",
}

VOCABULARY_FEATURE_TIER = "premium"

THROTTLE_RATE = 1.0
THROTTLE_KEY_PREFIX = "throttle"
