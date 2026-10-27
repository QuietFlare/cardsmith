"""Run one model over the eval passages and save what it wrote.

    uv run python scripts/run_eval.py qwen3
    uv run python scripts/run_eval.py qwen

Writes results/<name>.jsonl, one line per passage. Every line names the model
revision and the data version, so a result can be traced to exactly what made it.
"""
import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

import transformers

from cardsmith.baselines import MODELS

ROOT = Path(__file__).resolve().parent.parent
PASSAGES = ROOT / "data" / "eval" / "passages.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", choices=sorted(MODELS))
    args = parser.parse_args()

    raw = PASSAGES.read_bytes()
    passages = json.loads(raw)
    model = MODELS[args.model]()
    run = {
        "model": model.model_id,
        "model_revision": model.revision,
        "data_version": hashlib.sha256(raw).hexdigest()[:12],
        "date": date.today().isoformat(),
        "transformers": transformers.__version__,
    }

    out = ROOT / "results" / f"{args.model}.jsonl"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for passage in passages:
            prompt, output = model.ask(passage)
            row = {**run, "passage": passage["id"], "prompt": prompt, "output": output}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(f"[{passage['id']}]\n{output}\n")
    print("Saved", out.relative_to(ROOT))


if __name__ == "__main__":
    main()