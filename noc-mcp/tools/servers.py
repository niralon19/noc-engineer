"""noc-mcp tools: servers.

Monitored capture servers (read-only).

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - get_server_traffic(servers, window) -> rx/tx rate, utilization
  - get_server_drops(servers, window) -> NIC rx_dropped/missed, kernel drops, capture-app drops
  - get_server_health(servers) -> CPU/softirq, memory, uptime, app status/version
  - compare_servers(feed_or_group, metric, window) -> peer comparison

Rules for every tool in noc-mcp (see docs/tools-contract.md):
  - Return the ToolResult envelope from schemas/common.py: ok, data, error, source, queried_at (UTC ISO), time_range, truncated.
  - Never raise to the caller; map failures to an explicit error {code, message, retryable}.
  - Every outbound call has a timeout and bounded result size (aggregate or paginate; the environment has ~100K series, never one request per series).
  - Read-only unless the module says otherwise. Writes require a permission check (security/) and an audit record.
  - No arbitrary command execution on production hosts, ever.
  - Tool names must match noc-mcp/config/tool-contracts.yaml; if you rename one, update tool-contracts.yaml and tools.include in hermes-profile/config.yaml too.

Never reboot/restart. Drop counters are counters: return rates over the window.

Acceptance: unit tests with mocked backends; no network in tests.
"""
