from argparse import ArgumentParser
from pathlib import Path

from overcast.mcp_server import main as serve_mcp
from overcast.workspace import WorkspacePaths, initialize_workspace


def main() -> None:
    parser = ArgumentParser(prog="overcast", description="Create local AI podcasts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a user workspace.")
    init_parser.add_argument("workspace", type=Path, help="Path to the user workspace.")
    subparsers.add_parser("serve", help="Run the MCP server over stdio.")

    args = parser.parse_args()

    if args.command == "init":
        workspace_paths = WorkspacePaths(args.workspace)
        try:
            initialize_workspace(workspace_paths)
        except OSError as error:
            message = f"Can't initialize workspace {args.workspace}: {error}\n"
            init_parser.exit(status=1, message=message)

    elif args.command == "serve":
        serve_mcp()
