from __future__ import annotations

from typing import Sequence

import httpx

from app.providers.base import Embeddings
from app.registry import register
from app.settings import settings


@register("embeddings", "openai")
class OpenAIEmbeddings(Embeddings):
    def __init__(self) -> None:
        cfg = settings()
        self.base_url = cfg.openai_base_url.rstrip("/")
        self.api_key = cfg.openai_api_key
        self.model = "text-embedding-3-small"

    def healthy(self) -> bool:
        return bool(self.api_key)

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/embeddings",
                json={"model": self.model, "input": list(texts)},
                headers={"authorization": f"Bearer {self.api_key}"},
            )
            resp.raise_for_status()
            return [row["embedding"] for row in resp.json()["data"]]


@register("embeddings", "gemini")
class GeminiEmbeddings(Embeddings):
    def __init__(self) -> None:
        self.api_key = settings().gemini_api_key
        self.model = "text-embedding-004"

    def healthy(self) -> bool:
        return bool(self.api_key)

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{self.model}:batchEmbedContents")
        body = {"requests": [{"model": f"models/{self.model}",
                              "content": {"parts": [{"text": t}]}} for t in texts]}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, params={"key": self.api_key}, json=body)
            resp.raise_for_status()
            return [row["values"] for row in resp.json()["embeddings"]]
