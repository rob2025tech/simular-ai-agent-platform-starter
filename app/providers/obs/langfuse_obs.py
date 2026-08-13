from __future__ import annotations

from typing import Any

from app.providers.base import Observability
from app.registry import register
from app.settings import settings


@register("obs", "langfuse")
class LangfuseObservability(Observability):
    """Free hobby tier covers small projects."""

    def __init__(self) -> None:
        self._client = None

    def healthy(self) -> bool:
        cfg = settings()
        if not (cfg.langfuse_public_key and cfg.langfuse_secret_key):
            return False
        try:
            import langfuse  # noqa: F401
            return True
        except Exception:
            return False

    def _get(self):
        if self._client is None:
            from langfuse import Langfuse

            cfg = settings()
            self._client = Langfuse(public_key=cfg.langfuse_public_key,
                                    secret_key=cfg.langfuse_secret_key,
                                    host=cfg.langfuse_host)
        return self._client

    def event(self, name: str, **fields: Any) -> None:
        try:
            self._get().create_event(name=name, metadata=fields)
        except Exception as exc:
            print(f"[langfuse] dropped event {name}: {exc}")
