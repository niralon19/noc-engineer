# Hermes NOC — Autonomous Operations Engineer

Single primary Hermes agent for on-prem NOC investigation, early anomaly detection, operational coordination and reporting.

## Architecture
- Hermes is the only agent and owns reasoning, skill selection, investigation, recommendations and workflow decisions.
- Existing internal MCP server is the tool-access layer. No second MCP server is created here.
- Python anomaly engine performs deterministic/statistical detection outside the LLM path and publishes normalized events.
- RabbitMQ transports events/workflow messages; PostgreSQL stores incidents, investigation state, evidence references and operational memory.
- Jira enters through webhook plus bounded polling reconciliation. Slack is for notifications/updates; Web Chat remains the primary interactive channel.

## Repository map
`profile/` agent identity; `skills/` seven specializations; `mcp/` tool contracts and allowlist; `workflows/` incident lifecycle and event flows; `cron/` six scheduled jobs; `config/` runtime and detection configuration; `memory/` persistent memory schema; `tests/` architecture contracts.

## Cron design
Data Quality Scan `*/15 * * * *`; Enrichment Audit `*/30 * * * *`; Anomaly Baseline `0 * * * *`; Jira Polling Backup `*/2 * * * *`; NOC Daily Report `0 7 * * *`; Housekeeping `0 2 * * *`. Timezone is explicitly configured (example: Asia/Jerusalem). These are job specifications, not enabled schedules until installed in Hermes Cron or one approved scheduler.

## Start supporting services
```bash
cp .env.example .env
# Replace all example passwords before use
docker compose up -d
```
This starts PostgreSQL and RabbitMQ only. It does not install Hermes or connect to internal MCP, Prometheus/Thanos, Grafana, Loki/ECK, Jira or Slack.

## Integration sequence
1. Inspect the installed Hermes version and profile layout; merge `profile/` configuration without overwriting existing config.
2. Discover actual internal MCP tool names/schemas. Populate `mcp/allowlist.example.yaml` with verified names; default deny.
3. Decide whether metrics collection uses a read-only Prometheus/Thanos API or MCP batch tools. Do not issue one request per series; benchmark bounded batches for the ~100K-series environment.
4. Implement/enable Python detector, RabbitMQ publisher/consumer, idempotency, retry and DLQ.
5. Configure Jira webhook signature verification and polling cursor; connect Slack notification adapter.
6. Register Cron jobs with one scheduler only; verify timezone and delivery destinations.
7. Load test, test failure/recovery, backups, audit and approval controls before production.

## Production status
This repository is an implementation scaffold with explicit contracts and schedules, not a production-ready deployment. MCP endpoint/tool schemas, Jira project/workflow, Slack workspace, Hermes version, Prometheus limits, identity provider, secrets manager and operational runbooks must be supplied by the environment owner. Do not commit internal addresses, topology, logs or credentials. Keep the repository private before adding environment-specific data.
