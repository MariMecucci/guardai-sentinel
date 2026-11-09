"""Bounded, non-executing rules that favor evidence over speculative findings.

This is intentionally a small rule engine for an MVP, not a comprehensive SAST tool.
Python uses AST for SQL interpolation. SQL checks only explicit constructions.
"""
import ast
import re
from pathlib import Path

from .models import Finding, Report

MAX_SOURCE_BYTES = 30_000
MAX_LINES = 600
SUFFIXES = {".py": "python", ".sql": "sql"}


def validate_source(filename: str, source: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUFFIXES:
        raise ValueError("Somente arquivos .py e .sql são aceitos.")
    if not source or not source.strip():
        raise ValueError("O código não pode estar vazio.")
    if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ValueError(f"Limite de {MAX_SOURCE_BYTES} bytes excedido.")
    if len(source.splitlines()) > MAX_LINES:
        raise ValueError(f"Limite de {MAX_LINES} linhas excedido.")
    if "\x00" in source:
        raise ValueError("O código contém byte nulo e não pode ser analisado.")
    return SUFFIXES[suffix]


def _snippet(text: str, limit: int = 130) -> str:
    # Do not echo entire code or credentials in reports.
    normalized = re.sub(r"(?i)(password|api[_-]?key|secret|token)\s*=\s*['\"][^'\"]+['\"]", r"\1=<redacted>", text.strip())
    return (normalized[:limit] + "…") if len(normalized) > limit else normalized


def _strings(node: ast.AST) -> list[str]:
    out: list[str] = []
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
    return out


def _looks_like_sql(node: ast.AST) -> bool:
    return bool(re.search(r"\b(SELECT|INSERT|UPDATE|DELETE)\b", " ".join(_strings(node)), re.I))


def _is_dynamic(node: ast.AST) -> bool:
    return isinstance(node, (ast.JoinedStr, ast.BinOp, ast.Call))


def _extract_statement_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and _is_dynamic(node.value) and _looks_like_sql(node.value):
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
    return names


def _python_findings(source: str) -> tuple[list[Finding], list[str]]:
    findings: list[Finding] = []
    warnings: list[str] = []
    lines = source.splitlines()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [], [f"Python com erro de sintaxe próximo à linha {e.lineno}; análise parcial indisponível."]

    sql_vars = _extract_statement_names(tree)
    reported: set[int] = set()
    for node in ast.walk(tree):
        # SQL f-string or concat on an assignment or direct execute call.
        if isinstance(node, ast.Assign) and _is_dynamic(node.value) and _looks_like_sql(node.value):
            candidate = node.value
            if not (isinstance(candidate, ast.JoinedStr) or isinstance(candidate, ast.BinOp) and isinstance(candidate.op, ast.Add)):
                continue
            line = node.lineno
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"execute", "executemany"} and node.args:
            candidate = node.args[0]
            if isinstance(candidate, ast.Name) and candidate.id in sql_vars:
                # Already report at SQL construction; don't duplicate.
                continue
            if not (_looks_like_sql(candidate) and isinstance(candidate, (ast.JoinedStr, ast.BinOp))):
                continue
            line = node.lineno
        else:
            continue
        if line in reported:
            continue
        reported.add(line)
        findings.append(Finding(
            rule_id="PY-SQL-001", title="Possível SQL Injection por interpolação de SQL",
            severity="high", line=line,
            evidence=_snippet(lines[line - 1]),
            why="A consulta SQL aparenta incorporar valores dinâmicos na própria sintaxe.",
            remediation="Use consultas parametrizadas com placeholders e parâmetros separados, e valide no contexto da aplicação.",
            confidence="medium", reference="https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
        ))

    # subprocess with shell=True (risk depends on trust boundary, so not confirmed vulnerability).
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and any(k.arg == "shell" and isinstance(k.value, ast.Constant) and k.value.value is True for k in node.keywords):
            if not isinstance(node.func, (ast.Attribute, ast.Name)):
                continue
            name = node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
            if name not in {"run", "call", "Popen", "check_output", "check_call"}:
                continue
            findings.append(Finding(
                rule_id="PY-SHELL-002", title="Execução de shell habilitada",
                severity="medium", line=node.lineno, evidence=_snippet(lines[node.lineno - 1]),
                why="shell=True aumenta a superfície de ataque caso o comando contenha dados não confiáveis.",
                remediation="Prefira uma lista de argumentos e shell=False; valide todas as entradas.",
                confidence="medium", reference="https://docs.python.org/3/library/subprocess.html",
            ))

    return sorted(findings, key=lambda f: (f.line, f.rule_id)), warnings


def _sql_findings(source: str) -> tuple[list[Finding], list[str]]:
    """Detect explicit client-side SQL template markers, not SQL dialect parameters."""
    findings = []
    for idx, line in enumerate(source.splitlines(), start=1):
        if re.search(r"\b(SELECT|INSERT|UPDATE|DELETE)\b", line, re.I) and (
            re.search(r"\$\{(?:user|input|username|email|password)\w*\}", line, re.I)
            or re.search(r"\{(?:user|input|username|email|password)\w*\}", line, re.I)
        ):
            findings.append(Finding(
                rule_id="SQL-TEMPLATE-001", title="Marcador de interpolação em consulta SQL",
                severity="medium", line=idx, evidence=_snippet(line),
                why="O arquivo contém um marcador de template dentro da consulta; verifique como a aplicação o substitui.",
                remediation="Passe os valores por parâmetros suportados pelo driver, sem montar SQL com strings.",
                confidence="low", reference="https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
            ))
    return findings, []


def scan_code(filename: str, source: str) -> Report:
    language = validate_source(filename, source)
    findings, warnings = _python_findings(source) if language == "python" else _sql_findings(source)
    if not findings:
        warnings.append("Nenhuma regra do MVP detectou um padrão. Isso não confirma que o código é seguro.")
    return Report(filename=Path(filename).name, language=language,
                  findings=findings, lines_scanned=len(source.splitlines()), warnings=warnings)
