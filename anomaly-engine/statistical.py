"""
Statistical detectors.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - z-score / robust (median+MAD) deviation, rate-of-change, slow drift (gradual resource growth), seasonality-aware comparison
  - Pure functions over lists of samples; deterministic; unit-testable

ML is out of scope until there is labeled history.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
