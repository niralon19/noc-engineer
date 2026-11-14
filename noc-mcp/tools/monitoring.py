"""
noc-mcp tools: monitoring.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - query_metrics(query, start, end, step) -> aggregated series via clients/prometheus.py or thanos.py(...)
  - query_logs(query, start, end, limit) -> via clients/eck.py (Elasticsearch on ECK; aggregations, bounded)(...)
  - get_alerts(state, labels) -> active/firing Grafana alerts(...)
  - get_metric_history(metric, selector, window) -> downsampled history(...)
  - get_service_health(service) -> combined up/latency/error summary(...)
  - compare_baseline(metric, selector, window) -> current vs baseline with deviation(...)

Rules for every tool in noc-mcp (see docs/tools-contract.md):
  - Return the ToolResult envelope from schemas/common.py: ok, data, error, source, queried_at (UTC ISO), time_range, truncated.
  - Never raise to the caller; map failures to an explicit error {code, message, retryable}.
  - Every outbound call has a timeout and bounded result size (aggregate or paginate; the environment has ~100K series, never one request per series).
  - Read-only unless the module says otherwise. Writes require a permission check (security/) and an audit record.
  - No arbitrary command execution on production hosts, ever.
  - Tool names must match noc-mcp/config/tool-contracts.yaml; if you rename one, update tool-contracts.yaml and tools.include in hermes-profile/config.yaml too.

Always return the exact query and time window used so the agent can cite it as evidence. Return units and label sets. Report missing samples instead of interpolating.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
