from __future__ import annotations

from typing import Any, Sequence

import httpx

from app.providers.base import LLM, Completion, Message
from app.registry import register
from app.settings import settings

API = "https://generativelanguage.googleapis.com/v1beta/models"


@register("llm", "gemini")
class GeminiLLM(LLM):
    def __init__(self) -> None:
        self.api_key = settings().gemini_api_key
        self.model = "gemini-2.0-flash"

    def healthy(self) -> bool:
        return bool(self.api_key)

    async def complete(self, messages: Sequence[Message], **kw: Any) -> Completion:
        system = "\n".join(m.content for m in messages if m.role == "system")
        contents = [
            {"role": "model" if m.role == "assistant" else "user",
             "parts": [{"text": m.content}]}
            for m in messages if m.role != "system"
        ]
        payload: dict[str, Any] = {"contents": contents}
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{API}/{self.model}:generateContent",
                                     params={"key": self.api_key}, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text = data["candidates"][0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata") or {}
        return Completion(text=text, provider="gemini", model=self.model,
                          prompt_tokens=int(usage.get("promptTokenCount") or 0),
                          completion_tokens=int(usage.get("candidatesTokenCount") or 0))
