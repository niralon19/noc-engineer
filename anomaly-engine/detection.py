"""
Detection orchestration (5-minute scan).

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Fetch bounded batches of metrics (read-only Prometheus/Thanos API; benchmark batch size for ~100K series)
  - Run rules.py + statistical.py + baselines.py, emit normalized Event objects (anomaly_engine.Event, workflows/event-schema.json)
  - Deduplicate by event_id; hand significant events to Hermes via the ingestion bridge

Python detects; Hermes explains and correlates.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
