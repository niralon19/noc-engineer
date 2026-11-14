"""

REQUIRES FROM NIR: K3, C3 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file anomaly-engine/baselines.py`; if BLOCKED, ask Nir. Never invent.
Baseline computation.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Hourly baseline per metric/entity (the anomaly-baseline cron job)
  - Persist baselines in a file/DB store; expose lookup for compare_baseline in noc-mcp
  - Handle cold start (insufficient history -> no baseline, never fake one)

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
