"""Capability ports. A vendor is anything that satisfies one of these."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class Message:
    role: str
    content: str


@dataclass
class Completion:
    text: str
    provider: str
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


class Provider(ABC):
    """Base class for every vendor adapter."""

    capability: str = ""
    name: str = ""

    def healthy(self) -> bool:
        """Cheap reachability/credential check. Router skips unhealthy providers."""
        return True


class LLM(Provider):
    capability = "llm"

    @abstractmethod
    async def complete(self, messages: Sequence[Message], **kw: Any) -> Completion: ...


class Embeddings(Provider):
    capability = "embeddings"

    @abstractmethod
    async def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class VectorStore(Provider):
    capability = "vector"

    @abstractmethod
    async def upsert(self, ids: Sequence[str], vectors: Sequence[Sequence[float]],
                     payloads: Sequence[dict[str, Any]]) -> None: ...

    @abstractmethod
    async def query(self, vector: Sequence[float], k: int = 5) -> list[dict[str, Any]]: ...


class Search(Provider):
    capability = "search"

    @abstractmethod
    async def search(self, query: str, k: int = 5) -> list[SearchResult]: ...


class Storage(Provider):
    capability = "storage"

    @abstractmethod
    async def put(self, key: str, value: dict[str, Any]) -> None: ...

    @abstractmethod
    async def get(self, key: str) -> dict[str, Any] | None: ...


class Observability(Provider):
    capability = "obs"

    @abstractmethod
    def event(self, name: str, **fields: Any) -> None: ...
