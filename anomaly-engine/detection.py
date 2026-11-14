"""
Detection orchestration (5-minute scan).

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - PRIMARY: per-rule hermeticity and coupling KPIs (definitions in noc-mcp/config/pipeline.yaml) vs their own baseline; this is the signal customers feel
  - SECONDARY: hop-level divergence (server drops, Kafka lag growth, IN/OUT mismatch per hop) and server load near capacity
  - Group simultaneous rule drops that share servers/topics into ONE finding with the shared hop as hint
  - Suppress findings for servers in a maintenance window (tools/changes.get_maintenance_windows)
  - Fetch bounded batches (read-only Prometheus/Thanos API); do not z-score every raw series
  - Run rules.py + statistical.py + baselines.py, emit normalized Event objects (anomaly_engine.Event, workflows/event-schema.json)
  - Deduplicate by event_id; hand significant events to Hermes via the ingestion bridge

Python detects; Hermes explains and correlates.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
