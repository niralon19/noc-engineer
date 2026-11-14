"""
Evidence record referenced by investigations.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - Evidence: id, kind(metric|log|jira|network|change), source, query, time_range, observed_at, freshness_seconds, summary, raw_ref
  - Every finding in schemas/investigation.py must point to evidence ids.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
