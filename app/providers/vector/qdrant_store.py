from __future__ import annotations

from typing import Any, Sequence

import httpx

from app.providers.base import VectorStore
from app.registry import register
from app.settings import settings

COLLECTION = "documents"


@register("vector", "qdrant")
class QdrantStore(VectorStore):
    """Uses the REST API directly so no SDK pin is required."""

    def __init__(self) -> None:
        cfg = settings()
        self.url = cfg.qdrant_url.rstrip("/")
        self.headers = {"content-type": "application/json"}
        if cfg.qdrant_api_key:
            self.headers["api-key"] = cfg.qdrant_api_key

    def healthy(self) -> bool:
        if not self.url:
            return False
        try:
            return httpx.get(f"{self.url}/collections", headers=self.headers,
                             timeout=5).status_code < 500
        except Exception:
            return False

    async def _ensure(self, size: int) -> None:
        async with httpx.AsyncClient(timeout=30, headers=self.headers) as client:
            existing = await client.get(f"{self.url}/collections/{COLLECTION}")
            if existing.status_code == 404:
                await client.put(f"{self.url}/collections/{COLLECTION}",
                                 json={"vectors": {"size": size, "distance": "Cosine"}})

    async def upsert(self, ids: Sequence[str], vectors: Sequence[Sequence[float]],
                     payloads: Sequence[dict[str, Any]]) -> None:
        await self._ensure(len(vectors[0]))
        points = [{"id": i, "vector": list(v), "payload": p}
                  for i, v, p in zip(ids, vectors, payloads)]
        async with httpx.AsyncClient(timeout=60, headers=self.headers) as client:
            resp = await client.put(f"{self.url}/collections/{COLLECTION}/points",
                                    json={"points": points})
            resp.raise_for_status()

    async def query(self, vector: Sequence[float], k: int = 5) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=60, headers=self.headers) as client:
            resp = await client.post(f"{self.url}/collections/{COLLECTION}/points/search",
                                     json={"vector": list(vector), "limit": k,
                                           "with_payload": True})
            resp.raise_for_status()
            return [{"id": r["id"], "score": r["score"], "payload": r.get("payload")}
                    for r in resp.json()["result"]]
