"""

REQUIRES FROM NIR: K2, K3 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file anomaly-engine/statistical.py`; if BLOCKED, ask Nir. Never invent.
Statistical detectors.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - z-score / robust (median+MAD) deviation, rate-of-change, slow drift (gradual resource growth), seasonality-aware comparison
  - Pure functions over lists of samples; deterministic; unit-testable

ML is out of scope until there is labeled history.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
