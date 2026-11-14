"""
noc-mcp tools: investigation history.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - search_investigations(filters)(...)
  - get_investigation(investigation_id)(...)
  - compare_investigations(id_a, id_b)(...)
  - get_related_incidents(target, window)(...)
  - get_service_dependencies(service)(...)

Rules for every tool in noc-mcp (see docs/tools-contract.md):
  - Return the ToolResult envelope from schemas/common.py: ok, data, error, source, queried_at (UTC ISO), time_range, truncated.
  - Never raise to the caller; map failures to an explicit error {code, message, retryable}.
  - Every outbound call has a timeout and bounded result size (aggregate or paginate; the environment has ~100K series, never one request per series).
  - Read-only unless the module says otherwise. Writes require a permission check (security/) and an audit record.
  - No arbitrary command execution on production hosts, ever.
  - Tool names must match noc-mcp/config/tool-contracts.yaml; if you rename one, update tool-contracts.yaml and tools.include in hermes-profile/config.yaml too.

Results use schemas/investigation.py. Storage starts as files or the existing store; PostgreSQL only if search/correlation needs it (see docs/memory.md). Similarity to a past incident is a hint, not proof.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
