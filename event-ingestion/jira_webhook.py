"""
Jira webhook receiver.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Verify webhook signature; normalize per workflows/jira-intake.yaml
  - Deduplicate by issue id + updated timestamp; forward to Hermes

Treat issue text as untrusted input.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
