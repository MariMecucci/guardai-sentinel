# MVP build verification — 2026-11-09

Validated locally during project preparation:

- Python module compilation: success (`python -m compileall -q sentinel streamlit_app.py tests`).
- Unit and FastAPI integration suite: **22 tests passed**, 0 failures (`python -m unittest discover -s tests -v`).
- CLI scanner detected `PY-SQL-001` in the synthetic `examples/vulnerable_login.py` and produced structured JSON.
- Deterministic 32-example synthetic benchmark: TP=17, FP=1, TN=11, FN=3; precision=0.9444; recall=0.85; F1=0.8947.
- No live Gemini API calls made: Google GenAI SDK and personal key are not configured in this environment.
- Streamlit app syntax compiled, but no live browser deployment completed in this environment.
- GitHub CI workflow **prepared**; CI will only run after the code is pushed to a repository.

**Do not represent local tests as external deployment or LLM validation.**

## Addendum — 2026-11-10: published CI and browser smoke tests

- The independent repository is published at https://github.com/MariMecucci/guardai-sentinel.
- The GitHub Actions validation workflow completed **successfully** on the initial application commit: https://github.com/MariMecucci/guardai-sentinel/actions/runs/42686841544.
- The Streamlit demo is published at https://guardai-sentinel-sjpa8g326gtpaywtttcp8c.streamlit.app/.
- The repository owner provided browser screenshots of the vulnerable example producing **1 high-severity pattern** and the parameterized example producing **0 findings**. See [public demo validation](PUBLIC_DEMO_VALIDATION.md).
- **Gemini live API remains untested and disabled by default**; successful static results do not validate AI model behavior.

The initial section above documents the project preparation state on 2026-11-09; this addendum records later validations without retroactively rewriting those observations.

## Gemini API smoke tests — 2026-11-10

The repository owner ran two private Gemini API diagnostics in the local Windows/VS Code environment using the model `gemini-3.5-flash-lite` and a personal API key held only in the terminal session. The owner supplied screenshots of both successful executions:

- `python -m sentinel.diagnose_gemini`: **success**, simple response.
- `python -m sentinel.diagnose_gemini --structured`: **success**, JSON-structured response.

These observations demonstrate live API connectivity, authentication, and acceptance of a structured-output request with the tested model. They **do not yet establish** that the application's full security-review prompt succeeds, that Gemini's recommendations are accurate, or that Gemini is enabled in the public Streamlit demo. No API key or response payload is stored here.

## Addendum — 2026-11-10: end-to-end local Gemini review

The repository owner supplied a screenshot of the **local** Streamlit app with both explicit Gemini consent checkboxes selected. The *Python — SQL vulnerável* synthetic example was analyzed using the static rules and the live Gemini integration. The app displayed one static finding (`PY-SQL-001`, high, line 6) and a separate **Revisão opcional Gemini** section with a generated Portuguese summary and defensive recommendations. No Gemini error was displayed in that run.

This supersedes the earlier outstanding 'full security-review prompt remains to be verified' limitation for **this single synthetic example only**; it does not imply general LLM accuracy, production-grade security, model performance benchmarks, or public-hosted Gemini access. Full details in [LOCAL_GEMINI_VALIDATION.md](LOCAL_GEMINI_VALIDATION.md).

## Addendum — 2026-11-10: local Gemini review of a parameterized example

The repository owner supplied a second local Streamlit screenshot for the synthetic **Python — Consulta segura** example, with explicit consent to send the code to Gemini. The app showed **0 static findings**, **6 Python lines**, and a separate **Revisão opcional Gemini** response correctly recognizing bound SQL parameters. The model also offered context-dependent hardening recommendations, which are not proven vulnerabilities. The UI cautioned that 0 findings is not proof of safety. See [LOCAL_GEMINI_VALIDATION.md](LOCAL_GEMINI_VALIDATION.md).

The two observed examples do **not** constitute an LLM quality benchmark. The public demo continues to have Gemini disabled by default.
