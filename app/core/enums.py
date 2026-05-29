from enum import StrEnum


class LanguageLevel(StrEnum):
    A0 = "A0"
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"


class LearningGoal(StrEnum):
    RELOCATION = "relocation"
    TOURISM = "tourism"
    WORK = "work"
    COMMUNICATION = "communication"


class BotMode(StrEnum):
    CONVERSATION = "conversation"
    CORRECTION = "correction"
    SCENARIOS = "scenarios"
    GRAMMAR = "grammar"


class CorrectionIntensity(StrEnum):
    ALL = "all"
    IMPORTANT = "important"
    NONE = "none"


class SubscriptionTier(StrEnum):
    FREE = "free"
    PREMIUM = "premium"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class GrammarTopic(StrEnum):
    SER_ESTAR = "ser_estar"
    INDICATIVO = "indicativo"
    SUBJUNTIVO = "subjuntivo"
    IMPERATIVO = "imperativo"
    PRONOUNS = "pronouns"
    ARTICLES = "articles"
    PREPOSITIONS = "prepositions"
    PAST_TENSES = "past_tenses"
    FUTURE = "future"
    CONDITIONAL = "conditional"
