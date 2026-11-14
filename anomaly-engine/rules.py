"""

REQUIRES FROM NIR: K1, K2 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file anomaly-engine/rules.py`; if BLOCKED, ask Nir. Never invent.
Rule loading.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Load and validate rules from config/detection-rules.example.yaml (copy to a real file)
  - Reject rules with REPLACE_WITH_* placeholders; keep enabled: false until metric, units, labels, threshold and owner are verified
  - Produce Rule objects for anomaly_engine.evaluate()

No LLM calls anywhere in anomaly-engine/.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
