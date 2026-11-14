"""Backend client: kubernetes.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Kubernetes API client for BOTH clusters (Rancher and OpenShift): deployments, pods, events. Read-only service account per cluster.
  - Read URL/credentials from environment; never hardcode or log secrets.
  - Bounded results and timeouts; raise typed exceptions (tools/* converts them to ToolResult errors).

Acceptance: unit tests with mocked backends; no network in tests.
"""
