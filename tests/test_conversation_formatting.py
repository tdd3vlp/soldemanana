from app.bot.handlers.conversation import (
    _build_inline_corrections,
    _build_russian_input_translation,
    _contains_cyrillic,
    _is_likely_english,
    _is_likely_gibberish,
    _is_too_short_spanish_answer,
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


def test_build_inline_corrections_uses_punctuated_natural_variant() -> None:
    result = _build_inline_corrections(
        "Hola, coma esta",
        [
            {"original": "coma", "corrected": "cómo"},
            {"original": "esta", "corrected": "estás"},
        ],
        "Hola, ¿cómo estás?",
    )

    assert result == "Hola, <s>coma</s> ¿cómo <s>esta</s> estás?"


def test_build_inline_corrections_does_not_strike_same_word_with_punctuation() -> None:
    result = _build_inline_corrections(
        "No tieno planes para hoy",
        [{"original": "tieno", "corrected": "tengo"}],
        "No tengo planes para hoy.",
    )

    assert result == "No <s>tieno</s> tengo planes para hoy."


def test_build_inline_corrections_marks_missing_opening_exclamation() -> None:
    result = _build_inline_corrections(
        "Bien, gracias!",
        [{"original": "Bien, gracias!", "corrected": "¡Bien, gracias!"}],
        "¡Bien, gracias!",
    )

    assert result == "¡Bien, gracias!"


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
    assert _is_likely_english("Overall") is True
    assert _is_likely_english("Estoy de Rusia, pero quiero ir a Espana") is False
    assert _is_likely_english("Я хочу сказать это по-испански") is False


def test_is_likely_english_allows_titles_and_names() -> None:
    assert _is_likely_english("The Beatles") is False
    assert _is_likely_english("Bohemian Rhapsody") is False
    assert _is_likely_english("I Want to Break Free") is False


def test_is_too_short_spanish_answer_detects_insufficient_replies() -> None:
    assert _is_too_short_spanish_answer("Si, muy") is True
    assert _is_too_short_spanish_answer("Me gusta") is True
    assert _is_too_short_spanish_answer("Me encanta") is True
    assert _is_too_short_spanish_answer("Paella") is True
    assert _is_too_short_spanish_answer("Sobre comida") is True
    assert _is_too_short_spanish_answer("La comida italiana") is True
    assert _is_too_short_spanish_answer("Toco la guitarra") is False
    assert _is_too_short_spanish_answer("Играл на гитаре") is False


def test_is_too_short_spanish_answer_allows_complete_short_replies() -> None:
    assert _is_too_short_spanish_answer("Sí") is False
    assert _is_too_short_spanish_answer("No") is False
    assert _is_too_short_spanish_answer("Gracias") is False
    assert _is_too_short_spanish_answer("Tengo hambre") is False
    assert _is_too_short_spanish_answer("Quiero café") is False


def test_is_too_short_spanish_answer_allows_greetings() -> None:
    assert _is_too_short_spanish_answer("Hola!") is False
    assert _is_too_short_spanish_answer("Buenos días") is False
    assert _is_too_short_spanish_answer("Buenas tardes") is False


def test_is_likely_gibberish_blocks_keyboard_mash_and_numbers() -> None:
    assert _is_likely_gibberish("hjkdjhd dfghjdf") is True
    assert _is_likely_gibberish("орлова сорлов ыворппппв") is True
    assert _is_likely_gibberish("апиап") is True
    assert _is_likely_gibberish("Зкупгтефы,") is True
    assert _is_likely_gibberish("123456") is True
    assert _is_likely_gibberish("Estoy de Rusia") is False
    assert _is_likely_gibberish("Я хочу в Испанию") is False
    assert _is_likely_gibberish("Привет!") is False


def test_is_likely_gibberish_does_not_block_valid_russian_sentences() -> None:
    assert _is_likely_gibberish("Иногда я готовлю другие блюда") is False
    assert _is_likely_gibberish("Мне нравится испанская кухня") is False
    assert _is_likely_gibberish("хочу сказать что иногда я готовлю другие блюда") is False


def test_is_too_short_spanish_answer_allows_apology_forms() -> None:
    assert _is_too_short_spanish_answer("Perdone") is False
    assert _is_too_short_spanish_answer("Perdona") is False
