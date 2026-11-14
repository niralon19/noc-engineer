"""Backend client: rules.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Client for the rule & configuration management system (API or read-only DB).
  - Read URL/credentials from environment; never hardcode or log secrets.
  - Bounded results and timeouts; raise typed exceptions (tools/* converts them to ToolResult errors).

Acceptance: unit tests with mocked backends; no network in tests.
"""
