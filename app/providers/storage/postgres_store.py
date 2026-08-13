from __future__ import annotations

import json
from typing import Any

from app.providers.base import Storage
from app.registry import register
from app.settings import settings


@register("storage", "postgres")
class PostgresStorage(Storage):
    def __init__(self) -> None:
        self.dsn = settings().database_url

    def healthy(self) -> bool:
        if not self.dsn:
            return False
        try:
            import psycopg  # noqa: F401
            return True
        except Exception:
            return False

    def _conn(self):
        import psycopg

        conn = psycopg.connect(self.dsn)
        with conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value JSONB)")
        conn.commit()
        return conn

    async def put(self, key: str, value: dict[str, Any]) -> None:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO kv(key, value) VALUES(%s, %s) "
                        "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                        (key, json.dumps(value)))
            conn.commit()

    async def get(self, key: str) -> dict[str, Any] | None:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT value FROM kv WHERE key=%s", (key,))
            row = cur.fetchone()
            return row[0] if row else None
