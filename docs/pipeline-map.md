# Pipeline map (the most important document for investigations)

> **REQUIRES FROM NIR: E1, E2, E3, E4, E5 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file docs/pipeline-map.md`; if BLOCKED, ask Nir. Never invent.**

> LLM/DEVELOPER: fill from Nir at work. Source of truth for code is `noc-mcp/config/pipeline.yaml`; keep this file and the YAML in sync. Never commit hostnames, IPs or internal metric names while the repo is public.

Every customer-facing problem in this environment ends up as a **hermeticity** or **coupling** problem of a **rule**, but the cause can be any hop on a long path. The agent localizes by walking the path and finding the **first hop where IN and OUT diverge** (bisection), instead of summarizing tool outputs.

## Hops (proposed default, verify)
| # | Hop id | What | IN / OUT measure | Typical failures |
|---|---|---|---|---|
| 1 | `ingress_traffic` | Traffic arriving at the servers | TBD | upstream change, mirror/tap down, routing |
| 2 | `server_nic` | Server NIC | TBD | rx_dropped, ring buffer, saturation |
| 3 | `capture_app` | App on the server | TBD | crash, CPU, version after upgrade |
| 4 | `kafka_ingest` | Kafka topics | TBD | lag, rebalance, partition skew, retention |
| 5 | `stream_processing` | K8s services (Rancher/OpenShift) | TBD | rollout, OOM, throttling, Argo sync |
| 6 | `internal_enrichment` | Internal enrichment (coupling) | TBD | stale/missing enrichment source |
| 7 | `rule_matching` | Rule evaluation | TBD | rule/config change, overlapping rule |
| 8 | `storage_postgres` / `storage_eck` | Persistence/indexing | TBD | write errors, index/ILM, disk |
| 9 | `output` | What the customer sees | TBD | export/consumer side |

## KPIs
- **Hermeticity** of a rule: TBD (definition and where measured).
- **Coupling** of a rule: TBD (definition, enrichment source, where measured).

## Questions to answer at work
1. Real hop order and names (components only).
2. Which hops have per-rule counts; for the others, how to scope by rule (servers/topics the rule uses).
3. Metric or query for IN/OUT at each hop (Prometheus, Kafka exporter, Postgres, ECK).
4. Which servers/topics/services serve a given rule (needed for `get_rule_path`).
