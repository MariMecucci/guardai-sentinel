"""Offline BM25 retrieval over a small versioned, editorial corpus.

No network or embeddings. The corpus is vetted by allowlisted rule IDs; user
source code is never used as a retrieval query or executed.
"""
import json
import math
import re
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from .rag import Reference

CORPUS_PATH = Path(__file__).resolve().parent / "knowledge" / "security_passages.json"
TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")
STOP = {"the", "and", "with", "from", "when", "this", "that", "into", "where", "can", "not", "for", "are", "use", "than", "your"}
RULE_QUERIES = {
    "PY-SQL-001": "sql injection query dynamic interpolation prepared parameterized bound",
    "SQL-TEMPLATE-001": "sql template query interpolation injection prepared parameters",
    "PY-SHELL-002": "python subprocess shell true command injection arguments untrusted",
}

@dataclass(frozen=True)
class Passage:
    id: str
    source_id: str
    source_title: str
    source_url: str
    source_version: str
    topics: tuple[str, ...]
    rule_ids: tuple[str, ...]
    text: str

    def to_dict(self) -> dict:
        return {
            "id": self.id, "source_id": self.source_id,
            "title": self.source_title, "url": self.source_url,
            "source_version": self.source_version, "text": self.text,
        }

def _tokens(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if len(t) > 2 and t not in STOP]

def load_passages(path: Path = CORPUS_PATH) -> tuple[Passage, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        raise ValueError("Unsupported knowledge corpus schema")
    out = []
    ids = set()
    for entry in data["passages"]:
        if entry["id"] in ids:
            raise ValueError("Duplicate passage ID")
        ids.add(entry["id"])
        if not entry["source_url"].startswith("https://"):
            raise ValueError("Non-HTTPS reference")
        if not entry["text"].strip() or not entry["rule_ids"]:
            raise ValueError("Incomplete passage")
        out.append(Passage(
            id=entry["id"], source_id=entry["source_id"],
            source_title=entry["source_title"], source_url=entry["source_url"],
            source_version=entry["source_version"], topics=tuple(entry["topics"]),
            rule_ids=tuple(entry["rule_ids"]), text=entry["text"]))
    return tuple(out)

def retrieve_passages(findings, *, limit: int = 4, passages: tuple[Passage, ...] | None = None) -> list[Passage]:
    """Use BM25 to rank rule-allowlisted passages. Unknown rules retrieve nothing."""
    if limit <= 0:
        return []
    rules = sorted({f.rule_id for f in findings if f.rule_id in RULE_QUERIES})
    if not rules:
        return []
    corpus = passages if passages is not None else load_passages()
    candidates = [p for p in corpus if set(p.rule_ids).intersection(rules)]
    if not candidates:
        return []
    query = _tokens(" ".join(RULE_QUERIES[r] for r in rules))
    if not query:
        return []
    documents = [_tokens(" ".join([p.text, *p.topics])) for p in candidates]
    avglen = sum(len(d) for d in documents) / len(documents)
    scored = []
    for p, tokens in zip(candidates, documents):
        score = 0.0
        for term in set(query):
            tf = tokens.count(term)
            df = sum(term in d for d in documents)
            if tf == 0:
                continue
            idf = math.log(1 + (len(documents) - df + 0.5) / (df + 0.5))
            score += idf * tf * 2.2 / (tf + 1.2 * (0.25 + 0.75 * len(tokens) / max(avglen, 1)))
        if score > 0:
            scored.append((score, p))
    scored.sort(key=lambda pair: (-pair[0], pair[1].id))
    return [p for _, p in scored[:limit]]

def grounding_passage_context(passages: list[Passage]) -> str:
    if not passages:
        return "Nenhum trecho documental curado foi recuperado. Não alegue suporte de fontes."
    return "\n".join(
        f"[{p.id}] ({p.source_version}) {p.source_title} — {p.source_url}\n"
        f"RESUMO EDITORIAL NÃO VERIFICADO AUTOMATICAMENTE: {p.text}"
        for p in passages
    )
