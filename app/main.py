from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app import agent, router
from app.registry import available, discover
from app.settings import settings

app = FastAPI(title="ai-agent-platform-starter", version="0.1.0")


@app.on_event("startup")
def _startup() -> None:
    discover()


class RunRequest(BaseModel):
    input: str
    max_steps: int | None = None


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "strategy": settings().routing_strategy}


@app.get("/providers")
def providers() -> dict[str, Any]:
    """Which vendors are installed, credentialed, reachable — and what they cost."""
    return {
        "strategy": settings().routing_strategy,
        "selected": {
            cap: (router.candidates(cap)[0].name if router.candidates(cap) else None)
            for cap in ("llm", "embeddings", "vector", "search", "storage", "obs")
        },
        "registered": {cap: sorted(available(cap)) for cap in
                       ("llm", "embeddings", "vector", "search", "storage", "obs")},
        "ledger": router.report(),
    }


@app.post("/agent/run")
async def agent_run(body: RunRequest) -> dict[str, Any]:
    try:
        return await agent.run(body.input, body.max_steps)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
