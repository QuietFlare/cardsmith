"""The report decides which number a model is judged by, so it gets tests of its own."""
from cardsmith.report import by_category, summarise


def vocab(category, word_match, correct):
    return {
        "kind": "vocab", "category": category, "format_ok": True, "duplicates": 0, "too_long": 0,
        "phrase_match": correct, "meaning_match": correct, "word_match": word_match, "correct": correct,
    }


def test_knowledge_counts_only_the_cards_whose_word_was_picked():
    records = [
        vocab("noun", True, True),      # picked and right
        vocab("noun", True, False),     # picked, grammar wrong
        vocab("verb", False, False),    # other word chosen: not a knowledge miss
    ]
    summary = summarise(records)
    assert summary["selection"] == "2/3"
    assert summary["knowledge"] == "1/2"
    assert summary["correct"] == "1/3"


def test_by_category_keeps_the_two_numbers_apart_per_kind():
    records = [vocab("noun", True, True), vocab("noun", True, False), vocab("verb", False, False)]
    assert by_category(records) == {
        "noun": {"selection": "2/2", "knowledge": "1/2"},
        "verb": {"selection": "0/1", "knowledge": "0/0"},
    }
