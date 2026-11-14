"""Backend client: kafka.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Kafka admin/metrics client (consumer groups, lag, broker health). Prefer exporter metrics via Prometheus.
  - Read URL/credentials from environment; never hardcode or log secrets.
  - Bounded results and timeouts; raise typed exceptions (tools/* converts them to ToolResult errors).

Acceptance: unit tests with mocked backends; no network in tests.
"""
