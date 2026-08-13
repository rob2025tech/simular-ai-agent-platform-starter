from __future__ import annotations

from typing import Any, Sequence

import httpx

from app.providers.base import LLM, Completion, Message
from app.registry import register
from app.settings import settings


@register("llm", "anthropic")
class AnthropicLLM(LLM):
    def __init__(self) -> None:
        self.api_key = settings().anthropic_api_key
        self.model = "claude-sonnet-4-20250514"
        self.cost_per_1k = 0.90

    def healthy(self) -> bool:
        return bool(self.api_key)

    async def complete(self, messages: Sequence[Message], **kw: Any) -> Completion:
        system = "\n".join(m.content for m in messages if m.role == "system")
        turns = [{"role": m.role, "content": m.content}
                 for m in messages if m.role in ("user", "assistant")]
        payload: dict[str, Any] = {"model": self.model, "max_tokens": kw.get("max_tokens", 1024),
                                   "messages": turns}
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                json=payload,
                headers={"x-api-key": self.api_key,
                         "anthropic-version": "2023-06-01",
                         "content-type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()

        usage = data.get("usage") or {}
        prompt_t = int(usage.get("input_tokens") or 0)
        out_t = int(usage.get("output_tokens") or 0)
        return Completion(text=data["content"][0]["text"], provider="anthropic",
                          model=self.model, prompt_tokens=prompt_t, completion_tokens=out_t,
                          cost_usd=(prompt_t + out_t) / 1000 * self.cost_per_1k)
