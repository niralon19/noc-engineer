"""

REQUIRES FROM NIR: N1, D2 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file reporting/daily_report.py`; if BLOCKED, ask Nir. Never invent.
Daily NOC report entry (07:00 Asia/Jerusalem).

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Call report_builder, ask Hermes for the narrative, deliver to Slack/web
  - Run via deployment/cron/noc-daily-report.yaml in exactly one scheduler

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
