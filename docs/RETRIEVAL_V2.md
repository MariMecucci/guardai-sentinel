# Retrieval v2 — versioned knowledge and evidence checks

## Architecture

`static.py` → static rule identifiers → `retrieval.py` (rule-allowlisted local **BM25** ranking) → versioned editorial passage metadata → report UI/JSON → optional Gemini prompt.

Unlike v1 fixed reference mapping, v2 ranks passage-level descriptions using BM25 relevance within a deterministic rule-compatible shortlist. This is a **lexical** retrieval method, **not embedding or vector semantic search**. No code is uploaded for retrieval; retrieval runs offline, and no additional credentials/services are needed.

## Provenance and caveats

Corpus: `sentinel/knowledge/security_passages.json` (schema 1.0, editorial date 2026-11-11). Each passage has an immutable-style ID, reference link, source title, editorial-summary version, and rule mapping.

**Crucial:** the passages are independently written paraphrases. They are **not quotes or authenticated snapshots** of OWASP/MITRE/Python documentation. The URL is a reading reference rather than a precise citation anchor or evidence that the latest live source contains the exact text. Editorial checking, upstream revision tracking and snippet-level support audits remain outstanding. An LLM's claim is **not validated merely because a document was retrieved**.

Input code is never executed. Retrieval queries come from fixed, rule-ID-derived terms, not user-controlled snippets or uploaded documents. Unknown rules and clean scans abstain from retrieval. Gemini is still opt-in and stays disabled in the public demo by default.

## Evaluation

```bash
python -m unittest discover -s tests -v
python -m sentinel.evaluate_retrieval
```

`examples/rag_relevance_cases.json` contains five small author-labeled **synthetic rule-ID retrieval cases**, including negatives. The evaluator reports mean precision@k and recall@k per fixture. This corpus and fixture are co-designed and cannot establish real-world generalization, LLM factuality, hallucination rates, retrieval relevance for unseen questions, or passage-level faithfulness.

## Next milestones

1. Obtain and verify permission/attribution for true document snapshots and source revision dates.
2. Add gold-set judgments from independent review and unseen natural-language queries.
3. Compare BM25 with locally computed embeddings, controlling cost, latency, and data exposure.
4. Request structured per-claim passage IDs from Gemini, reject unsupported IDs, and **human-evaluate** claim-to-evidence faithfulness.
5. Run private Gemini tests with authorized synthetic code and check safety/privacy limits before any public AI rollout.
