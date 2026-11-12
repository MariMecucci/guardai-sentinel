# GuardAI Sentinel — Roadmap

## Milestone 1 — MVP (implemented locally)

- [x] Basic static Python AST rules and SQL string heuristics
- [x] Streamlit local-first dashboard and JSON report
- [x] FastAPI local endpoint
- [x] Optional Google Gemini adapter (live API and two end-to-end synthetic reviews validated privately on 2026-11-10)
- [x] Unit/integration tests and 32-case synthetic benchmark
- [x] CI workflow configuration
- [x] Publish independent GitHub repository
- [x] Deploy public static-only demo and verify two synthetic examples (see [validation](PUBLIC_DEMO_VALIDATION.md))

## Milestone 2 — Data engineering quality

- [ ] Detect sample anti-patterns in ETL/ELT SQL and PySpark
- [ ] Schema validation and SQL dialect-aware checks
- [ ] Enhanced confidence and false-positive analysis
- [ ] Larger independently reviewed benchmark

## Milestone 3 — Grounded AI engineering

- [x] Initial curated OWASP/CWE/Python summaries, deterministic rule-based retrieval, and attribution (offline prototype; no versioned source passages yet)
- [x] Versioned editorial summary corpus with source URLs, identifiers, and offline BM25 retrieval
- [ ] Independently authenticated source passages with upstream document revisions
- [x] Feed curated reference context into opt-in Gemini and display independently selected links
- [ ] Passage-level citations with faithfulness validation
- [x] Synthetic author-labeled BM25 retrieval evaluation fixture and runner
- [ ] Independent LLM hallucination and evidence-faithfulness evaluation
- [ ] Compare Gemini models, latency, cost and quality on controlled examples

## Milestone 4 — Safer deployment

- [ ] User authentication and strict quotas for paid model calls
- [ ] Content and privacy policies, abuse controls and rate limiting
- [ ] Dependency scanning, CI security gates and versioned releases
