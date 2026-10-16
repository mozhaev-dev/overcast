from typing import TypedDict

from mcp.server.mcpserver import MCPServer

server = MCPServer(name="Overcast")


class AppInfo(TypedDict):
    name: str
    version: str


@server.tool()
def get_app_info() -> AppInfo:
    """Return application name and version"""
    return {"name": "Overcast", "version": "0.1.0"}


def main() -> None:
    server.run(transport="stdio")
