"""The scorer decides what counts as good, so it gets tests of its own."""
from cardsmith.score import (
    duplicates, facts_covered, format_ok, head_words, parse_cards, score, too_long, vocab_match,
    card_correct, word_match,
)

FACTS = [
    "Mitochondria produce most of the cell's energy",
    "Mitochondria make ATP through oxidative phosphorylation",
    "Mitochondrial DNA is inherited from the mother",
]


def test_a_card_is_a_line_with_one_bar_and_text_on_both_sides():
    output = "What makes ATP? | Mitochondria\nno bar here\n | empty front\na | b | c"
    assert parse_cards(output) == [("What makes ATP?", "Mitochondria")]


def test_format_needs_every_line_to_be_a_card():
    assert format_ok("Q1 | A1\nQ2 | A2")
    assert not format_ok("German phrase | English meaning\n\nIch melde mich | I am | reminded")
    assert not format_ok("What are mitochondria?")
    assert not format_ok("")


def test_duplicates_ignore_case_and_punctuation():
    assert duplicates("What is ATP? | Energy\nwhat is atp | energy\nOther? | Thing") == 1


def test_duplicates_count_repeated_lines_that_are_not_cards():
    assert duplicates("What is X?\nWhat is Y?\nWhat is X?") == 1


def test_an_echoed_format_line_is_not_a_card():
    output = "German phrase | English meaning\n\nIch habe mich beworben | I have applied"
    assert parse_cards(output) == [("Ich habe mich beworben", "I have applied")]
    assert not format_ok(output)


def test_long_answers_are_counted():
    long = "a b c d e f g h i j k l m"
    assert too_long([("Q", long), ("Q", "short")]) == 1


def test_facts_count_when_most_of_their_words_appear():
    cards = [
        ("What does mitochondria produce?", "Energy (ATP)"),
        ("How do mitochondria make ATP?", "Through oxidative phosphorylation"),
        ("What is mitochondrial DNA?", "Inherited from the mother"),
    ]
    assert facts_covered(cards, FACTS) == 3


def test_no_cards_cover_no_facts():
    assert facts_covered([], FACTS) == 0


def test_vocab_matches_phrase_and_any_listed_meaning():
    cards = [("sich melden bei (+ Dat.)", "to get in touch with someone")]
    assert vocab_match(cards, "sich melden bei (+ Dat.) | to get in touch with") == (True, True)
    other = [("sich beschäftigen mit", "to work on")]
    assert vocab_match(other, "sich beschäftigen mit (+ Dat.) | to deal with, to work on") == (False, True)


def test_score_reports_the_checks_for_the_passage_kind():
    passage = {"id": "de-x", "kind": "vocab", "expected": "warten auf (+ Akk.) | to wait for"}
    record = score(passage, "warten auf (+ Akk.) | to wait for")
    assert record == {
        "passage": "de-x", "kind": "vocab", "cards": 1, "format_ok": True,
        "duplicates": 0, "too_long": 0, "category": "", "phrase_match": True,
        "meaning_match": True, "word_match": True, "correct": True,
    }


def test_a_format_word_as_the_question_is_not_a_card():
    # Qwen3 0.6B, mitochondria passage, 26 Oct 2026: passage sentences behind format labels.
    output = (
        "question | mitochondria are organelles that produce most of the cell's energy\n"
        "answer | they make ATP through a process called oxidative phosphorylation"
    )
    assert parse_cards(output) == []
    assert not format_ok(output)
    assert facts_covered(parse_cards(output), FACTS) == 0


def test_head_words_drop_articles_plurals_and_case_notes():
    assert head_words("der Termin, -e") == [{"termin"}]
    assert head_words("sich melden bei (+ Dat.)") == [{"melden", "bei"}]
    assert head_words("deswegen / deshalb") == [{"deswegen"}, {"deshalb"}]
    assert head_words("aufwachen (ist aufgewacht)") == [{"aufwachen"}]


def test_word_match_forgives_missing_grammar_but_not_a_conjugated_form():
    assert word_match([("Termin", "appointment")], "der Termin, -e | appointment")
    assert word_match([("deshalb", "therefore")], "deswegen / deshalb | therefore")
    assert not word_match([("melde mich bei", "to contact")], "sich melden bei (+ Dat.) | to get in touch with")
    assert not word_match([("Budget", "budget")], "abhängen von (+ Dat.) | to depend on")


def test_word_match_refuses_a_chunk_of_the_sentence():
    # Qwen3 0.6B few-shot, 27 Oct 2026: the right word inside a copied clause.
    assert not word_match([("bevor ich antworte (+ Dat.)", "to respond before reading")], "bevor | before")
    assert not word_match([("entscheiden + für + einfache Lösung", "decide")], "sich entscheiden für (+ Akk.) | to decide on")
    assert word_match([("Verantwortung haben (+ Dat.)", "to bear responsibility")], "die Verantwortung | responsibility")


def test_a_right_meaning_on_the_wrong_word_is_not_correct():
    # Qwen2.5 0.5B few-shot, 27 Oct 2026: "vergleichen" means to compare.
    passage = {"id": "de-v", "kind": "vocab", "expected": "vereinbaren | to arrange, to agree on"}
    record = score(passage, "vergleichen können (+ Dat.) | to agree on")
    assert record["meaning_match"] and not record["word_match"] and not record["correct"]


def test_the_right_verb_with_the_wrong_case_is_not_correct():
    # Qwen3 0.6B few-shot, 27 Oct 2026: "erinnern an" takes the accusative.
    expected = "sich erinnern an (+ Akk.) | to remember"
    assert not card_correct(("sich erinnern an (+ Dat.)", "to remember in the past"), expected)
    assert card_correct(("sich erinnern an (+ Akk.)", "to remember"), expected)
    assert card_correct(("Erfahrung", "to have experience"), "die Erfahrung, -en | experience")


def test_an_invented_case_note_without_a_plus_is_still_a_case():
    # EuroLLM 1.7B few-shot, 27 Oct 2026: grammar notes a noun or adjective does not have.
    assert not card_correct(("krankenkasse (Dat.)", "health insurance"), "die Krankenkasse, -n | health insurance")
    assert not card_correct(("zuverlässig (Dat.)", "reliable"), "zuverlässig | reliable")
    assert card_correct(("warten auf (+ Acc.)", "to wait for"), "warten auf (+ Akk.) | to wait for")
