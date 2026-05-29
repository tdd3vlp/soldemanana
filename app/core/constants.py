from app.core.enums import SubscriptionTier

DAILY_MESSAGE_LIMITS: dict[SubscriptionTier, int | None] = {
    SubscriptionTier.FREE: 10,
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

SCENARIO_LIST: list[dict] = [
    {"id": "restaurant", "emoji": "🍽️", "title": "В ресторане", "description": "Заказать еду, спросить счёт, сделать бронь"},
    {"id": "pharmacy", "emoji": "💊", "title": "В аптеке", "description": "Описать симптомы, купить лекарства"},
    {"id": "town_hall", "emoji": "🏛️", "title": "В мэрии (Ayuntamiento)", "description": "Прописка, empadronamiento, документы"},
    {"id": "doctor", "emoji": "👨‍⚕️", "title": "У врача", "description": "Описать самочувствие, понять назначения"},
    {"id": "market", "emoji": "🛒", "title": "На рынке/в магазине", "description": "Спросить цену, торговаться, выбрать товар"},
    {"id": "transport", "emoji": "🚇", "title": "Транспорт", "description": "Купить билет, спросить дорогу, метро"},
    {"id": "bank", "emoji": "🏦", "title": "В банке", "description": "Открыть счёт, разобраться с картой, переводы"},
    {"id": "landlord", "emoji": "🔑", "title": "Разговор с арендодателем", "description": "Аренда квартиры, проблемы, договор"},
    {"id": "police", "emoji": "👮", "title": "В полиции / NIE", "description": "Получить NIE, подать заявление"},
    {"id": "neighbors", "emoji": "👋", "title": "С соседями", "description": "Познакомиться, поговорить, решить вопрос"},
]

GRAMMAR_TOPICS: list[dict] = [
    {"id": "ser_estar", "title": "Ser vs Estar", "description": "Два глагола «быть» — главная путаница для русских"},
    {"id": "indicativo", "title": "Presente de Indicativo", "description": "Настоящее время — основа всего"},
    {"id": "past_tenses", "title": "Прошедшее время", "description": "Pretérito Indefinido vs Imperfecto — когда что использовать"},
    {"id": "subjuntivo", "title": "Subjuntivo", "description": "Сослагательное наклонение — самая сложная тема"},
    {"id": "imperativo", "title": "Imperativo", "description": "Повелительное наклонение — просьбы и команды"},
    {"id": "pronouns", "title": "Местоимения", "description": "Me, te, le, lo, la... — куда ставить и зачем"},
    {"id": "articles", "title": "Артикли", "description": "El, la, los, las, un, una — когда и какой"},
    {"id": "prepositions", "title": "Предлоги", "description": "Por vs Para, en, a, de — самые важные предлоги"},
    {"id": "future", "title": "Будущее время", "description": "Futuro Simple и конструкция ir a + infinitivo"},
    {"id": "conditional", "title": "Условные предложения", "description": "Si + indicativo/subjuntivo — если бы..."},
]

VOCABULARY_FEATURE_TIER = "premium"

THROTTLE_RATE = 1.0
THROTTLE_KEY_PREFIX = "throttle"
