"""Local ONNX embeddings — no key, no network, no cost."""

from __future__ import annotations

from typing import Sequence

from app.providers.base import Embeddings
from app.registry import register


@register("embeddings", "fastembed")
class FastEmbedEmbeddings(Embeddings):
    _model = None

    def _load(self):
        if self._model is None:
            from fastembed import TextEmbedding  # optional dependency
            type(self)._model = TextEmbedding("BAAI/bge-small-en-v1.5")
        return self._model

    def healthy(self) -> bool:
        try:
            import fastembed  # noqa: F401
            return True
        except Exception:
            return False

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        model = self._load()
        return [list(map(float, v)) for v in model.embed(list(texts))]
