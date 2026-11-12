"""Simple interoperable data structures; no runtime framework dependency."""
from dataclasses import asdict, dataclass, field
from typing import Literal

Severity = Literal["low", "medium", "high", "critical"]


@dataclass(frozen=True)
class Finding:
    rule_id: str
    title: str
    severity: Severity
    line: int
    evidence: str
    why: str
    remediation: str
    source: str = "static"
    confidence: str = "medium"
    reference: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Report:
    filename: str
    language: str
    findings: list[Finding] = field(default_factory=list)
    lines_scanned: int = 0
    model: str | None = None
    ai_summary: str | None = None
    ai_suggestions: list[str] = field(default_factory=list)
    grounding_references: list[dict] = field(default_factory=list)
    retrieved_passages: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "language": self.language,
            "lines_scanned": self.lines_scanned,
            "findings": [finding.to_dict() for finding in self.findings],
            "finding_count": len(self.findings),
            "model": self.model,
            "ai_summary": self.ai_summary,
            "ai_suggestions": list(self.ai_suggestions),
            "grounding_references": list(self.grounding_references),
            "retrieved_passages": list(self.retrieved_passages),
            "warnings": list(self.warnings),
            "disclaimer": "Triagem estática educacional, não uma auditoria nem prova de ausência de vulnerabilidades.",
        }
