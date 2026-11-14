"""
Backend client: thanos.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Thanos Query client for long-range/historical queries. Same interface as prometheus.py.
  - Read URL/credentials from environment (deployment/.env.example); never hardcode or log secrets.
  - Raise typed exceptions; tools/* converts them into ToolResult errors.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
