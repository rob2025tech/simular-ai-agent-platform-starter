from __future__ import annotations

from pathlib import Path
from typing import Any

from app.tools import tools
from app.tools.base import Tool


@tools.register
class ListFilesTool(Tool):
    name = "filesystem.list"
    description = "List files and directories under a path."

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        path = Path(arguments.get("path", "."))

        if not path.exists():
            return {
                "ok": False,
                "error": f"path does not exist: {path}",
            }

        if not path.is_dir():
            return {
                "ok": False,
                "error": f"path is not a directory: {path}",
            }

        entries = []

        for entry in sorted(path.iterdir(), key=lambda p: p.name.lower()):
            entries.append({
                "name": entry.name,
                "type": "directory" if entry.is_dir() else "file",
            })

        return {
            "ok": True,
            "path": str(path),
            "entries": entries,
        }
