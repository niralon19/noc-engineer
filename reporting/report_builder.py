"""

REQUIRES FROM NIR: N1, N2 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file reporting/report_builder.py`; if BLOCKED, ask Nir. Never invent.
Build daily report sections.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Collect last-24h incidents, open/recurring issues, verified root causes, anomalies without alerts, negative trends, data-quality and enrichment problems, at-risk services, Jira tasks needing action, recommendations
  - Separate VERIFIED from SUSPECTED

Numbers come from code; Hermes writes the narrative via the oncall-report skill.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
