from app.bot.handlers.conversation import _build_inline_corrections


def test_build_inline_corrections_strikes_original_and_inserts_correction() -> None:
    result = _build_inline_corrections(
        "¿Y comó te llamas?",
        [{"original": "comó", "corrected": "cómo"}],
    )

    assert result == "¿Y <s>comó</s> cómo te llamas?"


def test_build_inline_corrections_strikes_only_changed_word_in_phrase() -> None:
    result = _build_inline_corrections(
        "Estoy de Rusia, pero quiero voy a Espana.",
        [{"original": "quiero voy a Espana", "corrected": "quiero ir a España"}],
    )

    assert result == "Estoy de Rusia, pero quiero <s>voy</s> ir a <s>Espana</s> España."


def test_build_inline_corrections_uses_natural_variant_for_missing_correction_items() -> None:
    result = _build_inline_corrections(
        "Estoy de Rusia, pero quiero voy a Espana.",
        [{"original": "voy", "corrected": "ir"}],
        "Estoy de Rusia, pero quiero ir a España.",
    )

    assert result == "Estoy de Rusia, pero quiero <s>voy</s> ir a <s>Espana</s> España."
