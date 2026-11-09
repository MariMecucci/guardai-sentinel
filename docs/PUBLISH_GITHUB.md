# Publishing GuardAI Sentinel to GitHub

The GitHub connector may update repositories, but cannot create new ones. To create an independent repository:

1. Open https://github.com/new
2. Owner: `MariMecucci`; name: `guardai-sentinel`; visibility: **Public**.
3. Do **not** initialize it with an extra README, license, or .gitignore; the ZIP already includes those files.
4. Extract `guardai-sentinel-mvp.zip` and open the **inner** `guardai-sentinel` folder in VS Code.
5. In PowerShell, inside that folder, run:

```powershell
git init -b main
git add .
git commit -m "feat: initialize GuardAI Sentinel AI engineering MVP"
git remote add origin https://github.com/MariMecucci/guardai-sentinel.git
git push -u origin main
```

If you are prompted to log in to GitHub, follow the browser/Git Credential Manager login flow. Never paste a GitHub personal access token into chat or commit it.

**Verify** the repository has `streamlit_app.py`, `sentinel/`, `tests/` and `.github/workflows/test.yml`, and open GitHub Actions. A successful CI run confirms tests in GitHub's environment (different from local tests).

## Optional Streamlit Community Cloud

- Visit https://share.streamlit.io/
- Connect your GitHub account and create an app from `MariMecucci/guardai-sentinel`, branch `main`, entrypoint `streamlit_app.py`.
- Keep Gemini integration **off** for public demo (`GUARDAI_ENABLE_AI=0`).
- Deploy and verify the four synthetic examples. Do not publish API keys in repository code or settings screenshots.

The FastAPI endpoint is meant for **local use only** until authentication, TLS and rate limits are in place.
