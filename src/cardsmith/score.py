"""Score a model's raw output against a passage. Plain Python, no model.

These are the checks a rule can decide. Whether a card says something the
passage does not is a judgement about meaning, and needs a model of its own later.
"""
import re

# Card answers longer than this stop being flash cards.
MAX_ANSWER_WORDS = 12
# Share of a fact's content words that must appear in the cards to count it as covered.
FACT_COVERAGE = 0.6

STOPWORDS = {
    "a", "an", "the", "of", "to", "in", "on", "and", "or", "is", "are", "was",
    "that", "which", "by", "from", "for", "with", "it", "its", "they", "their",
    "most", "own", "through", "called", "process", "s",
}


def normalise(text):
    """Lower case, punctuation gone, single spaces: so 'Dat.' and 'dat' compare equal."""
    return " ".join(re.sub(r"[^\w+]+", " ", text.lower()).split())


# The format lines from the prompts. A model that copies one back, or uses one of its
# words as a question ("question | <a sentence>"), has written a label, not a card.
FORMATS = ["question | answer", "German | English", "German phrase | English meaning"]
LABELS = {normalise(side) for line in FORMATS for side in line.split("|")}


def parse_cards(output):
    """Every line with exactly one '|' and text on both sides is a card, unless its front is a label."""
    cards = []
    for line in output.splitlines():
        parts = line.split("|")
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            if normalise(parts[0]) not in LABELS:
                cards.append((parts[0].strip(), parts[1].strip()))
    return cards


def format_ok(output):
    """True when there is at least one card and every non-empty line is one."""
    lines = [line for line in output.splitlines() if line.strip()]
    return bool(lines) and len(parse_cards(output)) == len(lines)


def duplicates(output):
    """How many lines repeat an earlier line. Lines, not cards: a repeated question counts too."""
    lines = [normalise(line) for line in output.splitlines() if line.strip()]
    return len(lines) - len(set(lines))


def too_long(cards):
    """How many answers are longer than a card should be."""
    return sum(1 for _, back in cards if len(back.split()) > MAX_ANSWER_WORDS)


def content_words(text):
    return {w for w in normalise(text).split() if w not in STOPWORDS}


def facts_covered(cards, facts):
    """How many of the passage's facts the cards mention, by shared content words.

    A rough measure: it counts words, not meaning, so a card can share the words
    of a fact and still get it wrong.
    """
    card_words = set()
    for front, back in cards:
        card_words |= content_words(front + " " + back)
    covered = 0
    for fact in facts:
        words = content_words(fact)
        if words and len(words & card_words) / len(words) >= FACT_COVERAGE:
            covered += 1
    return covered


def vocab_match(cards, expected):
    """Whether any card has the expected phrase, and whether any has its meaning.

    The meaning counts when one of the expected alternatives ('to deal with, to
    work on') appears inside the card's answer.
    """
    want_front, want_back = (part.strip() for part in expected.split("|"))
    meanings = [normalise(m) for m in want_back.split(",")]
    phrase = any(normalise(front) == normalise(want_front) for front, _ in cards)
    meaning = any(m and m in normalise(back) for _, back in cards for m in meanings)
    return phrase, meaning


ARTICLES = {"der", "die", "das", "sich"}


def head_words(german):
    """The words a card must name, without the grammar notes around them.

    'der Termin, -e' gives {'termin'}, 'sich melden bei (+ Dat.)' gives {'melden', 'bei'},
    'deswegen / deshalb' gives either alternative.
    """
    core = re.sub(r"\(.*?\)", " ", german.split(",")[0])
    return [
        {w for w in normalise(alt).split() if w not in ARTICLES}
        for alt in core.split("/")
    ]


# Grammar notes a card may add without saying anything new: "+", case and plural markers.
GRAMMAR = ARTICLES | {"+", "dat", "akk", "gen", "pl", "ist", "hat"}


def word_match(cards, expected):
    """Looser than vocab_match: the card names the right word, whatever grammar it adds or drops.

    At most one extra word is allowed, so "Verantwortung haben" counts for "die Verantwortung"
    but a chunk of the sentence ("bevor ich antworte") does not count for "bevor".
    """
    want_front = expected.split("|")[0]
    for front, _ in cards:
        said = set(normalise(front).split())
        for words in head_words(want_front):
            if words and words <= said and len(said - words - GRAMMAR) <= 1:
                return True
    return False


def cases(text):
    """The case notes in order: 'sprechen mit (+ Dat.) über (+ Akk.)' gives ['dat', 'akk'].

    With or without the '+', and the English 'Acc.' counts as 'akk', so an invented
    '(Dat.)' on a noun is caught as well as a wrong '(+ Dat.)' on a verb.
    """
    found = re.findall(r"\b(dat|akk|acc|gen)\b", text, re.IGNORECASE)
    return ["akk" if c.lower() == "acc" else c.lower() for c in found]


def card_correct(card, expected):
    """One card that is right as a whole: the word, its meaning, and for a verb its cases.

    A guessed meaning on the wrong word is not right, and neither is the right verb with
    the wrong case, which is the mistake a learner most needs the card to prevent.
    """
    want_front = expected.split("|")[0]
    return (
        word_match([card], expected)
        and vocab_match([card], expected)[1]
        and cases(card[0]) == cases(want_front)
    )


def score(passage, output):
    """All the checks for one passage, as one flat record."""
    cards = parse_cards(output)
    record = {
        "passage": passage["id"],
        "kind": passage["kind"],
        "cards": len(cards),
        "format_ok": format_ok(output),
        "duplicates": duplicates(output),
        "too_long": too_long(cards),
    }
    if passage["kind"] == "qa":
        record["facts_covered"] = facts_covered(cards, passage["facts"])
        record["facts_total"] = len(passage["facts"])
    if passage["kind"] == "vocab":
        record["category"] = passage.get("category", "")
        record["phrase_match"], record["meaning_match"] = vocab_match(cards, passage["expected"])
        record["word_match"] = word_match(cards, passage["expected"])
        record["correct"] = any(card_correct(card, passage["expected"]) for card in cards)
    return record
