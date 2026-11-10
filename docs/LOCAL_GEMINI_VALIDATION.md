# GuardAI Sentinel — Local Gemini end-to-end verification

**Date:** 2026-11-10  
**Environment:** Windows / VS Code, local Streamlit app (`localhost:8501`)  
**Model:** `gemini-3.5-flash-lite`  
**Evidence source:** user-provided screenshots of the running application and PowerShell terminal, reviewed during the project workflow. The original screenshots are not archived in this repository.

## What was actually tested

The repository owner configured a personal Gemini API key privately in a local terminal (not committed to GitHub), set `GUARDAI_ENABLE_AI=1`, and selected both user-interface controls:

- **Solicitar revisão Gemini**
- **Autorizo enviar este código ao Gemini**

The input was the bundled fictional example **Python — SQL vulnerável**, featuring SQL constructed through f-string interpolation.

### Static analysis, observed

- **Findings:** 1
- **Language:** Python
- **Lines analyzed:** 7
- **Rule:** `PY-SQL-001`
- **Severity:** high (rule-level classification; not a contextual CVSS score)
- **Location:** line 6
- **Evidence:** direct interpolation of `username` into an SQL query
- **Primary mitigation:** parameterized queries and separate bound parameters

### Live Gemini review, observed

The application displayed the separate **Revisão opcional Gemini** section, indicating that the integration received a structured model response for the full security-review request.

The Portuguese LLM response described possible SQL Injection on line 6 and recommended:
1. Replacing the SQL f-string with parameterized `sqlite3` queries using bound parameters.
2. Validating user input; it also mentioned sanitizing input.
3. Running additional tests to establish whether the input could be influenced by a malicious user.

**Quality review:** the first recommendation directly addresses the SQL Injection mechanism. Input validation may be useful as defense in depth, but **sanitization or validation alone is not an adequate substitute for parameterized queries**. The user's ability to control this input and real-world exploitability were **not established** from the single synthetic example.

### Second local Gemini review — parameterized Python example

The repository owner selected the built-in **Python — Consulta segura** example in the local Streamlit app and opted into Gemini review and code sharing. A user-provided screenshot shows:

- **Language:** Python; **lines analyzed:** 6.
- **Static findings:** **0**.
- **Gemini response:** recognized bound SQL parameters as an effective mitigation of the SQL injection pattern demonstrated in the other example.
- **Additional advice:** continue using bound parameters; consider encrypted connections **if the database is accessed over external networks**; validate types and lengths for robustness.
- **UI warning:** *Nenhuma regra do MVP detectou um padrão. Isso não confirma que o código é seguro.*

**Quality assessment:** The model correctly distinguished the parameterized snippet from the vulnerable one. Encryption and input validation suggestions are generic context-dependent hardening measures, **not verified vulnerabilities** in the six-line example.

### Combined observations

| Local synthetic example | Static findings | Gemini interpretation | Outcome |
| --- | ---: | --- | --- |
| Python — SQL vulnerável | 1 (PY-SQL-001, high, line 6) | Interpolation creates SQL injection risk; recommends parameterization | Expected |
| Python — Consulta segura | 0 | Bound parameters mitigate the demonstrated SQL injection pattern | Expected |

These are **two qualitative end-to-end smoke tests** rather than a quantitative LLM-accuracy benchmark.

### Prior diagnostics

- `python -m sentinel.diagnose_gemini`: live simple response succeeded.
- `python -m sentinel.diagnose_gemini --structured`: live structured response succeeded.
- The final Streamlit review succeeded after earlier temporary Gemini errors and adjustments to client lifecycle/diagnostics.

## What this establishes

- The private local app can combine deterministic scanning and a real Gemini review for two authorized synthetic Python examples.
- Gemini output is shown **separately** from static evidence, with an explicit note that LLM suggestions were not independently verified.
- The source was transmitted only after explicit user opt-in for this test.

## What it does NOT establish

- No validated real-world accuracy, recall, precision, robustness, safety, or cost benchmark for Gemini.
- No demonstration of RAG or multi-agent behavior.
- No deployment of Gemini access to the publicly hosted Streamlit demo; AI remains disabled there by default.
- No claim that other files or vulnerabilities have been validated end to end beyond these two synthetic examples.

## Follow-up

1. Collect a versioned, synthetic evaluation dataset for optional LLM quality scoring, including secure, vulnerable and ambiguous examples.
2. Add retrieval of selected OWASP/CWE references and evaluate citation grounding.
3. Keep rate limiting, privacy controls, and authentication as prerequisites for any future public API-key-backed Gemini feature.
