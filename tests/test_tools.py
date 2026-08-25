import pytest

from app.tools import tools


@pytest.mark.asyncio
async def test_list_files():
    tool = tools.get("filesystem.list")

    result = await tool.execute({"path": "."})

    assert result["ok"] is True
    assert any(
        entry["name"] == "app"
        for entry in result["entries"]
    )


def test_filesystem_tool_registered():
    assert "filesystem.list" in tools.available()
