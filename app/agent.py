"""A deliberately small tool-using loop — the point is the swappable plumbing."""

from __future__ import annotations

import re
from typing import Any

from app.providers.base import Message
from app.router import select


SYSTEM = (
    "You are a concise assistant. If you need current facts, reply with exactly "
    "SEARCH: <query> on its own line and nothing else. Otherwise answer directly."
)


async def run(user_input: str, max_steps: int | None = None) -> dict[str, Any]:
    from app.settings import settings

    llm = select("llm")
    obs = select("obs")
    steps = max_steps or settings().agent_max_steps

    history = [Message("system", SYSTEM), Message("user", user_input)]
    trace: list[dict[str, Any]] = []
    total_cost = 0.0

    for step in range(steps):
        completion = await llm.complete(history)
        total_cost += completion.cost_usd
        obs.event("llm.complete", provider=completion.provider, step=step,
                  cost_usd=completion.cost_usd)
        trace.append({"step": step, "provider": completion.provider,
                      "output": completion.text, "cost_usd": completion.cost_usd})

        match = re.match(r"\s*SEARCH:\s*(.+)", completion.text)
        if not match:
            return {"answer": completion.text.strip(), "cost_usd": round(total_cost, 6),
                    "llm": completion.provider, "trace": trace}

        query = match.group(1).strip()
        searcher = select("search")
        results = await searcher.search(query, k=5)
        obs.event("search", provider=searcher.name, query=query, hits=len(results))
        trace.append({"step": step, "tool": "search", "provider": searcher.name,
                      "query": query, "hits": len(results)})

        evidence = "\n".join(f"- {r.title}: {r.snippet} ({r.url})" for r in results) or "no results"
        history.append(Message("assistant", completion.text))
        history.append(Message("user", f"Search results for '{query}':\n{evidence}\n\nNow answer."))

    return {"answer": "step budget exhausted", "cost_usd": round(total_cost, 6), "trace": trace}
