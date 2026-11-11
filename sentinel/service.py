"""Shared service used by Streamlit, CLI and FastAPI."""
from .static import scan_code
from .models import Report
from .rag import retrieve_for_findings


def analyze_code(filename: str, source: str, *, use_ai: bool = False, api_key: str | None = None) -> Report:
    report = scan_code(filename, source)
    report.grounding_references = [ref.to_dict() for ref in retrieve_for_findings(report.findings)]
    if use_ai:
        from .ai import enhance_with_gemini
        enhance_with_gemini(report, source, api_key=api_key)
    return report
