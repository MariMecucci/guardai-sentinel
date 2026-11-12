"""Offline retrieval fixture; metrics concern only curated passage relevance."""
import json
from pathlib import Path
from .models import Finding
from .retrieval import retrieve_passages

CASES_PATH = Path(__file__).resolve().parent.parent / "examples" / "rag_relevance_cases.json"

def score_cases(path: Path = CASES_PATH) -> dict:
    cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
    results = []
    for case in cases:
        findings = [Finding(rule_id=rule, title="test", severity="low", line=1,
                            evidence="synthetic", why="synthetic", remediation="synthetic")
                    for rule in case["rules"]]
        actual = [p.id for p in retrieve_passages(findings, limit=case.get("k", 3))]
        expected = set(case["relevant_ids"])
        hits = len(expected.intersection(actual))
        precision = hits / len(actual) if actual else (1.0 if not expected else 0.0)
        recall = hits / len(expected) if expected else (1.0 if not actual else 0.0)
        results.append({"name": case["name"], "returned": actual,
                        "precision_at_k": round(precision, 4), "recall_at_k": round(recall, 4)})
    return {"cases": results, "mean_precision_at_k": round(sum(r["precision_at_k"] for r in results)/len(results), 4),
            "mean_recall_at_k": round(sum(r["recall_at_k"] for r in results)/len(results), 4),
            "disclaimer": "Hand-labeled synthetic rule queries; not LLM citation faithfulness or real-world accuracy."}

if __name__ == "__main__":
    print(json.dumps(score_cases(), ensure_ascii=False, indent=2))
