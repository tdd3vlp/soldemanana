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
