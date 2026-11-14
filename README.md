# noc-engineer

Hermes-based autonomous NOC engineer, on-prem, Docker.

- `hermes-profile/` – version-controlled SOUL.md, config.yaml, skills (sync to the real HERMES_HOME on deploy)
- `noc-mcp/` – single MCP server exposing monitoring, network, Jira tools
- `anomaly-engine/` – deterministic anomaly detection (Python)
- `event-ingestion/` – Grafana/Jira webhooks and polling
- `reporting/` – daily NOC report
- `deployment/`, `docs/`

Start order: Day 0 local-LLM tool-calling test -> profile + MCP + one real investigation -> events -> proactive monitoring -> cron/reporting -> hardening.
