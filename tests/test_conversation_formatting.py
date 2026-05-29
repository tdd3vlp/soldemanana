from app.bot.handlers.conversation import (
    _build_inline_corrections,
    _build_russian_input_translation,
    _contains_cyrillic,
    _is_likely_english,
    _is_likely_gibberish,
)


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


def test_contains_cyrillic_detects_russian_input() -> None:
    assert _contains_cyrillic("Я хочу сказать это по-испански") is True
    assert _contains_cyrillic("Estoy aprendiendo español") is False


def test_build_russian_input_translation() -> None:
    result = _build_russian_input_translation(
        "Я хочу поехать в Испанию",
        "Quiero ir a España.",
    )

    assert result == "🇷🇺 Я хочу поехать в Испанию\n🇪🇸 <code>Quiero ir a España.</code>"


def test_is_likely_english_blocks_english_without_blocking_spanish_or_russian() -> None:
    assert _is_likely_english("I am from Russia but want to go to Spain") is True
    assert _is_likely_english("How can I say this?") is True
    assert _is_likely_english("Estoy de Rusia, pero quiero ir a Espana") is False
    assert _is_likely_english("Я хочу сказать это по-испански") is False


def test_is_likely_gibberish_blocks_keyboard_mash_and_numbers() -> None:
    assert _is_likely_gibberish("hjkdjhd dfghjdf") is True
    assert _is_likely_gibberish("орлова сорлов ыворппппв") is True
    assert _is_likely_gibberish("123456") is True
    assert _is_likely_gibberish("Estoy de Rusia") is False
    assert _is_likely_gibberish("Я хочу в Испанию") is False
