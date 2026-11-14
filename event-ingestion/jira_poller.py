"""
Jira polling reconciliation (every 2 minutes).

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Poll with a persisted cursor; find issues the webhook missed; idempotent
  - Plain Python, no LLM

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
