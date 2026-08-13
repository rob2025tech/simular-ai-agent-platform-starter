from __future__ import annotations

import httpx

from app.providers.base import Search, SearchResult
from app.registry import register
from app.settings import settings


@register("search", "tavily")
class TavilySearch(Search):
    """Free tier: ~1k credits/month, no card required."""

    def __init__(self) -> None:
        self.api_key = settings().tavily_api_key

    def healthy(self) -> bool:
        return bool(self.api_key)

    async def search(self, query: str, k: int = 5) -> list[SearchResult]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post("https://api.tavily.com/search",
                                     json={"api_key": self.api_key, "query": query,
                                           "max_results": k})
            resp.raise_for_status()
            return [SearchResult(title=r.get("title", ""), url=r.get("url", ""),
                                 snippet=r.get("content", ""))
                    for r in resp.json().get("results", [])]


@register("search", "brave")
class BraveSearch(Search):
    def __init__(self) -> None:
        self.api_key = settings().brave_api_key

    def healthy(self) -> bool:
        return bool(self.api_key)

    async def search(self, query: str, k: int = 5) -> list[SearchResult]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": k},
                headers={"x-subscription-token": self.api_key,
                         "accept": "application/json"},
            )
            resp.raise_for_status()
            web = resp.json().get("web", {}).get("results", [])
            return [SearchResult(title=r.get("title", ""), url=r.get("url", ""),
                                 snippet=r.get("description", "")) for r in web]
