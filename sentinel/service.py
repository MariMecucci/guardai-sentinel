"""Shared service used by Streamlit, CLI and FastAPI."""
from .static import scan_code
from .models import Report


def analyze_code(filename: str, source: str, *, use_ai: bool = False, api_key: str | None = None) -> Report:
    report = scan_code(filename, source)
    if use_ai:
        from .ai import enhance_with_gemini
        enhance_with_gemini(report, source, api_key=api_key)
    return report
