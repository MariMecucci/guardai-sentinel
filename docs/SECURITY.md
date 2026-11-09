# Security boundaries and threat model

## Assets and trust boundaries

- **Input code** is untrusted text, not executable instructions. Local engine parses/reads text only.
- **Gemini API key** is a secret provided by the operator, not stored in source control.
- **Gemini transmission** happens only when the operator enables the integration and explicitly opts in per scan in the UI.
- **Output suggestions** are untrusted model-generated content and must never trigger automatic code modification.

## Defenses implemented

- Input extension allowlist, encoding check in UI, byte and line limits.
- Python `ast.parse` without executing code.
- No dynamic imports or executions from uploaded source.
- AI disabled by default, with separation of static findings and model suggestions.
- JSON outputs specify evidence confidence and caveats.
- `.env` and Streamlit secrets excluded via `.gitignore`.
- No persisted user submissions in the scanner implementation.

## Not included (do not expose publicly without)

- Authentication, authorization, request quotas, abuse prevention, traffic inspection or TLS termination for the FastAPI server.
- Comprehensive secret/PII detection. Never send private code to the free Gemini API.
- Audit logging, consent-record retention or data deletion controls.
- Full-scale SAST, taint tracking, dependency CVE scanning, sandboxed execution, file-content malware scanning.

## Responsible use

Analyze only your own code or code you are authorized to inspect. Do not execute attack payloads against external systems. Code examples are synthetic and educational. If a model claims a finding, independently verify against code and repeatable tests.
