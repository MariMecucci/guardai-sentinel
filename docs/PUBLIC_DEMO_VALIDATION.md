# Public Streamlit demo — manually observed smoke tests

**Date:** 2026-11-10  
**App:** https://guardai-sentinel-sjpa8g326gtpaywtttcp8c.streamlit.app/  
**Code:** [GitHub repository](https://github.com/MariMecucci/guardai-sentinel)

## Provenance

The repository owner ran these two examples in a browser and shared screenshots of the deployed Streamlit UI. Results below are **observations from those screenshots**, not an independent security audit, browser automation, or a live Gemini API test. Screenshots are not included in this repository.

## Case A — vulnerable synthetic Python example

- Selected UI example: **Python — SQL vulnerável**
- Button: **Analisar código**
- Language: **PYTHON**; lines scanned: **7**
- Findings: **1**
- Finding: `HIGH · Possível SQL Injection por interpolação de SQL · linha 6`
- Rule: `PY-SQL-001`; confidence **medium**
- Evidence displayed: `query = f"SELECT id FROM users WHERE username = '{username}'"`
- Remediation displayed: use parameterized queries with placeholders and separated parameters; validate in application context
- Result: **expected rule triggered**

## Case B — secure synthetic Python example

- Selected UI example: **Python — Consulta segura**
- Button: **Analisar código**
- Language: **PYTHON**; lines scanned: **6**
- Findings: **0**
- Warning displayed: *Nenhuma regra do MVP detectou um padrão. Isso não confirma que o código é seguro.*
- Result: **expected rule not triggered**

## What these tests establish

The public Streamlit UI loaded, accepted the two built-in examples, executed the local static scan, and displayed expected findings and cautionary messaging.

**Not established:** any general absence of vulnerabilities, real-world detection accuracy, Gemini API connectivity, private-code safety, app uptime, or security of the hosted service.

## Other verification

- [22 local automated tests and 32 synthetic labeled examples](BUILD_VALIDATION.md)
- [GitHub Actions passing run](https://github.com/MariMecucci/guardai-sentinel/actions/runs/42686841544)
- [Evaluation limitations and metrics](EVALUATION.md)
