"""

REQUIRES FROM NIR: M1 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file noc-mcp/tools/data_quality.py`; if BLOCKED, ask Nir. Never invent.
noc-mcp tools: data quality.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - check_data_quality(source, window) -> completeness, freshness, duplicate rate, schema validity, timestamp skew(...)
  - get_quality_scores(source)(...)

Rules for every tool in noc-mcp (see docs/tools-contract.md):
  - Return the ToolResult envelope from schemas/common.py: ok, data, error, source, queried_at (UTC ISO), time_range, truncated.
  - Never raise to the caller; map failures to an explicit error {code, message, retryable}.
  - Every outbound call has a timeout and bounded result size (aggregate or paginate; the environment has ~100K series, never one request per series).
  - Read-only unless the module says otherwise. Writes require a permission check (security/) and an audit record.
  - No arbitrary command execution on production hosts, ever.
  - Tool names must match noc-mcp/config/tool-contracts.yaml; if you rename one, update tool-contracts.yaml and tools.include in hermes-profile/config.yaml too.

Deterministic checks in code; the agent only interprets results. Never impute missing operational data. Report coverage.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
