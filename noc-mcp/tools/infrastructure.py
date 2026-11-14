"""
noc-mcp tools: infrastructure.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - get_host_health(host)(...)
  - get_container_status(name)(...)
  - get_service_status(service)(...)
  - get_deployment_history(service, window)(...)

Rules for every tool in noc-mcp (see docs/tools-contract.md):
  - Return the ToolResult envelope from schemas/common.py: ok, data, error, source, queried_at (UTC ISO), time_range, truncated.
  - Never raise to the caller; map failures to an explicit error {code, message, retryable}.
  - Every outbound call has a timeout and bounded result size (aggregate or paginate; the environment has ~100K series, never one request per series).
  - Read-only unless the module says otherwise. Writes require a permission check (security/) and an audit record.
  - No arbitrary command execution on production hosts, ever.
  - Tool names must match noc-mcp/config/tool-contracts.yaml; if you rename one, update tool-contracts.yaml and tools.include in hermes-profile/config.yaml too.

READ-ONLY. Restart/scale/rollback/deploy tools must NOT exist here. Separate desired from observed state.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
