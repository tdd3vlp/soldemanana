from types import SimpleNamespace

from app.services.conversation_service import ConversationService


class FakeUsageService:
    def __init__(self) -> None:
        self.records = []

    async def record(self, user, mode, meta) -> None:
        self.records.append((user, mode, meta))


def test_keep_current_message_corrections_drops_history_items() -> None:
    response = {
        "has_errors": True,
        "corrections": [
            {
                "original": "Rusía",
                "corrected": "Rusia",
                "error_type": "accent",
            },
            {
                "original": "comó",
                "corrected": "cómo",
                "error_type": "accent",
            },
        ],
    }

    ConversationService._keep_current_message_corrections(response, "Estoy de Rusía, Moscú.")

    assert response["has_errors"] is True
    assert response["corrections"] == [
        {
            "original": "Rusía",
            "corrected": "Rusia",
            "error_type": "accent",
        }
    ]


def test_keep_current_message_corrections_clears_has_errors_when_only_history_items() -> None:
    response = {
        "has_errors": True,
        "corrections": [
            {
                "original": "comó",
                "corrected": "cómo",
                "error_type": "accent",
            },
        ],
    }

    ConversationService._keep_current_message_corrections(response, "Estoy de Rusia, Moscú.")

    assert response["has_errors"] is False
    assert response["corrections"] == []


def test_remove_repeated_correction_reply() -> None:
    response = {
        "natural_variant": "Estoy de Rusia, pero quiero ir a España.",
        "reply": "Estoy de Rusia, pero quiero ir a España.",
        "reply_translation": "Я из России, но хочу поехать в Испанию.",
    }

    ConversationService._remove_repeated_correction_reply(response)

    assert response["reply"] == ""
    assert response["reply_translation"] is None


def test_ensure_conversation_reply_adds_fallback_after_repeated_reply_removed() -> None:
    response = {
        "natural_variant": "Hola, ¿cómo estás?",
        "reply": "Hola, ¿cómo estás?",
        "reply_translation": "Привет, как дела?",
    }

    ConversationService._remove_repeated_correction_reply(response)
    ConversationService._ensure_conversation_reply(response)

    assert response["reply"] == "Estoy bien, gracias. ¿Qué tal tu día?"
    assert response["reply_translation"] == "Я хорошо, спасибо. Как проходит твой день?"


def test_ensure_natural_variant_reconstructs_question_from_word_corrections() -> None:
    response = {
        "has_errors": True,
        "corrections": [
            {"original": "coma", "corrected": "cómo"},
            {"original": "esta", "corrected": "estás"},
        ],
        "natural_variant": None,
    }

    ConversationService._ensure_natural_variant(response, "Hola, coma esta")

    assert response["natural_variant"] == "Hola, ¿cómo estás?"


def test_ensure_punctuation_natural_variant_adds_opening_exclamation() -> None:
    response = {"has_errors": False, "corrections": [], "natural_variant": None}

    ConversationService._ensure_punctuation_natural_variant(response, "Bien, gracias!")

    assert response["has_errors"] is True
    assert response["natural_variant"] == "¡Bien, gracias!"
    assert response["corrections"] == [
        {
            "original": "Bien, gracias!",
            "corrected": "¡Bien, gracias!",
            "error_type": "punctuation",
        }
    ]


def test_normalize_response_spanish_punctuation() -> None:
    response = {
        "natural_variant": "Mi día es perfecto, y tú?",
        "reply": "Estoy bien! Que has hecho hoy?",
        "corrections": [{"original": "tu?", "corrected": "tú?"}],
    }

    ConversationService._normalize_response_spanish_punctuation(response)

    assert response["natural_variant"] == "Mi día es perfecto, ¿y tú?"
    assert response["reply"] == "¡Estoy bien! ¿Que has hecho hoy?"
    assert response["corrections"][0]["corrected"] == "¿tú?"


def test_normalize_response_spanish_punctuation_infers_question_words() -> None:
    response = {
        "natural_variant": "Hola, cómo estás",
        "reply": "Qué has hecho hoy",
        "corrections": [{"original": "coma", "corrected": "cómo"}],
    }

    ConversationService._normalize_response_spanish_punctuation(response)

    assert response["natural_variant"] == "Hola, ¿cómo estás?"
    assert response["reply"] == "¿Qué has hecho hoy?"
    assert response["corrections"][0]["corrected"] == "cómo"


def test_normalize_response_spanish_punctuation_closes_opening_marks() -> None:
    response = {
        "natural_variant": "Hola, ¿cómo está",
        "reply": "¡Estoy bien",
        "corrections": [{"original": "coma esta", "corrected": "¿cómo está"}],
    }

    ConversationService._normalize_response_spanish_punctuation(response)

    assert response["natural_variant"] == "Hola, ¿cómo está?"
    assert response["reply"] == "¡Estoy bien!"
    assert response["corrections"][0]["corrected"] == "¿cómo está?"


def test_remove_stale_natural_variant_from_history_corrected_text() -> None:
    response = {"natural_variant": "Mi día es perfecto, ¿y tú?"}
    history = [
        SimpleNamespace(
            text="Mi dia es perfecta, y tu?",
            corrected_text="Mi día es perfecto, ¿y tú?",
        )
    ]

    ConversationService._remove_stale_natural_variant(response, history)

    assert response["natural_variant"] is None


async def test_ensure_russian_input_translation_fills_missing_natural_variant(monkeypatch) -> None:
    service = ConversationService.__new__(ConversationService)
    service.usage_service = FakeUsageService()
    user = SimpleNamespace(id=1)
    response = {"natural_variant": None}

    async def fake_complete(*args, **kwargs):
        return {
            "translation": "Quiero ir a España.",
            "_llm_usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

    monkeypatch.setattr("app.services.conversation_service.llm_client.complete", fake_complete)

    await service._ensure_russian_input_translation(response, "Я хочу поехать в Испанию", user)

    assert response["natural_variant"] == "Quiero ir a España."
    assert service.usage_service.records[0][1] == "conversation_translation"


async def test_ensure_russian_input_translation_keeps_existing_natural_variant(monkeypatch) -> None:
    service = ConversationService.__new__(ConversationService)
    service.usage_service = FakeUsageService()
    user = SimpleNamespace(id=1)
    response = {"natural_variant": "Quiero ir a España."}

    async def fake_complete(*args, **kwargs):
        raise AssertionError("translation request should not be called")

    monkeypatch.setattr("app.services.conversation_service.llm_client.complete", fake_complete)

    await service._ensure_russian_input_translation(response, "Я хочу поехать в Испанию", user)

    assert response["natural_variant"] == "Quiero ir a España."
    assert service.usage_service.records == []


async def test_ensure_russian_input_translation_replaces_cyrillic_natural_variant(
    monkeypatch,
) -> None:
    service = ConversationService.__new__(ConversationService)
    service.usage_service = FakeUsageService()
    user = SimpleNamespace(id=1)
    response = {"natural_variant": "Ничего"}

    async def fake_complete(*args, **kwargs):
        return {
            "translation": "Nada.",
            "_llm_usage": {"prompt_tokens": 10, "completion_tokens": 3, "total_tokens": 13},
        }

    monkeypatch.setattr("app.services.conversation_service.llm_client.complete", fake_complete)

    await service._ensure_russian_input_translation(response, "Ничего", user)

    assert response["natural_variant"] == "Nada."
