"""Turn an Anki deck (German, English, example sentence) into vocabulary eval passages.

    uv run python scripts/build_vocab_eval.py ~/workspace/deutsch/anki-alltag.txt

Rewrites the vocab entries in data/eval/passages.json and keeps every other entry.
Each example sentence becomes a passage, and the card I made for it is the expected answer.
Rows used as few-shot examples are left out, so the test never contains its own examples.
"""
import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PASSAGES = ROOT / "data" / "eval" / "passages.json"
EXAMPLES = ROOT / "data" / "prompts" / "examples.json"

# Rows that say something about me rather than about German. The repo is public.
PRIVATE = {"der Tagessatz, -sätze", "die Verfügbarkeit"}


def category(german):
    """What kind of thing the learner memorises. Lets the scorer report each kind on its own."""
    if re.search(r"\(\+ (Dat|Akk|Gen)\.\)", german):
        return "verb+case"
    if re.match(r"(der|die|das) ", german):
        return "noun"
    # A single infinitive, maybe reflexive, maybe with its perfect in brackets: "aufwachen (ist aufgewacht)".
    if re.fullmatch(r"(sich )?[a-zäöüß]+(en|ern|eln)", re.sub(r"\s*\(.*\)", "", german)):
        return "verb"
    # Connectors, adverbs, adjectives and set phrases: "trotzdem", "zuverlässig", "auf jeden Fall".
    return "phrase"


def slug(german):
    words = re.sub(r"\(.*?\)|,.*$", "", german).lower()
    words = words.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return "de-" + "-".join(re.findall(r"[a-z]+", words))


def read_deck(path):
    with open(path, encoding="utf-8") as f:
        return [row for row in csv.reader(f, delimiter="\t") if row and not row[0].startswith("#")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path)
    args = parser.parse_args()

    examples = json.loads(EXAMPLES.read_text(encoding="utf-8"))
    leaked = {e["cards"].split("|")[0].strip() for e in examples["vocab"]}

    vocab = []
    for german, english, sentence in read_deck(args.deck.expanduser()):
        if german in leaked or german in PRIVATE:
            continue
        vocab.append({
            "id": slug(german),
            "subject": "language",
            "language": "de",
            "kind": "vocab",
            "category": category(german),
            "text": sentence,
            "expected": f"{german} | {english}",
        })

    ids = [p["id"] for p in vocab]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        raise SystemExit(f"Two rows make the same id: {sorted(duplicates)}")

    others = [p for p in json.loads(PASSAGES.read_text(encoding="utf-8")) if p["kind"] != "vocab"]
    PASSAGES.write_text(json.dumps(others + vocab, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    counts = {}
    for p in vocab:
        counts[p["category"]] = counts.get(p["category"], 0) + 1
    print(f"{len(vocab)} vocab passages ({counts}), {len(others)} other passages kept")
    print(f"Left out: {len(leaked)} few-shot rows, {len(PRIVATE)} private rows")


if __name__ == "__main__":
    main()
