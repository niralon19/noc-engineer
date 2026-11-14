"""
Backend client: prometheus.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Prometheus HTTP API client (instant/range queries). Bounded batches, timeout, retry with backoff.
  - Read URL/credentials from environment (deployment/.env.example); never hardcode or log secrets.
  - Raise typed exceptions; tools/* converts them into ToolResult errors.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
