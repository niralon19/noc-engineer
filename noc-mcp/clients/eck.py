"""Backend client: ECK (Elasticsearch on Kubernetes).

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Search/aggregation client for log and record indices; always bound by time range, index pattern and size.
  - Cluster health (status, rejected writes, disk watermarks, ILM errors) for platform-operations.
  - Read URL/credentials from environment (deployment/.env.example); never hardcode or log secrets.
  - Raise typed exceptions; tools/* converts them into ToolResult errors.

Acceptance: unit tests with mocked backends; no network in tests.
"""
