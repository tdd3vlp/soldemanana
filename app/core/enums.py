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


class CorrectionIntensity(StrEnum):
    ALL = "all"
    IMPORTANT = "important"


class SubscriptionTier(StrEnum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"

