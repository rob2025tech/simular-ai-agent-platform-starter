from __future__ import annotations

import json
from typing import Any

from app.providers.base import Observability
from app.registry import register


@register("obs", "noop")
class NoopObservability(Observability):
    def event(self, name: str, **fields: Any) -> None:
        return None


@register("obs", "console")
class ConsoleObservability(Observability):
    def event(self, name: str, **fields: Any) -> None:
        print(f"[trace] {name} {json.dumps(fields, default=str)}")
