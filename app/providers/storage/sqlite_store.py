"""Local key/value store on stdlib sqlite3 — zero install, zero cost."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from app.providers.base import Storage
from app.registry import register
from app.settings import settings


@register("storage", "sqlite")
class SqliteStorage(Storage):
    def __init__(self) -> None:
        path = settings().sqlite_path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path), check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)")
        self.conn.commit()

    async def put(self, key: str, value: dict[str, Any]) -> None:
        self.conn.execute("INSERT INTO kv(key, value) VALUES(?, ?) "
                          "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                          (key, json.dumps(value)))
        self.conn.commit()

    async def get(self, key: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else None
