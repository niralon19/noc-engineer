"""

REQUIRES FROM NIR: L3, H1, H2 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file event-ingestion/jira_poller.py`; if BLOCKED, ask Nir. Never invent.
Jira polling reconciliation (every 2 minutes).

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Poll with a persisted cursor; find issues the webhook missed; idempotent
  - Plain Python, no LLM

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
