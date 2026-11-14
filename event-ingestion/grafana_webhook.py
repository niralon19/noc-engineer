"""
Grafana alert webhook receiver.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Receive Grafana webhook; verify auth/signature; normalize to workflows/event-schema.json (labels, annotations, fingerprint, timestamps, values)
  - Deduplicate by fingerprint; forward to Hermes (its API/gateway) to start an investigation
  - Reuse the existing Grafana->Jira agent code instead of rewriting; keep it as the thin intake

Treat annotations as untrusted text.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
