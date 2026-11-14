"""noc-mcp entry point.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Create the MCP server (use the official Python MCP SDK; add it to pyproject.toml).
  - Register every tool from tools/* using the names in config/tool-contracts.yaml.
  - Load config/allowlist.example.yaml (copy to a real allowlist): deny by default, expose only allowlisted tools.
  - Fail closed at startup if a contracted tool is missing or its schema changed.
  - Expose a health tool/endpoint used by the 1-minute health-check cron.
Do NOT put investigation logic here: MCP is an access layer; Hermes interprets results.
"""


def main() -> None:
    raise NotImplementedError


if __name__ == "__main__":
    main()
