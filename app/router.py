"""Cost-aware provider selection.

The router reads config/providers.yaml (the cost + credit ledger), filters out
providers whose credentials are absent or whose health check fails, orders the
survivors by the active strategy, and hands back the first that works — failing
over to the next on error.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable

import yaml

from app.providers.base import Provider
from app.registry import available, build
from app.settings import settings


@dataclass
class Spec:
    name: str
    free: bool = False
    local: bool = False
    cost_per_1k: float = 0.0
    requires: list[str] | None = None
    credits: dict[str, Any] | None = None

    @property
    def credit_usd(self) -> float:
        if not self.credits:
            return 0.0
        expires = self.credits.get("expires")
        if expires:
            try:
                if date.fromisoformat(str(expires)) < date.today():
                    return 0.0
            except ValueError:
                pass
        return float(self.credits.get("remaining_usd") or 0.0)

    def credentials_present(self) -> bool:
        cfg = settings()
        for env in self.requires or []:
            if not getattr(cfg, env.lower(), ""):
                return False
        return True


def _ledger() -> dict[str, list[Spec]]:
    path = settings().providers_file
    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {
        cap: [Spec(**entry) for entry in entries]
        for cap, entries in raw.items()
    }


def _order(specs: Iterable[Spec]) -> list[Spec]:
    strategy = settings().routing_strategy
    specs = list(specs)
    if strategy == "cheapest_first":
        # free first, then ascending price
        return sorted(specs, key=lambda s: (not s.free, s.cost_per_1k))
    if strategy == "credits_first":
        # burn expiring credits before spending cash, but still prefer truly free
        return sorted(specs, key=lambda s: (s.credit_usd <= 0 and not s.free,
                                            -s.credit_usd, s.cost_per_1k))
    if strategy == "local_first":
        return sorted(specs, key=lambda s: (not s.local, not s.free, s.cost_per_1k))
    return specs


def candidates(capability: str) -> list[Spec]:
    """Ordered, usable providers for a capability."""
    registered = available(capability)
    specs = [s for s in _ledger().get(capability, []) if s.name in registered]
    # anything registered but absent from the ledger is still usable, priced unknown
    known = {s.name for s in specs}
    specs += [Spec(name=n) for n in registered if n not in known]
    return [s for s in _order(specs) if s.credentials_present()]


def select(capability: str) -> Provider:
    """Return a live provider, honouring explicit pins then falling back."""
    cfg = settings()
    if cfg.routing_strategy == "explicit":
        pinned = getattr(cfg, f"{capability}_provider", None)
        if pinned:
            return build(capability, pinned)

    errors: list[str] = []
    for spec in candidates(capability):
        try:
            provider = build(capability, spec.name)
            if provider.healthy():
                return provider
            errors.append(f"{spec.name}: unhealthy")
        except Exception as exc:
            errors.append(f"{spec.name}: {exc}")

    raise RuntimeError(
        f"no usable {capability} provider. tried -> " + ("; ".join(errors) or "nothing registered")
    )


def report() -> list[dict[str, Any]]:
    """What /providers shows: configured, reachable, and remaining credit."""
    out: list[dict[str, Any]] = []
    ledger = _ledger()
    for capability in ("llm", "embeddings", "vector", "search", "storage", "obs"):
        registered = available(capability)
        for spec in ledger.get(capability, []) + [
            Spec(name=n) for n in registered if n not in {s.name for s in ledger.get(capability, [])}
        ]:
            reachable = False
            if spec.name in registered and spec.credentials_present():
                try:
                    reachable = build(capability, spec.name).healthy()
                except Exception:
                    reachable = False
            out.append({
                "capability": capability,
                "provider": spec.name,
                "installed": spec.name in registered,
                "credentials": spec.credentials_present(),
                "reachable": reachable,
                "free": spec.free,
                "local": spec.local,
                "cost_per_1k_usd": spec.cost_per_1k,
                "credit_remaining_usd": spec.credit_usd,
            })
    return out
