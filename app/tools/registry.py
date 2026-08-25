from __future__ import annotations

from typing import Type

from app.tools.base import Tool


class ToolRegistry:
    """Registry of executable agent tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Type[Tool]] = {}

    def register(self, tool: Type[Tool]) -> Type[Tool]:
        if not tool.name:
            raise ValueError("tool name cannot be empty")

        if tool.name in self._tools:
            raise ValueError(f"tool already registered: {tool.name}")

        self._tools[tool.name] = tool
        return tool

    def available(self) -> list[str]:
        return sorted(self._tools)

    def get(self, name: str) -> Tool:
        try:
            tool_cls = self._tools[name]
        except KeyError as exc:
            raise KeyError(f"unknown tool: {name}") from exc

        return tool_cls()

    def descriptions(self) -> list[dict[str, str]]:
        return [
            {
                "name": tool_cls.name,
                "description": tool_cls.description,
            }
            for tool_cls in self._tools.values()
        ]
