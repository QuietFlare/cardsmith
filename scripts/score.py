"""Score every results file and print one table to compare the models.

    uv run python scripts/score.py

Writes results/scores.json. A result made from a different data version than the
current passages is refused, because its scores would compare unlike things.
"""
import hashlib
import json
from pathlib import Path

from cardsmith.report import by_category, summarise
from cardsmith.score import score

ROOT = Path(__file__).resolve().parent.parent
PASSAGES = ROOT / "data" / "eval" / "passages.json"
RESULTS = ROOT / "results"


def main():
    raw = PASSAGES.read_bytes()
    data_version = hashlib.sha256(raw).hexdigest()[:12]
    passages = {p["id"]: p for p in json.loads(raw)}

    report = {"data_version": data_version, "models": {}}
    for path in sorted(RESULTS.glob("*.jsonl")):
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        if any(row["data_version"] != data_version for row in rows):
            print(f"Skipping {path.name}: made from other passages. Run it again first.")
            continue
        records = [score(passages[row["passage"]], row["output"]) for row in rows]
        report["models"][path.stem] = {
            "model": rows[0]["model"],
            "model_revision": rows[0]["model_revision"],
            "summary": summarise(records),
            "vocab_by_category": by_category(records),
            "passages": records,
        }

    columns = ["format_ok", "duplicates", "facts", "correct", "selection", "knowledge", "meaning"]
    print(f"data version {data_version}\n")
    print(f"{'model':<14}" + "".join(f"{c:>12}" for c in columns))
    for name, entry in report["models"].items():
        print(f"{name:<14}" + "".join(f"{entry['summary'][c]:>12}" for c in columns))

    categories = sorted({c for e in report["models"].values() for c in e["vocab_by_category"]})
    for number in ("selection", "knowledge"):
        if not categories:
            break
        print(f"\nvocab {number} by category")
        print(f"{'model':<14}" + "".join(f"{c:>12}" for c in categories))
        for name, entry in report["models"].items():
            row = entry["vocab_by_category"]
            cells = (row[c][number] if c in row else "-" for c in categories)
            print(f"{name:<14}" + "".join(f"{cell:>12}" for cell in cells))

    out = RESULTS / "scores.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nSaved {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
