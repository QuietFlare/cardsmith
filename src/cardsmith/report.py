"""Add up the per-passage scores of one model into the numbers that compare models.

Two vocabulary numbers are kept apart on purpose. Selection: did the model pick the
word I made a card for. Knowledge: of those, how many cards were fully right, with
meaning and case. A low first number wants better examples or training; a low second
number wants a dictionary in the prompt. One combined number cannot tell them apart.
"""


def ratio(hits, total):
    return f"{hits}/{total}"


def summarise(records):
    vocab = [r for r in records if r["kind"] == "vocab"]
    qa = [r for r in records if r["kind"] == "qa"]
    picked = [r for r in vocab if r["word_match"]]
    return {
        "format_ok": ratio(sum(r["format_ok"] for r in records), len(records)),
        "duplicates": sum(r["duplicates"] for r in records),
        "too_long": sum(r["too_long"] for r in records),
        "facts": ratio(sum(r["facts_covered"] for r in qa), sum(r["facts_total"] for r in qa)),
        "correct": ratio(sum(r["correct"] for r in vocab), len(vocab)),
        "selection": ratio(len(picked), len(vocab)),
        "knowledge": ratio(sum(r["correct"] for r in picked), len(picked)),
        "phrase": ratio(sum(r["phrase_match"] for r in vocab), len(vocab)),
        "meaning": ratio(sum(r["meaning_match"] for r in vocab), len(vocab)),
    }


def by_category(records):
    """Selection and knowledge per category, so one easy kind of word cannot hide a hard one."""
    out = {}
    for r in records:
        if r["kind"] == "vocab":
            picked, correct, total = out.get(r["category"], (0, 0, 0))
            out[r["category"]] = (picked + r["word_match"], correct + r["correct"], total + 1)
    return {
        c: {"selection": ratio(picked, total), "knowledge": ratio(correct, picked)}
        for c, (picked, correct, total) in sorted(out.items())
    }
