# GuardAI Sentinel — local BM25 + Gemini validation

**Date:** 2026-11-12  
**Environment:** Windows / VS Code; Python 3.11.9 virtual environment; Streamlit at `localhost:8501`  
**Branch tested:** `feature/rag-retrieval-evaluation-v2`  
**Evidence:** owner-provided screenshots of terminal and application during an interactive local smoke-test session. Original screenshots are not committed to this repository, and the run was not independently replayed.

## Observed offline validations

- **Unit/API suite:** `python -m unittest discover -s tests -v` — **40 tests passed**, according to the local terminal screenshot.
- **Retrieval fixture:** `python -m sentinel.evaluate_retrieval` — mean precision@k **1.0**, mean recall@k **1.0**, on five author-labeled, synthetic cases. This evaluation is intentionally tiny and co-designed with the corpus; it is **not** evidence of production retrieval accuracy or of Gemini quality.
- **Vulnerable bundled Python example:** seven lines analyzed, one `PY-SQL-001` rule-level high finding at line 6, showing SQL constructed with an f-string. BM25 produced three author-written editorial summaries (`OWASP-SQLI-PARAM-v1`, `CWE89-QUERY-v1`, `OWASP-SQLI-VALIDATION-v1`) and separate source links.
- **Parameterized bundled Python example:** six lines analyzed and **zero static findings**. The UI displayed the limitation warning that a clean scan does not prove code safety, and showed no retrieved passages for that example.

## Observed live Gemini review with BM25 v2

The owner enabled optional Gemini review in the local Streamlit UI using a personal key kept outside GitHub, with explicit consent to send the **bundled synthetic vulnerable Python example** to the Google Gemini API. The displayed **Revisão opcional Gemini** section responded in Portuguese, described the possible SQL injection indicator at line 6, referred to OWASP/CWE context, recommended parameterized queries and checked whether `username` might be externally controlled. It identified the result as a hypothesis requiring manual confirmation.

The application rendered static scanner evidence, retrieved BM25 summaries, reference links, and optional model output as separate sections. The screenshot does **not** show token usage, latency, full untruncated text of every suggestion, raw request/response, model version in the UI, nor a quantitative scoring of grounding faithfulness.

## Qualitative assessment

- **Pass:** end-to-end local integration displayed the expected static finding, retrieved references, and a live contextual Gemini response for one vulnerable synthetic example.
- **Appropriate guidance:** parameterized SQL queries are the relevant primary mitigation. Whether `username` is attacker-controlled remains unresolved by this limited example.
- **Not proven:** source passage fidelity; citation-by-claim matching; full RAG hallucination assessment; deployed public Gemini access; detection on real-world repositories; secure or compliant processing of proprietary code.

## Follow-up before broader claims

1. Validate that prompt construction includes BM25 passage IDs with an offline fake Gemini client test.
2. Independently verify editorial passage text against upstream documentation and archive source revision identifiers.
3. Keep public Gemini calls off without authentication, quotas, privacy constraints and abuse controls.
4. Consider private further tests on synthetic safe and ambiguous cases and independently label results.

**External reference links checked 2026-11-12:** [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html), [MITRE CWE-89](https://cwe.mitre.org/data/definitions/89.html), [MITRE CWE-78](https://cwe.mitre.org/data/definitions/78.html), and [Python subprocess security](https://docs.python.org/3/library/subprocess.html#security-considerations). This URL check is not an upstream content snapshot review.
