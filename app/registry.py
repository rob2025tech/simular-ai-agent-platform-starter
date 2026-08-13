"""Provider registry with package auto-discovery.

Adding a vendor = dropping a decorated class into app/providers/<capability>/.
Nothing here or in the router needs to change.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections import defaultdict
from typing import Callable, Type

from app.providers.base import Provider

_REGISTRY: dict[str, dict[str, Type[Provider]]] = defaultdict(dict)
_DISCOVERED = False


def register(capability: str, name: str) -> Callable[[Type[Provider]], Type[Provider]]:
    def deco(cls: Type[Provider]) -> Type[Provider]:
        cls.capability, cls.name = capability, name
        _REGISTRY[capability][name] = cls
        return cls

    return deco


def discover() -> None:
    """Import every module under app.providers so decorators run."""
    global _DISCOVERED
    if _DISCOVERED:
        return
    import app.providers as pkg

    for mod in pkgutil.walk_packages(pkg.__path__, prefix="app.providers."):
        if mod.name.endswith(".base"):
            continue
        try:
            importlib.import_module(mod.name)
        except Exception as exc:  # a missing optional SDK must not break boot
            print(f"[registry] skipped {mod.name}: {exc}")
    _DISCOVERED = True


def available(capability: str) -> dict[str, Type[Provider]]:
    discover()
    return dict(_REGISTRY[capability])


def build(capability: str, name: str) -> Provider:
    discover()
    try:
        return _REGISTRY[capability][name]()
    except KeyError:
        known = ", ".join(sorted(_REGISTRY[capability])) or "none"
        raise LookupError(f"no {capability} provider '{name}'. known: {known}") from None
