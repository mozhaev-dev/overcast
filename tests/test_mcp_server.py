import asyncio
import sys

from mcp import Client, StdioServerParameters

from overcast.mcp_server import get_app_info


async def check_app_info_over_mcp() -> None:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-c", "from overcast.mcp_server import main; main()"],
    )

    async with Client(params, read_timeout_seconds=5) as client:
        result = await client.call_tool("get_app_info", {})

    assert result.is_error is False
    assert result.structured_content == {"name": "Overcast", "version": "0.1.0"}


def test_get_app_info_over_mcp() -> None:
    asyncio.run(check_app_info_over_mcp())


def test_get_app_info() -> None:
    expected = {"name": "Overcast", "version": "0.1.0"}
    actual = get_app_info()
    assert actual == expected
