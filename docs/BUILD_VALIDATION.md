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
