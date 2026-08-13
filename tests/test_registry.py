from __future__ import annotations

import pytest

from app import router
from app.registry import available, build, discover


def test_every_capability_has_a_free_option():
    discover()
    for capability in ("llm", "embeddings", "vector", "search", "storage", "obs"):
        assert available(capability), f"{capability} has no registered provider"


def test_echo_llm_always_available():
    provider = build("llm", "echo")
    assert provider.healthy()


@pytest.mark.asyncio
async def test_echo_roundtrip():
    from app.providers.base import Message

    out = await build("llm", "echo").complete([Message("user", "ping")])
    assert "ping" in out.text
    assert out.cost_usd == 0.0


def test_router_never_picks_a_provider_without_credentials(monkeypatch):
    for spec in router.candidates("llm"):
        assert spec.credentials_present()


def test_report_shape():
    rows = router.report()
    assert rows and {"capability", "provider", "free", "cost_per_1k_usd"} <= set(rows[0])
