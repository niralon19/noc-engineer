# noc-mcp config
- `backends.example.yaml` → copy to `backends.yaml` (keep it out of a public repo): URLs, `${ENV}` secrets, PromQL templates for servers/Kafka, rules-system API paths, maintenance source, Jira, history, write gate.
- `pipeline.yaml`: hops + `*_query` templates + KPI queries (filled at work).
- `rule-paths.example.yaml` → `rule-paths.yaml`: rule → servers/topics/services/Argo apps, if the rules system has no API for it.
- `tool-contracts.yaml`: tool names by domain; `implemented:` lists what exists in `tools/`. The Hermes allowlist is `tools.include` in `hermes-profile/config.yaml` (a test checks every included tool is implemented).
