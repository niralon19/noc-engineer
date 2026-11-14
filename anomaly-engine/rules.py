"""
Rule loading.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Load and validate rules from config/detection-rules.example.yaml (copy to a real file)
  - Reject rules with REPLACE_WITH_* placeholders; keep enabled: false until metric, units, labels, threshold and owner are verified
  - Produce Rule objects for anomaly_engine.evaluate()

No LLM calls anywhere in anomaly-engine/.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
