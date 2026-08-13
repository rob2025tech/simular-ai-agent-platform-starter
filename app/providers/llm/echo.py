"""Zero-dependency stub so the platform runs with no vendor at all."""

from __future__ import annotations

from typing import Any, Sequence

from app.providers.base import LLM, Completion, Message
from app.registry import register


@register("llm", "echo")
class EchoLLM(LLM):
    async def complete(self, messages: Sequence[Message], **kw: Any) -> Completion:
        last = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return Completion(text=f"[echo] {last}", provider="echo", model="echo")
