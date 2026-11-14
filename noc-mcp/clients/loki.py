"""
Backend client: loki.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Loki (and/or ELK/ECK) log query client. Always cap lines and time range.
  - Read URL/credentials from environment (deployment/.env.example); never hardcode or log secrets.
  - Raise typed exceptions; tools/* converts them into ToolResult errors.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
