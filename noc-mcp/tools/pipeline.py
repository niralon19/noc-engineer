"""noc-mcp tools: pipeline.

Data-path tools used by the pipeline-walk skill.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - get_hop_counts(hop, rule_id=None, scope=None, window, compare=['1d','7d']) -> IN/OUT/drop counts per instance + baselines
  - get_pipeline_map() -> hops from config/pipeline.yaml (ids, descriptions, which are per-rule)

Rules for every tool in noc-mcp (see docs/tools-contract.md):
  - Return the ToolResult envelope from schemas/common.py: ok, data, error, source, queried_at (UTC ISO), time_range, truncated.
  - Never raise to the caller; map failures to an explicit error {code, message, retryable}.
  - Every outbound call has a timeout and bounded result size (aggregate or paginate; the environment has ~100K series, never one request per series).
  - Read-only unless the module says otherwise. Writes require a permission check (security/) and an audit record.
  - No arbitrary command execution on production hosts, ever.
  - Tool names must match noc-mcp/config/tool-contracts.yaml; if you rename one, update tool-contracts.yaml and tools.include in hermes-profile/config.yaml too.

Counts for all hops must use the same window and scope. Missing metric for a hop -> explicit error 'hop_not_instrumented', never zero.

Acceptance: unit tests with mocked backends; no network in tests.
"""
