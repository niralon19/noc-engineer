"""noc-mcp tools: rules.

Rule & configuration management system (read-only).

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - get_rule(rule_id) -> definition, scope, owner, status, version
  - get_rule_path(rule_id) -> servers, Kafka topics, services (cluster), enrichment sources that serve the rule
  - get_rule_changes(rule_id=None, window) -> who/when/what diff, including overlapping and global config changes
  - find_overlapping_rules(rule_id) -> rules whose scope intersects
  - validate_rule_change(rule_id, proposed) -> validation result only if the system offers a dry-run API; never apply
  - get_rule_kpis(rule_id, window) -> hermeticity and coupling series vs baseline (definitions in config/pipeline.yaml)

Rules for every tool in noc-mcp (see docs/tools-contract.md):
  - Return the ToolResult envelope from schemas/common.py: ok, data, error, source, queried_at (UTC ISO), time_range, truncated.
  - Never raise to the caller; map failures to an explicit error {code, message, retryable}.
  - Every outbound call has a timeout and bounded result size (aggregate or paginate; the environment has ~100K series, never one request per series).
  - Read-only unless the module says otherwise. Writes require a permission check (security/) and an audit record.
  - No arbitrary command execution on production hosts, ever.
  - Tool names must match noc-mcp/config/tool-contracts.yaml; if you rename one, update tool-contracts.yaml and tools.include in hermes-profile/config.yaml too.

Ask Nir: does the rule system have an API with change history and dry-run? If not, read from its DB read-only. Never expose create/update/delete of rules.

Acceptance: unit tests with mocked backends; no network in tests.
"""
