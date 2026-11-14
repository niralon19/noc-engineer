"""noc-mcp tools: changes.

What changed: Argo CD, rollouts, maintenance.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - get_argo_sync_history(apps=None, window) -> sync time, revision, status, OutOfSync/failed
  - get_deployment_history(cluster, namespace=None, service=None, window) -> rollouts in Rancher and OpenShift
  - get_maintenance_windows(servers=None, window) -> planned maintenance/upgrades (source TBD: Jira/calendar/Grafana silences)
  - get_server_versions(servers, window) -> OS/app version changes (upgrade detection)

Rules for every tool in noc-mcp (see docs/tools-contract.md):
  - Return the ToolResult envelope from schemas/common.py: ok, data, error, source, queried_at (UTC ISO), time_range, truncated.
  - Never raise to the caller; map failures to an explicit error {code, message, retryable}.
  - Every outbound call has a timeout and bounded result size (aggregate or paginate; the environment has ~100K series, never one request per series).
  - Read-only unless the module says otherwise. Writes require a permission check (security/) and an audit record.
  - No arbitrary command execution on production hosts, ever.
  - Tool names must match noc-mcp/config/tool-contracts.yaml; if you rename one, update tool-contracts.yaml and tools.include in hermes-profile/config.yaml too.

Read-only. No sync/rollback/restart tools. Ask Nir where maintenance windows are recorded.

Acceptance: unit tests with mocked backends; no network in tests.
"""
