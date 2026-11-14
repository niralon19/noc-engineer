"""noc-mcp: the NOC investigation tools for Hermes (MCP server).

Run:  python noc-mcp/server.py                      # stdio (Hermes spawns it: mcp_servers.noc_mcp.command/args)
      python noc-mcp/server.py --http --port 8765   # streamable HTTP (Hermes connects with mcp_servers.noc_mcp.url)
Config: NOC_MCP_CONFIG (backends.yaml), NOC_MCP_PIPELINE (pipeline.yaml). Secrets from the environment.
Works with the official MCP Python SDK v2 (MCPServer), v1 (FastMCP) or the standalone `fastmcp` package.

If the team's existing FastMCP server is the one Hermes uses, import `register(server)` from here into it instead.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import changes, health, investigation, jira, kafka, monitoring, pipeline, rules, servers  # noqa: E402,F401
from tools._base import REGISTRY, WRITE_TOOLS  # noqa: E402

INSTRUCTIONS = ("NOC investigation tools. Read-only except add_investigation_comment. Every result has ok/error/source/"
                "time_range; error.code 'not_configured' or 'hop_not_instrumented' means missing data, never 'healthy'.")


def _server_class():
    try:
        from mcp.server.mcpserver import MCPServer          # MCP SDK v2
        return MCPServer
    except ImportError:
        pass
    try:
        from mcp.server.fastmcp import FastMCP               # MCP SDK v1
        return FastMCP
    except ImportError:
        from fastmcp import FastMCP                          # standalone fastmcp
        return FastMCP


def register(server) -> list[str]:
    """Register every noc-mcp tool on an existing FastMCP/MCPServer instance."""
    for name, fn in sorted(REGISTRY.items()):
        server.tool(name=name)(fn)
    return sorted(REGISTRY)


def build():
    try:
        server = _server_class()("noc_mcp", instructions=INSTRUCTIONS)
    except TypeError:
        server = _server_class()("noc_mcp")
    register(server)
    return server


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--http", action="store_true", help="serve streamable HTTP instead of stdio")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--list", action="store_true", help="print registered tools and exit")
    a = ap.parse_args()
    if a.list:
        for n in sorted(REGISTRY):
            print(n + ("  [write]" if n in WRITE_TOOLS else ""))
        return
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    server = build()
    if a.http:
        try:                                              # SDK v2: options passed to run()
            server.run(transport="streamable-http", host=a.host, port=a.port)
        except TypeError:                                 # SDK v1 / fastmcp: options on settings
            server.settings.host, server.settings.port = a.host, a.port
            server.run(transport="streamable-http")
    else:
        server.run(transport="stdio")


if __name__ == "__main__":
    main()
