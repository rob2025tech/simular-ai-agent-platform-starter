"""Keyless web search — the default so the agent works out of the box."""

from __future__ import annotations

from app.providers.base import Search, SearchResult
from app.registry import register


@register("search", "duckduckgo")
class DuckDuckGoSearch(Search):
    def healthy(self) -> bool:
        try:
            import ddgs  # noqa: F401
            return True
        except Exception:
            try:
                import duckduckgo_search  # noqa: F401
                return True
            except Exception:
                return False

    async def search(self, query: str, k: int = 5) -> list[SearchResult]:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS  # older package name

        with DDGS() as ddgs:
            rows = list(ddgs.text(query, max_results=k))
        return [SearchResult(title=r.get("title", ""), url=r.get("href", ""),
                             snippet=r.get("body", "")) for r in rows]
