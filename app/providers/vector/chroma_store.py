"""Local, file-backed vector store. Free forever, no server to run."""

from __future__ import annotations

from typing import Any, Sequence

from app.providers.base import VectorStore
from app.registry import register
from app.settings import settings


@register("vector", "chroma")
class ChromaStore(VectorStore):
    def __init__(self) -> None:
        self._collection = None

    def healthy(self) -> bool:
        try:
            import chromadb  # noqa: F401
            return True
        except Exception:
            return False

    def _coll(self):
        if self._collection is None:
            import chromadb

            path = settings().chroma_path
            path.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(path))
            self._collection = client.get_or_create_collection("documents")
        return self._collection

    async def upsert(self, ids: Sequence[str], vectors: Sequence[Sequence[float]],
                     payloads: Sequence[dict[str, Any]]) -> None:
        self._coll().upsert(ids=list(ids), embeddings=[list(v) for v in vectors],
                            metadatas=list(payloads))

    async def query(self, vector: Sequence[float], k: int = 5) -> list[dict[str, Any]]:
        res = self._coll().query(query_embeddings=[list(vector)], n_results=k)
        return [
            {"id": i, "score": d, "payload": m}
            for i, d, m in zip(res["ids"][0], res["distances"][0], res["metadatas"][0])
        ]
