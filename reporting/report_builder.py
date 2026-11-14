"""
Build daily report sections.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Collect last-24h incidents, open/recurring issues, verified root causes, anomalies without alerts, negative trends, data-quality and enrichment problems, at-risk services, Jira tasks needing action, recommendations
  - Separate VERIFIED from SUSPECTED

Numbers come from code; Hermes writes the narrative.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
