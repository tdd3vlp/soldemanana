from pydantic import BaseModel, ConfigDict


class CorrectionItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    original: str = ""
    corrected: str = ""
    error_type: str = ""


class ConversationLLMResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    unclear: bool = False
    has_errors: bool = False
    corrections: list[CorrectionItem] = []
    natural_variant: str | None = None
    reply: str = ""
    reply_translation: str | None = None


class MemorySummaryLLMResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    memory_summary: str = ""
    mistake_summary: str = ""
    active_topic: str | None = None
    learned_vocabulary: str | None = None
    recent_goals: str | None = None
