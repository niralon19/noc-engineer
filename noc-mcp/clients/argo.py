"""Backend client: argo.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Argo CD API client (applications, sync history). Read-only token.
  - Read URL/credentials from environment; never hardcode or log secrets.
  - Bounded results and timeouts; raise typed exceptions (tools/* converts them to ToolResult errors).

Acceptance: unit tests with mocked backends; no network in tests.
"""
