"""Small, offline, deterministic retrieval layer for an educational security RAG MVP.

References are curated *summaries*, not downloaded external documents. Matching
uses scanner rule IDs, never arbitrary prompt text. No network, embedding API,
vector database, or untrusted document ingestion occurs here.
"""
from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class Reference:
    id: str
    title: str
    url: str
    summary: str
    applicable_rules: tuple[str, ...]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["applicable_rules"] = list(self.applicable_rules)
        return data

REFERENCES = (
    Reference(
        id="OWASP-SQLI-PREVENTION",
        title="OWASP SQL Injection Prevention Cheat Sheet",
        url="https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
        summary="Use prepared statements with bound parameters for untrusted values. Input validation is defense in depth, not a replacement for parameterization.",
        applicable_rules=("PY-SQL-001", "SQL-TEMPLATE-001"),
    ),
    Reference(
        id="CWE-89",
        title="MITRE CWE-89: Improper Neutralization of Special Elements used in an SQL Command",
        url="https://cwe.mitre.org/data/definitions/89.html",
        summary="Building SQL commands from externally influenced strings can change query meaning. Investigate actual input control and query construction before concluding exploitability.",
        applicable_rules=("PY-SQL-001", "SQL-TEMPLATE-001"),
    ),
    Reference(
        id="PYTHON-SUBPROCESS",
        title="Python subprocess documentation: Security Considerations",
        url="https://docs.python.org/3/library/subprocess.html#security-considerations",
        summary="Review the subprocess shell=True trust boundary. Prefer shell=False with an argument list where practical; shell use is not automatically exploitable.",
        applicable_rules=("PY-SHELL-002",),
    ),
    Reference(
        id="CWE-78",
        title="MITRE CWE-78: OS Command Injection",
        url="https://cwe.mitre.org/data/definitions/78.html",
        summary="If externally influenced input reaches operating-system command construction, command injection may arise. Confirm dataflow instead of treating shell=True as proof.",
        applicable_rules=("PY-SHELL-002",),
    ),
)

def retrieve_for_findings(findings, *, limit: int = 4) -> list[Reference]:
    """Return stable, de-duplicated references for supported static rule IDs."""
    if limit <= 0:
        return []
    rules = {f.rule_id for f in findings}
    return [ref for ref in REFERENCES if rules.intersection(ref.applicable_rules)][:limit]

def build_grounding_context(references: list[Reference]) -> str:
    """Grounding context; labels are fixed IDs, not model-provided citations."""
    if not references:
        return "Nenhuma referência curada corresponde aos achados. Não alegue suporte documental."
    return "\n".join(
        f"[{ref.id}] {ref.title}\nResumo curado: {ref.summary}\nURL: {ref.url}"
        for ref in references
    )
