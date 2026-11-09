"""Optional stateless FastAPI API, local-first and without execution of uploaded code.

Not intended for public, unauthenticated deployment without auth and rate limiting.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .service import analyze_code

app = FastAPI(title="GuardAI Sentinel API", version="0.1.0", docs_url="/docs")


class AnalyzeRequest(BaseModel):
    filename: str = Field(max_length=120)
    source: str = Field(max_length=30_000)
    use_ai: bool = False


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "engine": "guardai-sentinel"}


@app.post("/analyze")
def analyze(req: AnalyzeRequest) -> dict:
    try:
        return analyze_code(req.filename, req.source, use_ai=req.use_ai).to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
