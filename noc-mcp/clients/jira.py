"""
Backend client: jira.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Thin Jira REST client (auth from env). No business logic: tools/jira.py owns policy. Reuse the user's existing Jira code if available.
  - Read URL/credentials from environment (deployment/.env.example); never hardcode or log secrets.
  - Raise typed exceptions; tools/* converts them into ToolResult errors.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
