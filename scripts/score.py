"""Score every results file and print one table to compare the models.

    uv run python scripts/score.py

Writes results/scores.json. A result made from a different data version than the
current passages is refused, because its scores would compare unlike things.
"""
import hashlib
import json
from pathlib import Path

from cardsmith.score import score

ROOT = Path(__file__).resolve().parent.parent
PASSAGES = ROOT / "data" / "eval" / "passages.json"
RESULTS = ROOT / "results"


def summarise(records):
    vocab = [r for r in records if r["kind"] == "vocab"]
    qa = [r for r in records if r["kind"] == "qa"]
    return {
        "format_ok": f"{sum(r['format_ok'] for r in records)}/{len(records)}",
        "duplicates": sum(r["duplicates"] for r in records),
        "too_long": sum(r["too_long"] for r in records),
        "facts": f"{sum(r['facts_covered'] for r in qa)}/{sum(r['facts_total'] for r in qa)}",
        "phrase": f"{sum(r['phrase_match'] for r in vocab)}/{len(vocab)}",
        "meaning": f"{sum(r['meaning_match'] for r in vocab)}/{len(vocab)}",
    }


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
            "passages": records,
        }

    columns = ["format_ok", "duplicates", "too_long", "facts", "phrase", "meaning"]
    print(f"data version {data_version}\n")
    print(f"{'model':<14}" + "".join(f"{c:>12}" for c in columns))
    for name, entry in report["models"].items():
        print(f"{name:<14}" + "".join(f"{entry['summary'][c]:>12}" for c in columns))

    out = RESULTS / "scores.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nSaved {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
