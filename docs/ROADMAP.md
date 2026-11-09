# GuardAI Sentinel — Roadmap

## Milestone 1 — MVP (implemented locally)

- [x] Basic static Python AST rules and SQL string heuristics
- [x] Streamlit local-first dashboard and JSON report
- [x] FastAPI local endpoint
- [x] Optional Google Gemini adapter (code path implemented; live API not tested)
- [x] Unit/integration tests and 32-case synthetic benchmark
- [x] CI workflow configuration
- [ ] Publish independent GitHub repository
- [ ] Deploy public static-only demo

## Milestone 2 — Data engineering quality

- [ ] Detect sample anti-patterns in ETL/ELT SQL and PySpark
- [ ] Schema validation and SQL dialect-aware checks
- [ ] Enhanced confidence and false-positive analysis
- [ ] Larger independently reviewed benchmark

## Milestone 3 — Grounded AI engineering

- [ ] Curated OWASP/CWE documents with attribution and versions
- [ ] Retrieval-augmented explanations citing retrieved passages
- [ ] Hallucination and evidence-faithfulness evaluation
- [ ] Compare Gemini models, latency, cost and quality on controlled examples

## Milestone 4 — Safer deployment

- [ ] User authentication and strict quotas for paid model calls
- [ ] Content and privacy policies, abuse controls and rate limiting
- [ ] Dependency scanning, CI security gates and versioned releases
