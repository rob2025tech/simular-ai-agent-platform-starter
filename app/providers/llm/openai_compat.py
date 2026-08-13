"""One adapter covering every OpenAI-compatible /chat/completions endpoint.

Ollama, Groq, OpenRouter, Together and OpenAI itself all speak this dialect, so
switching between free-local and paid-hosted is a base-url change.
"""

from __future__ import annotations

from typing import Any, Sequence

import httpx

from app.providers.base import LLM, Completion, Message
from app.registry import register
from app.settings import settings


class OpenAICompatLLM(LLM):
    base_url: str = ""
    api_key: str = ""
    model: str = ""
    cost_per_1k: float = 0.0

    async def complete(self, messages: Sequence[Message], **kw: Any) -> Completion:
        headers = {"content-type": "application/json"}
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        payload = {
            "model": kw.get("model", self.model),
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": kw.get("temperature", 0.2),
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{self.base_url}/chat/completions",
                                     json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        usage = data.get("usage") or {}
        prompt_t = int(usage.get("prompt_tokens") or 0)
        out_t = int(usage.get("completion_tokens") or 0)
        return Completion(
            text=data["choices"][0]["message"]["content"],
            provider=self.name,
            model=payload["model"],
            prompt_tokens=prompt_t,
            completion_tokens=out_t,
            cost_usd=(prompt_t + out_t) / 1000 * self.cost_per_1k,
        )

    def healthy(self) -> bool:
        if not self.base_url:
            return False
        try:
            httpx.get(f"{self.base_url}/models", timeout=5,
                      headers={"authorization": f"Bearer {self.api_key}"} if self.api_key else {})
            return True
        except Exception:
            return False


@register("llm", "ollama")
class OllamaLLM(OpenAICompatLLM):
    def __init__(self) -> None:
        cfg = settings()
        self.base_url = cfg.ollama_base_url.rstrip("/") + "/v1"
        self.model = cfg.ollama_model


@register("llm", "groq")
class GroqLLM(OpenAICompatLLM):
    def __init__(self) -> None:
        self.base_url = "https://api.groq.com/openai/v1"
        self.api_key = settings().groq_api_key
        self.model = "llama-3.3-70b-versatile"

    def healthy(self) -> bool:
        return bool(self.api_key)


@register("llm", "openrouter")
class OpenRouterLLM(OpenAICompatLLM):
    def __init__(self) -> None:
        self.base_url = "https://openrouter.ai/api/v1"
        self.api_key = settings().openrouter_api_key
        self.model = "meta-llama/llama-3.3-70b-instruct"
        self.cost_per_1k = 0.10

    def healthy(self) -> bool:
        return bool(self.api_key)


@register("llm", "openai")
class OpenAILLM(OpenAICompatLLM):
    def __init__(self) -> None:
        cfg = settings()
        self.base_url = cfg.openai_base_url.rstrip("/")
        self.api_key = cfg.openai_api_key
        self.model = "gpt-4o-mini"
        self.cost_per_1k = 0.60

    def healthy(self) -> bool:
        return bool(self.api_key)
