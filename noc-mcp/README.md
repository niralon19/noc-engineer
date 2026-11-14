# noc-mcp: the investigation tools

MCP server with the tools Hermes needs for `change-correlation` and `pipeline-walk`. Read-only except one gated write.
Everything environment-specific (URLs, metric names, rule-system API paths) comes from config; anything left `TBD`
returns `error.code = not_configured` / `hop_not_instrumented`, never a guessed value.

## Run
```bash
pip install -r noc-mcp/requirements.txt          # mcp, requests, pyyaml
python noc-mcp/server.py --list                  # registered tools
python noc-mcp/server.py                         # stdio (Hermes spawns it)
python noc-mcp/server.py --http --port 8765      # streamable HTTP at /mcp (k8s: deployment/k8s/noc-mcp.yaml)
```
Config: `NOC_MCP_CONFIG` → `config/backends.yaml` (copy from `backends.example.yaml`), `NOC_MCP_PIPELINE` → `config/pipeline.yaml`,
`config/rule-paths.yaml` (copy from example) if the rules system has no "rule → path" API. Secrets via `${ENV}` in the YAML.

Already have a FastMCP server at work? `from server import register; register(your_server)` adds all tools to it.

## Tools
| Tool | What it answers | Needs (config) |
|---|---|---|
| `get_pipeline_map` | Hops in order, which are instrumented, KPI definitions | `pipeline.yaml` |
| `get_hop_counts` | IN/OUT/DROP/LAG/MATCHED at one hop, per instance, vs 1d/7d; ratios + divergence hints | hop `*_query` templates, Prometheus/Thanos |
| `get_rule` | Rule definition | `rules.get_rule_path` |
| `get_rule_path` | Servers, topics, consumer groups, services, enrichment, Argo apps serving a rule | `rules.rule_path_path` or `rule-paths.yaml` |
| `get_rule_changes` | Rule + global config changes in a window | `rules.changes_path`, `global_changes_path`, `change_fields` |
| `get_rule_kpis` | Hermeticity / coupling series + window value vs baselines | `kpis.*.query` |
| `get_argo_sync_history` | Argo CD deploys in window, sync/health, last operation | `argocd.url/token` |
| `get_deployment_history` | Rollouts (new ReplicaSets) on `openshift` / `rancher` | `kubernetes.clusters.*` |
| `get_maintenance_windows` | Maintenance/upgrades overlapping the window, by server | `maintenance.source` (grafana_silences / jira) |
| `get_server_drops` | NIC/kernel/app drops and load per server vs baseline | `server_queries.*` |
| `get_consumer_lag` | Lag per partition: start/end/max/trend | `kafka_queries.consumer_lag_by_partition` |
| `query_metrics` | Bounded PromQL range query (Thanos for old windows) | Prometheus |
| `query_logs` | ECK search + terms agg with `first_seen` | `elasticsearch.*` |
| `search_investigations` | Past investigations by rule/fingerprint/hop/text | `history.path` |
| `get_issue`, `search_issues` | Jira reads | `jira.*` |
| `add_investigation_comment` | **WRITE**: posts a validated investigation once (dedup marker), audited | `security.allow_writes=true` |
| `noc_mcp_health` | What is configured; which hops are instrumented | - |

## Guarantees
- Result envelope on every call: `ok, data, error{code,message,retryable}, source, queried_at, time_range, truncated, notes`; never raises.
- Timeouts, 5 MB body cap, ~20 KB result cap, series/hit caps; Thanos automatically for windows older than local retention.
- `add_investigation_comment` refuses output that fails `Investigation.validate()` (hop must exist, evidence cited, ruled_out for CONFIRMED, next_check otherwise) and is disabled unless the server allows writes. Every write attempt is audited without secrets.
- Tests: `python3 -m pytest -q tests` (offline fake backends + real MCP stdio/HTTP smoke checked manually).
