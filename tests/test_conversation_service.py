from types import SimpleNamespace

from app.services.conversation_service import ConversationService


def test_keep_current_message_corrections_drops_history_items() -> None:
    response = {
        "has_errors": True,
        "corrections": [
            {
                "original": "Rusía",
                "corrected": "Rusia",
                "error_type": "accent",
                "explanation": "La forma correcta es Rusia.",
            },
            {
                "original": "comó",
                "corrected": "cómo",
                "error_type": "accent",
                "explanation": "Cómo lleva tilde en una pregunta.",
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
            "explanation": "La forma correcta es Rusia.",
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
                "explanation": "Cómo lleva tilde en una pregunta.",
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
