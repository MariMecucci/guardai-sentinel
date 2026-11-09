# Evaluation protocol — GuardAI Sentinel MVP

## Scope

- Subject under test: deterministic scanning rules in `sentinel/static.py`.
- Not tested: Gemini output, end-to-end remote model quality, RAG, authentication, production deployment.
- Cases: 32 **synthetic, author-labeled** code snippets stored in `examples/benchmark_cases.json`.
- Input labels: `is_risky = true/false` based on whether the snippet depicts a potentially unsafe coding pattern.
- Classifier: a predicted positive means **one or more** static findings.

## Reproduce

```bash
python -m sentinel.evaluate --output docs/benchmark-results.json
python -m unittest discover -s tests -v
```

## Metrics

- True positive (TP): risky snippet flagged.
- False positive (FP): labeled safe snippet flagged.
- True negative (TN): labeled safe snippet not flagged.
- False negative (FN): risky snippet missed.
- Precision = TP / (TP + FP).
- Recall = TP / (TP + FN).
- F1 = 2 × precision × recall / (precision + recall).

Observed: **TP=17, FP=1, TN=11, FN=3**; **precision=0.9444, recall=0.8500, F1=0.8947**.

### Known difficult cases

- Unsafe use of Python `.format` and `%` is missed in this narrow rule engine.
- `os.system()` with dynamic string is not covered (false negative).
- Controlled `f-string` SQL built from a trusted table name is flagged due to lack of dataflow analysis (false positive).

### Interpretation

This is a **small demonstration benchmark**, not a representative sample of real software, and labels are **not independent**. Higher scores here should not be generalized to actual security risk. Real evaluation requires diverse source repositories, expert labeling, leakage controls, controls for code provenance, precision/recall by rule and severity, and independent validation.

### AI evaluation next

For the optional Gemini adapter, collect model outputs for an authorized synthetic set and score factual accuracy, grounding, hallucinated findings, risk classification calibration, privacy leakage, cost and latency. No such measurements are claimed in the MVP.
