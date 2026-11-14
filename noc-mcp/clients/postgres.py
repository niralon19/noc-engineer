"""Backend client: postgres.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Read-only Postgres client (health, locks, replication; and the investigation-history store).
  - Read URL/credentials from environment; never hardcode or log secrets.
  - Bounded results and timeouts; raise typed exceptions (tools/* converts them to ToolResult errors).

Acceptance: unit tests with mocked backends; no network in tests.
"""
