"""Reproducible synthetic rule benchmark (not a benchmark of Gemini/LLMs).

Runs in memory. Labels are authored for illustrative patterns, not independently audited.
"""
import argparse
import json
from pathlib import Path
from .static import scan_code

DATASET = Path(__file__).resolve().parent.parent / "examples" / "benchmark_cases.json"


def evaluate() -> dict:
    data = json.loads(DATASET.read_text(encoding="utf-8"))
    tp = fp = tn = fn = 0
    details = []
    for item in data:
        report = scan_code(item["filename"], item["source"])
        predicted = bool(report.findings)
        expected = item["is_risky"]
        if predicted and expected:
            tp += 1
        elif predicted and not expected:
            fp += 1
        elif not predicted and expected:
            fn += 1
        else:
            tn += 1
        details.append({"case_id": item["id"], "predicted": predicted, "expected": expected,
                        "finding_count": len(report.findings)})
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"dataset_size": len(data), "model": "deterministic-heuristics-only",
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4),
            "notice": "Synthetic, hand-labeled educational dataset; not representative of real-world vulnerability detection or Gemini.",
            "cases": details}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()
    result = evaluate()
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
