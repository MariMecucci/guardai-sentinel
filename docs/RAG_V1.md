# GuardAI Sentinel — Grounded AI / RAG v1

## What this actually implements

This is a **deterministic, local retrieval prototype** integrated with the optional Gemini reviewer. It is *not* a vector-search RAG system. A small set of manually curated source summaries maps to known static rule IDs; the selected context is supplied to Gemini, and the UI/JSON report displays the selected references independently of Gemini's response. No new service, keys, or network retrieval is required.

**Trust model:** the static rule engine creates possible findings; retrieval is keyed only by those rule IDs. The model never chooses reference links. Reference presence does **not** prove that a finding is exploitable, or that the model's explanation is faithful. Unknown rules and clean scans retrieve nothing. Source code is still sent to Gemini **only** when AI is explicitly enabled and sharing is authorized in the UI.

## References

- OWASP SQL Injection Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- MITRE CWE-89: https://cwe.mitre.org/data/definitions/89.html
- Python subprocess security considerations: https://docs.python.org/3/library/subprocess.html#security-considerations
- MITRE CWE-78: https://cwe.mitre.org/data/definitions/78.html

Curated summaries are maintained in `sentinel/rag.py`. These are short author-written descriptions, **not live copies** or automatically synchronized versions of the linked documents. Links and summaries require periodic editorial review.

## Offline evaluation

```bash
python -m unittest discover -s tests -v
```

The new `tests/test_rag.py` checks rule-specific selection, deterministic order, deduplication, unsupported rules and limits. Existing scanner benchmarks measure **only static rule detection** and must not be presented as RAG or Gemini performance.

## Next before claiming production-grade RAG

1. Add versioned, permitted source passages with stable document IDs and chunk provenance.
2. Define retrieval relevance and coverage gold labels, test negatives and adversarial prompts.
3. Evaluate Gemini grounding/faithfulness against retrieved excerpts, citations, unsupported claims, response quality and model cost.
4. Consider embeddings/vector retrieval only after this evaluation; measure whether it actually improves retrieval.
5. Keep the public Gemini flow off until authentication, quotas, privacy protection and abuse controls are implemented.

This educational feature cannot guarantee correctness or safety of user-provided code.
