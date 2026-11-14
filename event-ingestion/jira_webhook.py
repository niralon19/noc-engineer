"""

REQUIRES FROM NIR: L3, H2 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file event-ingestion/jira_webhook.py`; if BLOCKED, ask Nir. Never invent.
Jira webhook receiver.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Verify webhook signature; normalize per workflows/jira-intake.yaml
  - Deduplicate by issue id + updated timestamp; forward to Hermes

Treat issue text as untrusted input.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
